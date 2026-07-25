import pandas as pd


class DashboardBuilder:

    @staticmethod
    def build(df: pd.DataFrame):

        metrics = {}

        metrics["Rows"] = len(df)
        metrics["Columns"] = len(df.columns)
        metrics["Missing Values"] = int(df.isnull().sum().sum())
        metrics["Duplicate Rows"] = int(df.duplicated().sum())

        numeric = df.select_dtypes(include="number")

        if not numeric.empty:

            metrics["Numeric Columns"] = len(numeric.columns)

            for column in numeric.columns[:3]:

                metrics[f"Avg {column}"] = round(
                    numeric[column].mean(),
                    2
                )

                metrics[f"Max {column}"] = round(
                    numeric[column].max(),
                    2
                )

        categorical = df.select_dtypes(
            include=["object", "category"]
        )

        if not categorical.empty:

            metrics["Categorical Columns"] = len(
                categorical.columns
            )

        return metrics