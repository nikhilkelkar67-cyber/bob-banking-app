"""
models/transaction.py
---------------------
Data-access helpers for the 'transactions' table.
"""


def record_transaction(db, account_id: int, tx_type: str, amount: float) -> int:
    """Insert a transaction log entry and return the new row id.

    *tx_type* must be 'deposit' or 'withdrawal' (enforced by DB CHECK constraint).
    This function does NOT commit — the caller commits together with the
    balance update to keep both writes atomic.
    """
    cursor = db.execute(
        """
        INSERT INTO transactions (account_id, type, amount)
        VALUES (?, ?, ?)
        """,
        (account_id, tx_type, amount),
    )
    return cursor.lastrowid


def recent_transactions(db, account_id: int, limit: int = 10):
    """Return the *limit* most recent transactions for *account_id*.

    Rows are ordered newest-first.
    Columns: id, account_id, type, amount, created_at
    """
    return db.execute(
        """
        SELECT id, account_id, type, amount, created_at
        FROM   transactions
        WHERE  account_id = ?
        ORDER  BY created_at DESC, id DESC
        LIMIT  ?
        """,
        (account_id, limit),
    ).fetchall()
