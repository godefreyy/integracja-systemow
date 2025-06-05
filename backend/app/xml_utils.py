from lxml import etree
from datetime import date
from decimal import Decimal
from .models import db, Region, PropertyType, InterestRate, HousingPrice

# ---------- PARSE ----------
def import_stream(file_stream):
    tree = etree.parse(file_stream)
    root = tree.getroot()

    # interest rates
    for rate in root.xpath("./interestRates/rate"):
        d = date.fromisoformat(rate.get("date"))
        v = Decimal(rate.get("value"))
        obj = InterestRate.query.filter_by(rate_date=d).first() \
              or InterestRate(rate_date=d)
        obj.value = v
        db.session.merge(obj)

    # housing prices
    for price in root.xpath("./housingPrices/price"):
        region = _get_or_create(Region, name=price.get("region"))
        ptype  = _get_or_create(PropertyType, name=price.get("type"))
        db.session.add(HousingPrice(
            quarter       = price.get("quarter"),
            average_price = Decimal(price.get("average")),
            region        = region,
            type          = ptype
        ))
    db.session.commit()

def _get_or_create(model, **kw):
    instance = model.query.filter_by(**kw).first()
    if instance:
        return instance
    instance = model(**kw)
    db.session.add(instance)
    db.session.flush()          # get id
    return instance


# ---------- GENERATE ----------
def export_stream():
    root = etree.Element("dataset")

    ir_el = etree.SubElement(root, "interestRates")
    for ir in InterestRate.query.order_by(InterestRate.rate_date):
        etree.SubElement(
            ir_el, "rate",
            date=str(ir.rate_date),
            value=str(ir.value)
        )

    hp_el = etree.SubElement(root, "housingPrices")
    for hp in HousingPrice.query:
        etree.SubElement(
            hp_el, "price",
            region=hp.region.name,
            type=hp.type.name,
            quarter=hp.quarter,
            average=str(hp.average_price)
        )
    return etree.tostring(root, xml_declaration=True, encoding="utf-8")
