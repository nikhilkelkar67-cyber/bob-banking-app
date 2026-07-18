"""
routes/auth_routes.py
---------------------
Authentication Blueprint: /login, /logout
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from database.db import get_db
from services.auth_service import verify_credentials

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# GET /login  — show login form
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET"])
def login():
    """Render the login page.

    If the user is already authenticated, send them straight to the
    dashboard — no need to show the login form again.
    """
    if session.get("customer_id"):
        return redirect(url_for("account.dashboard"))
    return render_template("login.html")


# ---------------------------------------------------------------------------
# POST /login  — process credentials
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login_post():
    """Validate submitted credentials and create a session on success."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Basic presence check before hitting the database.
    if not username or not password:
        flash("Username and password are required.", "danger")
        return render_template("login.html"), 400

    db = get_db()
    customer = verify_credentials(db, username, password)

    if customer is None:
        # Generic message — do not reveal which field was wrong.
        flash("Invalid username or password.", "danger")
        return render_template("login.html"), 401

    # Credentials are valid — store minimal identity in the signed cookie.
    session.clear()
    session["customer_id"] = customer["id"]
    session["customer_name"] = customer["name"]

    return redirect(url_for("account.dashboard"))


# ---------------------------------------------------------------------------
# GET /logout  — end the session
# ---------------------------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    """Clear the session and redirect to the login page."""
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# GET /  — root redirect
# ---------------------------------------------------------------------------
@auth_bp.route("/")
def index():
    """Redirect the application root to the login page."""
    return redirect(url_for("auth.login"))
