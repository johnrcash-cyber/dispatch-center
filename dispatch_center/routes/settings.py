from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from dispatch_center.forms import form_bool, form_int, form_text
from dispatch_center.models import PlatformSetting, db
from dispatch_center.workspace import platform_setting_query


settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

PLATFORM_PRESETS = {
    "Discord": {
        "posting_method": "Manual",
        "character_limit": 2000,
        "supports_markdown": True,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Discord webhook, server, or channel URL",
    },
    "Facebook": {
        "posting_method": "Manual",
        "character_limit": 63206,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Facebook page URL",
    },
    "Instagram": {
        "posting_method": "Manual",
        "character_limit": 2200,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "#update",
        "destination_hint": "Instagram profile URL",
    },
    "LinkedIn": {
        "posting_method": "Manual",
        "character_limit": 3000,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "#update",
        "destination_hint": "LinkedIn company page URL",
    },
    "X / Twitter": {
        "posting_method": "Manual",
        "character_limit": 280,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "X profile or compose URL",
    },
    "Bluesky": {
        "posting_method": "Manual",
        "character_limit": 300,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Bluesky profile URL",
    },
    "Threads": {
        "posting_method": "Manual",
        "character_limit": 500,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Threads profile URL",
    },
    "TikTok": {
        "posting_method": "Manual",
        "character_limit": 2200,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "#update",
        "destination_hint": "TikTok profile or upload URL",
    },
    "YouTube": {
        "posting_method": "Manual",
        "character_limit": 5000,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "#update",
        "destination_hint": "YouTube channel or Studio URL",
    },
    "Reddit": {
        "posting_method": "Manual",
        "character_limit": 40000,
        "supports_markdown": True,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Subreddit submit URL",
    },
    "Website / Blog": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": True,
        "supports_html": True,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Website blog URL",
    },
    "WordPress Blog": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": True,
        "supports_html": True,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "WordPress wp-admin post URL or public blog URL",
    },
    "Email Newsletter": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": False,
        "supports_html": True,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Email platform campaign URL",
    },
    "Substack": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": True,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Substack publication URL",
    },
    "Medium": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "#update",
        "destination_hint": "Medium publication URL",
    },
    "Google Business Profile": {
        "posting_method": "Manual",
        "character_limit": 1500,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Google Business Profile manager URL",
    },
    "Custom": {
        "posting_method": "Manual",
        "character_limit": None,
        "supports_markdown": False,
        "supports_html": False,
        "supports_images": True,
        "default_hashtags": "",
        "destination_hint": "Destination or admin URL",
    },
}


@settings_bp.route("/")
def list_settings():
    settings = platform_setting_query().order_by(PlatformSetting.platform_name).all()
    return render_template("settings/list.html", settings=settings)


@settings_bp.route("/new", methods=["GET", "POST"])
def create_setting():
    setting = PlatformSetting()
    if request.method == "POST":
        save_setting(setting)
        flash("Platform setting created.", "success")
        return redirect(url_for("settings.list_settings"))
    setting.organization_id = g.active_organization.id
    return render_setting_form(setting, "New Platform Setting")


@settings_bp.route("/<int:setting_id>/edit", methods=["GET", "POST"])
def edit_setting(setting_id):
    setting = platform_setting_query().filter(PlatformSetting.id == setting_id).first_or_404()
    if request.method == "POST":
        save_setting(setting)
        flash("Platform setting updated.", "success")
        return redirect(url_for("settings.list_settings"))
    return render_setting_form(setting, "Edit Platform Setting")


def render_setting_form(setting, title):
    return render_template(
        "settings/form.html",
        setting=setting,
        title=title,
        platform_presets=PLATFORM_PRESETS,
        preset_names=list(PLATFORM_PRESETS.keys()),
        organization=g.active_organization,
    )


def save_setting(setting):
    setting.organization_id = g.active_organization.id
    preset_name = form_text(request.form, "platform_preset") or "Custom"
    if preset_name == "Custom":
        setting.platform_name = form_text(request.form, "custom_platform_name") or "Custom"
    else:
        setting.platform_name = preset_name
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
