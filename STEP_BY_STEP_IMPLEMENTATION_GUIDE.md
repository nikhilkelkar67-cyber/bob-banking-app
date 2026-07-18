# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** This guide is derived from `IMPLEMENTATION_PLAN.md`.
> Instructions are written in plain English — they describe **what to build**,
> **why each piece exists**, and **how the pieces connect**. No full source code
> is provided; the intent is to guide a developer through every decision.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites

Before writing a single line of application code, confirm the following tools
are available on the development machine:

- **Python 3.10+** — the runtime for the Flask backend.
- **pip** — the Python package installer (bundled with Python).
- **A code editor** (VS Code, PyCharm, or any preferred editor).
- **A terminal / command prompt** with the project directory accessible.

No other global tools are required; everything else is installed locally inside
a virtual environment.

---

### 1.2 Create a Virtual Environment

A virtual environment isolates this project's Python dependencies from the rest
of the system. This prevents version conflicts with other Python projects.

- Navigate to the root of the project (`BankingApp/`) in the terminal.
- Create a new virtual environment in a folder conventionally called `venv`.
- Once created, **activate** the virtual environment. After activation the
  terminal prompt will show the environment name, confirming all subsequent
  `pip install` commands install into this isolated space rather than globally.
- The `venv/` folder should be added to `.gitignore` — it is machine-specific
  and should never be committed.

---

### 1.3 Define and Install Dependencies

All required packages are declared in `BACKEND/requirements.txt` so that the
environment can be reproduced exactly on any machine.

The packages needed for this project are:

| Package | Why it is needed |
|---|---|
| `Flask` | The web framework — handles routing, templates, and sessions |
| `werkzeug` | Bundled with Flask; provides the password hashing utilities |
| `flask-session` | Optional: server-side session store if signed cookies are not enough |

With the virtual environment active, run the install command pointing at
`requirements.txt`. All packages will be downloaded and installed locally.

---

### 1.4 Create the Folder Structure

Physically create the directories as laid out in the architecture plan before
writing any files inside them. Having the structure in place first prevents
import path confusion later.

```
BankingApp/
├── FRONTEND/
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── BACKEND/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── database/
│   └── requirements.txt
└── IMPLEMENTATION_PLAN.md
```

Each folder maps to a specific responsibility described in Section 4 of the
implementation plan. Creating them up front makes it obvious where each new
file belongs.

---

### 1.5 Verify Flask is Working

Before any application logic is written, create a minimal `app.py` that
starts the Flask development server and returns a simple "Hello, Banking App"
response. Run it and open the browser at `http://127.0.0.1:5000`. If the page
loads, the environment is correctly configured and you can proceed.

---

## 2. Backend Implementation

### 2.1 Application Entry Point — `app.py`

`app.py` is the root of the Flask application. Its responsibilities are:

1. **Create the Flask app instance** — this is the object that powers the
   entire server.
2. **Load configuration** from `config.py` — this includes the secret key used
   to sign session cookies and the path to the SQLite database file.
3. **Tell Flask where to find templates and static files** — point it at the
   `FRONTEND/templates/` and `FRONTEND/static/` directories, since they live
   outside the default `BACKEND/` folder.
4. **Register Blueprints** — Blueprints are Flask's way of grouping related
   routes. Register the authentication blueprint and the account blueprint.
5. **Initialize the database** — call the database setup function so that
   tables are created if they do not already exist when the server starts.
6. **Run the development server** — only when the script is executed directly,
   not when it is imported as a module.

---

### 2.2 Configuration — `config.py`

Centralizing configuration in one file means you only change one place when
switching between development and production settings.

Key values to define here:

- **SECRET_KEY** — a long, random string Flask uses to sign and verify session
  cookies. If this leaks, sessions can be forged. Use a randomly generated
  value, not a guessable string.
- **DATABASE_PATH** — the file system path to `banking.db` so that every part
  of the backend that needs the database can find it consistently.
- **DEBUG** — a boolean flag. Set to `True` during development (auto-reloads
  on code changes, shows detailed error pages) and `False` in production.

---

### 2.3 Database Setup — `database/db.py`

This file owns the relationship between the application and SQLite. Its single
responsibility is to provide a clean, open database connection whenever the
rest of the application needs one.

How to think about it:

- When a request comes in, the route or service asks for a connection.
- `db.py` opens a connection to `banking.db` (creating the file if it does not
  exist) and returns it.
- When the request finishes, the connection is closed to free up resources.

Flask provides a mechanism called the **application context** (specifically
`g`, a per-request global) that is the conventional place to store the
connection for the lifetime of a single request. Using this pattern prevents
opening multiple connections for the same request and ensures automatic cleanup.

Also define an `init_db()` function here that reads a setup script and creates
all tables from scratch. This function is called once at startup.

---

### 2.4 Data Models — `models/`

Models describe the shape of the data. Each model file contains logic for
reading and writing one kind of entity to and from the database.

#### `models/customer.py`

Represents a bank customer (a person who can log in).

What it needs to do:
- **Find a customer by username** — used during login to look up who is trying
  to authenticate.
- **Create a new customer** — used by the seed/setup script to insert test
  accounts. Passwords must be hashed before being passed to this function.

#### `models/account.py`

Represents a bank account belonging to a customer.

What it needs to do:
- **Get the account for a customer** — given a customer ID, return their
  account record including the current balance.
- **Update the balance** — write a new balance value for an account. This is
  called by the service layer after a deposit or withdrawal is approved.

#### `models/transaction.py`

Represents a single financial event (deposit or withdrawal).

What it needs to do:
- **Record a transaction** — insert a row with the account ID, the type
  ("deposit" or "withdrawal"), the amount, and the current timestamp.
- **List recent transactions** — optionally, fetch the last N transactions for
  an account to display on the dashboard.

---

### 2.5 Authentication Routes — `routes/auth_routes.py`

This file defines a Flask **Blueprint** containing two routes.

#### `GET /login`

Simply renders the login page template. If the user already has an active
session (they are already logged in), redirect them straight to the dashboard
— there is no reason to show the login form again.

#### `POST /login`

This route handles the form submission from the login page.

The logic flow:
1. Extract the username and password from the submitted form data.
2. Call the `AuthService` to verify the credentials.
3. If verification succeeds, store the customer's ID (and optionally their
   name) into the session. Then redirect to the dashboard.
4. If verification fails, re-render the login page with a clear error message
   like "Invalid username or password." Do not reveal which field was wrong —
   this is a security best practice.

#### `GET /logout`

Clear all data from the session object. Redirect to the login page. The
session cookie is effectively invalidated because its contents are erased.

---

### 2.6 Account Routes — `routes/account_routes.py`

This Blueprint contains routes for everything the customer does after logging
in. Every route here must be **protected** — if there is no active session,
the user is redirected to `/login` immediately.

#### `GET /dashboard`

1. Read the customer ID from the session.
2. Ask `AccountService` for the current balance.
3. Render the dashboard template, passing in the customer name and balance.

#### `GET /deposit`

Render the deposit form template. Pass in any flash messages (e.g., a success
or error message from a previous submission).

#### `POST /deposit`

1. Read the amount from the form.
2. Pass it to `AccountService.deposit()`.
3. The service validates and processes the deposit.
4. On success, redirect back to the dashboard (or re-render the deposit page
   with a success message).
5. On failure (invalid input), re-render the deposit form with the error.

#### `GET /withdraw`

Render the withdrawal form template. Same pattern as the deposit GET.

#### `POST /withdraw`

Exactly the same pattern as POST /deposit, but calls
`AccountService.withdraw()` instead.

---

### 2.7 Authentication Service — `services/auth_service.py`

The service layer contains **pure business logic** — no Flask objects, no HTTP
concepts, just functions that take inputs and return outputs.

#### `verify_credentials(username, password)`

1. Query the customer model for a record matching the given username.
2. If no record is found, return failure immediately. Do not expose that the
   username does not exist — just return a generic failure.
3. If a record is found, use `werkzeug.security.check_password_hash()` to
   compare the submitted password against the stored hash.
4. Return the customer record on success, or `None` on failure.

#### `hash_password(plain_text_password)`

A thin wrapper around `werkzeug.security.generate_password_hash()`. Used by
the seed script when creating test customer records. Keeping this in the
service layer means the hash algorithm is configured in one place.

---

### 2.8 Account Service — `services/account_service.py`

#### `get_balance(customer_id)`

Look up the account record for this customer and return the balance value.
This is called by the dashboard route.

#### `deposit(customer_id, amount)`

1. Validate that the amount is a positive number (greater than zero).
2. Fetch the current balance.
3. Compute the new balance by adding the amount to the current balance.
4. Write the new balance to the account record.
5. Write a transaction log entry with type "deposit".
6. Return a success result.

If the amount is invalid, return an error result **without touching the
database**. The route will forward this error to the template.

#### `withdraw(customer_id, amount)`

1. Validate that the amount is a positive number.
2. Fetch the current balance.
3. Check that `amount <= current_balance`. If not, return an "Insufficient
   funds" error without touching the database.
4. Compute the new balance.
5. Write the new balance to the account record.
6. Write a transaction log entry with type "withdrawal".
7. Return a success result.

The balance update and transaction log insert should happen inside a single
**database transaction** so that they either both succeed or both fail
together.

---

### 2.9 Session Management Strategy

Flask stores session data in a **signed cookie** by default. The cookie is
signed with the `SECRET_KEY`, which means tampering with it on the client side
will be detected and the session will be rejected.

What to store in the session:
- `session['customer_id']` — the database ID of the logged-in customer.
- `session['customer_name']` — the display name shown in the nav bar.

What **not** to store in the session:
- Passwords (even hashed) — never put credential data in a cookie.
- Account balances — these change frequently; always read them fresh from the
  database.

**Protecting routes:** Create a helper function (or decorator) called
`login_required` that checks whether `session['customer_id']` exists. If it
does not, it redirects to `/login`. Apply this to every account route.

---

### 2.10 Error Handling

Flask provides a mechanism to register custom error handlers for HTTP status
codes. Set up handlers for the two most common cases:

- **404 Not Found** — render a simple "Page not found" page rather than
  Flask's default debug output.
- **500 Internal Server Error** — render a generic "Something went wrong"
  page. Log the actual error server-side for diagnosis.

For user-facing form errors (wrong password, invalid amount), use Flask's
`flash()` system. Flash messages are stored in the session for exactly one
request and then deleted, making them ideal for one-time feedback after a
form submission redirect.

---

## 3. Frontend Implementation

### 3.1 Base Layout — `base.html`

All pages extend this single template. Building it first means that styling
and navigation only need to be written once.

What to include:

- **Bootstrap CDN link** in the `<head>` so all pages automatically pick up
  Bootstrap's CSS and JS without any local file management.
- **Navigation bar** using Bootstrap's `navbar` component. The nav bar should
  show the application name on the left. On the right, show the customer's
  name and a "Logout" link when a session is active. Show nothing (or a
  "Login" link) when no session is active.
- **Flash message container** — a section below the nav bar that loops through
  any flash messages and displays them as Bootstrap alerts (green for success,
  red for error). This block is defined once here and appears on every page
  automatically.
- **Content block** — an empty `{% block content %}{% endblock %}` placeholder
  that child templates fill in with their specific page content.
- **Bootstrap JS** at the bottom of `<body>` for interactive components.

---

### 3.2 Login Page — `login.html`

This is the only page accessible without a session.

Layout intent:
- Use a centered Bootstrap card or a `col-md-4 offset-md-4` grid column so
  the form sits in the middle of the screen on all screen sizes.
- The card contains a heading ("Welcome — Please Log In"), the username field,
  the password field, and a submit button.
- Use `type="password"` on the password field so the browser masks the input.
- The form's `action` attribute must point to `POST /login`.
- Display any flash error messages above the form fields.

No client-side validation is needed beyond the HTML `required` attribute on
both fields — the server handles all real validation.

---

### 3.3 Dashboard Page — `dashboard.html`

This is the customer's home screen after login.

Layout intent:
- Display a greeting at the top: "Welcome back, [Customer Name]."
- Show the current balance in a prominent Bootstrap card — large font, clearly
  labelled "Account Balance."
- Below the balance card, show two action buttons side by side: "Deposit" and
  "Withdraw." Each is a link styled as a Bootstrap button pointing to the
  respective routes.
- Optionally add a simple transaction history section below — a Bootstrap
  table listing the last few transactions (type, amount, date). This can be
  added in a later iteration.

---

### 3.4 Deposit Page — `deposit.html`

Layout intent:
- A centered card (same visual pattern as the login page for consistency).
- Heading: "Deposit Funds."
- A single number input field labelled "Amount" with `min="0.01"` and
  `step="0.01"` attributes. This gives the browser's native number picker
  sensible increments and prevents obviously invalid values at the UI level.
- A "Deposit" submit button.
- A "Back to Dashboard" link below the button.
- Display any flash error or success messages above the form.

---

### 3.5 Withdraw Page — `withdraw.html`

Identical structure to the deposit page with two differences:

- Heading reads "Withdraw Funds."
- It is helpful to show the current balance above the form so the customer
  knows their limit before they type an amount. Pass the balance from the
  route to the template for this purpose.

---

### 3.6 Bootstrap Layout Principles to Follow

- Use the **12-column grid** (`col-md-*`) to control how wide elements are on
  medium and larger screens.
- Wrap page content in a `container` or `container-fluid` div to provide
  automatic horizontal padding.
- Use Bootstrap's **spacing utilities** (`mt-`, `mb-`, `p-`) instead of
  writing custom CSS for margins and padding — this keeps the markup clean and
  consistent.
- Use Bootstrap's **color utilities** for contextual meaning: `text-success`
  for positive balance messages, `text-danger` for errors and low-balance
  warnings, `btn-primary` for main actions, `btn-secondary` for back links.

---

## 4. Integration Steps

### 4.1 Tell Flask Where the Frontend Lives

By default, Flask looks for templates in a folder called `templates/` inside
the same directory as `app.py`. Since the templates are in `FRONTEND/templates/`
and static files are in `FRONTEND/static/`, you must tell Flask where to look
when creating the app instance.

Flask's `Flask()` constructor accepts `template_folder` and `static_folder`
parameters. Set both to the correct relative paths from `app.py`'s location.
Once this is configured, `render_template('login.html')` will correctly resolve
to `FRONTEND/templates/login.html`.

---

### 4.2 Connecting HTML Forms to Flask Routes

Every HTML `<form>` needs two attributes to reach the correct Flask route:

- `action` — the URL the form data is sent to (e.g., `"/login"`,
  `"/deposit"`).
- `method` — must be `"POST"` for any operation that changes data (login,
  deposit, withdraw). Use `"GET"` only for navigation.

The `name` attribute on each `<input>` field determines the key that Flask
uses to read the value on the server side via `request.form['field_name']`.
Make sure the `name` attributes in the HTML match exactly what the route code
expects to receive.

---

### 4.3 Passing Data from Flask to Templates

Flask routes pass data to templates through a dictionary called the **template
context**. Any key-value pair in this dictionary becomes a variable available
inside the Jinja2 template.

For example, the dashboard route passes `balance` and `customer_name`. The
template then references them as `{{ balance }}` and `{{ customer_name }}`.

Keep context dictionaries lean — only pass what the template actually needs to
render. Passing entire database objects when only one field is needed creates
unnecessary coupling.

---

### 4.4 Connecting Flask to SQLite

The connection between Flask and SQLite is managed entirely in `database/db.py`.
No route or service file should open a database connection directly — they all
go through the `db.py` functions.

The connection flow:

1. A request arrives at a Flask route.
2. The route calls a service function.
3. The service function calls a model function.
4. The model function calls `db.get_connection()` to get an open connection.
5. The model executes a query and returns the result.
6. At the end of the request, the connection is closed automatically via a
   Flask teardown hook registered in `db.py`.

This single-path dependency means that if the database path ever changes, only
`config.py` and `db.py` need to be updated — nothing else.

---

### 4.5 Using Blueprints to Register Routes

A Flask Blueprint is a self-contained collection of routes. The application
registers Blueprints in `app.py`, which is the only place that knows about all
Blueprints. The Blueprints themselves only know about their own routes.

Steps:
1. In `auth_routes.py`, create a Blueprint object (e.g., `auth_bp`).
2. Define route functions attached to `auth_bp` instead of `app`.
3. In `app.py`, import `auth_bp` and call `app.register_blueprint(auth_bp)`.
4. Repeat for `account_routes.py`.

This keeps route files from growing too large and makes it easy to find which
file owns which URL.

---

## 5. Validation Rules

### 5.1 Login Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Username field is not empty | Server (route) | Re-render login with error |
| Password field is not empty | Server (route) | Re-render login with error |
| Username exists in the database | Service (`verify_credentials`) | Return generic "Invalid credentials" |
| Password hash matches stored hash | Service (`verify_credentials`) | Return generic "Invalid credentials" |

**Security note:** Always return the same generic error message regardless of
whether the username does not exist or the password is wrong. Separate messages
like "Username not found" help attackers enumerate valid accounts.

---

### 5.2 Balance Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Balance is read fresh from DB on every request | Service | Always up to date |
| Balance is never modified directly by the client | Server | Client only submits an amount; the server computes the new balance |

The balance is a server-side truth. The frontend displays it but never sends
it back in a form. This prevents a malicious user from submitting a fake
balance.

---

### 5.3 Deposit Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Amount field is not empty | Server (route) | Re-render deposit form with error |
| Amount is a valid number | Server (route, type conversion) | Re-render with "Please enter a valid amount" |
| Amount is greater than zero | Service (`deposit`) | Return "Amount must be greater than zero" |
| Amount does not exceed a maximum (optional business rule) | Service | Return appropriate message |

---

### 5.4 Withdrawal Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Amount field is not empty | Server (route) | Re-render withdraw form with error |
| Amount is a valid number | Server (route, type conversion) | Re-render with "Please enter a valid amount" |
| Amount is greater than zero | Service (`withdraw`) | Return "Amount must be greater than zero" |
| Amount does not exceed current balance | Service (`withdraw`) | Return "Insufficient funds" |

**Concurrency note:** The balance check and the balance update must happen
inside a single database transaction. If two requests for the same account
arrive simultaneously, one must wait for the other to commit before the second
one reads the balance. SQLite's serialized write model handles this
automatically.

---

### 5.5 Session Validation

| Rule | Where Enforced | Behaviour on Failure |
|---|---|---|
| Session contains `customer_id` on every protected route | `login_required` helper | Redirect to `/login` |
| Session is cleared on logout | `/logout` route | All session keys removed |
| Session cookie is signed with `SECRET_KEY` | Flask internals | Tampered cookie is rejected |

---

## 6. Testing

### 6.1 Unit Tests

Unit tests cover individual functions in isolation, with no real database or
HTTP server involved. Use Python's built-in `unittest` module or `pytest`.

**What to unit test:**

| Target | Test Cases |
|---|---|
| `auth_service.verify_credentials` | Correct password returns customer; wrong password returns None; unknown username returns None |
| `auth_service.hash_password` | Returns a string; the hash verifies correctly against the original password; two hashes of the same password are not identical (salt is applied) |
| `account_service.deposit` | Positive amount increases balance; zero amount returns error; negative amount returns error |
| `account_service.withdraw` | Valid amount decreases balance; amount exceeding balance returns "Insufficient funds"; zero/negative amount returns error |

For service tests, use a **test database** (a separate in-memory SQLite
instance) rather than the real `banking.db`. This ensures tests do not corrupt
real data and can run in any order without side effects.

---

### 6.2 Integration Tests

Integration tests verify that the HTTP layer (routes) and the service layer
work together correctly. Flask provides a **test client** that simulates HTTP
requests without starting a real server.

**What to integration test:**

| Scenario | Expected Result |
|---|---|
| `POST /login` with valid credentials | Redirects to `/dashboard`; session contains `customer_id` |
| `POST /login` with invalid credentials | Returns 200 with login page; error message visible; no session created |
| `GET /dashboard` with active session | Returns 200 with balance displayed |
| `GET /dashboard` without session | Redirects to `/login` |
| `POST /deposit` with valid amount | Balance increases; redirect to dashboard with success message |
| `POST /deposit` with zero amount | Returns deposit page with validation error |
| `POST /withdraw` with amount ≤ balance | Balance decreases; redirect to dashboard with success message |
| `POST /withdraw` with amount > balance | Returns withdraw page with "Insufficient funds" error |
| `GET /logout` | Session cleared; redirect to `/login` |

---

### 6.3 Manual Testing Checklist

Run through this checklist in the browser before considering a feature
complete.

#### Authentication
- [ ] Visiting `/dashboard` directly (without logging in) redirects to `/login`.
- [ ] Submitting the login form with an empty username shows an error.
- [ ] Submitting the login form with an empty password shows an error.
- [ ] Submitting with wrong credentials shows a generic error (not field-specific).
- [ ] Submitting with correct credentials lands on the dashboard.
- [ ] The nav bar shows the customer name after login.
- [ ] Clicking "Logout" returns to the login page.
- [ ] After logout, the browser back button does not restore the dashboard session.

#### Dashboard
- [ ] The displayed balance matches the value in the database.
- [ ] The "Deposit" and "Withdraw" buttons navigate to the correct pages.

#### Deposit
- [ ] Submitting a valid amount shows a success message and updates the balance.
- [ ] Submitting zero or a negative number shows a validation error.
- [ ] Submitting a non-numeric string shows a validation error.
- [ ] The balance on the dashboard reflects the deposit immediately after redirect.

#### Withdrawal
- [ ] Submitting a valid amount that is less than the balance succeeds.
- [ ] Submitting an amount equal to the balance succeeds (balance becomes zero).
- [ ] Submitting an amount greater than the balance shows "Insufficient funds."
- [ ] Submitting zero or a negative number shows a validation error.

#### Responsive Layout
- [ ] All pages display correctly at 1280px wide (desktop).
- [ ] All pages display correctly at 375px wide (mobile, portrait).
- [ ] The nav bar collapses gracefully on small screens (Bootstrap hamburger menu).

---

## 7. Deployment

### 7.1 Running Locally

Once the environment is set up and code is in place, the application starts
with a single command.

Steps:

1. Make sure the virtual environment is **activated** in the terminal.
2. Navigate to the `BACKEND/` directory (or set the `FLASK_APP` environment
   variable to point at `app.py`).
3. Run `python app.py` (or `flask run` if using the Flask CLI).
4. Open a browser and go to `http://127.0.0.1:5000`.
5. Log in with a seeded test account.

If tables do not exist yet, the `init_db()` call in `app.py` will create them
automatically on first startup. If the seed data script is separate, run it
once before the first login.

**Useful local development tips:**

- Keep `DEBUG = True` in `config.py` locally. Flask will auto-reload on file
  saves and show detailed stack traces in the browser on errors.
- The SQLite file `banking.db` is created in `BACKEND/database/` on first
  startup. You can inspect it with any SQLite browser tool (e.g., DB Browser
  for SQLite) to verify data is being written correctly.

---

### 7.2 Production Considerations

The Flask built-in development server is **not suitable for production**. It
is single-threaded, lacks hardening, and is not designed to handle real traffic.
For a production deployment, the following changes are needed:

| Concern | Development Approach | Production Approach |
|---|---|---|
| WSGI Server | Flask dev server (`python app.py`) | Gunicorn or uWSGI |
| Web Server / Reverse Proxy | None | Nginx or Apache in front of Gunicorn |
| SECRET_KEY | Hardcoded placeholder in `config.py` | Read from environment variable or secrets manager |
| DEBUG mode | `True` | Must be `False` — never expose debug output in production |
| Database | SQLite (file-based) | PostgreSQL or MySQL for multi-user concurrent load |
| HTTPS | Not applicable locally | TLS certificate via Let's Encrypt or a load balancer |
| Session Storage | Signed cookie | Server-side sessions (Redis-backed) for larger payloads |

**Minimum steps to go production-ready:**

1. Set `DEBUG = False` and read `SECRET_KEY` from an environment variable.
2. Install Gunicorn and create a startup command like
   `gunicorn -w 4 app:app` (4 worker processes).
3. Configure Nginx to proxy requests to the Gunicorn socket.
4. Obtain and configure a TLS certificate for the domain.
5. Run the application as a non-root system user.

These steps are outside the scope of this project's current phase but should
be planned for before any real customer data is handled.

---

*End of Step-by-Step Implementation Guide*
