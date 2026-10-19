import pandas as pd

file_path = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(file_path)

usd = df[df["currency"] == "USD"].copy()

print("\n===== USD JOBS =====")

print("Number of USD jobs:", len(usd))

print("\nUSD salary statistics:")

print(
    usd[
        ["minimumsalary", "maximumsalary"]
    ].describe()
)

print("\n===== USD JOB SAMPLES =====")

print(
    usd[
        [
            "title",
            "companyname",
            "location",
            "minimumsalary",
            "maximumsalary"
        ]
    ].head(30).to_string(index=False)
)