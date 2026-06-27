from flask import Blueprint, g, render_template

from dispatch_center.models import (
    Dispatch,
    PublishingQueueItem,
)
from dispatch_center.workspace import (
    campaign_query,
    dispatch_query,
    media_asset_query,
    publishing_queue_query,
)


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    active_org = g.active_organization
    counts = {
        "campaigns": campaign_query().count(),
        "dispatches": dispatch_query().count(),
        "assets": media_asset_query().count(),
        "queue": publishing_queue_query().filter(PublishingQueueItem.status != "Published").count(),
    }
    recent_dispatches = dispatch_query().order_by(Dispatch.updated_at.desc()).limit(5).all()
    queue_items = (
        publishing_queue_query().filter(PublishingQueueItem.status != "Published")
        .order_by(PublishingQueueItem.updated_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        counts=counts,
        recent_dispatches=recent_dispatches,
        queue_items=queue_items,
        active_org=active_org,
    )
