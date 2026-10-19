import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

print("\n===== JOB MARKET OVERVIEW =====")

# Basic statistics
print("Total Jobs:", len(df))
print("Unique Job Titles:", df["title"].nunique())
print("Unique Companies:", df["companyname"].nunique())
print("Unique Locations:", df["location"].nunique())


# Top job titles
print("\n===== TOP 20 JOB TITLES =====")

top_titles = df["title"].value_counts().head(20)
print(top_titles)


# Top companies
print("\n===== TOP 20 COMPANIES =====")

top_companies = df["companyname"].value_counts().head(20)
print(top_companies)


# Top locations
print("\n===== TOP 20 LOCATIONS =====")

top_locations = df["location"].value_counts().head(20)
print(top_locations)