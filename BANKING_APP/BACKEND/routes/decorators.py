"""
routes/decorators.py
--------------------
Shared route decorators.

login_required wraps any view function and redirects unauthenticated
visitors to the login page before the view body executes.
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_func):
    """Decorator: redirect to /login if no active session exists."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get("customer_id") is None:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper
