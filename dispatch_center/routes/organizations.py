from flask import Blueprint, flash, redirect, render_template, request, url_for

from dispatch_center.forms import form_text
from dispatch_center.models import Organization, db
from dispatch_center.utils import slugify
from dispatch_center.workspace import set_active_organization


organizations_bp = Blueprint("organizations", __name__, url_prefix="/organizations")


@organizations_bp.route("/select")
def select_organization():
    organizations = Organization.query.order_by(Organization.name).all()
    return render_template("organizations/select.html", organizations=organizations)


@organizations_bp.route("/set/<int:org_id>", methods=["POST"])
def set_active_organization_route(org_id):
    organization = Organization.query.get_or_404(org_id)
    set_active_organization(organization)
    flash(f"Workspace switched to {organization.name}.", "success")
    next_url = request.form.get("next") or url_for("main.dashboard")
    return redirect(next_url)


@organizations_bp.route("/")
def list_organizations():
    organizations = Organization.query.order_by(Organization.name).all()
    return render_template("organizations/list.html", organizations=organizations)


@organizations_bp.route("/new", methods=["GET", "POST"])
def create_organization():
    organization = Organization()
    if request.method == "POST":
        save_organization(organization)
        set_active_organization(organization)
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
    organization.slug = unique_organization_slug(
        form_text(request.form, "slug") or organization.name,
        organization.id,
    )
    organization.description = form_text(request.form, "description")
    organization.website_url = form_text(request.form, "website_url")
    organization.logo_url = form_text(request.form, "logo_url")
    organization.default_cta = form_text(request.form, "default_cta")
    organization.default_footer = form_text(request.form, "default_footer")
    organization.notes = form_text(request.form, "notes")
    db.session.add(organization)
    db.session.commit()


def unique_organization_slug(value, current_id=None):
    base_slug = slugify(value, "organization")
    candidate = base_slug
    suffix = 2
    query = Organization.query.filter(Organization.slug == candidate)
    if current_id:
        query = query.filter(Organization.id != current_id)
    while query.first() is not None:
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
        query = Organization.query.filter(Organization.slug == candidate)
        if current_id:
            query = query.filter(Organization.id != current_id)
    return candidate
