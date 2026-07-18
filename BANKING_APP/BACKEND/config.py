import os

# ---------------------------------------------------------------------------
# Application Configuration
# All tunable values live here.  Import this module; never hard-code values
# in routes or services.
# ---------------------------------------------------------------------------

# Secret key used by Flask to sign session cookies.
# In production, set the SECRET_KEY environment variable to a long random
# string and never commit it to source control.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Absolute path to the SQLite database file.
# __file__ resolves to config.py inside BACKEND/, so we anchor the db path
# relative to that directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "banking.db")

# SQL script that creates the schema tables.
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Enable auto-reload and detailed error pages during development.
# Set to False (or the env var DEBUG=0) before any production deployment.
DEBUG = os.environ.get("DEBUG", "1") == "1"
