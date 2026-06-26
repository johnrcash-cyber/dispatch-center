from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_text
from dispatch_center.models import PlatformVersion, db


queue_bp = Blueprint("queue", __name__, url_prefix="/queue")


@queue_bp.route("/")
def publishing_queue():
    versions = (
        PlatformVersion.query.filter(PlatformVersion.status != "Published")
        .order_by(PlatformVersion.updated_at.desc())
        .all()
    )
    return render_template("queue/list.html", versions=versions)


@queue_bp.route("/<int:version_id>/publish", methods=["POST"])
def mark_published(version_id):
    version = PlatformVersion.query.get_or_404(version_id)
    version.status = "Published"
    version.posted_url = form_text(request.form, "posted_url") or version.posted_url
    version.posted_at = datetime.utcnow()
    db.session.commit()
    # Future publishing automation or webhook callbacks can write richer history here.
    flash(f"{version.platform_name} marked as published.", "success")
    return redirect(url_for("queue.publishing_queue"))
