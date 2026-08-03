import streamlit as st
import pandas as pd

from app.tools.dataset_inspector import DatasetInspector
from app.ui.dataset_section import render_dataset_section
from app.ui.visualization_section import render_visualizations
from app.ui.report_section import render_report
from app.ui.chat_section import render_chat_section
from app.ui.python_section import render_python_section
from app.ui.chart_section import render_chart_section
from app.ui.sql_section import render_sql_section

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

    render_dataset_section(df)

    # -----------------------------
    # Inspection Report
    # -----------------------------

    report = DatasetInspector.inspect(df)

    st.subheader("Dataset Inspection Report")
    st.json(report)

    # -----------------------------
    # Visualizations
    # -----------------------------

    render_visualizations(df)

    # -----------------------------
    # AI Analysis Button
    # -----------------------------

    render_report(report)

    # -----------------------------
    # Chat Section
    # -----------------------------

    render_chat_section(report, df)

    # -----------------------------
    # Python Analyst Section
    # -----------------------------

    render_python_section(df)

    # -----------------------------
    # AI chart generation Section
    # -----------------------------

    render_chart_section(df)

    # -----------------------------
    # SQL Section
    # -----------------------------

    render_sql_section()