**Dispatch Center** is a centralized communications hub that helps organizations plan, create, manage, and distribute content across every communication channel from a single source. Instead of rewriting the same announcement for a website, blog, newsletter, Discord, LinkedIn, Substack, and other platforms, users create one campaign, build the content once, and generate platform-specific versions that can be published manually or through future integrations. Every announcement, image, document, and published link is organized and tracked throughout its lifecycle.

Built around a simple hierarchy of **Organizations → Campaigns → Dispatches → Platform Versions**, Dispatch Center gives teams a clear view of what they're communicating, where it's being published, and what still needs to be done. Whether managing product launches, release notes, investor updates, community announcements, or marketing campaigns, Dispatch Center serves as the operational command center for communications—keeping messaging consistent, assets organized, and publishing workflows efficient while remaining flexible enough to grow from manual copy-and-paste publishing into full automation over time.



this is the starting map:
================================================================================
DISPATCH CENTER
Communications • Publishing • Distribution
================================================================================

MISSION

Create once.
Adapt everywhere.
Track everything.

Organization
    ↓
Campaign
    ↓
Dispatch
    ↓
Platform Version
    ↓
Publish

================================================================================
ORGANIZATIONS
================================================================================

Top-level container.

Examples

Grid & Ink

Northstar

Personal

Client XYZ

Each Organization contains:

- Name
- Description
- Logo
- Website
- Brand Colors
- Default CTA
- Default Footer
- Brand Assets
- Team Members (Future)
- Platform Accounts
- Settings

Organization Dashboard

Campaigns

Media Library

Templates

Publishing Queue

Settings

Analytics (Future)

================================================================================
CAMPAIGNS
================================================================================

A Campaign represents ONE initiative.

Examples

GRID & INK

Arbiter Soft Launch

Monster Manifest

The Intrusion Event

Arena Expansion

Northstar

Investor Raise

Platform Release 1.2

Weekly Market Report

Customer Webinar

Campaign Fields

Name

Description

Category

Status

Planning

Active

Review

Publishing

Completed

Archived

Owner

Priority

Start Date

Target Publish Date

Completion %

Tags

Notes

================================================================================
CAMPAIGN ASSETS
================================================================================

Hero Image

Thumbnail

Banner

Videos

Documents

Attachments

Shared Media

Brand Assets

Media Notes

================================================================================
CAMPAIGN TIMELINE
================================================================================

Campaign Created

Assets Ready

Copy Complete

Review Complete

Publishing Started

Publishing Finished

Archived

================================================================================
DISPATCHES
================================================================================

Each Campaign contains one or more Dispatches.

Examples

Website Article

Substack

Discord Announcement

Newsletter

Release Notes

Facebook

LinkedIn

Investor Email

Dispatch Fields

Title

Internal Name

Status

Primary Body

Summary

Short Version

Call To Action

Canonical Link

Tags

Notes

================================================================================
PLATFORM VERSIONS
================================================================================

Each Dispatch can generate one version per platform.

Supported Platforms

Website

WordPress

Substack

Discord

LinkedIn

Facebook

Instagram

X

Bluesky

Email Newsletter

Slack

Teams

Customer Portal

Investor Portal

Each Platform Version stores

Title

Body

Short Text

CTA

Images

Hashtags

Formatting Notes

Character Count

Destination URL

Posted URL

Posted Date

Publishing Status

================================================================================
PUBLISHING QUEUE
================================================================================

Campaign
↓

Dispatch
↓

Platform

Queue

□ Website

□ WordPress

□ Substack

□ Discord

□ LinkedIn

□ Facebook

□ Email

Actions

Copy Title

Copy Body

Copy Images

Open Destination

Mark Published

View Published Link

================================================================================
MEDIA LIBRARY
================================================================================

Organization-wide.

Folders

Images

Videos

Documents

Logos

Icons

Brand Kits

Search

Tags

Usage Tracking

================================================================================
TEMPLATES
================================================================================

Campaign Templates

Product Launch

Release Notes

Weekly Update

Investor Update

Maintenance

Community Update

Dispatch Templates

Website

WordPress

Substack

Discord

LinkedIn

Facebook

Newsletter

================================================================================
SETTINGS
================================================================================

Organization Settings

Branding

Publishing Accounts

Platform Defaults

Character Limits

Footer Templates

CTA Templates

Webhook/API Settings

================================================================================
HISTORY
================================================================================

Campaign History

Dispatch History

Publishing Log

Version History

Posted URLs

================================================================================
ROADMAP
================================================================================

PHASE 1 (MVP)

Organizations

Campaigns

Dispatches

Platform Versions

Media Library

Publishing Queue

Copy Buttons

Open Destination Buttons

Mark Published

Posted URLs

--------------------------------------------------

PHASE 2

WordPress Publishing

Discord Webhooks

Scheduling

Approval Workflow

Calendar View

Kanban View

--------------------------------------------------

PHASE 3

AI Platform Rewrites

Analytics

Email Integration

Campaign Metrics

Auto Publishing

URL Shortening

Multi-user Collaboration

================================================================================
DATA MODEL
================================================================================

Organization
    ├── Campaigns
    ├── Assets
    ├── Templates
    ├── Platform Accounts
    └── Settings

Campaign
    ├── Dispatches
    ├── Assets
    ├── Timeline
    └── Notes

Dispatch
    ├── Platform Versions
    ├── Media
    └── Publishing Status

Platform Version
    ├── Platform
    ├── Content
    ├── Formatting
    ├── Posted URL
    └── Publishing Status
	
	
	
	
	
	initial codex instructions:
	
	We are starting a new standalone project called **Dispatch Center**.

Dispatch Center is a lightweight communications and publishing hub. It is not part of Arbiter or Grid & Ink, though those may be future users of it.

Build the project as a clean standalone Flask web app with a simple admin-style interface.

Core hierarchy:

Organization
→ Campaign
→ Dispatch
→ Platform Version

Purpose:
Users should be able to create one organization, create campaigns under that organization, create dispatches under each campaign, and create platform-specific publishing versions for each dispatch.

MVP Requirements:

1. Organizations

* Create/edit/list organizations
* Fields:

  * name
  * description
  * website_url
  * logo_url
  * default_cta
  * default_footer
  * notes

2. Campaigns

* Campaigns belong to an Organization
* Create/edit/list campaigns
* Fields:

  * organization_id
  * name
  * description
  * category
  * status
  * owner
  * priority
  * start_date
  * target_publish_date
  * tags
  * notes

3. Dispatches

* Dispatches belong to a Campaign
* Create/edit/list dispatches
* Fields:

  * campaign_id
  * title
  * internal_name
  * status
  * primary_body
  * summary
  * short_version
  * call_to_action
  * canonical_link
  * tags
  * notes

4. Platform Versions

* Platform versions belong to a Dispatch
* Create/edit/list platform versions
* Fields:

  * dispatch_id
  * platform_name
  * status
  * platform_title
  * platform_body
  * short_text
  * call_to_action
  * selected_image_urls
  * hashtags
  * formatting_notes
  * destination_url
  * posted_url
  * posted_at

5. Media Assets

* Assets can belong to an Organization, Campaign, or Dispatch
* Create/edit/list assets
* Fields:

  * organization_id
  * campaign_id
  * dispatch_id
  * asset_type
  * title
  * url
  * alt_text
  * notes
  * approved

6. Publishing Queue

* Show platform versions that are not published
* Include buttons or controls for:

  * Copy title
  * Copy body
  * Copy image URLs
  * Open destination URL
  * Mark as Published
  * Add posted URL

7. Settings

* Basic platform settings table
* Fields:

  * organization_id
  * platform_name
  * enabled
  * destination_url
  * posting_method
  * character_limit
  * supports_markdown
  * supports_html
  * supports_images
  * default_hashtags
  * default_footer
  * notes

Technical Direction:

* Use Flask
* Use SQLite
* Use SQLAlchemy if appropriate
* Use templates with clean reusable layout
* Use Bootstrap or simple custom CSS
* Keep the interface clean, dark-mode friendly, and practical
* No external APIs yet
* No scheduling yet
* No authentication required for the first local prototype unless already easy to add
* Manual copy/paste workflow is the priority
* Include a seeded example organization, campaign, dispatch, and platform versions for testing

Initial pages/routes wanted:

* Dashboard
* Organizations list/detail/edit
* Campaigns list/detail/edit
* Dispatches list/detail/edit
* Platform Versions edit/list
* Media Library
* Publishing Queue
* Settings

Please start by creating the project structure, database models, routes, templates, and a minimal working interface. Keep the code organized so future API integrations can be added later.
