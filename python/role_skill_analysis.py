import pandas as pd

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

print("\n===== DYNAMIC ROLE SKILL ANALYSIS =====")


# ------------------------------------------------
# GET ROLE FROM USER
# ------------------------------------------------

role = input("\nEnter a job role: ").strip()

if not role:
    print("Please enter a job role.")
    exit()


print(f"\nSearching for: {role}")


# ------------------------------------------------
# FIND RELEVANT JOBS
# ------------------------------------------------

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .str.lower()
    .str.contains(role_lower, na=False)
].copy()


# ------------------------------------------------
# CHECK RESULTS
# ------------------------------------------------

print("\n===== ROLE SEARCH RESULTS =====")

print("Jobs found:", len(role_jobs))


if len(role_jobs) == 0:

    print("\nNo matching jobs found.")

    print("\nTry a broader role such as:")
    print("Data Analyst")
    print("Software Engineer")
    print("Frontend Developer")
    print("Java Developer")
    print("Business Analyst")

    exit()


# ------------------------------------------------
# EXTRACT SKILLS
# ------------------------------------------------

all_skills = []

for skills in role_jobs["tagsandskills"]:

    skill_list = str(skills).split(",")

    for skill in skill_list:

        skill = skill.strip().lower()

        if skill and skill != "not specified":
            all_skills.append(skill)


# ------------------------------------------------
# COUNT SKILLS
# ------------------------------------------------

skill_counts = pd.Series(all_skills).value_counts()


# ------------------------------------------------
# TOP SKILLS
# ------------------------------------------------

print("\n===== TOP 30 SKILLS =====")

print(
    skill_counts
    .head(30)
    .to_string()
)


# ------------------------------------------------
# SKILL PERCENTAGE
# ------------------------------------------------

skill_analysis = pd.DataFrame({
    "skill": skill_counts.index,
    "job_count": skill_counts.values
})


skill_analysis["percentage"] = (
    skill_analysis["job_count"]
    / len(role_jobs)
    * 100
)


print("\n===== TOP 30 SKILLS WITH PERCENTAGE =====")

print(
    skill_analysis
    .head(30)
    .to_string(index=False)
)