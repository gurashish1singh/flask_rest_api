from __future__ import annotations

import os
from pathlib import Path


class Config:
    DEBUG = False
    ENV = os.getenv("ENV", "testing")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", "5000")

    SQLALCHEMY_DATABASE_URI = "sqlite:///videos.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "dev"
    TESTING = True


class TestingConfig(Config):
    DEBUG = True
    ENV = "testing"
    TESTING = True
    DB_PATH = f"{Path('.').resolve() / Path('tests')}/videos.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
