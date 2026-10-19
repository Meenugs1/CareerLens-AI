import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(file_path)


# =====================================
# SALARY DATA
# =====================================

salary_df = df[
    df["minimumsalary"].notna() &
    df["maximumsalary"].notna()
].copy()


print("\n===== SALARY DATA =====")

print("Jobs with salary:", len(salary_df))


# =====================================
# BASIC SALARY STATISTICS
# =====================================

print("\n===== MINIMUM SALARY STATISTICS =====")

print(salary_df["minimumsalary"].describe())


print("\n===== MAXIMUM SALARY STATISTICS =====")

print(salary_df["maximumsalary"].describe())


# =====================================
# SALARY PERCENTILES
# =====================================

print("\n===== SALARY PERCENTILES =====")

print("Minimum salary median:",
      salary_df["minimumsalary"].median())

print("Maximum salary median:",
      salary_df["maximumsalary"].median())

print("Minimum salary 90th percentile:",
      salary_df["minimumsalary"].quantile(0.90))

print("Maximum salary 90th percentile:",
      salary_df["maximumsalary"].quantile(0.90))


# =====================================
# TOP JOB TITLES BY SALARY
# =====================================

print("\n===== TOP 20 JOB TITLES BY AVERAGE MAXIMUM SALARY =====")

top_salary_roles = (
    salary_df
    .groupby("title")
    .agg(
        average_max_salary=("maximumsalary", "mean"),
        job_count=("title", "count")
    )
    .query("job_count >= 10")
    .sort_values("average_max_salary", ascending=False)
    .head(20)
)

print(top_salary_roles)


# =====================================
# SALARY BY EXPERIENCE
# =====================================

print("\n===== SALARY BY EXPERIENCE =====")

experience_salary = (
    salary_df
    .groupby("minimumexperience")
    .agg(
        average_min_salary=("minimumsalary", "mean"),
        average_max_salary=("maximumsalary", "mean"),
        job_count=("title", "count")
    )
    .sort_index()
)

print(experience_salary.head(20))