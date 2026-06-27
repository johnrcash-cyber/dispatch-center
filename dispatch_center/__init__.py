from pathlib import Path

from flask import Flask

from .models import db


def create_app(config_object=None):
    app = Flask(__name__)
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)
    database_path = (instance_path / "dispatch_center.sqlite3").as_posix()
    upload_path = Path(app.static_folder) / "uploads"
    upload_path.mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(upload_path),
    )

    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)

    from .routes.campaigns import campaigns_bp
    from .routes.dispatches import dispatches_bp
    from .routes.main import main_bp
    from .routes.media import media_bp
    from .routes.organizations import organizations_bp
    from .routes.platform_versions import platform_versions_bp
    from .routes.queue import queue_bp
    from .routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(dispatches_bp)
    app.register_blueprint(platform_versions_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(queue_bp)
    app.register_blueprint(settings_bp)

    from .seed import register_seed_command

    register_seed_command(app)

    from .workspace import workspace_guard

    app.before_request(workspace_guard)

    return app
