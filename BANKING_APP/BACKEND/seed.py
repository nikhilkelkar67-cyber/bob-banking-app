"""
seed.py
-------
One-time script to populate the database with test customer accounts.

Run once after initialising the database:
    python seed.py

Do NOT run this in production against a database that already has real data —
it will skip existing usernames but this script is purely for development.
"""

import sys
import os

# Allow imports from the BACKEND directory when run directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from config import DATABASE_PATH
from werkzeug.security import generate_password_hash

SEED_CUSTOMERS = [
    {
        "username": "alice",
        "password": "password123",
        "name": "Alice Johnson",
        "opening_balance": 5000.00,
    },
    {
        "username": "bob",
        "password": "securepass",
        "name": "Bob Smith",
        "opening_balance": 1200.50,
    },
    {
        "username": "carol",
        "password": "carol2024",
        "name": "Carol Williams",
        "opening_balance": 350.75,
    },
]


def seed():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    for customer in SEED_CUSTOMERS:
        existing = conn.execute(
            "SELECT id FROM customers WHERE username = ?",
            (customer["username"],),
        ).fetchone()

        if existing:
            print(f"  [skip] username '{customer['username']}' already exists.")
            continue

        hashed = generate_password_hash(customer["password"])
        cursor = conn.execute(
            "INSERT INTO customers (username, password, name) VALUES (?, ?, ?)",
            (customer["username"], hashed, customer["name"]),
        )
        customer_id = cursor.lastrowid

        conn.execute(
            "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
            (customer_id, customer["opening_balance"]),
        )
        conn.commit()
        print(
            f"  [ok]   Created '{customer['name']}' "
            f"(username: {customer['username']}, "
            f"balance: £{customer['opening_balance']:,.2f})"
        )

    conn.close()
    print("\nSeeding complete.")


if __name__ == "__main__":
    seed()
