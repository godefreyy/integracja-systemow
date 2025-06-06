import json
import yaml
from datetime import date
from decimal import Decimal
from io import BytesIO
from .models import db, Region, PropertyType, InterestRate, HousingPrice


# helpers 


def _money(value: str | Decimal):
    """Convert str → Decimal or just pass Decimal through."""
    if isinstance(value, Decimal):
        return value
    return Decimal(value)


def _get_or_create(model, **filters):
    """Return existing row or create a new one."""
    obj = model.query.filter_by(**filters).first()
    if obj:
        return obj
    obj = model(**filters)
    db.session.add(obj)
    return obj


# EXPORT


def dump_json() -> bytes:
    """Return a JSON document (bytes) representing current DB snapshot."""
    payload = {
        "interestRates": [
            {
                "date": ir.rate_date.isoformat(),
                "value": str(ir.value),
            }
            for ir in InterestRate.query.order_by(InterestRate.rate_date)
        ],
        "housingPrices": [
            {
                "region": hp.region.name,
                "type": hp.type.name,
                "quarter": hp.quarter,
                "average": str(hp.average_price),
            }
            for hp in HousingPrice.query.order_by(HousingPrice.quarter)
        ],
    }
    return json.dumps(payload, indent=2).encode("utf-8")


def dump_yaml() -> bytes:
    """Return a YAML document (bytes) representing current DB snapshot."""
    payload = yaml.safe_dump(
        yaml.safe_load(dump_json().decode("utf-8")),
        sort_keys=False,
        allow_unicode=True,
    )
    return payload.encode("utf-8")


# IMPORT 


def load_json(stream):
    """
    Read a JSON stream and upsert rows in all four tables.
    Every entry is inserted if missing; duplicates are ignored.
    """
    content = json.load(stream)
    if "dataset" in content:
        content = content["dataset"]

    for item in content.get("interestRates", []):
        ir = InterestRate.query.filter_by(
            rate_date=date.fromisoformat(item["date"])
        ).first() or InterestRate(
            rate_date=date.fromisoformat(item["date"])
        )
        ir.value = _money(item["value"])
        db.session.add(ir)

    for item in content.get("housingPrices", []):
        region = _get_or_create(Region, name=item["region"])
        ptype = _get_or_create(PropertyType, name=item["type"])
        hp = HousingPrice.query.filter_by(
            quarter=item["quarter"],
            region=region,
            type=ptype,
        ).first() or HousingPrice(
            quarter=item["quarter"],
            region=region,
            type=ptype,
        )
        hp.average_price = _money(item["average"])
        db.session.add(hp)

    db.session.commit()


def load_yaml(stream):
    """Read YAML stream, convert to JSON dict and reuse load_json()."""
    data = yaml.safe_load(stream)
    if "dataset" in data:
        data = data["dataset"]
    load_json(BytesIO(json.dumps(data).encode("utf-8")))
