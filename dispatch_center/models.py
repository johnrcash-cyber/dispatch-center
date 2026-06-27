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
    slug = db.Column(db.String(180), nullable=True)
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
    tags = db.Column(db.String(500))
    notes = db.Column(db.Text)

    campaign = db.relationship("Campaign", back_populates="dispatches")
    queue_items = db.relationship(
        "PublishingQueueItem", back_populates="dispatch", cascade="all, delete-orphan"
    )
    assets = db.relationship("MediaAsset", back_populates="dispatch")
    media_links = db.relationship(
        "DispatchMedia",
        back_populates="dispatch",
        cascade="all, delete-orphan",
        order_by="DispatchMedia.sort_order",
    )


class DispatchMedia(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatch.id"), nullable=False)
    media_asset_id = db.Column(db.Integer, db.ForeignKey("media_asset.id"), nullable=False)
    usage_type = db.Column(db.String(80), default="Supporting Asset")
    sort_order = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    dispatch = db.relationship("Dispatch", back_populates="media_links")
    media_asset = db.relationship("MediaAsset", back_populates="dispatch_links")


class MediaAsset(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"))
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"))
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatch.id"))
    asset_type = db.Column(db.String(80), default="Image")
    source_type = db.Column(db.String(80), default="External URL")
    title = db.Column(db.String(180), nullable=False)
    url = db.Column(db.String(500))
    filename = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(160))
    uploaded_at = db.Column(db.DateTime)
    alt_text = db.Column(db.String(500))
    notes = db.Column(db.Text)
    approved = db.Column(db.Boolean, default=False)

    organization = db.relationship("Organization", back_populates="assets")
    campaign = db.relationship("Campaign", back_populates="assets")
    dispatch = db.relationship("Dispatch", back_populates="assets")
    dispatch_links = db.relationship(
        "DispatchMedia", back_populates="media_asset", cascade="all, delete-orphan"
    )

    @property
    def is_uploaded_file(self):
        return self.source_type == "Uploaded File" and bool(self.filename)

    @property
    def is_external_url(self):
        return self.source_type == "External URL" and bool(self.url)


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
    login_url = db.Column(db.String(500))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    recovery_email = db.Column(db.String(255))
    two_factor_notes = db.Column(db.Text)
    credential_notes = db.Column(db.Text)

    organization = db.relationship("Organization", back_populates="platform_settings")
    queue_items = db.relationship("PublishingQueueItem", back_populates="platform_setting")


class PublishingQueueItem(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey("dispatch.id"), nullable=False)
    platform_setting_id = db.Column(db.Integer, db.ForeignKey("platform_setting.id"))
    platform_name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), default="Draft")
    destination_url = db.Column(db.String(500))
    posted_url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    dispatch = db.relationship("Dispatch", back_populates="queue_items")
    platform_setting = db.relationship("PlatformSetting", back_populates="queue_items")
