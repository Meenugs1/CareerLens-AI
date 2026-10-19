import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

# Keep only INR jobs with salary information
salary_df = df[
    (df["currency"] == "INR") &
    (df["salary_available"] == True)
].copy()

print("\n===== SALARY ANALYSIS =====")

print("Total INR jobs with salary:", len(salary_df))

print("\n===== SALARY STATISTICS =====")

print("Average Salary:",
      salary_df["average_salary"].mean())

print("Median Salary:",
      salary_df["average_salary"].median())

print("Minimum Salary:",
      salary_df["average_salary"].min())

print("Maximum Salary:",
      salary_df["average_salary"].max())


print("\n===== SALARY IN LAKHS =====")

print("Average Salary (Lakhs):",
      salary_df["salary_lakh"].mean())

print("Median Salary (Lakhs):",
      salary_df["salary_lakh"].median())


print("\n===== SALARY RANGE =====")

print(
    salary_df["salary_range"]
    .value_counts()
    .sort_index()
)


print("\n===== TOP 20 ROLES BY AVERAGE SALARY =====")

top_salary_roles = (
    salary_df
    .groupby("title")
    .agg(
        average_salary=("average_salary", "mean"),
        job_count=("title", "count")
    )
    .query("job_count >= 10")
    .sort_values("average_salary", ascending=False)
    .head(20)
)

print(top_salary_roles)


print("\n===== SALARY BY EXPERIENCE =====")

salary_experience = (
    salary_df
    .groupby("minimumexperience")
    .agg(
        average_salary=("average_salary", "mean"),
        job_count=("title", "count")
    )
    .sort_index()
)

print(salary_experience.head(20))