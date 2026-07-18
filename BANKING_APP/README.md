# Banking Web Application

A lightweight full-stack banking application built with **Python Flask**, **SQLite**, and **Bootstrap**.

## Features

| Feature | Description |
|---|---|
| Customer Login | Secure login with hashed passwords (werkzeug) |
| Dashboard | View account balance and recent transactions |
| Deposit Funds | Add money to your account |
| Withdraw Funds | Withdraw with balance validation |
| Logout | Session cleared on logout |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 + Bootstrap 5 (Jinja2 templates) |
| Backend | Python 3.10+ / Flask 3.x |
| Database | SQLite (via built-in sqlite3 module) |
| Auth | werkzeug password hashing + Flask signed sessions |

## Project Structure

```
BANKING_APP/
├── FRONTEND/
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── deposit.html
│   │   └── withdraw.html
│   └── static/
│       ├── css/
│       └── js/
├── BACKEND/
│   ├── app.py            # Flask app factory + entry point
│   ├── config.py         # Centralised configuration
│   ├── seed.py           # Seed test customer accounts
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── account_routes.py
│   │   └── decorators.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── account_service.py
│   ├── models/
│   │   ├── customer.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── database/
│   │   ├── db.py
│   │   └── schema.sql
│   ├── tests/
│   │   ├── test_auth_service.py
│   │   ├── test_account_service.py
│   │   └── test_routes.py
│   └── requirements.txt
└── README.md
```

## Quick Start

### 1. Create and activate virtual environment
```bash
cd BANKING_APP/BACKEND
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**

The database and tables are created automatically on first startup.
Seed accounts are inserted on first run.

### 4. Test accounts

| Username | Password | Opening Balance |
|---|---|---|
| alice | password123 | £5,000.00 |
| bob | securepass | £1,200.50 |
| carol | carol2024 | £350.75 |

## Running Tests

```bash
cd BANKING_APP/BACKEND
pytest tests/ -v
```

## Planning Documents

| Document | Description |
|---|---|
| `IMPLEMENTATION_PLAN.md` | High-level architecture and planning |
| `STEP_BY_STEP_IMPLEMENTATION_GUIDE.md` | Step-by-step implementation guide |

---

*Built with IBM Bob*
