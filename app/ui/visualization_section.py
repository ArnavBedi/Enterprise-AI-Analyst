import streamlit as st

from app.tools.visualizer import Visualizer


def render_visualizations(df):

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