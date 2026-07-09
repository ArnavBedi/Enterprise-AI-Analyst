from tools.data_loader import DataLoader

df = DataLoader.load("../data/sample.csv")

print(df)

print("\n===== DATASET SUMMARY =====\n")

summary = DataLoader.summary(df)

for key, value in summary.items():
    print(f"{key}:")
    print(value)
    print()