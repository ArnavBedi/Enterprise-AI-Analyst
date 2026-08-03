import streamlit as st
import tempfile

from app.services.sql_service import SQLService
from app.tools.sql_executor import SQLExecutor


def render_sql_section():

    st.divider()

    st.subheader("🗄 SQL Data Analyst")

    uploaded_db = st.file_uploader(
        "Upload SQLite Database",
        type=["db", "sqlite", "sqlite3"],
        key="database_upload"
    )

    database_path = None

    if uploaded_db:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".db"
        ) as tmp:

            tmp.write(uploaded_db.read())

            database_path = tmp.name

        st.success("Database uploaded successfully!")

    sql_question = st.text_input(
        "Ask a question about your database",
        key="sql_question"
    )

    if st.button("Run SQL Query"):

        if database_path is None:

            st.warning("Please upload a SQLite database first.")

        elif not sql_question.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("Generating SQL..."):

                sql_service = SQLService()

                sql = sql_service.generate_sql(
                    database_path,
                    sql_question
                )

            st.markdown("### Generated SQL")

            st.code(sql, language="sql")

            try:

                result = SQLExecutor.execute(
                    database_path,
                    sql
                )

                st.markdown("### Query Result")

                st.dataframe(result)

            except Exception as e:

                st.error(str(e))