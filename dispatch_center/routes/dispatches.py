from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_int, form_text
from dispatch_center.models import (
    Campaign,
    Dispatch,
    DispatchMedia,
    MediaAsset,
    PlatformSetting,
    PublishingQueueItem,
    db,
)
from dispatch_center.workspace import (
    campaign_query,
    dispatch_query,
    media_asset_query,
    platform_setting_query,
    publishing_queue_query,
)


dispatches_bp = Blueprint("dispatches", __name__, url_prefix="/dispatches")

USAGE_TYPES = [
    "Hero Image",
    "Banner",
    "Thumbnail",
    "Gallery",
    "Attachment",
    "Video",
    "Audio",
    "Logo",
    "Supporting Asset",
]

ASSET_TYPES = ["Image", "Video", "Audio", "Document", "External Link", "Other"]


@dispatches_bp.route("/")
def list_dispatches():
    dispatches = dispatch_query().order_by(Dispatch.updated_at.desc()).all()
    return render_template("dispatches/list.html", dispatches=dispatches)


@dispatches_bp.route("/new", methods=["GET", "POST"])
def create_dispatch():
    dispatch = Dispatch()
    campaigns = campaign_query().order_by(Campaign.name).all()
    if request.method == "POST":
        save_dispatch(dispatch)
        flash("Dispatch created.", "success")
        return redirect(url_for("dispatches.detail_dispatch", dispatch_id=dispatch.id))
    dispatch.campaign_id = request.args.get("campaign_id", type=int)
    return render_dispatch_form(dispatch, campaigns, "New Dispatch")


@dispatches_bp.route("/<int:dispatch_id>")
def detail_dispatch(dispatch_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    return render_dispatch_detail(dispatch)


@dispatches_bp.route("/<int:dispatch_id>/edit", methods=["GET", "POST"])
def edit_dispatch(dispatch_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    campaigns = campaign_query().order_by(Campaign.name).all()
    if request.method == "POST":
        save_dispatch(dispatch)
        flash("Dispatch updated.", "success")
        return redirect(url_for("dispatches.detail_dispatch", dispatch_id=dispatch.id))
    return render_dispatch_form(dispatch, campaigns, "Edit Dispatch")


@dispatches_bp.route("/<int:dispatch_id>/media", methods=["POST"])
def add_dispatch_media(dispatch_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    media_asset_id = form_int(request.form, "media_asset_id")
    media_asset = (
        media_asset_query()
        .filter(MediaAsset.id == media_asset_id, MediaAsset.approved.is_(True))
        .first_or_404()
    )
    link = DispatchMedia(
        dispatch_id=dispatch.id,
        media_asset_id=media_asset.id,
        usage_type=normalize_usage_type(form_text(request.form, "usage_type")),
        sort_order=form_int(request.form, "sort_order") or 0,
        notes=form_text(request.form, "media_notes"),
    )
    db.session.add(link)
    db.session.commit()
    flash(f"{media_asset.title} added to dispatch.", "success")
    return redirect(url_for("dispatches.edit_dispatch", dispatch_id=dispatch.id))


@dispatches_bp.route("/<int:dispatch_id>/media/<int:link_id>/remove", methods=["POST"])
def remove_dispatch_media(dispatch_id, link_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    link = DispatchMedia.query.filter(
        DispatchMedia.id == link_id, DispatchMedia.dispatch_id == dispatch.id
    ).first_or_404()
    db.session.delete(link)
    db.session.commit()
    flash("Media asset removed from dispatch.", "success")
    return redirect(url_for("dispatches.edit_dispatch", dispatch_id=dispatch.id))


@dispatches_bp.route("/<int:dispatch_id>/queue/<int:setting_id>", methods=["POST"])
def add_publishing_target(dispatch_id, setting_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    setting = (
        platform_setting_query()
        .filter(PlatformSetting.id == setting_id, PlatformSetting.enabled.is_(True))
        .first_or_404()
    )
    existing = publishing_queue_query().filter(
        PublishingQueueItem.dispatch_id == dispatch.id,
        PublishingQueueItem.platform_setting_id == setting.id,
        PublishingQueueItem.status != "Published",
    ).first()
    if existing:
        flash(f"{setting.platform_name} is already in the queue.", "success")
        return redirect(url_for("dispatches.detail_dispatch", dispatch_id=dispatch.id))

    item = PublishingQueueItem(
        dispatch_id=dispatch.id,
        platform_setting_id=setting.id,
        platform_name=setting.platform_name,
        status="Queued",
        destination_url=setting.destination_url,
        notes=form_text(request.form, "queue_notes"),
    )
    db.session.add(item)
    db.session.commit()
    flash(f"{setting.platform_name} added to the publishing queue.", "success")
    return redirect(url_for("dispatches.detail_dispatch", dispatch_id=dispatch.id))


def render_dispatch_form(dispatch, campaigns, title):
    media_assets = (
        media_asset_query()
        .order_by(MediaAsset.title)
        .all()
    )
    return render_template(
        "dispatches/form.html",
        dispatch=dispatch,
        campaigns=campaigns,
        media_assets=media_assets,
        usage_types=USAGE_TYPES,
        asset_types=ASSET_TYPES,
        title=title,
    )


def render_dispatch_detail(dispatch):
    platform_settings = (
        platform_setting_query()
        .filter(PlatformSetting.enabled.is_(True))
        .order_by(PlatformSetting.platform_name)
        .all()
    )
    open_queue_items = publishing_queue_query().filter(
        PublishingQueueItem.dispatch_id == dispatch.id,
        PublishingQueueItem.status != "Published",
    ).all()
    queued_setting_ids = {
        item.platform_setting_id for item in open_queue_items if item.platform_setting_id
    }
    return render_template(
        "dispatches/detail.html",
        dispatch=dispatch,
        usage_types=USAGE_TYPES,
        platform_settings=platform_settings,
        queued_setting_ids=queued_setting_ids,
    )


def save_dispatch(dispatch):
    campaign_id = form_int(request.form, "campaign_id")
    campaign_query().filter(Campaign.id == campaign_id).first_or_404()
    dispatch.campaign_id = campaign_id
    dispatch.title = form_text(request.form, "title") or "Untitled Dispatch"
    dispatch.internal_name = form_text(request.form, "internal_name")
    dispatch.status = form_text(request.form, "status") or "Draft"
    dispatch.primary_body = form_text(request.form, "primary_body")
    dispatch.summary = form_text(request.form, "summary")
    dispatch.short_version = form_text(request.form, "short_version")
    dispatch.call_to_action = form_text(request.form, "call_to_action")
    dispatch.tags = form_text(request.form, "tags")
    dispatch.notes = form_text(request.form, "notes")
    db.session.add(dispatch)
    db.session.commit()


def normalize_usage_type(value):
    return value if value in USAGE_TYPES else "Supporting Asset"
