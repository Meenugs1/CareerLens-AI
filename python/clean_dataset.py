import pandas as pd


# ==============================
# 1. LOAD DATASET
# ==============================

input_file = "data/raw/indian-job-market-dataset-2025.xlsx"

df = pd.read_excel(input_file)

print("Original shape:", df.shape)


# ==============================
# 2. CLEAN COLUMN NAMES
# ==============================

df.columns = df.columns.str.strip().str.lower()


# ==============================
# 3. REMOVE DUPLICATES
# ==============================

duplicates_before = df.duplicated().sum()

df = df.drop_duplicates()

print("Duplicates removed:", duplicates_before)


# ==============================
# 4. CLEAN TEXT COLUMNS
# ==============================

text_columns = [
    "title",
    "companyname",
    "tagsandskills",
    "experience",
    "salary",
    "location",
    "jobdescription"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].astype("string").str.strip()


# ==============================
# 5. HANDLE MISSING VALUES
# ==============================

df["companyname"] = df["companyname"].fillna("Unknown Company")

df["tagsandskills"] = df["tagsandskills"].fillna("Not Specified")

df["experience"] = df["experience"].fillna("Not Specified")


# ==============================
# 6. CONVERT JOB POSTING AGE
# ==============================

df["jobuploaded"] = df["jobuploaded"].fillna("Unknown")

df["days_ago"] = (
    df["jobuploaded"]
    .str.extract(r"(\d+)")
    .astype(float)
)

df.loc[
    df["jobuploaded"].str.lower().str.contains("today", na=False),
    "days_ago"
] = 0

df.loc[
    df["jobuploaded"].str.lower().str.contains("just now", na=False),
    "days_ago"
] = 0


# ==============================
# 7. CLEAN SALARY DATA
# ==============================

df["minimumsalary"] = pd.to_numeric(
    df["minimumsalary"],
    errors="coerce"
)

df["maximumsalary"] = pd.to_numeric(
    df["maximumsalary"],
    errors="coerce"
)


# Treat 0 salary as "not disclosed"
df.loc[df["minimumsalary"] == 0, "minimumsalary"] = pd.NA
df.loc[df["maximumsalary"] == 0, "maximumsalary"] = pd.NA


# Salary availability
df["salary_available"] = (
    (df["minimumsalary"].notna()) &
    (df["maximumsalary"].notna())
)


# Average salary
df["average_salary"] = (
    df["minimumsalary"] + df["maximumsalary"]
) / 2


# Average salary in lakhs
df["salary_lakh"] = df["average_salary"] / 100000


# Salary range
def get_salary_range(salary):

    if pd.isna(salary):
        return "Not Disclosed"

    elif salary < 100000:
        return "Below 1 Lakh"

    elif salary < 200000:
        return "1-2 Lakhs"

    elif salary < 300000:
        return "2-3 Lakhs"

    elif salary < 500000:
        return "3-5 Lakhs"

    elif salary < 1000000:
        return "5-10 Lakhs"

    else:
        return "10+ Lakhs"


df["salary_range"] = df["average_salary"].apply(
    get_salary_range
)


# ==============================
# 8. CONVERT EXPERIENCE
# ==============================

df["minimumexperience"] = pd.to_numeric(
    df["minimumexperience"],
    errors="coerce"
)

df["maximumexperience"] = pd.to_numeric(
    df["maximumexperience"],
    errors="coerce"
)


# ==============================
# 9. CLEAN LOCATION
# ==============================

df["location"] = (
    df["location"]
    .fillna("Unknown")
    .str.strip()
)


# ==============================
# 10. SAVE CLEANED DATASET
# ==============================

output_file = "data/processed/jobs_cleaned.xlsx"

df.to_excel(output_file, index=False)


# ==============================
# 11. FINAL REPORT
# ==============================

print("\n===== CLEANING COMPLETE =====")

print("Final shape:", df.shape)

print("\nMissing values:")

print(df.isnull().sum())

print("\nDuplicate rows remaining:")

print(df.duplicated().sum())

print("\nSalary available:")

print(df["salary_available"].value_counts())

print("\nSalary ranges:")

print(df["salary_range"].value_counts())

print("\nCleaned dataset saved to:")

print(output_file)