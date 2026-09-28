import hmac
import io
import os
import tempfile

import pandas as pd
import streamlit as st

from app.database.connection import DatabaseConnection, DatabaseError
from app.database.profiles import load_database_profiles
from app.graph.workflow import workflow
from app.security.audit import record_audit_event


def render_authentication_gate():
    """Require an optional shared app password before showing any data."""
    expected = os.getenv("APP_ACCESS_PASSWORD", "").strip()
    if not expected or st.session_state.get("authenticated"):
        return

    st.title("🔐 Enterprise AI Analyst")
    with st.form("authentication_form"):
        password = st.text_input("Access password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary")
    if submitted:
        if hmac.compare_digest(password, expected):
            st.session_state.authenticated = True
            record_audit_event("authentication", success=True)
            st.rerun()
        record_audit_event("authentication", success=False)
        st.error("Incorrect access password.")
    st.stop()


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
    profiles = load_database_profiles()
    profile_options = list(profiles)
    source = st.selectbox(
        "SQL source",
        ["None", "Upload SQLite", *profile_options],
        key="agent_database_source",
    )
    database_path = None
    database_url = None
    profile_name = None

    if source == "Upload SQLite":
        uploaded_db = st.file_uploader(
            "Upload SQLite database",
            type=["db", "sqlite", "sqlite3"],
            key="agent_database_upload",
        )
        if uploaded_db is not None:
            database_path = _uploaded_sqlite_path(uploaded_db)
            profile_name = "Uploaded SQLite"
    elif source in profiles:
        profile = profiles[source]
        database_url = profile.url
        profile_name = profile.name

    if not profiles:
        st.caption(
            "No environment database profiles found. Configure DATABASE_URL "
            "or DATABASE_PROFILES in .env."
        )

    database = None
    if database_path or database_url:
        database = (
            DatabaseConnection(database_url, profile_name=profile_name or "Default")
            if database_url
            else DatabaseConnection.from_sqlite_path(database_path)
        )
        st.caption(database.safe_label)
        if st.button("Test database connection", key="test_database_connection"):
            try:
                database.test()
                schema = database.schema()
                record_audit_event(
                    "connection_test",
                    success=True,
                    profile=profile_name,
                    dialect=database.dialect,
                )
                st.success("Read-only database connection succeeded.")
                with st.expander("View detected schema and relationships"):
                    st.code(schema, language="text")
            except DatabaseError as exc:
                record_audit_event(
                    "connection_test",
                    success=False,
                    profile=profile_name,
                    reason=str(exc),
                )
                st.error(str(exc))

    source_key = (
        f"sqlite:{st.session_state.get('sqlite_upload_key')}"
        if database_path
        else f"profile:{profile_name}"
    )
    return database_path, database_url, profile_name, source_key


def _initialize_conversation():
    st.session_state.setdefault("agent_conversations", {})
    st.session_state.setdefault("analysis_memories", {})
    st.session_state.setdefault("agent_last_results", {})


def _conversation_controls(source_key):
    left, right = st.columns([4, 1])
    with left:
        st.markdown("#### Conversation")
    with right:
        if st.button("Clear", key="clear_agent_conversation"):
            st.session_state.agent_conversations.pop(source_key, None)
            st.session_state.analysis_memories.pop(source_key, None)
            st.session_state.agent_last_results.pop(source_key, None)
            st.rerun()

    messages = st.session_state.agent_conversations.get(source_key, [])
    for message in messages[-10:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_agent_section(
    df=None,
    report=None,
    database_path=None,
    csv_source_id=None,
):
    _initialize_conversation()
    st.divider()
    st.subheader("🤖 Autonomous AI Analyst")
    st.write(
        "Ask a question, then continue with follow-ups such as “visualize that” "
        "or “explain the highest result.”"
    )

    selected_path, database_url, profile_name, source_key = _database_picker()
    database_path = selected_path or database_path
    if df is not None:
        source_key = f"{source_key}:csv:{csv_source_id or 'uploaded'}"

    _conversation_controls(source_key)
    question = st.text_area(
        "What would you like to analyze?",
        placeholder=(
            "Example: Use the connected database to show average salary "
            "by department and explain the result."
        ),
        key="agent_question",
    )

    run_requested = st.button("Run AI Analysis", type="primary", key="run_agent")
    if not run_requested:
        last_result = st.session_state.agent_last_results.get(source_key)
        if last_result is not None:
            _render_analysis(last_result)
        return
    if not question.strip():
        st.warning("Please enter a question.")
        return

    memory = st.session_state.analysis_memories.get(source_key, {})
    history = st.session_state.agent_conversations.get(source_key, [])[-10:]
    state = {
        "question": question.strip(),
        "df": df,
        "report": report,
        "database_path": database_path,
        "database_url": database_url,
        "database_dialect": None,
        "database_profile": profile_name,
        "conversation_history": history,
        "prior_question": memory.get("question"),
        "prior_answer": memory.get("answer"),
        "prior_python_result": memory.get("python_result"),
        "prior_sql_result": memory.get("sql_result"),
        "plan": [],
        "current_step": 0,
        "python_code": None,
        "python_result": None,
        "chart_code": None,
        "chart_source": None,
        "figure": None,
        "sql": None,
        "sql_result": None,
        "sql_diagnostics": None,
        "answer": None,
        "error": None,
    }

    try:
        with st.spinner("Planning and executing analysis..."):
            result = workflow.invoke(state)
    except Exception:
        st.error("Analysis failed unexpectedly. Check the application logs.")
        return

    assistant_message = result.get("answer")
    if not assistant_message:
        if result.get("error"):
            assistant_message = result["error"]
        else:
            agents = " → ".join(agent.title() for agent in result.get("plan", []))
            assistant_message = f"Analysis completed using {agents or 'the analyst'}."
    conversation = st.session_state.agent_conversations.setdefault(source_key, [])
    conversation.extend(
        [
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": assistant_message},
        ]
    )
    st.session_state.analysis_memories[source_key] = {
        "question": question.strip(),
        "answer": result.get("answer") or memory.get("answer"),
        "python_result": result.get("python_result")
        if result.get("python_result") is not None
        else memory.get("python_result"),
        "sql_result": result.get("sql_result")
        if result.get("sql_result") is not None
        else memory.get("sql_result"),
    }
    st.session_state.agent_last_results[source_key] = result
    _render_analysis(result)


def _render_analysis(result):
    if result.get("error"):
        st.warning(result["error"])
    if result.get("plan"):
        st.markdown("### 🧠 Agents Used")
        st.write(" → ".join(agent.title() for agent in result["plan"]))
    if result.get("answer"):
        st.markdown("### 📋 Analysis")
        st.markdown(result["answer"])

    _render_result(
        "### 🐍 Python Analysis",
        result.get("python_result"),
        key_prefix="python_result",
    )
    if result.get("figure") is not None:
        st.markdown("### 📈 Visualization")
        st.plotly_chart(result["figure"], use_container_width=True)
        _render_chart_downloads(result["figure"])
    _render_result(
        "### 🗄️ SQL Result",
        result.get("sql_result"),
        key_prefix="sql_result",
    )
    _render_sql_diagnostics(result.get("sql_diagnostics"))

    with st.expander("🔧 View Agent Execution Details"):
        for label, key, language in (
            ("Python Agent", "python_code", "python"),
            ("Chart Agent", "chart_code", "python"),
            ("SQL Agent", "sql", "sql"),
        ):
            if result.get(key):
                st.markdown(f"**{label}**")
                st.code(result[key], language=language)


def _render_result(heading, value, key_prefix):
    if value is None:
        return
    st.markdown(heading)
    if isinstance(value, pd.Series):
        value = value.to_frame()
    if isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True)
        _render_table_downloads(value, key_prefix)
    elif hasattr(value, "item"):
        st.write(value.item())
    else:
        st.write(value)


def _render_table_downloads(frame, key_prefix):
    csv_data = frame.to_csv(index=False).encode("utf-8")
    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine="xlsxwriter") as writer:
        frame.to_excel(writer, index=False, sheet_name="Analysis")
    left, right = st.columns(2)
    left.download_button(
        "Download CSV",
        data=csv_data,
        file_name=f"{key_prefix}.csv",
        mime="text/csv",
        key=f"download_{key_prefix}_csv",
    )
    right.download_button(
        "Download Excel",
        data=excel_data.getvalue(),
        file_name=f"{key_prefix}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"download_{key_prefix}_xlsx",
    )


def _render_chart_downloads(figure):
    html = figure.to_html(include_plotlyjs="cdn").encode("utf-8")
    left, right = st.columns(2)
    left.download_button(
        "Download interactive chart",
        data=html,
        file_name="analysis_chart.html",
        mime="text/html",
        key="download_chart_html",
    )
    try:
        import plotly.io as pio

        previous_headers = pio.defaults.headers
        pio.defaults.headers = {}
        png = figure.to_image(format="png", width=1400, height=800, scale=2)
    except Exception:
        right.caption("PNG export needs the optional Kaleido browser runtime.")
    else:
        right.download_button(
            "Download chart image",
            data=png,
            file_name="analysis_chart.png",
            mime="image/png",
            key="download_chart_png",
        )
    finally:
        if "previous_headers" in locals():
            pio.defaults.headers = previous_headers


def _render_sql_diagnostics(diagnostics):
    if not diagnostics:
        return
    st.markdown("### 🔎 Query Details")
    columns = st.columns(4)
    columns[0].metric("Rows", diagnostics.get("row_count", 0))
    columns[1].metric("Execution", f"{diagnostics.get('duration_ms', 0)} ms")
    columns[2].metric("Profile", diagnostics.get("profile") or "Database")
    columns[3].metric(
        "Truncated",
        "Yes" if diagnostics.get("truncated") else "No",
    )
    st.caption(diagnostics.get("database") or diagnostics.get("dialect") or "")
    if diagnostics.get("estimated_cost") is not None:
        st.caption(f"PostgreSQL estimated cost: {diagnostics['estimated_cost']}")
