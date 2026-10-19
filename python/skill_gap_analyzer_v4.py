import pandas as pd

# ============================================================
# DYNAMIC SKILL GAP ANALYZER V4
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/skill_gap_report_v4.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("      DYNAMIC SKILL GAP ANALYZER V4")
print("================================================")


# ============================================================
# SKILL ALIASES
# ============================================================

skill_aliases = {

    # Python
    "python programming": "python",
    "python scripting": "python",

    # SQL
    "structured query language": "sql",

    # Excel
    "ms excel": "excel",
    "microsoft excel": "excel",

    # Power BI
    "powerbi": "power bi",
    "power bi desktop": "power bi",

    # JavaScript
    "java script": "javascript",
    "java-script": "javascript",

    # React
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    # HTML
    "html5": "html",
    "html 5": "html",

    # CSS
    "css3": "css",
    "css 3": "css",

    # AWS
    "amazon web services": "aws",

    # Machine Learning
    "machinelearning": "machine learning",
    "ml": "machine learning",
}


# ============================================================
# GENERIC / NOISE TERMS
# ============================================================

ignored_skills = {

    "not specified",

    # Generic words
    "data",
    "analysis",
    "analytical",
    "analytics",
    "development",
    "software",
    "technical",
    "project",
    "management",
    "manager technology",
    "usage",
    "handling",
    "assistance",
    "generation",
    "calling",
    "voice",
    "work",
    "job",
    "jobs",
    "candidate",
    "employee",
    "joining formalities",
    "screening",
    "experience",

    # Role names
    "data analyst",
    "business analyst",

    # Generic process terms
    "process",
    "activities",
    "responsibilities",
    "requirements"
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    if not skill:
        return None

    if skill in ignored_skills:
        return None

    if skill in skill_aliases:
        return skill_aliases[skill]

    return skill


# ============================================================
# USER INPUT
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
# NORMALIZE USER SKILLS
# ============================================================

user_skills = set()

for skill in skills_input.split(","):

    normalized = normalize_skill(skill)

    if normalized:

        user_skills.add(normalized)


print("\n================================================")
print("YOUR SKILLS")
print("================================================")

for skill in sorted(user_skills):

    print("✓", skill)


# ============================================================
# FIND ROLE JOBS
# ============================================================

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .str.lower()
    .str.contains(role_lower, na=False)
].copy()


if len(role_jobs) == 0:

    print("\nNo matching jobs found.")

    print("\nTry a broader role name.")

    exit()


print("\n================================================")
print("ROLE ANALYSIS")
print("================================================")

print("Target Role:", role)
print("Jobs Found:", len(role_jobs))


# ============================================================
# EXTRACT SKILLS FROM JOBS
# ============================================================

all_skills = []

for skills in role_jobs["tagsandskills"]:

    for skill in str(skills).split(","):

        normalized = normalize_skill(skill)

        if normalized:

            all_skills.append(normalized)


# ============================================================
# COUNT SKILLS
# ============================================================

skill_counts = pd.Series(
    all_skills
).value_counts()


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
# At least 5% of matching jobs
# ============================================================

important_skills = skill_analysis[
    skill_analysis["percentage"] >= 5
].copy()


# ============================================================
# MATCH USER SKILLS
# ============================================================

required_skill_set = set(
    important_skills["skill"]
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
# WEIGHTED SCORE
# ============================================================

total_weight = important_skills[
    "percentage"
].sum()


matched_weight = important_skills[
    important_skills["skill"].isin(
        matched_skills
    )
]["percentage"].sum()


if total_weight > 0:

    match_score = (
        matched_weight
        / total_weight
        * 100
    )

else:

    match_score = 0


# ============================================================
# PRIORITY
# ============================================================

def priority(percentage):

    if percentage >= 30:
        return "HIGH"

    elif percentage >= 15:
        return "MEDIUM"

    else:
        return "LOW"


important_skills["priority"] = (
    important_skills["percentage"]
    .apply(priority)
)


# ============================================================
# DISPLAY TOP SKILLS
# ============================================================

print("\n================================================")
print("TOP REQUIRED SKILLS")
print("================================================")

print(
    important_skills
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

    matched_df = important_skills[
        important_skills["skill"].isin(
            matched_skills
        )
    ].sort_values(
        "percentage",
        ascending=False
    )

    for _, row in matched_df.iterrows():

        print(
            f"✓ {row['skill']} "
            f"- {row['percentage']:.2f}% of jobs"
        )

else:

    print("No important skills matched.")


# ============================================================
# MISSING SKILLS
# ============================================================

print("\n================================================")
print("SKILL GAPS")
print("================================================")

if missing_skills:

    missing_df = important_skills[
        important_skills["skill"].isin(
            missing_skills
        )
    ].sort_values(
        "percentage",
        ascending=False
    )

    for _, row in missing_df.iterrows():

        print(
            f"✗ {row['skill']} "
            f"- {row['percentage']:.2f}% "
            f"- {row['priority']}"
        )

else:

    print("No important skill gaps found!")


# ============================================================
# SCORE
# ============================================================

print("\n================================================")
print("OVERALL SKILL MATCH")
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

    print(
        "Excellent match for this job role."
    )

elif match_score >= 60:

    print(
        "Good match. Focus on the remaining important skills."
    )

elif match_score >= 40:

    print(
        "Moderate match. Several important skills "
        "should be developed."
    )

else:

    print(
        "Low match. Focus on the highest-frequency "
        "missing skills first."
    )


# ============================================================
# SAVE REPORT
# ============================================================

important_skills["target_role"] = role

important_skills["user_has_skill"] = (
    important_skills["skill"]
    .isin(user_skills)
)

important_skills["overall_match"] = match_score


important_skills.to_csv(
    output_file,
    index=False
)


print("\n================================================")
print("REPORT SAVED")
print("================================================")

print(output_file)


print("\n================================================")
print("ANALYSIS COMPLETE")
print("================================================")