import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

# Keep only INR jobs with salary information
salary_df = df[
    (df["currency"] == "INR") &
    (df["salary_available"] == True)
].copy()

# Salary column we will analyze
salary = salary_df["average_salary"]

print("\n===== SALARY OUTLIER ANALYSIS =====")

# Basic statistics
print("\nTotal salary records:", len(salary))

print("Minimum salary:", salary.min())
print("Maximum salary:", salary.max())
print("Median salary:", salary.median())


# Calculate Q1 and Q3
Q1 = salary.quantile(0.25)
Q3 = salary.quantile(0.75)

# Calculate IQR
IQR = Q3 - Q1

# Calculate boundaries
lower_bound = Q1 - (1.5 * IQR)
upper_bound = Q3 + (1.5 * IQR)

print("\n===== QUARTILES =====")
print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)

print("\n===== OUTLIER BOUNDARIES =====")
print("Lower Bound:", lower_bound)
print("Upper Bound:", upper_bound)


# Identify potential outliers
outliers = salary_df[
    (salary_df["average_salary"] < lower_bound) |
    (salary_df["average_salary"] > upper_bound)
].copy()

print("\n===== OUTLIER SUMMARY =====")

print("Potential outliers:", len(outliers))

print(
    "Percentage of salary records that are outliers:",
    round((len(outliers) / len(salary_df)) * 100, 2),
    "%"
)


# Show highest salary records
print("\n===== TOP 20 HIGHEST SALARIES =====")

highest = outliers.sort_values(
    "average_salary",
    ascending=False
)[
    [
        "title",
        "companyname",
        "location",
        "minimumsalary",
        "maximumsalary",
        "average_salary"
    ]
].head(20)

print(highest.to_string(index=False))


# Show lowest salary records
print("\n===== LOWEST 20 SALARIES =====")

lowest = salary_df.sort_values(
    "average_salary",
    ascending=True
)[
    [
        "title",
        "companyname",
        "location",
        "minimumsalary",
        "maximumsalary",
        "average_salary"
    ]
].head(20)

print(lowest.to_string(index=False))