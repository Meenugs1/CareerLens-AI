import pandas as pd

file_path = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(file_path)


# =====================================
# CURRENCY CHECK
# =====================================

print("\n===== CURRENCY =====")
print(df["currency"].value_counts(dropna=False))


# =====================================
# ZERO SALARY CHECK
# =====================================

print("\n===== ZERO SALARY =====")

print("Minimum salary = 0:",
      (df["minimumsalary"] == 0).sum())

print("Maximum salary = 0:",
      (df["maximumsalary"] == 0).sum())


# =====================================
# POSITIVE SALARY STATISTICS
# =====================================

salary_df = df[
    (df["minimumsalary"] > 0) &
    (df["maximumsalary"] > 0)
].copy()

print("\n===== POSITIVE SALARY DATA =====")

print("Jobs with positive salary:",
      len(salary_df))

print("\nMinimum salary statistics:")
print(salary_df["minimumsalary"].describe())

print("\nMaximum salary statistics:")
print(salary_df["maximumsalary"].describe())


# =====================================
# HIGHEST SALARIES
# =====================================

print("\n===== HIGHEST SALARIES =====")

highest = salary_df.sort_values(
    "maximumsalary",
    ascending=False
)[
    [
        "title",
        "companyname",
        "location",
        "currency",
        "minimumsalary",
        "maximumsalary"
    ]
].head(20)

print(highest.to_string(index=False))


# =====================================
# SALARY DISTRIBUTION
# =====================================

print("\n===== SALARY RANGES =====")

bins = [
    0,
    100000,
    200000,
    300000,
    500000,
    1000000,
    float("inf")
]

labels = [
    "Below 1 Lakh",
    "1-2 Lakhs",
    "2-3 Lakhs",
    "3-5 Lakhs",
    "5-10 Lakhs",
    "10+ Lakhs"
]

salary_df["salary_range"] = pd.cut(
    salary_df["maximumsalary"],
    bins=bins,
    labels=labels,
    right=False
)

print(
    salary_df["salary_range"]
    .value_counts()
    .sort_index()
)