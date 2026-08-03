import streamlit as st

from app.services.chart_service import ChartService
from app.tools.python_executor import PythonExecutor


def render_chart_section(df):

    st.divider()

    st.subheader("📈 AI Chart Generator")

    chart_question = st.text_input(
        "Describe the chart you want",
        key="chart_question"
    )

    if st.button("Generate Chart"):

        if chart_question.strip():

            with st.spinner("Generating chart..."):

                chart_service = ChartService()

                code = chart_service.generate_chart(
                    df,
                    chart_question
                )

                

            st.markdown("### Generated Python")

            st.code(code, language="python")

            with st.spinner("Rendering chart..."):

                figure = PythonExecutor.execute_chart(
                    df,
                    code
                )

            st.plotly_chart(
                figure,
                use_container_width=True
            )