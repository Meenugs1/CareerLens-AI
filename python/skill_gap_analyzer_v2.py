import pandas as pd

# ============================================================
# SKILL GAP ANALYZER V2
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"

df = pd.read_excel(input_file)

print("\n================================================")
print("          SKILL GAP ANALYZER V2")
print("================================================")


# ============================================================
# SKILL NORMALIZATION
# ============================================================

skill_aliases = {

    # Data / Analytics
    "data analytics": "data analysis",
    "data analyst": None,
    "analytical": None,
    "analysis": None,
    "data": None,
    "bi": None,

    # Power BI
    "powerbi": "power bi",
    "power bi desktop": "power bi",

    # Excel
    "ms excel": "excel",
    "microsoft excel": "excel",

    # Python
    "python programming": "python",
    "python scripting": "python",

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

    # SQL
    "structured query language": "sql",

    # Machine Learning
    "machinelearning": "machine learning",
    "ml": "machine learning",

    # AI
    "ai": "artificial intelligence",

    # AWS
    "amazon web services": "aws",

    # Git
    "git version control": "git",
}


# ============================================================
# SKILLS THAT SHOULD NOT BE TREATED AS INDIVIDUAL SKILLS
# ============================================================

ignored_skills = {

    "data",
    "analysis",
    "analytical",
    "data analyst",
    "bi",
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
    "jobs",
    "job",
    "employee",
    "candidate",
    "joining formalities",
    "screening",
    "experience",
}


# ============================================================
# NORMALIZE ONE SKILL
# ============================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    if not skill:
        return None

    if skill == "not specified":
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

    exit()


print("\n================================================")
print("ROLE ANALYSIS")
print("================================================")

print("Target Role:", role)
print("Jobs Analyzed:", len(role_jobs))


# ============================================================
# EXTRACT AND NORMALIZE JOB SKILLS
# ============================================================

all_skills = []

for skills in role_jobs["tagsandskills"]:

    for skill in str(skills).split(","):

        normalized = normalize_skill(skill)

        if normalized:

            all_skills.append(normalized)


skill_counts = pd.Series(all_skills).value_counts()


# ============================================================
# SKILL REQUIREMENT TABLE
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
# IMPORTANT SKILLS
# ============================================================

required_skills = skill_analysis[
    skill_analysis["percentage"] >= 5
].copy()


# ============================================================
# MATCH USER SKILLS
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
# WEIGHTED MATCH SCORE
# ============================================================

total_weight = required_skills["percentage"].sum()


matched_weight = required_skills[
    required_skills["skill"].isin(matched_skills)
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
# PRIORITY FUNCTION
# ============================================================

def get_priority(percentage):

    if percentage >= 30:

        return "HIGH"

    elif percentage >= 15:

        return "MEDIUM"

    else:

        return "LOW"


required_skills["priority"] = (
    required_skills["percentage"]
    .apply(get_priority)
)


# ============================================================
# MATCHED SKILLS
# ============================================================

print("\n================================================")
print("MATCHED SKILLS")
print("================================================")

if matched_skills:

    matched_df = required_skills[
        required_skills["skill"].isin(
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

    print("No major skills matched.")


# ============================================================
# MISSING SKILLS
# ============================================================

print("\n================================================")
print("MISSING SKILLS")
print("================================================")

if missing_skills:

    missing_df = required_skills[
        required_skills["skill"].isin(
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
            f"- {row['priority']} PRIORITY"
        )

else:

    print("No major skill gaps found!")


# ============================================================
# FINAL SCORE
# ============================================================

print("\n================================================")
print("WEIGHTED SKILL MATCH")
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
        "Excellent match for this role."
    )

elif match_score >= 60:

    print(
        "Good match. Focus on a few missing skills."
    )

elif match_score >= 40:

    print(
        "Moderate match. Several important skills "
        "should be developed."
    )

else:

    print(
        "Low match. Focus on the highest-priority "
        "skills first."
    )


# ============================================================
# SAVE REPORT
# ============================================================

output_file = (
    "data/processed/"
    + role_lower.replace(" ", "_")
    + "_skill_gap_v2.csv"
)


required_skills.to_csv(
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