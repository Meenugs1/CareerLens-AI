import pandas as pd

file_path = "data/raw/indian-job-market-dataset-2025.xlsx"

df = pd.read_excel(file_path)

print("\n===== TOTAL JOBS =====")
print(len(df))

print("\n===== UNIQUE JOB TITLES =====")
print(df["title"].nunique())

print("\n===== TOP 50 JOB TITLES =====")
print(df["title"].value_counts().head(50))