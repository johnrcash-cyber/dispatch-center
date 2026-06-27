from datetime import date

import click
from flask import current_app
from sqlalchemy import inspect, text

from .utils import slugify
from .models import (
    Campaign,
    Dispatch,
    DispatchMedia,
    MediaAsset,
    Organization,
    PlatformSetting,
    PublishingQueueItem,
    db,
)


def register_seed_command(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("upgrade-db")
    def upgrade_db():
        db.create_all()
        inspector = inspect(db.engine)
        organization_columns = {
            column["name"] for column in inspector.get_columns("organization")
        }
        media_columns = {column["name"] for column in inspector.get_columns("media_asset")}
        platform_setting_columns = {
            column["name"] for column in inspector.get_columns("platform_setting")
        }
        media_additions = {
            "source_type": "VARCHAR(80) DEFAULT 'External URL'",
            "filename": "VARCHAR(255)",
            "original_filename": "VARCHAR(255)",
            "file_size": "INTEGER",
            "mime_type": "VARCHAR(160)",
            "uploaded_at": "DATETIME",
        }
        platform_setting_additions = {
            "login_url": "VARCHAR(500)",
            "username": "VARCHAR(255)",
            "password": "VARCHAR(255)",
            "recovery_email": "VARCHAR(255)",
            "two_factor_notes": "TEXT",
            "credential_notes": "TEXT",
        }
        with db.engine.begin() as connection:
            if "slug" not in organization_columns:
                connection.execute(text("ALTER TABLE organization ADD COLUMN slug VARCHAR(180)"))
                click.echo("Added organization.slug")
            for column, ddl in media_additions.items():
                if column not in media_columns:
                    connection.execute(text(f"ALTER TABLE media_asset ADD COLUMN {column} {ddl}"))
                    click.echo(f"Added media_asset.{column}")
            for column, ddl in platform_setting_additions.items():
                if column not in platform_setting_columns:
                    connection.execute(text(f"ALTER TABLE platform_setting ADD COLUMN {column} {ddl}"))
                    click.echo(f"Added platform_setting.{column}")
            table_names = set(inspector.get_table_names())
            if "platform_version" in table_names:
                connection.execute(text("DROP TABLE platform_version"))
                click.echo("Dropped platform_version")
            if "publishing_queue_item" in table_names:
                connection.execute(
                    text("UPDATE publishing_queue_item SET status = 'Ready' WHERE status = 'Queued'")
                )
        backfill_organization_slugs()
        click.echo("Database upgraded.")

    @app.cli.command("seed")
    def seed():
        db.drop_all()
        db.create_all()

        org = Organization(
            name="Northstar Labs",
            slug="northstar-labs",
            description="Example organization for testing Dispatch Center workflows.",
            website_url="https://example.com",
            logo_url="https://example.com/logo.png",
            default_cta="Read the full update",
            default_footer="Thanks for following along.",
            notes="Seeded local prototype account.",
        )
        db.session.add(org)
        db.session.flush()

        campaign = Campaign(
            organization_id=org.id,
            name="Platform Release 1.2",
            description="Launch communications for a small product release.",
            category="Product Launch",
            status="Active",
            owner="Communications",
            priority="High",
            start_date=date.today(),
            target_publish_date=date.today(),
            tags="release, product, customers",
            notes="Manual publishing test campaign.",
        )
        db.session.add(campaign)
        db.session.flush()

        dispatch = Dispatch(
            campaign_id=campaign.id,
            title="Platform Release 1.2 Is Live",
            internal_name="release-1-2-announcement",
            status="Review",
            primary_body=(
                "Platform Release 1.2 is now live. This update improves the daily "
                "publishing workflow, adds better queue visibility, and makes it "
                "easier to track posted links after each channel goes live."
            ),
            summary="Release 1.2 improves workflow visibility and manual publishing.",
            short_version="Release 1.2 is live with queue and tracking improvements.",
            call_to_action="Open the release notes",
            tags="release-notes, launch",
            notes="Use platform settings to add publishing queue targets.",
        )
        db.session.add(dispatch)
        db.session.flush()

        db.session.add(
            MediaAsset(
                organization_id=org.id,
                asset_type="Image",
                source_type="External URL",
                title="Release Hero",
                url="https://example.com/release-hero.png",
                alt_text="Abstract product release hero image",
                notes="Approved for website and social use.",
                approved=True,
            )
        )

        settings = [
            PlatformSetting(
                organization_id=org.id,
                platform_name="Website",
                enabled=True,
                destination_url="https://example.com/admin/posts/new",
                posting_method="Manual CMS",
                supports_markdown=True,
                supports_html=True,
                supports_images=True,
                default_footer=org.default_footer,
            ),
            PlatformSetting(
                organization_id=org.id,
                platform_name="LinkedIn",
                enabled=True,
                destination_url="https://www.linkedin.com/feed/",
                posting_method="Manual",
                character_limit=3000,
                supports_images=True,
                default_hashtags="#ProductUpdate",
            ),
            PlatformSetting(
                organization_id=org.id,
                platform_name="Discord",
                enabled=True,
                destination_url="https://discord.com/channels/",
                posting_method="Manual",
                character_limit=2000,
                supports_markdown=True,
                supports_images=True,
            ),
        ]
        db.session.add_all(settings)
        db.session.flush()
        db.session.add_all(
            [
                PublishingQueueItem(
                    dispatch_id=dispatch.id,
                    platform_setting_id=settings[0].id,
                    platform_name=settings[0].platform_name,
                    status="Ready",
                    destination_url=settings[0].destination_url,
                    notes="Seeded manual publishing queue item.",
                ),
                PublishingQueueItem(
                    dispatch_id=dispatch.id,
                    platform_setting_id=settings[1].id,
                    platform_name=settings[1].platform_name,
                    status="Ready",
                    destination_url=settings[1].destination_url,
                    notes="Adapt manually from the source dispatch copy.",
                ),
            ]
        )
        db.session.commit()

        click.echo(f"Seeded {current_app.name} with example data.")


def backfill_organization_slugs():
    used_slugs = {
        slug
        for (slug,) in db.session.query(Organization.slug).filter(Organization.slug.isnot(None))
    }
    changed = False
    for organization in Organization.query.order_by(Organization.id).all():
        if organization.slug:
            continue
        base_slug = slugify(organization.name, f"organization-{organization.id}")
        candidate = base_slug
        suffix = 2
        while candidate in used_slugs:
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        organization.slug = candidate
        used_slugs.add(candidate)
        changed = True
    if changed:
        db.session.commit()
