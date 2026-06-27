from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_text
from dispatch_center.models import PublishingQueueItem, db
from dispatch_center.workspace import publishing_queue_query


queue_bp = Blueprint("queue", __name__, url_prefix="/queue")


@queue_bp.route("/")
def publishing_queue():
    queue_items = (
        publishing_queue_query()
        .order_by(PublishingQueueItem.created_at.desc())
        .all()
    )
    return render_template("queue/list.html", queue_items=queue_items)


@queue_bp.route("/<int:item_id>")
def queue_item_detail(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    media_urls, media_groups = build_media_context(item)
    full_post = build_full_post(item, media_urls)
    return render_template(
        "queue/detail.html",
        item=item,
        media_urls=media_urls,
        media_groups=media_groups,
        full_post=full_post,
    )


@queue_bp.route("/<int:item_id>/publish", methods=["POST"])
def mark_published(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    item.status = "Published"
    item.posted_url = form_text(request.form, "posted_url") or item.posted_url
    item.notes = form_text(request.form, "notes") or item.notes
    item.posted_at = datetime.utcnow()
    db.session.commit()
    # Future publishing automation or webhook callbacks can write richer history here.
    flash(f"{item.platform_name} marked as published.", "success")
    return redirect(url_for("queue.queue_item_detail", item_id=item.id))


@queue_bp.route("/<int:item_id>/save", methods=["POST"])
def save_posted_url(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    item.posted_url = form_text(request.form, "posted_url")
    item.notes = form_text(request.form, "notes") or item.notes
    db.session.commit()
    flash(f"{item.platform_name} queue item saved.", "success")
    return redirect(url_for("queue.queue_item_detail", item_id=item.id))


@queue_bp.route("/<int:item_id>/skip", methods=["POST"])
def skip_item(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    item.status = "Skipped"
    item.notes = form_text(request.form, "notes") or item.notes
    db.session.commit()
    flash(f"{item.platform_name} skipped.", "success")
    return redirect(url_for("queue.queue_item_detail", item_id=item.id))


def build_media_context(item):
    usage_order = [
        "Hero Image",
        "Banner",
        "Thumbnail",
        "Gallery",
        "Video",
        "Audio",
        "Attachment",
        "Supporting Asset",
        "Logo",
    ]
    groups = {usage_type: [] for usage_type in usage_order}
    urls = []
    seen_asset_ids = set()
    seen_urls = set()

    for link in item.dispatch.media_links:
        asset = link.media_asset
        url = media_asset_url(asset, external=True)
        if url and url not in seen_urls:
            urls.append(url)
            seen_urls.add(url)

        if asset.id in seen_asset_ids:
            continue
        seen_asset_ids.add(asset.id)

        usage_type = link.usage_type if link.usage_type in groups else "Supporting Asset"
        groups[usage_type].append(link)

    return urls, groups


def build_full_post(item, media_urls):
    parts = [
        item.dispatch.title,
        item.dispatch.summary,
        item.dispatch.primary_body,
        item.dispatch.call_to_action,
        item.destination_url,
    ]
    if media_urls:
        parts.append("\n".join(media_urls))
    if item.platform_setting:
        parts.extend(
            [
                item.platform_setting.default_hashtags,
                item.platform_setting.default_footer,
            ]
        )
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


def media_asset_url(asset, external=False):
    if asset.filename:
        return url_for("static", filename=f"uploads/{asset.filename}", _external=external)
    return asset.url or ""
