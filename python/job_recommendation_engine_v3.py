import pandas as pd
import math

# ============================================================
# JOB RECOMMENDATION ENGINE V3
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/job_recommendations_v3.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("        JOB RECOMMENDATION ENGINE V3")
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
    "ml": "machine learning",

    "nlp": "natural language processing",

    "nodejs": "node.js",
    "node js": "node.js",

    "angularjs": "angular",
}


# ============================================================
# GENERIC TERMS TO IGNORE
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

experience_input = input(
    "Enter your experience in years: "
).strip()

preferred_location = input(
    "Enter preferred location (or type Any): "
).strip()


if not role or not skills_input:

    print("\nRole and skills are required.")
    exit()


# ============================================================
# EXPERIENCE
# ============================================================

try:

    user_experience = float(
        experience_input
    )

except:

    user_experience = 0


# ============================================================
# USER SKILLS
# ============================================================

user_skills = set()

for skill in skills_input.split(","):

    normalized = normalize_skill(skill)

    if normalized:

        user_skills.add(normalized)


print("\n================================================")
print("USER PROFILE")
print("================================================")

print("Target Role:", role)
print("Experience:", user_experience, "years")

print("Skills:")

for skill in sorted(user_skills):

    print("✓", skill)

print(
    "Preferred Location:",
    preferred_location
)


# ============================================================
# ROLE FILTER
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
print("ROLE SEARCH")
print("================================================")

print(
    "Jobs found:",
    len(role_jobs)
)


if len(role_jobs) == 0:

    print("\nNo jobs found for this role.")
    exit()


# ============================================================
# EXTRACT SKILLS
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
            market_skill_counts.get(
                skill,
                0
            ) + 1
        )


# ============================================================
# SKILL WEIGHT
# ============================================================

def skill_weight(skill):

    frequency = market_skill_counts.get(
        skill,
        1
    )

    frequency_ratio = (
        frequency / len(role_jobs)
    )

    return 1 + math.log1p(
        frequency_ratio * 100
    )


# ============================================================
# ROLE RELEVANCE
# ============================================================

def calculate_role_relevance(job_title, target_role):

    title = str(job_title).lower()
    target = target_role.lower()

    if title.strip() == target.strip():

        return 100

    if target in title:

        return 90

    target_words = set(
        target.split()
    )

    title_words = set(
        title.split()
    )

    overlap = len(
        target_words & title_words
    )

    if len(target_words) > 0:

        return (
            overlap
            / len(target_words)
            * 100
        )

    return 0


# ============================================================
# EXPERIENCE MATCH
# ============================================================

def calculate_experience_match(
    experience_text,
    user_years
):

    text = str(experience_text).lower()

    # No usable requirement
    if (
        text == "not specified"
        or text.strip() == ""
        or text == "nan"
    ):

        return 100

    numbers = []

    for part in text.replace(
        "-", " "
    ).split():

        try:

            value = float(
                part.replace(
                    "yrs",
                    ""
                ).replace(
                    "yr",
                    ""
                )
            )

            numbers.append(value)

        except:

            continue

    if len(numbers) == 0:

        return 100

    minimum = min(numbers)

    maximum = max(numbers)

    if (
        user_years >= minimum
        and user_years <= maximum
    ):

        return 100

    if user_years < minimum:

        difference = (
            minimum
            - user_years
        )

        return max(
            0,
            100 - difference * 20
        )

    difference = (
        user_years
        - maximum
    )

    return max(
        0,
        100 - difference * 10
    )


# ============================================================
# FRESHNESS SCORE
# ============================================================

def calculate_freshness(days):

    if pd.isna(days):

        return 50

    try:

        days = float(days)

    except:

        return 50

    if days <= 1:

        return 100

    if days <= 7:

        return 90

    if days <= 14:

        return 80

    if days <= 30:

        return 65

    if days <= 60:

        return 50

    return 30


# ============================================================
# LOCATION SCORE
# ============================================================

def calculate_location_score(
    job_location,
    preferred
):

    if not preferred:

        return 50

    if preferred.lower() == "any":

        return 50

    location = str(
        job_location
    ).lower()

    preferred = preferred.lower()

    if preferred in location:

        return 100

    if "remote" in location:

        return 80

    if "hybrid" in location:

        return 70

    return 40


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

results = []


for _, row in role_jobs.iterrows():

    job_skills = row[
        "normalized_skills"
    ]

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
    # SKILL SCORE
    # --------------------------------------------------------

    total_weight = sum(
        skill_weight(skill)
        for skill in job_skills
    )

    matched_weight = sum(
        skill_weight(skill)
        for skill in matched
    )

    if total_weight > 0:

        skill_score = (
            matched_weight
            / total_weight
            * 100
        )

    else:

        skill_score = 0


    # --------------------------------------------------------
    # OTHER SCORES
    # --------------------------------------------------------

    role_score = calculate_role_relevance(
        row["title"],
        role
    )

    experience_score = (
        calculate_experience_match(
            row["experience"],
            user_experience
        )
    )

    freshness_score = (
        calculate_freshness(
            row["days_ago"]
        )
    )

    location_score = (
        calculate_location_score(
            row["location"],
            preferred_location
        )
    )


    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    recommendation_score = (

        skill_score * 0.50

        + role_score * 0.20

        + experience_score * 0.10

        + freshness_score * 0.10

        + location_score * 0.10

    )


    # --------------------------------------------------------
    # REQUIRE AT LEAST 2 MATCHED SKILLS
    # --------------------------------------------------------

    if len(matched) < 2:

        continue


    # --------------------------------------------------------
    # RECOMMENDATION LEVEL
    # --------------------------------------------------------

    if recommendation_score >= 75:

        recommendation = "Excellent Match"

    elif recommendation_score >= 60:

        recommendation = "Strong Match"

    elif recommendation_score >= 45:

        recommendation = "Moderate Match"

    else:

        recommendation = "Low Match"


    results.append({

        "job_id": row["jobid"],

        "job_title": row["title"],

        "company": row["companyname"],

        "location": row["location"],

        "experience": row["experience"],

        "salary_range": row["salary_range"],

        "currency": row["currency"],

        "job_uploaded": row["jobuploaded"],

        "days_ago": row["days_ago"],

        "skill_score": round(
            skill_score,
            2
        ),

        "role_relevance": round(
            role_score,
            2
        ),

        "experience_match": round(
            experience_score,
            2
        ),

        "freshness_score": round(
            freshness_score,
            2
        ),

        "location_score": round(
            location_score,
            2
        ),

        "recommendation_score": round(
            recommendation_score,
            2
        ),

        "recommendation": recommendation,

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
# RESULTS
# ============================================================

results_df = pd.DataFrame(results)


if len(results_df) == 0:

    print(
        "\nNo suitable recommendations found."
    )

    exit()


results_df = results_df.sort_values(

    by=[
        "recommendation_score",
        "skill_score"
    ],

    ascending=[
        False,
        False
    ]

).reset_index(drop=True)


# ============================================================
# DISPLAY TOP 20
# ============================================================

print("\n================================================")
print("TOP JOB RECOMMENDATIONS")
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
        f"   Recommendation Score: "
        f"{row['recommendation_score']}%"
    )

    print(
        f"   {row['recommendation']}"
    )

    print(
        f"   Skill Score: "
        f"{row['skill_score']}%"
    )

    print(
        f"   Role Relevance: "
        f"{row['role_relevance']}%"
    )

    print(
        f"   Experience Match: "
        f"{row['experience_match']}%"
    )

    print(
        f"   Matched: "
        f"{row['matched_skills']}"
    )

    if row["missing_skills"]:

        print(
            f"   Missing: "
            f"{row['missing_skills']}"
        )


# ============================================================
# SUMMARY
# ============================================================

print("\n================================================")
print("RECOMMENDATION SUMMARY")
print("================================================")

print(
    "Jobs analyzed:",
    len(role_jobs)
)

print(
    "Jobs recommended:",
    len(results_df)
)

print(
    "Excellent matches:",
    len(
        results_df[
            results_df[
                "recommendation_score"
            ] >= 75
        ]
    )
)

print(
    "Strong matches:",
    len(
        results_df[
            (
                results_df[
                    "recommendation_score"
                ] >= 60
            )
            &
            (
                results_df[
                    "recommendation_score"
                ] < 75
            )
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
print("V3 COMPLETE")
print("================================================")