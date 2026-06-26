from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_text
from dispatch_center.models import Organization, db


organizations_bp = Blueprint("organizations", __name__, url_prefix="/organizations")


@organizations_bp.route("/")
def list_organizations():
    organizations = Organization.query.order_by(Organization.name).all()
    return render_template("organizations/list.html", organizations=organizations)


@organizations_bp.route("/new", methods=["GET", "POST"])
def create_organization():
    organization = Organization()
    if request.method == "POST":
        save_organization(organization)
        flash("Organization created.", "success")
        return redirect(url_for("organizations.detail_organization", org_id=organization.id))
    return render_template("organizations/form.html", organization=organization, title="New Organization")


@organizations_bp.route("/<int:org_id>")
def detail_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    return render_template("organizations/detail.html", organization=organization)


@organizations_bp.route("/<int:org_id>/edit", methods=["GET", "POST"])
def edit_organization(org_id):
    organization = Organization.query.get_or_404(org_id)
    if request.method == "POST":
        save_organization(organization)
        flash("Organization updated.", "success")
        return redirect(url_for("organizations.detail_organization", org_id=organization.id))
    return render_template("organizations/form.html", organization=organization, title="Edit Organization")


def save_organization(organization):
    organization.name = form_text(request.form, "name") or "Untitled Organization"
    organization.description = form_text(request.form, "description")
    organization.website_url = form_text(request.form, "website_url")
    organization.logo_url = form_text(request.form, "logo_url")
    organization.default_cta = form_text(request.form, "default_cta")
    organization.default_footer = form_text(request.form, "default_footer")
    organization.notes = form_text(request.form, "notes")
    db.session.add(organization)
    db.session.commit()
