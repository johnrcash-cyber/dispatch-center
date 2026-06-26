from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_datetime, form_int, form_text
from dispatch_center.models import Dispatch, PlatformVersion, db
from dispatch_center.workspace import dispatch_query, platform_version_query


platform_versions_bp = Blueprint("platform_versions", __name__, url_prefix="/platform-versions")


@platform_versions_bp.route("/")
def list_platform_versions():
    versions = platform_version_query().order_by(PlatformVersion.updated_at.desc()).all()
    return render_template("platform_versions/list.html", versions=versions)


@platform_versions_bp.route("/new", methods=["GET", "POST"])
def create_platform_version():
    version = PlatformVersion()
    dispatches = dispatch_query().order_by(Dispatch.title).all()
    if request.method == "POST":
        save_platform_version(version)
        flash("Platform version created.", "success")
        return redirect(url_for("platform_versions.edit_platform_version", version_id=version.id))
    version.dispatch_id = request.args.get("dispatch_id", type=int)
    return render_template(
        "platform_versions/form.html",
        version=version,
        dispatches=dispatches,
        title="New Platform Version",
    )


@platform_versions_bp.route("/<int:version_id>/edit", methods=["GET", "POST"])
def edit_platform_version(version_id):
    version = platform_version_query().filter(PlatformVersion.id == version_id).first_or_404()
    dispatches = dispatch_query().order_by(Dispatch.title).all()
    if request.method == "POST":
        save_platform_version(version)
        flash("Platform version updated.", "success")
        return redirect(url_for("platform_versions.edit_platform_version", version_id=version.id))
    return render_template(
        "platform_versions/form.html",
        version=version,
        dispatches=dispatches,
        title="Edit Platform Version",
    )


def save_platform_version(version):
    dispatch_id = form_int(request.form, "dispatch_id")
    dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    version.dispatch_id = dispatch_id
    version.platform_name = form_text(request.form, "platform_name") or "Website"
    version.status = form_text(request.form, "status") or "Draft"
    version.platform_title = form_text(request.form, "platform_title")
    version.platform_body = form_text(request.form, "platform_body")
    version.short_text = form_text(request.form, "short_text")
    version.call_to_action = form_text(request.form, "call_to_action")
    version.selected_image_urls = form_text(request.form, "selected_image_urls")
    version.hashtags = form_text(request.form, "hashtags")
    version.formatting_notes = form_text(request.form, "formatting_notes")
    version.destination_url = form_text(request.form, "destination_url")
    version.posted_url = form_text(request.form, "posted_url")
    version.posted_at = form_datetime(request.form, "posted_at")
    db.session.add(version)
    db.session.commit()
