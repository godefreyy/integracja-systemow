from flask import Blueprint, render_template

bp = Blueprint("ui", __name__)

@bp.route("/xml")
def xml_home():
    return render_template("xml.html")
