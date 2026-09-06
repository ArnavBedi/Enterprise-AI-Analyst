import io

import pandas as pd
import streamlit as st

from app.tools.dataset_inspector import DatasetInspector
from app.ui.agent_section import render_agent_section
from app.ui.dataset_section import render_dataset_section


st.set_page_config(page_title="Enterprise AI Analyst", page_icon="📊", layout="wide")
st.title("📊 Enterprise AI Analyst")
st.write(
    "Analyze an uploaded CSV, an uploaded SQLite database, or a configured "
    "PostgreSQL database from one autonomous workspace."
)

uploaded_file = st.file_uploader("Optional: Upload CSV", type=["csv"])
df = None
report = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV is empty.")
        st.stop()
    except Exception:
        st.error("Unable to read the CSV file.")
        st.stop()

    render_dataset_section(df)
    report = DatasetInspector.inspect(df)
    with st.expander("Dataset inspection report"):
        st.json(report)

render_agent_section(df, report)
