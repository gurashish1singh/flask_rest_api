from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

basedir = Path().resolve()
load_dotenv(basedir / Path(".env"))


class Config:
    DEBUG = False
    ENV = os.getenv("ENV", "testing")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT", "5000")


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    TESTING = True


class TestingConfig(Config):
    DEBUG = True
    ENV = "testing"
    TESTING = True
