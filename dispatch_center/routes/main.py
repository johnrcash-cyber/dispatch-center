from flask import Blueprint, render_template

from dispatch_center.models import (
    Campaign,
    Dispatch,
    MediaAsset,
    Organization,
    PlatformVersion,
)


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    counts = {
        "organizations": Organization.query.count(),
        "campaigns": Campaign.query.count(),
        "dispatches": Dispatch.query.count(),
        "platform_versions": PlatformVersion.query.count(),
        "assets": MediaAsset.query.count(),
        "queue": PlatformVersion.query.filter(PlatformVersion.status != "Published").count(),
    }
    recent_dispatches = Dispatch.query.order_by(Dispatch.updated_at.desc()).limit(5).all()
    queue_items = (
        PlatformVersion.query.filter(PlatformVersion.status != "Published")
        .order_by(PlatformVersion.updated_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        counts=counts,
        recent_dispatches=recent_dispatches,
        queue_items=queue_items,
    )
