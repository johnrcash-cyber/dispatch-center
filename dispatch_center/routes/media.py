from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from dispatch_center.forms import form_bool, form_text
from dispatch_center.models import MediaAsset, db
from dispatch_center.workspace import media_asset_query


media_bp = Blueprint("media", __name__, url_prefix="/media")

ASSET_TYPES = ["Image", "Video", "Audio", "Document", "External Link", "Other"]
SOURCE_TYPES = ["Uploaded File", "External URL"]
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "mp4",
    "mov",
    "webm",
    "mp3",
    "wav",
    "m4a",
    "pdf",
    "docx",
    "txt",
    "md",
}


@media_bp.route("/")
def list_assets():
    assets = media_asset_query().order_by(MediaAsset.updated_at.desc()).all()
    return render_template("media/list.html", assets=assets)


@media_bp.route("/new", methods=["GET", "POST"])
def create_asset():
    asset = MediaAsset()
    choices = relation_choices()
    if request.method == "POST":
        if save_asset(asset):
            flash("Asset created.", "success")
            return redirect(url_for("media.list_assets"))
    asset.organization_id = g.active_organization.id
    return render_template("media/form.html", asset=asset, title="New Asset", **choices)


@media_bp.route("/<int:asset_id>")
def detail_asset(asset_id):
    asset = media_asset_query().filter(MediaAsset.id == asset_id).first_or_404()
    return render_template("media/detail.html", asset=asset)


@media_bp.route("/<int:asset_id>/edit", methods=["GET", "POST"])
def edit_asset(asset_id):
    asset = media_asset_query().filter(MediaAsset.id == asset_id).first_or_404()
    choices = relation_choices()
    if request.method == "POST":
        if save_asset(asset):
            flash("Asset updated.", "success")
            return redirect(url_for("media.list_assets"))
    return render_template("media/form.html", asset=asset, title="Edit Asset", **choices)


def relation_choices():
    return {
        "asset_types": ASSET_TYPES,
        "source_types": SOURCE_TYPES,
    }


def save_asset(asset):
    asset.organization_id = g.active_organization.id
    asset.campaign_id = None
    asset.dispatch_id = None
    asset.asset_type = normalize_choice(form_text(request.form, "asset_type"), ASSET_TYPES, "Image")
    asset.source_type = normalize_choice(
        form_text(request.form, "source_type"), SOURCE_TYPES, "External URL"
    )
    asset.title = form_text(request.form, "title") or "Untitled Asset"
    asset.url = form_text(request.form, "url")
    asset.alt_text = form_text(request.form, "alt_text")
    asset.notes = form_text(request.form, "notes")
    asset.approved = form_bool(request.form, "approved")

    uploaded_file = request.files.get("file")
    if uploaded_file and uploaded_file.filename:
        save_uploaded_file(asset, uploaded_file)

    if asset.source_type == "Uploaded File" and not asset.filename:
        flash("Upload a file or switch the asset source to External URL.", "error")
        return False
    if asset.source_type == "External URL" and not asset.url:
        flash("Add an external URL or switch the asset source to Uploaded File.", "error")
        return False
    if not asset.filename and not asset.url:
        flash("A media asset needs either an uploaded file or an external URL.", "error")
        return False

    db.session.add(asset)
    db.session.commit()
    return True


def normalize_choice(value, choices, default):
    return value if value in choices else default


def save_uploaded_file(asset, uploaded_file):
    original_filename = secure_filename(uploaded_file.filename)
    extension = Path(original_filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        flash(f"Files ending in .{extension or 'unknown'} are not supported.", "error")
        return

    unique_filename = f"{uuid4().hex}_{original_filename}"
    target = Path(current_app.config["UPLOAD_FOLDER"]) / unique_filename
    uploaded_file.save(target)

    asset.source_type = "Uploaded File"
    asset.filename = unique_filename
    asset.original_filename = original_filename
    asset.file_size = target.stat().st_size
    asset.mime_type = uploaded_file.mimetype
    asset.uploaded_at = datetime.utcnow()
