from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_bool, form_int, form_text
from dispatch_center.models import Campaign, Dispatch, MediaAsset, Organization, db


media_bp = Blueprint("media", __name__, url_prefix="/media")


@media_bp.route("/")
def list_assets():
    assets = MediaAsset.query.order_by(MediaAsset.updated_at.desc()).all()
    return render_template("media/list.html", assets=assets)


@media_bp.route("/new", methods=["GET", "POST"])
def create_asset():
    asset = MediaAsset()
    choices = relation_choices()
    if request.method == "POST":
        save_asset(asset)
        flash("Asset created.", "success")
        return redirect(url_for("media.list_assets"))
    asset.organization_id = request.args.get("organization_id", type=int)
    asset.campaign_id = request.args.get("campaign_id", type=int)
    asset.dispatch_id = request.args.get("dispatch_id", type=int)
    return render_template("media/form.html", asset=asset, title="New Asset", **choices)


@media_bp.route("/<int:asset_id>/edit", methods=["GET", "POST"])
def edit_asset(asset_id):
    asset = MediaAsset.query.get_or_404(asset_id)
    choices = relation_choices()
    if request.method == "POST":
        save_asset(asset)
        flash("Asset updated.", "success")
        return redirect(url_for("media.list_assets"))
    return render_template("media/form.html", asset=asset, title="Edit Asset", **choices)


def relation_choices():
    return {
        "organizations": Organization.query.order_by(Organization.name).all(),
        "campaigns": Campaign.query.order_by(Campaign.name).all(),
        "dispatches": Dispatch.query.order_by(Dispatch.title).all(),
    }


def save_asset(asset):
    asset.organization_id = form_int(request.form, "organization_id")
    asset.campaign_id = form_int(request.form, "campaign_id")
    asset.dispatch_id = form_int(request.form, "dispatch_id")
    asset.asset_type = form_text(request.form, "asset_type") or "Image"
    asset.title = form_text(request.form, "title") or "Untitled Asset"
    asset.url = form_text(request.form, "url")
    asset.alt_text = form_text(request.form, "alt_text")
    asset.notes = form_text(request.form, "notes")
    asset.approved = form_bool(request.form, "approved")
    db.session.add(asset)
    db.session.commit()
