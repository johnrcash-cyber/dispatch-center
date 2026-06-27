# Dispatch Center

Dispatch Center is a standalone Flask prototype for planning communications, adapting dispatches for each platform, and tracking manual publishing.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Initialize And Seed

```powershell
$env:FLASK_APP = "run.py"
flask seed
```

The seed command creates a sample organization, campaign, dispatch, platform versions, media asset, and platform settings.

For an existing local database, apply non-destructive schema updates with:

```powershell
$env:FLASK_APP = "run.py"
flask upgrade-db
```

## Run

```powershell
$env:FLASK_APP = "run.py"
flask run --host 127.0.0.1 --port 5055
```

Open `http://127.0.0.1:5055`.

## Included MVP

- Dashboard
- Organizations list, detail, create, edit
- Campaigns list, detail, create, edit
- Dispatches list, detail, create, edit
- Platform versions list, create, edit
- Media library list, create, edit
- Media assets can be uploaded locally to `dispatch_center/static/uploads/<organization-slug>/<asset-type>/` or tracked as external URLs
- Publishing queue with copy controls, destination links, posted URL entry, and mark-published action
- Platform settings list, create, edit

## Notes For Future Work

- Authentication can be added at the app factory or blueprint level.
- Publishing APIs and webhooks belong behind service modules called from queue or platform-version actions.
- Scheduling can be introduced as a separate queue/status layer without changing the core hierarchy.
- Publishing history/version history should be added before automated posting.
