import pandas as pd


class DatasetInspector:

    @staticmethod
    def inspect(df: pd.DataFrame):

        report = {}

        report["rows"] = len(df)
        report["columns"] = len(df.columns)

        report["column_names"] = list(df.columns)

        report["data_types"] = {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        }

        report["missing_values"] = (
            df.isnull()
            .sum()
            .to_dict()
        )

        report["duplicate_rows"] = int(df.duplicated().sum())

        report["memory_usage_mb"] = round(
            df.memory_usage(deep=True).sum() / 1024 / 1024,
            2
        )

        numeric = df.select_dtypes(include="number")

        if not numeric.empty:
            report["numeric_summary"] = (
                numeric.describe()
                .round(2)
                .to_dict()
            )

        categorical = df.select_dtypes(include=["object", "category"])

        if not categorical.empty:

            report["categorical_summary"] = {}

            for col in categorical.columns:

                report["categorical_summary"][col] = (
                    categorical[col]
                    .value_counts()
                    .head(10)
                    .to_dict()
                )

        return report