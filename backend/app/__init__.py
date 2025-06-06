from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

db = SQLAlchemy()

def create_app():
    """
    Factory pattern – lets CLI or gunicorn import the same app.
    """
    app = Flask(__name__)

    # ---- configuration ----------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://app:app@db:3306/integracja"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "change-me-in-prod"

    # ---- init extensions ---------------------------------------------------
    db.init_app(app)

    # ---- blueprints / routes ----------------------------------------------
    from .routes import bp
    app.register_blueprint(bp)

    # ---- template auto-reload (handy in dev) -------------------------------
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    return app
