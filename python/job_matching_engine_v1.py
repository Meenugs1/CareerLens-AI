import pandas as pd

# ============================================================
# JOB MATCHING ENGINE V1
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/job_matching_results.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("             JOB MATCHING ENGINE V1")
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

    "tensorflow framework": "tensorflow",

    "pytorch framework": "pytorch",

    "nodejs": "node.js",
    "node js": "node.js",

    "angularjs": "angular",
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    if not skill:
        return None

    if skill in skill_aliases:

        return skill_aliases[skill]

    return skill


# ============================================================
# USER INPUT
# ============================================================

skills_input = input(
    "\nEnter your skills (comma separated): "
).strip()


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
print("YOUR SKILLS")
print("================================================")

for skill in sorted(user_skills):

    print("✓", skill)


# ============================================================
# PREPARE JOB SKILLS
# ============================================================

print("\nPreparing job skill data...")


def extract_skills(skill_text):

    skills = set()

    for skill in str(skill_text).split(","):

        normalized = normalize_skill(skill)

        if normalized:

            skills.add(normalized)

    return skills


df["normalized_skills"] = (
    df["tagsandskills"]
    .apply(extract_skills)
)


# ============================================================
# CALCULATE MATCH SCORE
# ============================================================

def calculate_match(job_skills):

    if not job_skills:

        return 0, set()

    matched = (
        user_skills
        & job_skills
    )

    score = (
        len(matched)
        / len(job_skills)
        * 100
    )

    return score, matched


results = []


print("\nCalculating job matches...")


for index, row in df.iterrows():

    job_skills = row["normalized_skills"]

    score, matched = calculate_match(
        job_skills
    )

    if score > 0:

        missing = (
            job_skills
            - user_skills
        )

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
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


if len(results_df) == 0:

    print(
        "\nNo jobs matched any of your skills."
    )

    exit()


# ============================================================
# SORT BY MATCH SCORE
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
# TOP MATCHING JOBS
# ============================================================

print("\n================================================")
print("TOP MATCHING JOBS")
print("================================================")


top_jobs = results_df.head(20)


for position, (_, row) in enumerate(
    top_jobs.iterrows(),
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
        f"   Match: {row['match_score']:.2f}%"
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
    "Total jobs in dataset:",
    len(df)
)

print(
    "Jobs matching at least one skill:",
    len(results_df)
)

print(
    "Jobs with 50%+ skill match:",
    len(
        results_df[
            results_df["match_score"] >= 50
        ]
    )
)

print(
    "Jobs with 75%+ skill match:",
    len(
        results_df[
            results_df["match_score"] >= 75
        ]
    )
)

print(
    "Jobs with 100% skill match:",
    len(
        results_df[
            results_df["match_score"] >= 100
        ]
    )
)


# ============================================================
# SAVE RESULTS
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
print("ANALYSIS COMPLETE")
print("================================================")