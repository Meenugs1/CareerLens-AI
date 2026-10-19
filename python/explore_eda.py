import pandas as pd

# ==============================
# LOAD CLEANED DATASET
# ==============================

file_path = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(file_path)


# ==============================
# BASIC DATASET OVERVIEW
# ==============================

print("\n===== DATASET OVERVIEW =====")

print("Total Jobs:", len(df))
print("Total Columns:", len(df.columns))
print("Unique Job Titles:", df["title"].nunique())
print("Unique Companies:", df["companyname"].nunique())
print("Unique Locations:", df["location"].nunique())


# ==============================
# TOP JOB TITLES
# ==============================

print("\n===== TOP 20 JOB TITLES =====")

top_titles = df["title"].value_counts().head(20)

print(top_titles)


# ==============================
# TOP COMPANIES
# ==============================

print("\n===== TOP 20 COMPANIES =====")

top_companies = df["companyname"].value_counts().head(20)

print(top_companies)


# ==============================
# TOP LOCATIONS
# ==============================

print("\n===== TOP 20 LOCATIONS =====")

top_locations = df["location"].value_counts().head(20)

print(top_locations)


# ==============================
# JOB EXPERIENCE
# ==============================

print("\n===== EXPERIENCE SAMPLE =====")

print(df["experience"].value_counts().head(20))


# ==============================
# SALARY OVERVIEW
# ==============================

print("\n===== SALARY OVERVIEW =====")

print("Jobs with salary information:",
      df["minimumsalary"].notna().sum())

print("Average Minimum Salary:",
      df["minimumsalary"].mean())

print("Average Maximum Salary:",
      df["maximumsalary"].mean())


# ==============================
# JOB FRESHNESS
# ==============================

print("\n===== JOB POSTING FRESHNESS =====")

print("Jobs with days_ago information:",
      df["days_ago"].notna().sum())

print("Average days ago:",
      df["days_ago"].mean())

print("Median days ago:",
      df["days_ago"].median())