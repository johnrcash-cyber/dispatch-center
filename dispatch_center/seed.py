from datetime import date

import click
from flask import current_app

from .models import (
    Campaign,
    Dispatch,
    MediaAsset,
    Organization,
    PlatformSetting,
    PlatformVersion,
    db,
)


def register_seed_command(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("seed")
    def seed():
        db.drop_all()
        db.create_all()

        org = Organization(
            name="Northstar Labs",
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
            canonical_link="https://example.com/releases/1-2",
            tags="release-notes, launch",
            notes="Create platform versions for web, LinkedIn, Discord, and newsletter.",
        )
        db.session.add(dispatch)
        db.session.flush()

        versions = [
            PlatformVersion(
                dispatch_id=dispatch.id,
                platform_name="Website",
                status="Ready",
                platform_title="Platform Release 1.2 Is Live",
                platform_body=dispatch.primary_body,
                call_to_action="Read the release notes",
                selected_image_urls="https://example.com/release-hero.png",
                destination_url="https://example.com/admin/posts/new",
            ),
            PlatformVersion(
                dispatch_id=dispatch.id,
                platform_name="LinkedIn",
                status="Ready",
                platform_title="Platform Release 1.2 is live",
                platform_body=(
                    "Release 1.2 is live. We improved queue visibility, manual "
                    "publishing workflows, and posted-link tracking for teams "
                    "coordinating across channels."
                ),
                short_text="Release 1.2 is live.",
                hashtags="#ProductUpdate #ReleaseNotes",
                selected_image_urls="https://example.com/release-social.png",
                destination_url="https://www.linkedin.com/feed/",
            ),
            PlatformVersion(
                dispatch_id=dispatch.id,
                platform_name="Discord",
                status="Draft",
                platform_title="Release 1.2 is live",
                platform_body=(
                    "Release 1.2 is live. Check out the improved queue and tracking "
                    "workflow in the release notes."
                ),
                destination_url="https://discord.com/channels/",
            ),
        ]
        db.session.add_all(versions)

        db.session.add(
            MediaAsset(
                organization_id=org.id,
                campaign_id=campaign.id,
                dispatch_id=dispatch.id,
                asset_type="Image",
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
        db.session.commit()

        click.echo(f"Seeded {current_app.name} with example data.")
