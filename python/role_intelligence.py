import pandas as pd

# ============================================================
# LOAD DATA
# ============================================================

file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

print("\n================================================")
print("          JOB MARKET INTELLIGENCE")
print("================================================")


# ============================================================
# USER INPUT
# ============================================================

role = input("\nEnter a job role: ").strip()

if not role:
    print("Please enter a job role.")
    exit()


print(f"\nSearching for: {role}")


# ============================================================
# FIND JOBS
# ============================================================

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .str.lower()
    .str.contains(role_lower, na=False)
].copy()


# ============================================================
# CHECK RESULTS
# ============================================================

if len(role_jobs) == 0:

    print("\nNo matching jobs found.")
    exit()


print("\n================================================")
print("ROLE OVERVIEW")
print("================================================")

print("Role:", role)
print("Jobs found:", len(role_jobs))


# ============================================================
# SKILL ANALYSIS
# ============================================================

all_skills = []

for skills in role_jobs["tagsandskills"]:

    skill_list = str(skills).split(",")

    for skill in skill_list:

        skill = skill.strip().lower()

        if skill and skill != "not specified":
            all_skills.append(skill)


skill_counts = pd.Series(all_skills).value_counts()


skill_analysis = pd.DataFrame({
    "skill": skill_counts.index,
    "job_count": skill_counts.values
})


skill_analysis["percentage"] = (
    skill_analysis["job_count"]
    / len(role_jobs)
    * 100
)


print("\n================================================")
print("TOP 20 SKILLS")
print("================================================")

print(
    skill_analysis
    .head(20)
    .to_string(index=False)
)


# ============================================================
# SALARY ANALYSIS
# ============================================================

salary_jobs = role_jobs[
    (role_jobs["currency"] == "INR") &
    (role_jobs["salary_available"] == True)
].copy()


print("\n================================================")
print("SALARY INTELLIGENCE")
print("================================================")

print("Jobs with salary information:", len(salary_jobs))


if len(salary_jobs) > 0:

    average_salary = salary_jobs["average_salary"].mean()
    median_salary = salary_jobs["average_salary"].median()

    print(
        "Average Salary: ₹",
        round(average_salary, 2)
    )

    print(
        "Median Salary: ₹",
        round(median_salary, 2)
    )

    print(
        "Average Salary (LPA):",
        round(average_salary / 100000, 2)
    )

    print(
        "Median Salary (LPA):",
        round(median_salary / 100000, 2)
    )

else:

    print("No INR salary data available.")


# ============================================================
# EXPERIENCE ANALYSIS
# ============================================================

print("\n================================================")
print("EXPERIENCE INTELLIGENCE")
print("================================================")

experience_counts = (
    role_jobs["experience"]
    .value_counts()
    .head(15)
)

print(experience_counts)


# ============================================================
# LOCATION ANALYSIS
# ============================================================

print("\n================================================")
print("TOP LOCATIONS")
print("================================================")

location_counts = (
    role_jobs["location"]
    .value_counts()
    .head(15)
)

print(location_counts)


# ============================================================
# COMPANY ANALYSIS
# ============================================================

print("\n================================================")
print("TOP COMPANIES")
print("================================================")

company_counts = (
    role_jobs["companyname"]
    .value_counts()
    .head(15)
)

print(company_counts)


# ============================================================
# WORK MODE
# ============================================================

print("\n================================================")
print("WORK MODE")
print("================================================")

location_text = (
    role_jobs["location"]
    .fillna("")
    .str.lower()
)

remote_jobs = location_text.str.contains(
    "remote",
    na=False
).sum()

hybrid_jobs = location_text.str.contains(
    "hybrid",
    na=False
).sum()

onsite_jobs = len(role_jobs) - remote_jobs - hybrid_jobs


print("Remote:", remote_jobs)
print("Hybrid:", hybrid_jobs)
print("On-site/Other:", onsite_jobs)


# ============================================================
# SAVE ROLE REPORT
# ============================================================

role_name = (
    role.lower()
    .replace(" ", "_")
    .replace("/", "_")
)

output_file = (
    f"data/processed/{role_name}_intelligence.csv"
)

skill_analysis.to_csv(
    output_file,
    index=False
)


print("\n================================================")
print("REPORT SAVED")
print("================================================")

print(output_file)