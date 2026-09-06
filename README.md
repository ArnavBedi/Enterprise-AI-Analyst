# Enterprise AI Analyst

A Streamlit and LangGraph application that routes questions across Python,
charting, SQL, and business-analysis agents. It supports CSV data, uploaded
SQLite files, and environment-configured PostgreSQL databases.

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and add your AI API key.
4. Run the app with `streamlit run streamlit_app.py`.

CSV and SQLite continue to work without Docker.

## PostgreSQL demo

Start the local database with `docker compose up -d postgres`. The stack creates
an `employees` table and a dedicated `analyst_reader` login. The sample
`DATABASE_URL` uses that read-only login. Restart Streamlit after changing
`.env`, select **PostgreSQL from environment**, and use **Test database
connection** before asking a question.

The bundled passwords are only for the local Docker demo. Replace them for any
shared or deployed environment.

The demo publishes PostgreSQL on port `5433` so it does not conflict with a
PostgreSQL installation already using the standard local port `5432`.

Example: “Using the connected database, show average salary by department and
explain which department is highest.”

Stop it with `docker compose stop`. Only use `docker compose down -v` when you
intentionally want to remove the local database data.

## Safety model

- Credentials are loaded from `.env`; `.env` is ignored by Git.
- PostgreSQL uses a SELECT-only role and read-only default transactions.
- The app independently accepts only one SELECT or read-only CTE.
- SQLAlchemy provides one interface for SQLite and PostgreSQL.
- Query results are capped at 1,000 rows.
- UI errors do not expose credentials or raw driver errors.

Database permissions remain the strongest security boundary. Production should
use a separately managed read-only account and restrictive network rules.

## MySQL extension

The connection layer already recognizes MySQL URLs. Later, install a MySQL
SQLAlchemy driver, configure a `mysql+pymysql://...` URL, and expose that source
in the UI. The SQL agent and introspection layer need no redesign.

## Tests

Run `pytest -q`. To include PostgreSQL, set `TEST_DATABASE_URL` to the read-only
URL and run `pytest -q tests/test_postgres_integration.py`.
