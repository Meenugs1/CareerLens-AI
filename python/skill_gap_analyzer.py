import pandas as pd

# ============================================================
# DYNAMIC SKILL GAP ANALYZER
# ============================================================

file_path = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(file_path)

print("\n================================================")
print("             SKILL GAP ANALYZER")
print("================================================")


# ============================================================
# GET USER INPUT
# ============================================================

role = input("\nEnter target job role: ").strip()

if not role:
    print("Please enter a job role.")
    exit()

skills_input = input(
    "Enter your current skills (comma separated): "
).strip()

if not skills_input:
    print("Please enter at least one skill.")
    exit()


# ============================================================
# PROCESS USER SKILLS
# ============================================================

user_skills = {
    skill.strip().lower()
    for skill in skills_input.split(",")
    if skill.strip()
}


print("\nYour Skills:")

for skill in sorted(user_skills):
    print("✓", skill)


# ============================================================
# FIND JOBS FOR TARGET ROLE
# ============================================================

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .str.lower()
    .str.contains(role_lower, na=False)
].copy()


if len(role_jobs) == 0:

    print("\nNo matching jobs found.")

    print("\nTry a broader role such as:")
    print("Data Analyst")
    print("Business Analyst")
    print("Frontend Developer")
    print("Full Stack Developer")
    print("ML Engineer")

    exit()


print("\n================================================")
print("ROLE ANALYSIS")
print("================================================")

print("Target Role:", role)
print("Jobs Analyzed:", len(role_jobs))


# ============================================================
# EXTRACT REQUIRED SKILLS
# ============================================================

all_skills = []

for skills in role_jobs["tagsandskills"]:

    skill_list = str(skills).split(",")

    for skill in skill_list:

        skill = skill.strip().lower()

        if skill and skill != "not specified":
            all_skills.append(skill)


skill_counts = pd.Series(all_skills).value_counts()


# ============================================================
# CREATE SKILL REQUIREMENTS
# ============================================================

skill_analysis = pd.DataFrame({
    "skill": skill_counts.index,
    "job_count": skill_counts.values
})

skill_analysis["percentage"] = (
    skill_analysis["job_count"]
    / len(role_jobs)
    * 100
)


# ============================================================
# SELECT IMPORTANT SKILLS
# ============================================================

required_skills = skill_analysis[
    skill_analysis["percentage"] >= 5
].copy()


# ============================================================
# FIND MATCHED AND MISSING SKILLS
# ============================================================

required_skill_set = set(
    required_skills["skill"]
)

matched_skills = (
    required_skill_set
    & user_skills
)

missing_skills = (
    required_skill_set
    - user_skills
)


# ============================================================
# MATCH SCORE
# ============================================================

if len(required_skill_set) > 0:

    match_score = (
        len(matched_skills)
        / len(required_skill_set)
        * 100
    )

else:

    match_score = 0


# ============================================================
# DISPLAY REQUIRED SKILLS
# ============================================================

print("\n================================================")
print("TOP REQUIRED SKILLS")
print("================================================")

print(
    required_skills
    .head(20)
    .to_string(index=False)
)


# ============================================================
# MATCHED SKILLS
# ============================================================

print("\n================================================")
print("MATCHED SKILLS")
print("================================================")

if matched_skills:

    matched_df = required_skills[
        required_skills["skill"].isin(matched_skills)
    ]

    for _, row in matched_df.iterrows():

        print(
            f"✓ {row['skill']} "
            f"({row['percentage']:.2f}% of jobs)"
        )

else:

    print("No major required skills matched.")


# ============================================================
# MISSING SKILLS
# ============================================================

print("\n================================================")
print("MISSING SKILLS")
print("================================================")

if missing_skills:

    missing_df = required_skills[
        required_skills["skill"].isin(missing_skills)
    ].sort_values(
        "percentage",
        ascending=False
    )

    for _, row in missing_df.iterrows():

        print(
            f"✗ {row['skill']} "
            f"({row['percentage']:.2f}% of jobs)"
        )

else:

    print("No major skill gaps found!")


# ============================================================
# FINAL SCORE
# ============================================================

print("\n================================================")
print("SKILL MATCH SCORE")
print("================================================")

print(
    f"{match_score:.2f}%"
)


# ============================================================
# INTERPRETATION
# ============================================================

print("\n================================================")
print("INTERPRETATION")
print("================================================")

if match_score >= 80:

    print("Excellent skill match!")

elif match_score >= 60:

    print("Good skill match. A few important skills are missing.")

elif match_score >= 40:

    print("Moderate skill match. You should focus on the missing skills.")

else:

    print("Low skill match. Several important skills should be developed.")


print("\n================================================")
print("ANALYSIS COMPLETE")
print("================================================")