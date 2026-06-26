from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Organization(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    website_url = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    default_cta = db.Column(db.Text)
    default_footer = db.Column(db.Text)
    notes = db.Column(db.Text)

    campaigns = db.relationship(
        "Campaign", back_populates="organization", cascade="all, delete-orphan"
    )
    assets = db.relationship("MediaAsset", back_populates="organization")
    platform_settings = db.relationship(
        "PlatformSetting", back_populates="organization", cascade="all, delete-orphan"
    )


class Campaign(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    name = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(120))
    status = db.Column(db.String(80), default="Planning")
    owner = db.Column(db.String(120))
    priority = db.Column(db.String(80))
    start_date = db.Column(db.Date)
    target_publish_date = db.Column(db.Date)
    tags = db.Column(db.String(500))
    notes = db.Column(db.Text)

    organization = db.relationship("Organization", back_populates="campaigns")
    dispatches = db.relationship(
        "Dispatch", back_populates="campaign", cascade="all, delete-orphan"
    )
    assets = db.relationship("MediaAsset", back_populates="campaign")


class Dispatch(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    title = db.Column(db.String(220), nullable=False)
    internal_name = db.Column(db.String(180))
    status = db.Column(db.String(80), default="Draft")
    primary_body = db.Column(db.Text)
    summary = db.Column(db.Text)
    short_version = db.Column(db.Text)
    call_to_action = db.Column(db.Text)
    canonical_link = db.Column(db.String(500))
    tags = db.Column(db.String(500))
    notes = db.Column(db.Text)

    campaign = db.relationship("Campaign", back_populates="dispatches")
    platform_versions = db.relationship(
        "PlatformVersion", back_populates="dispatch", cascade="all, delete-orphan"
    )
    assets = db.relationship("MediaAsset", back_populates="dispatch")


class PlatformVersion(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatch.id"), nullable=False)
    platform_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), default="Draft")
    platform_title = db.Column(db.String(240))
    platform_body = db.Column(db.Text)
    short_text = db.Column(db.Text)
    call_to_action = db.Column(db.Text)
    selected_image_urls = db.Column(db.Text)
    hashtags = db.Column(db.String(500))
    formatting_notes = db.Column(db.Text)
    destination_url = db.Column(db.String(500))
    posted_url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime)

    dispatch = db.relationship("Dispatch", back_populates="platform_versions")

    @property
    def is_published(self):
        return self.status == "Published"


class MediaAsset(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"))
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatch.id"))
    asset_type = db.Column(db.String(80), default="Image")
    title = db.Column(db.String(180), nullable=False)
    url = db.Column(db.String(500))
    alt_text = db.Column(db.String(500))
    notes = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)

    organization = db.relationship("Organization", back_populates="assets")
    campaign = db.relationship("Campaign", back_populates="assets")
    dispatch = db.relationship("Dispatch", back_populates="assets")


class PlatformSetting(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    platform_name = db.Column(db.String(120), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    destination_url = db.Column(db.String(500))
    posting_method = db.Column(db.String(120), default="Manual")
    character_limit = db.Column(db.Integer)
    supports_markdown = db.Column(db.Boolean, default=False)
    supports_html = db.Column(db.Boolean, default=False)
    supports_images = db.Column(db.Boolean, default=True)
    default_hashtags = db.Column(db.String(500))
    default_footer = db.Column(db.Text)
    notes = db.Column(db.Text)

    organization = db.relationship("Organization", back_populates="platform_settings")
