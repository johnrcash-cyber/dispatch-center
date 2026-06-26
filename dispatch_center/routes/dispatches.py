from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_int, form_text
from dispatch_center.models import Campaign, Dispatch, db
from dispatch_center.workspace import campaign_query, dispatch_query


dispatches_bp = Blueprint("dispatches", __name__, url_prefix="/dispatches")


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
    return render_template("dispatches/form.html", dispatch=dispatch, campaigns=campaigns, title="New Dispatch")


@dispatches_bp.route("/<int:dispatch_id>")
def detail_dispatch(dispatch_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    return render_template("dispatches/detail.html", dispatch=dispatch)


@dispatches_bp.route("/<int:dispatch_id>/edit", methods=["GET", "POST"])
def edit_dispatch(dispatch_id):
    dispatch = dispatch_query().filter(Dispatch.id == dispatch_id).first_or_404()
    campaigns = campaign_query().order_by(Campaign.name).all()
    if request.method == "POST":
        save_dispatch(dispatch)
        flash("Dispatch updated.", "success")
        return redirect(url_for("dispatches.detail_dispatch", dispatch_id=dispatch.id))
    return render_template("dispatches/form.html", dispatch=dispatch, campaigns=campaigns, title="Edit Dispatch")


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
    dispatch.canonical_link = form_text(request.form, "canonical_link")
    dispatch.tags = form_text(request.form, "tags")
    dispatch.notes = form_text(request.form, "notes")
    db.session.add(dispatch)
    db.session.commit()
