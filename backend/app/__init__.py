from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # === DB connection string ===
    uri = (
        "mysql+pymysql://{user}:{pwd}@{host}/{name}"
        .format(
            user=os.getenv("DB_USER"),
            pwd=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST", "localhost"),
            name=os.getenv("DB_NAME")
        )
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Only now import and register the blueprint(s):
    from .routes import bp
    app.register_blueprint(bp)

    return app
