from flask import Blueprint, flash, redirect, render_template, request, url_for

from flask import g

from dispatch_center.forms import form_date, form_text
from dispatch_center.models import Campaign, db
from dispatch_center.workspace import campaign_query


campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")


@campaigns_bp.route("/")
def list_campaigns():
    campaigns = campaign_query().order_by(Campaign.updated_at.desc()).all()
    return render_template("campaigns/list.html", campaigns=campaigns)


@campaigns_bp.route("/new", methods=["GET", "POST"])
def create_campaign():
    campaign = Campaign()
    if request.method == "POST":
        save_campaign(campaign)
        flash("Campaign created.", "success")
        return redirect(url_for("campaigns.detail_campaign", campaign_id=campaign.id))
    campaign.organization_id = g.active_organization.id
    return render_template("campaigns/form.html", campaign=campaign, title="New Campaign")


@campaigns_bp.route("/<int:campaign_id>")
def detail_campaign(campaign_id):
    campaign = campaign_query().filter(Campaign.id == campaign_id).first_or_404()
    return render_template("campaigns/detail.html", campaign=campaign)


@campaigns_bp.route("/<int:campaign_id>/edit", methods=["GET", "POST"])
def edit_campaign(campaign_id):
    campaign = campaign_query().filter(Campaign.id == campaign_id).first_or_404()
    if request.method == "POST":
        save_campaign(campaign)
        flash("Campaign updated.", "success")
        return redirect(url_for("campaigns.detail_campaign", campaign_id=campaign.id))
    return render_template("campaigns/form.html", campaign=campaign, title="Edit Campaign")


def save_campaign(campaign):
    campaign.organization_id = g.active_organization.id
    campaign.name = form_text(request.form, "name") or "Untitled Campaign"
    campaign.description = form_text(request.form, "description")
    campaign.category = form_text(request.form, "category")
    campaign.status = form_text(request.form, "status") or "Planning"
    campaign.owner = form_text(request.form, "owner")
    campaign.priority = form_text(request.form, "priority")
    campaign.start_date = form_date(request.form, "start_date")
    campaign.target_publish_date = form_date(request.form, "target_publish_date")
    campaign.tags = form_text(request.form, "tags")
    campaign.notes = form_text(request.form, "notes")
    db.session.add(campaign)
    db.session.commit()
