from datetime import date
from decimal import Decimal
from app import db


class Region(db.Model):
    __tablename__ = "region"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


class PropertyType(db.Model):
    __tablename__ = "property_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


class InterestRate(db.Model):
    __tablename__ = "interest_rate"
    id = db.Column(db.Integer, primary_key=True)
    rate_date = db.Column(db.Date, nullable=False, unique=True)
    value = db.Column(db.Numeric(precision=4, scale=2), nullable=False)


class HousingPrice(db.Model):
    __tablename__ = "housing_price"
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(10), nullable=False)
    average_price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    region_id = db.Column(db.Integer, db.ForeignKey("region.id"), nullable=False)
    region = db.relationship("Region", backref="housing_prices")

    type_id = db.Column(db.Integer, db.ForeignKey("property_type.id"), nullable=False)
    type = db.relationship("PropertyType", backref="housing_prices") 
