"""
routes/account_routes.py
------------------------
Account Blueprint: /dashboard, /deposit, /withdraw

Every route is protected by the login_required decorator.
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
from services.account_service import get_balance, deposit, withdraw
from models.transaction import recent_transactions
from routes.decorators import login_required

account_bp = Blueprint("account", __name__)


# ---------------------------------------------------------------------------
# Helper: read authenticated customer ID from session
# ---------------------------------------------------------------------------
def _customer_id() -> int:
    return session["customer_id"]


# ---------------------------------------------------------------------------
# GET /dashboard
# ---------------------------------------------------------------------------
@account_bp.route("/dashboard")
@login_required
def dashboard():
    """Render the customer dashboard with current balance and recent activity."""
    db = get_db()
    result = get_balance(db, _customer_id())

    if not result["ok"]:
        flash(result["error"], "danger")
        return redirect(url_for("auth.logout"))

    account_id = result["data"]["account_id"]
    balance = result["data"]["balance"]
    txns = recent_transactions(db, account_id, limit=10)

    return render_template(
        "dashboard.html",
        customer_name=session["customer_name"],
        balance=balance,
        transactions=txns,
    )


# ---------------------------------------------------------------------------
# GET /deposit  — show deposit form
# ---------------------------------------------------------------------------
@account_bp.route("/deposit", methods=["GET"])
@login_required
def deposit_get():
    return render_template("deposit.html", customer_name=session["customer_name"])


# ---------------------------------------------------------------------------
# POST /deposit  — process deposit
# ---------------------------------------------------------------------------
@account_bp.route("/deposit", methods=["POST"])
@login_required
def deposit_post():
    raw_amount = request.form.get("amount", "").strip()

    if not raw_amount:
        flash("Please enter an amount.", "danger")
        return render_template("deposit.html", customer_name=session["customer_name"]), 400

    db = get_db()
    result = deposit(db, _customer_id(), raw_amount)

    if not result["ok"]:
        flash(result["error"], "danger")
        return render_template("deposit.html", customer_name=session["customer_name"]), 400

    flash(result["data"]["message"], "success")
    return redirect(url_for("account.dashboard"))


# ---------------------------------------------------------------------------
# GET /withdraw  — show withdrawal form
# ---------------------------------------------------------------------------
@account_bp.route("/withdraw", methods=["GET"])
@login_required
def withdraw_get():
    db = get_db()
    result = get_balance(db, _customer_id())
    balance = result["data"]["balance"] if result["ok"] else 0.0
    return render_template(
        "withdraw.html",
        customer_name=session["customer_name"],
        balance=balance,
    )


# ---------------------------------------------------------------------------
# POST /withdraw  — process withdrawal
# ---------------------------------------------------------------------------
@account_bp.route("/withdraw", methods=["POST"])
@login_required
def withdraw_post():
    raw_amount = request.form.get("amount", "").strip()

    if not raw_amount:
        flash("Please enter an amount.", "danger")
        db = get_db()
        result = get_balance(db, _customer_id())
        balance = result["data"]["balance"] if result["ok"] else 0.0
        return render_template(
            "withdraw.html",
            customer_name=session["customer_name"],
            balance=balance,
        ), 400

    db = get_db()
    result = withdraw(db, _customer_id(), raw_amount)

    if not result["ok"]:
        flash(result["error"], "danger")
        balance_result = get_balance(db, _customer_id())
        balance = balance_result["data"]["balance"] if balance_result["ok"] else 0.0
        return render_template(
            "withdraw.html",
            customer_name=session["customer_name"],
            balance=balance,
        ), 400

    flash(result["data"]["message"], "success")
    return redirect(url_for("account.dashboard"))
