import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from .models import db, Region, PropertyType, InterestRate, HousingPrice


# IMPORT   

def import_stream(stream):
    """Wczytaj XML i uaktualnij bazę (upsert)."""
    tree = ET.parse(stream)
    root = tree.getroot()

    # ceny procentowe 
    for node in root.find("interestRates") or []:
        d = date.fromisoformat(node.get("date"))
        ir = InterestRate.query.filter_by(rate_date=d).first() or InterestRate(rate_date=d)
        ir.value = Decimal(node.get("value"))
        db.session.add(ir)

    # ceny mieszkan
    for node in root.find("housingPrices") or []:
        region = _get_or_create(Region,       name=node.get("region"))
        ptype  = _get_or_create(PropertyType, name=node.get("type"))
        hp = HousingPrice.query.filter_by(
            quarter=node.get("quarter"), region=region, type=ptype
        ).first() or HousingPrice(
            quarter=node.get("quarter"), region=region, type=ptype
        )
        hp.average_price = Decimal(node.get("average"))
        db.session.add(hp)

    db.session.commit()


def _get_or_create(model, **kw):
    obj = model.query.filter_by(**kw).first()
    if obj:
        return obj
    obj = model(**kw)
    db.session.add(obj)
    return obj

# EXPORT 

def export_stream() -> bytes:
    """Zbuduj XML z aktualnej zawartości DB i zwróć jako bytes."""
    root = ET.Element("dataset")

    # stopy procentowe
    irs = ET.SubElement(root, "interestRates")
    for ir in InterestRate.query.order_by(InterestRate.rate_date):
        ET.SubElement(
            irs,
            "rate",
            date=ir.rate_date.isoformat(),
            value=str(ir.value),
        )

    # ceny mieszkan
    hps = ET.SubElement(root, "housingPrices")
    for hp in HousingPrice.query.order_by(HousingPrice.quarter):
        ET.SubElement(
            hps,
            "price",
            region=hp.region.name,
            type=hp.type.name,
            quarter=hp.quarter,
            average=str(hp.average_price),
        )

    #PRETTY PRINT
    tree = ET.ElementTree(root)

    try:                                    
        ET.indent(tree, space="  ", level=0)
        return ET.tostring(
            root, encoding="utf-8", xml_declaration=True
        )
    except AttributeError:                 
        import xml.dom.minidom as minidom
        rough = ET.tostring(root, encoding="utf-8")
        dom = minidom.parseString(rough)
        return dom.toprettyxml(indent="  ", encoding="utf-8")
