# Contributing

Thank you for considering a contribution to Enterprise AI Analyst.

## Development setup

1. Fork and clone the repository.
2. Create a Python 3.12 virtual environment.
3. Install `requirements.txt`.
4. Copy `.env.example` to `.env` and add your own `GOOGLE_API_KEY`.
5. Run `pytest -q tests` before submitting changes.

Never commit `.env`, credentials, real customer data, database exports, or
audit logs.

## Pull requests

- Keep changes focused and describe the user-visible behavior.
- Add or update tests for changed behavior.
- Preserve the read-only database boundary.
- Document new environment variables and dependencies.
- Confirm that CSV, SQLite, and PostgreSQL paths still work.

## Reporting bugs

Include reproduction steps, expected behavior, actual behavior, and sanitized
logs. Do not include API keys, connection strings, or proprietary data.
