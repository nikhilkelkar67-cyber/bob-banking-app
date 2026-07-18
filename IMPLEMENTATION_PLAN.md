# Banking Web Application — Implementation Plan

> **Planning document only.** No database schema, SQL scripts, API contracts, or
> detailed implementation steps are included. This document covers architecture,
> component design, folder structure, module breakdown, and the implementation
> roadmap.

---

## 1. Solution Overview

### 1.1 Objective

Deliver a lightweight, browser-based banking application that allows customers to
securely log in, view their account balance, and perform basic transactions
(deposit and withdrawal) through a clean, responsive interface.

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Customer login / logout | Admin or multi-role access |
| View account balance | Inter-account transfers |
| Deposit funds | Loan or credit features |
| Withdraw funds | Mobile native application |
| Session-based security | External payment gateway |

### 1.3 Users

| Actor | Description |
|---|---|
| **Customer** | Authenticated bank customer who manages their own account |

### 1.4 Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | A customer can log in using valid credentials |
| FR-02 | An authenticated customer is redirected to their personal dashboard |
| FR-03 | The dashboard displays the current account balance |
| FR-04 | A customer can deposit a positive monetary amount |
| FR-05 | A customer can withdraw a positive amount not exceeding the current balance |
| FR-06 | A customer can log out, ending the session |
| FR-07 | Unauthenticated users are redirected to the login page |

### 1.5 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | Pages must render correctly on desktop and mobile (Bootstrap responsive grid) |
| NFR-02 | Passwords must be stored as hashed values — never plain text |
| NFR-03 | Session tokens must be invalidated on logout |
| NFR-04 | All monetary amounts must be validated server-side before committing |
| NFR-05 | The application must run locally with a single startup command |

### 1.6 Assumptions

- A single SQLite file is sufficient; no concurrent multi-user production load is
  expected at this stage.
- Each customer has exactly one account.
- The initial customer records (seed data) are created manually or via a helper
  script — not through a registration flow.
- The Flask development server is acceptable for local use; production deployment
  (e.g., Gunicorn + Nginx) is out of scope.

---

## 2. High-Level Architecture

### 2.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                         │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │            FRONTEND  (HTML + Bootstrap)                 │  │
│   │   login.html │ dashboard.html │ deposit.html │          │  │
│   │   withdraw.html │ base template (nav + layout)          │  │
│   └──────────────────────┬──────────────────────────────────┘  │
└─────────────────────────-│──────────────────────────────────────┘
                           │  HTTP Request (form POST / GET)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   BACKEND  (Python Flask)                        │
│                                                                  │
│   Routes / Views          │  Business Logic Layer                │
│   ─────────────────────   │  ──────────────────────────────────  │
│   /login  /logout         │  AuthService   — credential check,  │
│   /dashboard              │                  session management  │
│   /deposit  /withdraw     │  AccountService — balance queries,   │
│                           │                  deposit/withdraw    │
│                           │                  validation          │
│                           │                                      │
│   Session Management (Flask-Session / signed cookie)            │
└──────────────────────────────┬───────────────────────────────────┘
                               │  SQL queries via ORM / sqlite3
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   DATABASE  (SQLite)                             │
│                                                                  │
│   customers table  │  accounts table  │  transactions table      │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Frontend → Backend → Database Interaction

```
Frontend (HTML form)
      │
      │  1. User submits credentials / transaction request
      ▼
Flask Route (view function)
      │
      │  2. Route validates input format; calls service layer
      ▼
Service Layer (AuthService / AccountService)
      │
      │  3. Business rules applied (e.g., balance ≥ withdrawal)
      ▼
Database (SQLite via ORM/sqlite3)
      │
      │  4. Read or write operation executed
      ▼
Service Layer
      │
      │  5. Returns result / error to route
      ▼
Flask Route
      │
      │  6. Renders HTML template with result data or error message
      ▼
Frontend (Browser displays updated page)
```

### 2.3 Request Lifecycle

| Step | Actor | Action |
|---|---|---|
| 1 | Browser | Sends HTTP GET/POST to a Flask route |
| 2 | Flask Route | Checks session validity; rejects or proceeds |
| 3 | Service Layer | Applies domain logic; queries/updates SQLite |
| 4 | Flask Route | Passes context dict to Jinja2 template |
| 5 | Template Engine | Renders HTML with Bootstrap styling |
| 6 | Browser | Displays the rendered page to the customer |

---

## 3. Component Design

### 3.1 Frontend Responsibilities

- Render all user-facing pages using **Bootstrap** for responsive layout.
- Provide HTML forms for login, deposit, and withdrawal input.
- Display server-rendered feedback (success messages, validation errors).
- Enforce basic client-side input constraints (e.g., `required`, `min="0.01"` on
  amount fields) as a UX aid — not as the security boundary.
- Navigation bar shows username and logout link when a session is active.

### 3.2 Backend Responsibilities

- Expose URL routes that map to each application feature.
- Manage user sessions (login, session check on every protected route, logout).
- Validate and sanitize all incoming data **server-side** before acting on it.
- Enforce business rules (e.g., insufficient funds check for withdrawals).
- Render Jinja2 templates, injecting the data the frontend needs.
- Hash passwords on record creation; verify hashes on login — never expose raw
  passwords.

### 3.3 Database Responsibilities

- Persist customer identity and hashed credentials.
- Persist account balance per customer.
- Persist a transaction log (type, amount, timestamp) for auditability.
- Provide transactional integrity for concurrent balance updates (SQLite
  serialized writes are acceptable at this scale).

---

## 4. Folder Structure

```
BankingApp/
│
├── FRONTEND/                  # All browser-facing assets
│   ├── templates/             # Jinja2 HTML templates rendered by Flask
│   │   ├── base.html          # Shared layout, Bootstrap CDN link, nav bar
│   │   ├── login.html         # Login form page
│   │   ├── dashboard.html     # Account summary + action links
│   │   ├── deposit.html       # Deposit form page
│   │   └── withdraw.html      # Withdrawal form page
│   └── static/                # Static assets served directly
│       ├── css/               # Custom stylesheet overrides (if any)
│       └── js/                # Optional client-side scripts
│
├── BACKEND/                   # All server-side Python code
│   ├── app.py                 # Flask app factory and startup entry point
│   ├── config.py              # Environment / app configuration constants
│   ├── routes/                # URL route definitions grouped by feature
│   │   ├── auth_routes.py     # /login, /logout
│   │   └── account_routes.py  # /dashboard, /deposit, /withdraw
│   ├── services/              # Business logic, decoupled from HTTP layer
│   │   ├── auth_service.py    # Credential verification, session helpers
│   │   └── account_service.py # Balance queries, deposit/withdraw logic
│   ├── models/                # Data-layer abstractions (ORM models or helpers)
│   │   ├── customer.py        # Customer entity
│   │   ├── account.py         # Account entity
│   │   └── transaction.py     # Transaction entity
│   ├── database/              # Database lifecycle management
│   │   ├── db.py              # Connection factory / session setup
│   │   └── banking.db         # SQLite database file (auto-created)
│   └── requirements.txt       # Python package dependencies
│
└── IMPLEMENTATION_PLAN.md     # This document
```

| Folder / File | Responsibility |
|---|---|
| `FRONTEND/templates/` | Jinja2 HTML pages rendered server-side by Flask |
| `FRONTEND/static/` | CSS, JS, and image assets served directly by Flask |
| `BACKEND/app.py` | Creates the Flask app, registers blueprints, runs server |
| `BACKEND/config.py` | Centralized config (secret key, DB path, debug flag) |
| `BACKEND/routes/` | Maps HTTP verbs + URLs to handler functions |
| `BACKEND/services/` | Pure business logic with no Flask dependency |
| `BACKEND/models/` | Database entity definitions and query helpers |
| `BACKEND/database/` | DB connection setup and the SQLite file |
| `BACKEND/requirements.txt` | Reproducible Python environment specification |

---

## 5. Module Breakdown

### 5.1 Authentication Module

**Purpose:** Verify customer identity and manage session lifecycle.

| Concern | Detail |
|---|---|
| Login flow | Accept username + password → verify hash → create session |
| Session guard | Decorator / helper that blocks unauthenticated access |
| Logout flow | Clear session data → redirect to login |
| Password security | Hashing via `werkzeug.security` (bcrypt-based) |

**Key files:** `auth_routes.py`, `auth_service.py`, `models/customer.py`

---

### 5.2 Dashboard Module

**Purpose:** Provide the customer's home screen after login.

| Concern | Detail |
|---|---|
| Balance display | Fetch current balance from account record |
| Navigation | Links to Deposit and Withdraw actions |
| Session context | Greet customer by name; show session-based info |

**Key files:** `account_routes.py`, `account_service.py`, `dashboard.html`

---

### 5.3 Account Management Module

**Purpose:** Maintain accurate account state.

| Concern | Detail |
|---|---|
| Balance query | Read balance for authenticated customer's account |
| Data integrity | Ensure balance never drops below zero |
| Audit record | Each transaction creates a transaction log entry |

**Key files:** `account_service.py`, `models/account.py`, `models/transaction.py`

---

### 5.4 Transactions Module

**Purpose:** Handle deposit and withdrawal operations.

| Concern | Detail |
|---|---|
| Deposit | Validate positive amount → increment balance → log entry |
| Withdrawal | Validate positive amount ≤ balance → decrement → log entry |
| Error feedback | Return user-friendly messages on validation failure |
| Atomicity | Balance update + transaction log written in one DB transaction |

**Key files:** `account_routes.py`, `account_service.py`, `deposit.html`, `withdraw.html`

---

## 6. Implementation Roadmap

### Phase 1 — Project Scaffold & Environment Setup

| Task | Effort | Depends On |
|---|---|---|
| Initialize folder structure (`FRONTEND/`, `BACKEND/`) | Low | — |
| Create `requirements.txt` and virtual environment | Low | — |
| Create `app.py` with Flask factory + Blueprint stubs | Low | Folder structure |
| Create `config.py` with placeholder values | Low | — |

**Goal:** A running Flask server that returns a placeholder page with no errors.

---

### Phase 2 — Database Layer

| Task | Effort | Depends On |
|---|---|---|
| Define `db.py` connection factory | Low | Phase 1 |
| Define `customer`, `account`, `transaction` models | Medium | `db.py` |
| Create DB initialization script to set up tables + seed data | Medium | Models |

**Goal:** SQLite file is created and contains seed customer + account records.

---

### Phase 3 — Authentication

| Task | Effort | Depends On |
|---|---|---|
| Implement `AuthService` (hash verify, session helpers) | Medium | Phase 2 |
| Implement `/login` and `/logout` routes | Medium | `AuthService` |
| Build `login.html` template with Bootstrap form | Low | Phase 1 |
| Add session guard decorator for protected routes | Low | `AuthService` |

**Goal:** Customer can log in with valid credentials and is blocked when invalid.

---

### Phase 4 — Dashboard & Account View

| Task | Effort | Depends On |
|---|---|---|
| Implement balance query in `AccountService` | Low | Phase 2 |
| Implement `/dashboard` route | Low | `AccountService`, session guard |
| Build `base.html` layout + `dashboard.html` template | Medium | Phase 1 |

**Goal:** Authenticated customer sees their name and current balance on the dashboard.

---

### Phase 5 — Deposit & Withdrawal

| Task | Effort | Depends On |
|---|---|---|
| Implement deposit logic in `AccountService` | Medium | Phase 2 |
| Implement withdrawal logic + insufficient-funds guard | Medium | Phase 2 |
| Implement `/deposit` and `/withdraw` routes | Medium | `AccountService` |
| Build `deposit.html` and `withdraw.html` templates | Low | `base.html` |

**Goal:** Customer can deposit and withdraw; balance updates correctly; errors shown.

---

### Phase 6 — Integration & Polish

| Task | Effort | Depends On |
|---|---|---|
| End-to-end flow verification (login → transact → logout) | Medium | Phases 3–5 |
| Error and edge-case handling (invalid input, session expiry) | Medium | Phases 3–5 |
| Responsive layout review across screen sizes | Low | All templates |
| Code cleanup, comments, and README | Low | Phase 6 integration |

**Goal:** Complete, working application passes all functional requirements.

---

### Effort Key

| Label | Meaning |
|---|---|
| Low | Small, focused task — straightforward to implement |
| Medium | Requires design thought or touches multiple files |
| High | Complex logic, many edge cases, or cross-cutting concern |

---

*End of Implementation Plan*
