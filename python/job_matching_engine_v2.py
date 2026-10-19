import pandas as pd
import math

# ============================================================
# JOB MATCHING ENGINE V2
# WEIGHTED + MINIMUM MATCH REQUIREMENT
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/job_matching_results_v2.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("        JOB MATCHING ENGINE V2")
print("================================================")


# ============================================================
# SKILL ALIASES
# ============================================================

skill_aliases = {

    "python programming": "python",
    "python scripting": "python",

    "structured query language": "sql",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "powerbi": "power bi",
    "power bi desktop": "power bi",

    "java script": "javascript",
    "java-script": "javascript",

    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    "html5": "html",
    "html 5": "html",

    "css3": "css",
    "css 3": "css",

    "amazon web services": "aws",

    "machinelearning": "machine learning",

    "nlp": "natural language processing",

    "nodejs": "node.js",
    "node js": "node.js",

    "angularjs": "angular",

    "ml": "machine learning",
}


# ============================================================
# GENERIC / NOISY TERMS
# ============================================================

ignored_skills = {

    "not specified",
    "data",
    "analysis",
    "analytical",
    "analytics",
    "development",
    "technical",
    "software",
    "project",
    "management",
    "usage",
    "handling",
    "assistance",
    "generation",
    "calling",
    "voice",
    "candidate",
    "employee",
    "screening",
    "experience",
    "joining formalities",
    "responsibilities",
    "activities",
    "requirements",
    "process",
    "role",
    "office",
    "microsoft",
    "bi",
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

role = input(
    "\nEnter target job role: "
).strip()

skills_input = input(
    "Enter your skills (comma separated): "
).strip()


if not role:

    print("Please enter a job role.")
    exit()


if not skills_input:

    print("Please enter your skills.")
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
print("TARGET ROLE")
print("================================================")

print(role)


print("\n================================================")
print("YOUR SKILLS")
print("================================================")

for skill in sorted(user_skills):

    print("✓", skill)


# ============================================================
# FILTER JOBS BY ROLE
# ============================================================

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .astype(str)
    .str.lower()
    .str.contains(
        role_lower,
        na=False
    )
].copy()


print("\n================================================")
print("ROLE FILTER")
print("================================================")

print(
    "Jobs found for role:",
    len(role_jobs)
)


if len(role_jobs) == 0:

    print("\nNo jobs found for this role.")

    print(
        "Try a broader role such as Data Analyst, "
        "Business Analyst, Frontend Developer, "
        "Full Stack Developer or ML Engineer."
    )

    exit()


# ============================================================
# EXTRACT JOB SKILLS
# ============================================================

def extract_skills(skill_text):

    skills = set()

    for skill in str(skill_text).split(","):

        normalized = normalize_skill(skill)

        if normalized:

            skills.add(normalized)

    return skills


role_jobs["normalized_skills"] = (
    role_jobs["tagsandskills"]
    .apply(extract_skills)
)


# ============================================================
# MARKET SKILL FREQUENCY
# ============================================================

market_skill_counts = {}

for skills in role_jobs["normalized_skills"]:

    for skill in skills:

        market_skill_counts[skill] = (
            market_skill_counts.get(skill, 0) + 1
        )


# ============================================================
# CALCULATE SKILL WEIGHT
# ============================================================

def skill_weight(skill):

    frequency = market_skill_counts.get(
        skill,
        1
    )

    total_jobs = len(role_jobs)

    frequency_ratio = (
        frequency / total_jobs
    )

    # Log scaling prevents extremely common
    # skills from dominating the score.

    weight = 1 + math.log1p(
        frequency_ratio * 100
    )

    return weight


# ============================================================
# MATCH JOB
# ============================================================

results = []


for _, row in role_jobs.iterrows():

    job_skills = row["normalized_skills"]

    if not job_skills:

        continue


    matched = (
        user_skills
        & job_skills
    )


    missing = (
        job_skills
        - user_skills
    )


    # --------------------------------------------------------
    # WEIGHTED SCORE
    # --------------------------------------------------------

    total_weight = sum(
        skill_weight(skill)
        for skill in job_skills
    )


    matched_weight = sum(
        skill_weight(skill)
        for skill in matched
    )


    if total_weight == 0:

        score = 0

    else:

        score = (
            matched_weight
            / total_weight
            * 100
        )


    # --------------------------------------------------------
    # REQUIRE AT LEAST 2 MATCHED SKILLS
    # --------------------------------------------------------

    if len(matched) < 2:

        continue


    # --------------------------------------------------------
    # MATCH LEVEL
    # --------------------------------------------------------

    if score >= 75:

        match_level = "Excellent"

    elif score >= 55:

        match_level = "Strong"

    elif score >= 35:

        match_level = "Moderate"

    else:

        match_level = "Low"


    results.append({

        "job_id": row["jobid"],

        "job_title": row["title"],

        "company": row["companyname"],

        "location": row["location"],

        "experience": row["experience"],

        "salary_range": row["salary_range"],

        "currency": row["currency"],

        "job_uploaded": row["jobuploaded"],

        "match_score": round(
            score,
            2
        ),

        "match_level": match_level,

        "matched_skills": ", ".join(
            sorted(matched)
        ),

        "missing_skills": ", ".join(
            sorted(missing)
        ),

        "matched_skill_count": len(
            matched
        ),

        "required_skill_count": len(
            job_skills
        )
    })


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


if len(results_df) == 0:

    print(
        "\nNo jobs matched at least "
        "2 of your skills."
    )

    exit()


# ============================================================
# SORT RESULTS
# ============================================================

results_df = results_df.sort_values(

    by=[
        "match_score",
        "matched_skill_count"
    ],

    ascending=[
        False,
        False
    ]

).reset_index(drop=True)


# ============================================================
# TOP 20 JOBS
# ============================================================

print("\n================================================")
print("TOP MATCHING JOBS")
print("================================================")


for position, (_, row) in enumerate(
    results_df.head(20).iterrows(),
    start=1
):

    print(
        f"\n{position}. {row['job_title']}"
    )

    print(
        f"   Company: {row['company']}"
    )

    print(
        f"   Location: {row['location']}"
    )

    print(
        f"   Match Score: {row['match_score']}%"
    )

    print(
        f"   Match Level: {row['match_level']}"
    )

    print(
        f"   Matched: {row['matched_skills']}"
    )

    if row["missing_skills"]:

        print(
            f"   Missing: {row['missing_skills']}"
        )


# ============================================================
# SUMMARY
# ============================================================

print("\n================================================")
print("MATCHING SUMMARY")
print("================================================")

print(
    "Role:",
    role
)

print(
    "Jobs analyzed:",
    len(role_jobs)
)

print(
    "Jobs with 2+ matched skills:",
    len(results_df)
)

print(
    "Excellent matches (75%+):",
    len(
        results_df[
            results_df["match_score"] >= 75
        ]
    )
)

print(
    "Strong matches (55-74%):",
    len(
        results_df[
            (results_df["match_score"] >= 55)
            &
            (results_df["match_score"] < 75)
        ]
    )
)

print(
    "Moderate matches (35-54%):",
    len(
        results_df[
            (results_df["match_score"] >= 35)
            &
            (results_df["match_score"] < 55)
        ]
    )
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(
    output_file,
    index=False
)


print("\n================================================")
print("REPORT SAVED")
print("================================================")

print(output_file)


print("\n================================================")
print("V2 ANALYSIS COMPLETE")
print("================================================")