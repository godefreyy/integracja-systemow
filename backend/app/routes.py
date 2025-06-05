from flask import Blueprint, render_template

bp = Blueprint("ui", __name__)

@bp.route("/xml")
def xml_home():
    return render_template("xml.html")

from flask import request, send_file, Response
from io import BytesIO
from .xml_utils import import_stream, export_stream
from . import db

@bp.post("/xml/import")
def xml_import():
    f = request.files.get("xmlfile")
    if not f:
        return "No file", 400
    import_stream(f.stream)
    return "XML imported ✔ – rows now in database."

@bp.get("/xml/export")
def xml_export():
    payload = export_stream()
    return Response(
        payload,
        headers={"Content-Disposition": "attachment; filename=dataset.xml"},
        mimetype="application/xml"
    )
    