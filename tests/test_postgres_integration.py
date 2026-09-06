import os

import pytest

from app.database.connection import DatabaseConnection


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to run the PostgreSQL integration test.",
)
def test_postgres_read_only_connection():
    database = DatabaseConnection(os.environ["TEST_DATABASE_URL"])
    assert "Postgresql" in database.test()
    assert "employees" in database.schema()
    result = database.execute_read_only("SELECT COUNT(*) AS count FROM employees")
    assert result.iloc[0]["count"] > 0
