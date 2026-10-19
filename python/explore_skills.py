import pandas as pd

file_path = "data/raw/indian-job-market-dataset-2025.xlsx"

df = pd.read_excel(file_path)

print("\n===== SAMPLE SKILLS =====")
print(df["tagsAndSkills"].head(20).to_string())

print("\n===== SKILL VALUES WITH MOST JOBS =====")
print(df["tagsAndSkills"].value_counts().head(20))

print("\n===== MISSING SKILLS =====")
print(df["tagsAndSkills"].isna().sum())