# Enterprise AI Analyst

[![CI](https://github.com/ArnavBedi/Enterprise-AI-Analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/ArnavBedi/Enterprise-AI-Analyst/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An autonomous, conversational data-analysis workspace built with Streamlit,
LangGraph, Gemini, SQLAlchemy, Pandas, and Plotly. Ask a business question in
plain English and the supervisor routes it through the right combination of
Python, SQL, charting, and business-analysis agents.

## Highlights

- Analyze CSV files, uploaded SQLite databases, PostgreSQL, and MySQL.
- Route work through `Python`, `SQL`, `Chart`, and `Business` agents.
- Continue with contextual follow-ups such as “visualize that.”
- Discover tables, columns, primary keys, and foreign-key relationships.
- Generate safe read-only SQL and visualize query results with Plotly.
- Export tables to CSV/Excel and charts to PNG/interactive HTML.
- Display query duration, row count, truncation status, profile, and estimated
  PostgreSQL cost.
- Configure multiple named database profiles through environment variables.
- Apply optional authentication, host allowlists, query timeouts, cost limits,
  result limits, audit events, and restricted generated-Python execution.

## Architecture

```mermaid
flowchart TD
    U[User question] --> UI[Streamlit workspace]
    UI --> P[Gemini planner]
    P --> PY[Python agent]
    P --> SQL[SQL agent]
    P --> CH[Chart agent]
    P --> B[Business agent]
    SQL --> SA[SQLAlchemy read-only layer]
    SA --> DB[(SQLite / PostgreSQL / MySQL)]
    SQL --> CH
    PY --> CH
    SQL --> B
    PY --> B
    CH --> B
    B --> UI
```

The LangGraph supervisor builds an execution plan for each question. SQL
queries pass through an application validator and a database connection that
enforces read-only behavior, timeouts, result limits, and PostgreSQL cost
checks. Conversation memory is isolated by selected data source.

## Quick start

Requirements: Python 3.12+, a Google AI Studio API key, and optionally Docker
Desktop for the PostgreSQL demo.

```bash
git clone https://github.com/ArnavBedi/Enterprise-AI-Analyst.git
cd Enterprise-AI-Analyst
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini key to `.env`:

```env
GOOGLE_API_KEY=your_google_ai_studio_key
```

Start the app:

```bash
streamlit run streamlit_app.py
```

CSV and uploaded SQLite analysis work without Docker.

## PostgreSQL demo

The bundled Docker service creates a sample analytics database with
`employees`, `departments`, and `projects` tables, declared relationships, and
a dedicated `analyst_reader` account.

```bash
docker compose up -d postgres
docker compose ps
```

The demo publishes PostgreSQL on `localhost:5433` to avoid conflicting with a
local server on the standard port. The example `DATABASE_URL` already points to
this service. In the app, choose **Default Database**, click **Test database
connection**, and try:

> Show employee count and total project budget by department as a bar chart,
> then explain the results.

Stop the service without deleting its volume:

```bash
docker compose stop
```

The bundled passwords are development-only. Replace them before sharing or
deploying the database.

## Database profiles

Credentials stay in `.env`. Map user-facing profile names to environment
variables with `DATABASE_PROFILES`:

```env
DATABASE_PROFILES=Finance:DATABASE_URL,Warehouse:MYSQL_DATABASE_URL
DATABASE_URL=postgresql+psycopg2://readonly_user:password@host:5432/finance
MYSQL_DATABASE_URL=mysql+pymysql://readonly_user:password@host:3306/warehouse
```

When `DATABASE_PROFILES` is omitted, the app discovers `DATABASE_URL` and
variables ending in `_DATABASE_URL`.

## Security controls

The application includes defense in depth:

- Single-statement `SELECT`/read-only CTE validation
- Database-level read-only roles and transactions
- Dangerous SQL function and locking-clause blocking
- Connection host allowlists
- Connection and statement timeouts
- PostgreSQL estimated-cost limits
- Schema and result-size limits
- Restricted generated-Python syntax and operations
- Optional shared-password gate
- Metadata-only JSONL audit events
- Sanitized UI error messages

Database permissions are the strongest boundary. Always use a separately
managed least-privilege account in deployed environments.

### Data privacy

The configured Gemini API receives prompts containing relevant schema context,
questions, and analysis results needed by the selected agents. Do not connect
data that your organization does not permit sending to the configured model
provider. Raw database credentials are never placed in prompts.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Gemini API authentication | Required |
| `DATABASE_URL` | Default SQLAlchemy connection URL | Demo PostgreSQL URL |
| `DATABASE_PROFILES` | Named profile-to-environment-variable mappings | Auto-discovery |
| `APP_ACCESS_PASSWORD` | Optional shared UI password | Disabled |
| `ALLOWED_DATABASE_HOSTS` | Comma-separated host allowlist | Unrestricted unless set |
| `QUERY_TIMEOUT_MS` | SQL statement timeout | `15000` |
| `MAX_POSTGRES_QUERY_COST` | Maximum accepted PostgreSQL plan cost | `100000` |
| `MAX_SCHEMA_OBJECTS` | Maximum introspected tables/views | `100` |
| `MAX_COLUMNS_PER_TABLE` | Maximum columns exposed per object | `100` |
| `AUDIT_LOG_PATH` | Metadata-only audit log destination | `logs/audit.jsonl` |

## Testing

Run the local suite:

```bash
pytest -q tests
```

Run PostgreSQL integration tests after starting Docker:

```bash
TEST_DATABASE_URL="postgresql+psycopg2://analyst_reader:analyst_reader_password@127.0.0.1:5433/analytics" \
pytest -q tests
```

## Project structure

```text
app/
├── agents/       LangGraph agent nodes
├── database/     Profiles, introspection, and read-only connections
├── graph/        Workflow construction and routing
├── security/     Metadata-only audit events
├── services/     Gemini-backed planning and code/SQL generation
├── state/        Shared workflow state
├── tools/        Restricted execution helpers
└── ui/           Streamlit interface
docker/postgres/  Reproducible PostgreSQL demo schema
tests/            SQLite, PostgreSQL, security, and routing tests
```

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before
opening a pull request. For vulnerabilities, follow [SECURITY.md](SECURITY.md)
instead of opening a public issue.

## License

Released under the [MIT License](LICENSE).
