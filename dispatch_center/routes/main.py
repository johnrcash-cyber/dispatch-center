from flask import Blueprint, g, render_template

from dispatch_center.models import (
    Campaign,
    Dispatch,
    MediaAsset,
    PlatformVersion,
)
from dispatch_center.workspace import (
    campaign_query,
    dispatch_query,
    media_asset_query,
    platform_version_query,
)


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    active_org = g.active_organization
    counts = {
        "campaigns": campaign_query().count(),
        "dispatches": dispatch_query().count(),
        "platform_versions": platform_version_query().count(),
        "assets": media_asset_query().count(),
        "queue": platform_version_query().filter(PlatformVersion.status != "Published").count(),
    }
    recent_dispatches = dispatch_query().order_by(Dispatch.updated_at.desc()).limit(5).all()
    queue_items = (
        platform_version_query().filter(PlatformVersion.status != "Published")
        .order_by(PlatformVersion.updated_at.desc())
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
