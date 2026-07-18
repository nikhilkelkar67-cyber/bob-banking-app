"""
database/db.py
--------------
Database connection factory.

All database access throughout the application goes through get_db().
The connection is stored on Flask's per-request 'g' object so that each
request uses exactly one connection, which is automatically closed when
the request teardown fires.
"""

import sqlite3
import click
from flask import g, current_app


def get_db():
    """Return an open SQLite connection for the current request.

    Opens a new connection the first time it is called within a request and
    stores it on `g`.  Subsequent calls within the same request return the
    cached connection.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # Return rows as dict-like objects so columns are accessible by name.
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection at the end of a request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables from schema.sql if they do not already exist."""
    db = get_db()
    with current_app.open_resource(current_app.config["SCHEMA_PATH"]) as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
def init_db_command():
    """Flask CLI command: flask init-db"""
    init_db()
    click.echo("Database initialised.")


def init_app(app):
    """Register teardown and CLI command with the Flask application."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
