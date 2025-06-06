import json, yaml
from datetime import date
from decimal import Decimal
from io import BytesIO
from .models import db, Region, PropertyType, HousingPrice, InterestRate

# helpers  

def _money(v):          # str | float | Decimal  →  Decimal
    from decimal import Decimal
    return v if isinstance(v, Decimal) else Decimal(str(v))

def _get_or_create(model, **kw):
    obj = model.query.filter_by(**kw).first()
    if obj:
        return obj
    obj = model(**kw)
    db.session.add(obj)
    return obj


# EXPORT 

def _export_rates():
    return [
        {"year": ir.rate_date.year, "month": ir.rate_date.month, "value": str(ir.value)}
        for ir in InterestRate.query.order_by(InterestRate.rate_date)
    ]

def _export_prices():
    return [
        {
            "year":   int(hp.quarter),
            "market": hp.type.name,
            "city":   hp.region.name,
            "price_m2": str(hp.average_price),
        }
        for hp in HousingPrice.query.order_by(HousingPrice.quarter)
    ]

def dump_json() -> bytes:
    return json.dumps(
        {"prices": _export_prices(), "rates": _export_rates()},
        indent=2, ensure_ascii=False
    ).encode("utf-8")

def dump_yaml() -> bytes:
    return yaml.safe_dump(
        yaml.safe_load(dump_json().decode("utf-8")),
        sort_keys=False, allow_unicode=True
    ).encode("utf-8")


# IMPORT  

def _import_prices(items):
    for item in items:
        region = _get_or_create(Region,       name=item["city"])
        market = _get_or_create(PropertyType, name=item["market"])
        hp = HousingPrice.query.filter_by(
            quarter=str(item["year"]), region=region, type=market
        ).first() or HousingPrice(
            quarter=str(item["year"]), region=region, type=market
        )
        hp.average_price = _money(item["price_m2"])
        db.session.add(hp)

def _import_rates(items):
    for item in items:
        y, m, val = int(item["year"]), int(item.get("month", 1)), item["value"]
        d = date(y, m, 1)
        ir = InterestRate.query.filter_by(rate_date=d).first() or InterestRate(rate_date=d)
        ir.value = _money(val)
        db.session.add(ir)

def load_json(stream):
    data = json.load(stream)

    if isinstance(data, list):
        _import_prices(data)
        db.session.commit()
        return

    if "prices" in data:
        _import_prices(data["prices"])
    if "rates" in data:
        _import_rates(data["rates"])

    if "housingPrices" in data:
        _import_prices(data["housingPrices"])
    if "interestRates" in data:
        _import_rates(data["interestRates"])

    db.session.commit()

def load_yaml(stream):
    load_json(BytesIO(json.dumps(yaml.safe_load(stream)).encode("utf-8")))
