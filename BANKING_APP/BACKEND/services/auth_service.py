"""
services/auth_service.py
------------------------
Pure business logic for authentication.

No Flask objects (request, session, g) are imported here.  The service
receives plain Python values and returns plain Python values.  This keeps
the logic testable without starting an HTTP server.
"""

from werkzeug.security import check_password_hash, generate_password_hash
from models.customer import find_by_username


def verify_credentials(db, username: str, password: str):
    """Verify *username* + *password* against the stored hash.

    Returns the customer row (sqlite3.Row) on success, or None on failure.

    Security note: a generic None is returned regardless of whether the
    username does not exist or the password is wrong.  Never leak which
    field failed — doing so helps attackers enumerate valid usernames.
    """
    if not username or not password:
        return None

    customer = find_by_username(db, username)
    if customer is None:
        # Username not found.  Run check_password_hash anyway with a dummy
        # hash to maintain constant-time behaviour and resist timing attacks.
        check_password_hash("pbkdf2:sha256:dummy", password)
        return None

    if not check_password_hash(customer["password"], password):
        return None

    return customer


def hash_password(plain_text_password: str) -> str:
    """Return a salted hash of *plain_text_password*.

    Uses werkzeug's default algorithm (scrypt / pbkdf2:sha256).
    Two calls with the same input produce different hashes because of the
    random salt — that is intentional and correct.
    """
    return generate_password_hash(plain_text_password)
