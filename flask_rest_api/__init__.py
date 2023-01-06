from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from werkzeug.utils import import_string

basedir = Path().resolve()
load_dotenv(basedir / Path(".env"))

CONFIGS = {
    "default": "config.DevelopmentConfig",
    "dev": "config.DevelopmentConfig",
    "testing": "config.TestingConfig",
}


def create_app() -> Flask:
    app = Flask(__name__)
    config_name = os.environ.get("ENV", "default")
    try:
        config = import_string(CONFIGS[config_name])()
        app.config.from_object(config)
    except KeyError as e:
        raise KeyError(f"Failed to create app, {config_name!r} isn't a valid environment string", e)

    api = Api(app)
    app.api = api

    from flask_rest_api.models import db

    db.init_app(app)
    app.db = db
    with app.app_context():
        db.create_all()

    from flask_rest_api.app import Video

    api.add_resource(Video, "/video/<int:video_id>")

    return app
