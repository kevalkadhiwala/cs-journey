"""Central settings for file paths and allowed origins.

Every path is built from this file's location, so the project works
no matter which folder you run it from.
"""
import os
from pathlib import Path

# Folder that contains app/, data/, static/ and tests/
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# Can be overridden with an environment variable (the tests use this)
DATABASE_PATH = Path(os.getenv("LOG_ANALYZER_DB", BASE_DIR / "security.db"))
DEFAULT_LOG_PATH = DATA_DIR / "security.log"

# Web pages allowed to call the API from a different origin.
# The dashboard is served by the API itself, so this is only needed
# if you open index.html some other way.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "LOG_ANALYZER_ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000",
    ).split(",")
    if origin.strip()
]

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
