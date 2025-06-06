from datetime import datetime
from decimal import Decimal
from io import BytesIO

from lxml import etree
from .models import db, Region, PropertyType, InterestRate, HousingPrice


# ---------------------------------------------------------------------------
# XML  ➜  DATABASE
# ---------------------------------------------------------------------------
def import_stream(stream):
    """
    Parse uploaded XML and upsert rows into MySQL.
    """
    root = etree.parse(stream).getroot()

    # -------- Interest rates ------------------------------------------------
    for rate_el in root.xpath("./interestRates/rate"):
        date_str = rate_el.attrib["date"]
        value_str = rate_el.attrib["value"]

        d = datetime.fromisoformat(date_str).date()
        v = Decimal(value_str)

        obj = (
            InterestRate.query.filter_by(rate_date=d).first()
            or InterestRate(rate_date=d)
        )
        obj.value = v
        db.session.add(obj)

    # -------- Housing prices ------------------------------------------------
    for price_el in root.xpath("./housingPrices/price"):
        region_name = price_el.attrib["region"]
        type_name = price_el.attrib["type"]
        quarter = price_el.attrib["quarter"]
        average = Decimal(price_el.attrib["average"])

        region = Region.query.filter_by(name=region_name).first() or Region(name=region_name)
        ptype  = PropertyType.query.filter_by(name=type_name).first() or PropertyType(name=type_name)

        db.session.add_all([region, ptype])
        db.session.flush()  # make sure IDs are available

        hp = HousingPrice(
            region=region,
            type=ptype,
            quarter=quarter,
            average_price=average,
        )
        db.session.add(hp)

    db.session.commit()


# ---------------------------------------------------------------------------
# DATABASE  ➜  XML
# ---------------------------------------------------------------------------
def export_stream():
    root = etree.Element("dataset")

    # interestRates
    ir_wrapper = etree.SubElement(root, "interestRates")
    for ir in InterestRate.query.order_by(InterestRate.rate_date).all():
        node = etree.SubElement(ir_wrapper, "rate")
        node.set("date", ir.rate_date.isoformat())
        node.set("value", str(ir.value))

    # housingPrices
    hp_wrapper = etree.SubElement(root, "housingPrices")
    for hp in HousingPrice.query.all():
        node = etree.SubElement(hp_wrapper, "price")
        node.set("region", hp.region.name)
        node.set("type", hp.type.name)           # <-- matches models.py
        node.set("quarter", hp.quarter)
        node.set("average", f"{hp.average_price:.2f}")

    # pretty-print XML
    xml_bytes = etree.tostring(
        root,
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=True
    )
    return xml_bytes
