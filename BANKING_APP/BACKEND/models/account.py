"""
models/account.py
-----------------
Data-access helpers for the 'accounts' table.
"""


def find_by_customer_id(db, customer_id: int):
    """Return the account row for *customer_id*, or None if not found.

    Columns: id, customer_id, balance
    """
    return db.execute(
        "SELECT id, customer_id, balance FROM accounts WHERE customer_id = ?",
        (customer_id,),
    ).fetchone()


def create_account(db, customer_id: int, opening_balance: float = 0.0) -> int:
    """Create a new account for *customer_id* and return the new account id."""
    cursor = db.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
        (customer_id, opening_balance),
    )
    db.commit()
    return cursor.lastrowid


def update_balance(db, account_id: int, new_balance: float) -> None:
    """Overwrite the stored balance for *account_id*.

    This function does NOT commit — the caller is responsible for committing
    so that the balance update and transaction log insert are atomic.
    """
    db.execute(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (new_balance, account_id),
    )
