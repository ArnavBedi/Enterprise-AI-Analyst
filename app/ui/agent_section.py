import os
import tempfile

import pandas as pd
import streamlit as st

from app.database.connection import DatabaseConnection, DatabaseError
from app.graph.workflow import workflow


def _uploaded_sqlite_path(uploaded_db):
    upload_key = (uploaded_db.name, uploaded_db.size)
    if st.session_state.get("sqlite_upload_key") != upload_key:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            temp_file.write(uploaded_db.getvalue())
            st.session_state.sqlite_database_path = temp_file.name
        st.session_state.sqlite_upload_key = upload_key
    return st.session_state.sqlite_database_path


def _database_picker():
    st.markdown("#### Optional database connection")
    source = st.radio(
        "SQL source",
        ["None", "Upload SQLite", "PostgreSQL from environment"],
        horizontal=True,
        key="agent_database_source",
    )
    database_path = None
    database_url = None

    if source == "Upload SQLite":
        uploaded_db = st.file_uploader(
            "Upload SQLite database",
            type=["db", "sqlite", "sqlite3"],
            key="agent_database_upload",
        )
        if uploaded_db is not None:
            database_path = _uploaded_sqlite_path(uploaded_db)
    elif source == "PostgreSQL from environment":
        database_url = os.getenv("DATABASE_URL", "").strip() or None
        if not database_url:
            st.info("Add DATABASE_URL to .env, then restart the app.")

    if database_path or database_url:
        database = (
            DatabaseConnection(database_url)
            if database_url
            else DatabaseConnection.from_sqlite_path(database_path)
        )
        st.caption(database.safe_label)
        if st.button("Test database connection", key="test_database_connection"):
            try:
                database.test()
                schema = database.schema()
                st.success("Read-only database connection succeeded.")
                with st.expander("View detected schema"):
                    st.code(schema, language="text")
            except DatabaseError as exc:
                st.error(str(exc))

    return database_path, database_url


def render_agent_section(df=None, report=None, database_path=None):
    st.divider()
    st.subheader("🤖 Autonomous AI Analyst")
    st.write("Ask a question and the AI will choose the appropriate analysis tools.")

    selected_path, database_url = _database_picker()
    database_path = selected_path or database_path
    question = st.text_area(
        "What would you like to analyze?",
        placeholder=(
            "Example: Use the connected database to show average salary "
            "by department and explain the result."
        ),
        key="agent_question",
    )

    if not st.button("Run AI Analysis", type="primary", key="run_agent"):
        return
    if not question.strip():
        st.warning("Please enter a question.")
        return

    state = {
        "question": question,
        "df": df,
        "report": report,
        "database_path": database_path,
        "database_url": database_url,
        "database_dialect": None,
        "plan": [],
        "current_step": 0,
        "python_code": None,
        "python_result": None,
        "chart_code": None,
        "figure": None,
        "sql": None,
        "sql_result": None,
        "answer": None,
        "error": None,
    }

    try:
        with st.spinner("Planning and executing analysis..."):
            result = workflow.invoke(state)
    except Exception:
        st.error("Analysis failed unexpectedly. Check the application logs.")
        return

    if result.get("error"):
        st.warning(result["error"])
    if result.get("plan"):
        st.markdown("### 🧠 Agents Used")
        st.write(" → ".join(agent.title() for agent in result["plan"]))
    if result.get("answer"):
        st.markdown("### 📋 Analysis")
        st.markdown(result["answer"])

    _render_result("### 🐍 Python Analysis", result.get("python_result"))
    if result.get("figure") is not None:
        st.markdown("### 📈 Visualization")
        st.plotly_chart(result["figure"], use_container_width=True)
    _render_result("### 🗄️ SQL Result", result.get("sql_result"))

    with st.expander("🔧 View Agent Execution Details"):
        for label, key, language in (
            ("Python Agent", "python_code", "python"),
            ("Chart Agent", "chart_code", "python"),
            ("SQL Agent", "sql", "sql"),
        ):
            if result.get(key):
                st.markdown(f"**{label}**")
                st.code(result[key], language=language)
        sql_result = result.get("sql_result")
        if isinstance(sql_result, pd.DataFrame) and sql_result.attrs.get("truncated"):
            st.caption(f"Result limited to {sql_result.attrs['max_rows']} rows for safety.")


def _render_result(heading, value):
    if value is None:
        return
    st.markdown(heading)
    if isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True)
    elif isinstance(value, pd.Series):
        st.dataframe(value.to_frame(), use_container_width=True)
    elif hasattr(value, "item"):
        st.write(value.item())
    else:
        st.write(value)
