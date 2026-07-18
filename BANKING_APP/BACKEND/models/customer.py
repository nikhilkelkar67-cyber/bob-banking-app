"""
models/customer.py
------------------
Data-access helpers for the 'customers' table.

Each function accepts an open db connection (sqlite3.Connection) so that
callers control transaction boundaries and connection lifecycle.
"""


def find_by_username(db, username: str):
    """Return the customer row matching *username*, or None if not found.

    The returned object is a sqlite3.Row; access columns by name:
        row["id"], row["username"], row["password"], row["name"]
    """
    return db.execute(
        "SELECT id, username, password, name FROM customers WHERE username = ?",
        (username,),
    ).fetchone()


def find_by_id(db, customer_id: int):
    """Return the customer row for *customer_id*, or None if not found."""
    return db.execute(
        "SELECT id, username, name FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()


def create_customer(db, username: str, hashed_password: str, name: str) -> int:
    """Insert a new customer record and return the new row id.

    *hashed_password* must already be a werkzeug hash string — never pass a
    plain-text password to this function.
    """
    cursor = db.execute(
        "INSERT INTO customers (username, password, name) VALUES (?, ?, ?)",
        (username, hashed_password, name),
    )
    db.commit()
    return cursor.lastrowid
