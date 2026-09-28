import json

import pandas as pd
import pytest

from app.database.connection import DatabaseConnection
from app.database.profiles import load_database_profiles
from app.security.audit import query_fingerprint, record_audit_event
from app.services.planner_service import PlannerService
from app.tools.python_executor import PythonExecutor


def test_named_database_profiles_are_allowlisted(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_PROFILES",
        "Finance:FINANCE_DATABASE_URL,Warehouse:WAREHOUSE_DATABASE_URL",
    )
    monkeypatch.setenv(
        "FINANCE_DATABASE_URL",
        "postgresql+psycopg2://reader:secret@finance.internal/data",
    )
    monkeypatch.setenv(
        "WAREHOUSE_DATABASE_URL",
        "mysql+pymysql://reader:secret@warehouse.internal/data",
    )
    profiles = load_database_profiles()
    assert list(profiles) == ["Finance", "Warehouse"]
    assert profiles["Warehouse"].connection().dialect == "mysql"


def test_mysql_driver_can_build_engine(monkeypatch):
    monkeypatch.delenv("ALLOWED_DATABASE_HOSTS", raising=False)
    database = DatabaseConnection(
        "mysql+pymysql://reader:password@localhost/analytics",
        profile_name="MySQL",
    )
    engine = database._engine()
    try:
        assert engine.dialect.name == "mysql"
    finally:
        engine.dispose()


def test_python_executor_blocks_imports_private_access_and_file_writes():
    frame = pd.DataFrame({"value": [1, 2]})
    with pytest.raises(ValueError):
        PythonExecutor.execute(frame, "import os\nresult = 1")
    with pytest.raises(ValueError):
        PythonExecutor.execute(frame, "result = df.__class__")
    with pytest.raises(ValueError):
        PythonExecutor.execute(frame, "result = df.to_csv('/tmp/data.csv')")


def test_python_executor_still_allows_analysis():
    frame = pd.DataFrame({"value": [1, 2, 3]})
    assert PythonExecutor.execute(frame, 'result = df["value"].mean()') == 2.0


class _PlannerModel:
    def generate_json(self, prompt, schema):
        return {"plan": ["chart"]}


def test_database_chart_plan_runs_sql_when_no_prior_result():
    planner = PlannerService()
    planner.gemini = _PlannerModel()
    plan = planner.create_plan(
        "Chart salary by department",
        has_database=True,
        has_csv=False,
        has_prior_sql_result=False,
    )
    assert plan == ["sql", "chart"]


def test_follow_up_chart_reuses_prior_sql_result():
    planner = PlannerService()
    planner.gemini = _PlannerModel()
    plan = planner.create_plan(
        "Now visualize that",
        conversation_history=[
            {"role": "user", "content": "Show salary by department"},
            {"role": "assistant", "content": "Analysis completed using SQL."},
        ],
        has_database=True,
        has_prior_sql_result=True,
    )
    assert plan == ["chart"]


def test_audit_log_contains_metadata_not_query(monkeypatch, tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    query = "SELECT salary FROM employees"
    record_audit_event(
        "sql_query",
        success=True,
        query_id=query_fingerprint(query),
        row_count=3,
    )
    payload = json.loads(audit_path.read_text())
    assert payload["row_count"] == 3
    assert query not in audit_path.read_text()
