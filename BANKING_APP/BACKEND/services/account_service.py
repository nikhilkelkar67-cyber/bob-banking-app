"""
services/account_service.py
----------------------------
Business logic for account management: balance queries, deposits, and
withdrawals.

All functions return a dict with two keys:
    {"ok": True,  "data":  <value>}   on success
    {"ok": False, "error": <message>} on failure

Routes inspect the "ok" flag and forward the error string to the template
via flash() when needed.
"""

from models.account import find_by_customer_id, update_balance
from models.transaction import record_transaction


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _get_account_or_error(db, customer_id: int):
    """Return (account_row, None) or (None, error_dict)."""
    account = find_by_customer_id(db, customer_id)
    if account is None:
        return None, {"ok": False, "error": "Account not found."}
    return account, None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_balance(db, customer_id: int) -> dict:
    """Return the current balance for *customer_id*.

    Success: {"ok": True, "data": {"account_id": int, "balance": float}}
    """
    account, err = _get_account_or_error(db, customer_id)
    if err:
        return err
    return {"ok": True, "data": {"account_id": account["id"], "balance": account["balance"]}}


def deposit(db, customer_id: int, raw_amount) -> dict:
    """Deposit *raw_amount* into the account belonging to *customer_id*.

    Validation:
    - Amount must be convertible to a positive float.
    - Amount must be greater than zero.

    On success the balance is updated and a transaction log entry is created
    in a single commit (atomic).
    """
    # --- Amount validation ---
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Please enter a valid numeric amount."}

    if amount <= 0:
        return {"ok": False, "error": "Deposit amount must be greater than zero."}

    # Round to 2 decimal places to avoid floating-point drift.
    amount = round(amount, 2)

    account, err = _get_account_or_error(db, customer_id)
    if err:
        return err

    new_balance = round(account["balance"] + amount, 2)

    # Both writes must succeed or neither should — use a single commit.
    update_balance(db, account["id"], new_balance)
    record_transaction(db, account["id"], "deposit", amount)
    db.commit()

    return {
        "ok": True,
        "data": {
            "new_balance": new_balance,
            "amount": amount,
            "message": f"Successfully deposited £{amount:,.2f}.",
        },
    }


def withdraw(db, customer_id: int, raw_amount) -> dict:
    """Withdraw *raw_amount* from the account belonging to *customer_id*.

    Validation:
    - Amount must be convertible to a positive float.
    - Amount must be greater than zero.
    - Amount must not exceed the current balance.

    On success the balance is updated and a transaction log entry is created
    in a single commit (atomic).
    """
    # --- Amount validation ---
    try:
        amount = float(raw_amount)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Please enter a valid numeric amount."}

    if amount <= 0:
        return {"ok": False, "error": "Withdrawal amount must be greater than zero."}

    amount = round(amount, 2)

    account, err = _get_account_or_error(db, customer_id)
    if err:
        return err

    if amount > round(account["balance"], 2):
        return {
            "ok": False,
            "error": (
                f"Insufficient funds. "
                f"Your balance is £{account['balance']:,.2f} "
                f"but you requested £{amount:,.2f}."
            ),
        }

    new_balance = round(account["balance"] - amount, 2)

    update_balance(db, account["id"], new_balance)
    record_transaction(db, account["id"], "withdrawal", amount)
    db.commit()

    return {
        "ok": True,
        "data": {
            "new_balance": new_balance,
            "amount": amount,
            "message": f"Successfully withdrew £{amount:,.2f}.",
        },
    }
