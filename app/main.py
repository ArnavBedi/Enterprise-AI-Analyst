from app.tools.data_loader import DataLoader
from app.tools.dataset_inspector import DatasetInspector
from app.services.analyst_service import AnalystService


def main():

    print("=" * 60)
    print("ENTERPRISE AI ANALYST")
    print("=" * 60)

    # Load dataset
    df = DataLoader.load("data/sample.csv")

    # Inspect dataset
    report = DatasetInspector.inspect(df)

    print("\nInspecting dataset...\n")

    analyst = AnalystService()

    print("Sending report to Gemini...\n")

    analysis = analyst.analyze(report)

    print("=" * 60)
    print("AI ANALYSIS")
    print("=" * 60)

    print(analysis)


if __name__ == "__main__":
    main()
