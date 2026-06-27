from flask import g, redirect, request, session, url_for

from .models import Campaign, Dispatch, MediaAsset, Organization, PlatformSetting, PlatformVersion


PUBLIC_ENDPOINTS = {
    "organizations.select_organization",
    "organizations.set_active_organization_route",
    "organizations.list_organizations",
    "organizations.create_organization",
    "organizations.detail_organization",
    "organizations.edit_organization",
    "static",
}


def get_active_organization():
    org_id = session.get("active_organization_id")
    if not org_id:
        return None
    organization = Organization.query.get(org_id)
    if organization is None:
        session.pop("active_organization_id", None)
    return organization


def set_active_organization(organization):
    session["active_organization_id"] = organization.id
    g.active_organization = organization


def workspace_guard():
    if request.endpoint in PUBLIC_ENDPOINTS:
        g.active_organization = get_active_organization()
        g.organizations = Organization.query.order_by(Organization.name).all()
        return None

    organizations = Organization.query.order_by(Organization.name).all()
    g.organizations = organizations
    active = get_active_organization()

    if active is None and len(organizations) == 1:
        set_active_organization(organizations[0])
        active = organizations[0]

    g.active_organization = active
    if active is None:
        return redirect(url_for("organizations.select_organization"))
    return None


def campaign_query():
    return Campaign.query.filter(Campaign.organization_id == g.active_organization.id)


def dispatch_query():
    return Dispatch.query.join(Campaign).filter(Campaign.organization_id == g.active_organization.id)


def platform_version_query():
    return (
        PlatformVersion.query.join(Dispatch)
        .join(Campaign)
        .filter(Campaign.organization_id == g.active_organization.id)
    )


def media_asset_query():
    return MediaAsset.query.filter(MediaAsset.organization_id == g.active_organization.id)


def platform_setting_query():
    return PlatformSetting.query.filter(
        PlatformSetting.organization_id == g.active_organization.id
    )
