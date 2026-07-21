import pandas as pd
import plotly.express as px


class Visualizer:

    @staticmethod
    def salary_histograms(df: pd.DataFrame):

        charts = []

        numeric = df.select_dtypes(include="number")

        for column in numeric.columns:

            fig = px.histogram(
                df,
                x=column,
                nbins=20,
                title=f"{column} Distribution"
            )

            charts.append(fig)

        return charts

    @staticmethod
    def categorical_charts(df: pd.DataFrame):

        charts = []

        categorical = df.select_dtypes(include=["object", "category"])

        for column in categorical.columns:

            counts = (
                df[column]
                .value_counts()
                .reset_index()
            )

            counts.columns = [column, "Count"]

            fig = px.bar(
                counts,
                x=column,
                y="Count",
                title=f"{column} Counts"
            )

            charts.append(fig)

        return charts

    @staticmethod
    def correlation_heatmap(df: pd.DataFrame):

        numeric = df.select_dtypes(include="number")

        if len(numeric.columns) < 2:
            return None

        corr = numeric.corr(numeric_only=True)

        fig = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap"
        )

        return fig

    @staticmethod
    def boxplots(df: pd.DataFrame):

        charts = []

        numeric = df.select_dtypes(include="number")

        for column in numeric.columns:

            fig = px.box(
                df,
                y=column,
                title=f"{column} Box Plot"
            )

            charts.append(fig)

        return charts