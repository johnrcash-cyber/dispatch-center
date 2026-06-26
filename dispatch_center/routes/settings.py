from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_bool, form_int, form_text
from dispatch_center.models import Organization, PlatformSetting, db


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/")
def list_settings():
    settings = PlatformSetting.query.order_by(PlatformSetting.platform_name).all()
    return render_template("settings/list.html", settings=settings)


@settings_bp.route("/new", methods=["GET", "POST"])
def create_setting():
    setting = PlatformSetting()
    organizations = Organization.query.order_by(Organization.name).all()
    if request.method == "POST":
        save_setting(setting)
        flash("Platform setting created.", "success")
        return redirect(url_for("settings.list_settings"))
    setting.organization_id = request.args.get("organization_id", type=int)
    return render_template("settings/form.html", setting=setting, organizations=organizations, title="New Platform Setting")


@settings_bp.route("/<int:setting_id>/edit", methods=["GET", "POST"])
def edit_setting(setting_id):
    setting = PlatformSetting.query.get_or_404(setting_id)
    organizations = Organization.query.order_by(Organization.name).all()
    if request.method == "POST":
        save_setting(setting)
        flash("Platform setting updated.", "success")
        return redirect(url_for("settings.list_settings"))
    return render_template("settings/form.html", setting=setting, organizations=organizations, title="Edit Platform Setting")


def save_setting(setting):
    setting.organization_id = form_int(request.form, "organization_id")
    setting.platform_name = form_text(request.form, "platform_name") or "Website"
    setting.enabled = form_bool(request.form, "enabled")
    setting.destination_url = form_text(request.form, "destination_url")
    setting.posting_method = form_text(request.form, "posting_method") or "Manual"
    setting.character_limit = form_int(request.form, "character_limit")
    setting.supports_markdown = form_bool(request.form, "supports_markdown")
    setting.supports_html = form_bool(request.form, "supports_html")
    setting.supports_images = form_bool(request.form, "supports_images")
    setting.default_hashtags = form_text(request.form, "default_hashtags")
    setting.default_footer = form_text(request.form, "default_footer")
    setting.notes = form_text(request.form, "notes")
    db.session.add(setting)
    db.session.commit()
