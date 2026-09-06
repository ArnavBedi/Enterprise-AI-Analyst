import sqlite3

import pytest

from app.database.connection import DatabaseConnection, DatabaseError
from app.database.sql_safety import validate_read_only_sql


@pytest.fixture
def sqlite_database(tmp_path):
    path = tmp_path / "employees.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE employees (department TEXT, salary INTEGER)")
    connection.executemany(
        "INSERT INTO employees VALUES (?, ?)",
        [("Engineering", 85000), ("Engineering", 90000), ("Finance", 91000)],
    )
    connection.commit()
    connection.close()
    return DatabaseConnection.from_sqlite_path(str(path))


def test_sqlite_schema_and_query(sqlite_database):
    assert "Table: employees" in sqlite_database.schema()
    result = sqlite_database.execute_read_only(
        "SELECT department, AVG(salary) AS average_salary "
        "FROM employees GROUP BY department ORDER BY department"
    )
    assert result.to_dict("records") == [
        {"department": "Engineering", "average_salary": 87500.0},
        {"department": "Finance", "average_salary": 91000.0},
    ]


@pytest.mark.parametrize("query", [
    "DELETE FROM employees",
    "SELECT * FROM employees; DROP TABLE employees",
    "SELECT * FROM employees FOR UPDATE",
    "PRAGMA table_info(employees)",
])
def test_mutating_or_multiple_statements_are_rejected(query):
    with pytest.raises(DatabaseError):
        validate_read_only_sql(query)


def test_cte_select_is_allowed():
    query = "WITH totals AS (SELECT 1 AS value) SELECT value FROM totals"
    assert validate_read_only_sql(query) == query
