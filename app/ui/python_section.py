import streamlit as st
import pandas as pd

from app.services.python_service import PythonService


def render_python_section(df):

    st.divider()

    st.subheader("🐍 Python Data Analyst")

    python_question = st.text_input(
        "Ask a question that requires calculations",
        key="python_question"
    )

    if st.button("Run Python Analysis"):

        if python_question.strip():

            with st.spinner("Generating Python..."):

                python_service = PythonService()

                code, result = python_service.ask(
                    df,
                    python_question
                )

            st.markdown("### Generated Python")

            st.code(code, language="python")

            st.markdown("### Result")

            if isinstance(result, pd.DataFrame):
                st.dataframe(result)

            elif isinstance(result, pd.Series):
                st.dataframe(result)

            else:
                st.write(result)