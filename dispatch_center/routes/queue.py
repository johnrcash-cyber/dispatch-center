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
        .order_by(PublishingQueueItem.updated_at.desc())
        .all()
    )
    return render_template("queue/list.html", queue_items=queue_items)


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
    return redirect(url_for("queue.publishing_queue"))


@queue_bp.route("/<int:item_id>/save", methods=["POST"])
def save_posted_url(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    item.posted_url = form_text(request.form, "posted_url")
    item.notes = form_text(request.form, "notes") or item.notes
    db.session.commit()
    flash(f"{item.platform_name} queue item saved.", "success")
    return redirect(url_for("queue.publishing_queue"))


@queue_bp.route("/<int:item_id>/skip", methods=["POST"])
def skip_item(item_id):
    item = publishing_queue_query().filter(PublishingQueueItem.id == item_id).first_or_404()
    item.status = "Skipped"
    item.notes = form_text(request.form, "notes") or item.notes
    db.session.commit()
    flash(f"{item.platform_name} skipped.", "success")
    return redirect(url_for("queue.publishing_queue"))
