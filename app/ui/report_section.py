import streamlit as st

from app.services.analyst_service import AnalystService


def render_report(report):

    if st.button("Generate AI Analysis"):

        with st.spinner("Analyzing dataset with Gemini..."):

            analyst = AnalystService()

            st.session_state.analysis = analyst.analyze(report)

            st.session_state.messages = []

    if st.session_state.analysis:

        st.subheader("AI Business Report")

        st.markdown(st.session_state.analysis)

        st.divider()