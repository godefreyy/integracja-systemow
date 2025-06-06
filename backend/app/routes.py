from flask import (
    Blueprint, render_template, send_file, request,
    flash, redirect, url_for
)
from io import BytesIO

# XML helpers (already exist)
from .xml_utils import export_stream as xml_dump
from .xml_utils import import_stream as xml_load

# NEW: JSON / YAML helpers
from .json_utils import dump_json, dump_yaml, load_json, load_yaml

bp = Blueprint("data", __name__)   # no url_prefix → /xml, /json, /yaml live at root


# ────────────────────────────── UI page ──────────────────────────────────────
@bp.route("/", methods=["GET"])
def home():
    """
    One simple HTML page with three panes:
    • XML  • JSON  • YAML
    """
    return render_template("data.html")


# ────────────────────────────── XML ──────────────────────────────────────────
@bp.route("/xml/export")
def xml_export():
    return send_file(
        BytesIO(xml_dump()),
        mimetype="application/xml",
        as_attachment=True,
        download_name="dataset.xml",
    )


@bp.route("/xml/import", methods=["POST"])
def xml_import():
    f = request.files.get("file")
    if not f:
        flash("No XML file selected!", "error")
    else:
        xml_load(f.stream)
        flash("XML imported ✔", "success")
    return redirect(url_for("data.home"))


# ────────────────────────────── JSON ─────────────────────────────────────────
@bp.route("/json/export")
def json_export():
    return send_file(
        BytesIO(dump_json()),
        mimetype="application/json",
        as_attachment=True,
        download_name="dataset.json",
    )


@bp.route("/json/import", methods=["POST"])
def json_import():
    f = request.files.get("file")
    if not f:
        flash("No JSON file selected!", "error")
    else:
        load_json(f.stream)
        flash("JSON imported ✔", "success")
    return redirect(url_for("data.home"))


# ────────────────────────────── YAML ─────────────────────────────────────────
@bp.route("/yaml/export")
def yaml_export():
    return send_file(
        BytesIO(dump_yaml()),
        mimetype="application/x-yaml",
        as_attachment=True,
        download_name="dataset.yaml",
    )


@bp.route("/yaml/import", methods=["POST"])
def yaml_import():
    f = request.files.get("file")
    if not f:
        flash("No YAML file selected!", "error")
    else:
        load_yaml(f.stream)
        flash("YAML imported ✔", "success")
    return redirect(url_for("data.home"))
