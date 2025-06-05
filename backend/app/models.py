from . import db

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class PropertyType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

class InterestRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate_date = db.Column(db.Date, nullable=False, unique=True)
    value = db.Column(db.Numeric(5,2), nullable=False)

class HousingPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(7), nullable=False)           # e.g. 2024Q4
    average_price = db.Column(db.Numeric(12,2), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"))
    type_id   = db.Column(db.Integer, db.ForeignKey("property_type.id"))

    region = db.relationship("Region")
    type   = db.relationship("PropertyType")
