from __future__ import annotations

from flask import Flask
from flask_restful import Api


def create_app() -> Flask:
    app = Flask(__name__)
    api = Api(app)
    app.api = api

    from flask_rest_api.app import Video

    api.add_resource(Video, "/video/<int:video_id>")

    return app
