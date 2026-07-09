from pathlib import Path
import pandas as pd


class DataLoader:
    @staticmethod
    def load(file_path: str) -> pd.DataFrame:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        suffix = path.suffix.lower()

        if suffix == ".csv":
            return pd.read_csv(path)

        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path)

        elif suffix == ".parquet":
            return pd.read_parquet(path)

        elif suffix == ".json":
            return pd.read_json(path)

        raise ValueError(f"Unsupported file type: {suffix}")

    @staticmethod
    def summary(df: pd.DataFrame):
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isna().sum().to_dict(),
        }