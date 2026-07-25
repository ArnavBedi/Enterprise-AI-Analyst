import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.tools.dataset_inspector import DatasetInspector
from app.services.analyst_service import AnalystService
from app.tools.visualizer import Visualizer
from app.services.chat_service import ChatService
from app.services.python_service import PythonService
from app.tools.dashboard_builder import DashboardBuilder
from app.services.chart_service import ChartService

st.set_page_config(
    page_title="Enterprise AI Analyst",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Header
# -----------------------------

st.title("📊 Enterprise AI Analyst")
st.write("Upload any CSV dataset and receive an AI-generated business analysis.")

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

# -----------------------------
# Main App
# -----------------------------

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully!")

    # -----------------------------
    # Dataset Preview
    # -----------------------------

    st.subheader("Dataset Preview")
    st.dataframe(df)

    # -----------------------------
    # Overview
    # -----------------------------

    st.subheader("Dataset Overview")

    metrics = DashboardBuilder.build(df)

    cols = st.columns(4)

    for i, (name, value) in enumerate(metrics.items()):
        cols[i % 4].metric(name, value)

    # -----------------------------
    # Inspection Report
    # -----------------------------

    report = DatasetInspector.inspect(df)

    st.subheader("Dataset Inspection Report")
    st.json(report)

    # -----------------------------
    # Visualizations
    # -----------------------------

    st.subheader("Visualizations")

    histograms = Visualizer.salary_histograms(df)

    for fig in histograms:
        st.plotly_chart(fig, use_container_width=True)

    bar_charts = Visualizer.categorical_charts(df)

    for fig in bar_charts:
        st.plotly_chart(fig, use_container_width=True)

    heatmap = Visualizer.correlation_heatmap(df)

    if heatmap:
        st.plotly_chart(heatmap, use_container_width=True)

    boxplots = Visualizer.boxplots(df)

    for fig in boxplots:
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # AI Analysis Button
    # -----------------------------

    if st.button("Generate AI Analysis"):

        with st.spinner("Analyzing dataset with Gemini..."):

            analyst = AnalystService()

            st.session_state.analysis = analyst.analyze(report)

            # Start a fresh conversation whenever
            # a new analysis is generated
            st.session_state.messages = []

    # -----------------------------
    # Show AI Report
    # -----------------------------

    if st.session_state.analysis:

        st.subheader("AI Business Report")
        st.markdown(st.session_state.analysis)

        st.divider()

        # -----------------------------
        # Chat Section
        # -----------------------------

        st.subheader("💬 Chat with your Dataset")

        # Display previous conversation

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input

        prompt = st.chat_input("Ask anything about your dataset...")

        if prompt:

            # Show user message

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            # AI response

            chat = ChatService()

            with st.spinner("Thinking..."):

                answer = chat.ask(report, df, prompt)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            with st.chat_message("assistant"):
                st.markdown(answer)
    
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
                    st.dataframe(result, use_container_width=True)

                elif isinstance(result, pd.Series):
                    st.dataframe(result.to_frame(), use_container_width=True)

                elif isinstance(result, go.Figure):
                    st.plotly_chart(result, use_container_width=True)

                elif isinstance(result, (list, tuple, dict)):
                    st.json(result)

                else:
                    st.write(result)

        st.divider()

        st.subheader("🎨 AI Chart Generator")

        chart_prompt = st.text_input(
            "Describe a chart to generate",
            placeholder="Example: Plot Salary vs Age",
            key="chart_prompt"
        )

        if st.button("Generate Chart"):

            if chart_prompt.strip():

                with st.spinner("Generating chart..."):

                    chart_service = ChartService()

                    code = chart_service.generate_chart(
                        df,
                        chart_prompt
                    )

                    st.markdown("### Generated Python")

                    st.code(code, language="python")

                    from app.tools.python_executor import PythonExecutor

                    chart = PythonExecutor.execute(
                        df,
                        code
                    )

                    st.markdown("### Chart")

                    if hasattr(chart, "to_plotly_json"):
                        st.plotly_chart(
                            chart,
                            use_container_width=True
                        )
                    else:
                        st.error(chart)