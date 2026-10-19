import pandas as pd
import math
import re

# ============================================================
# JOB RECOMMENDATION ENGINE V4
# SMART ROLE + SKILL + EXPERIENCE + LOCATION + FRESHNESS
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/job_recommendations_v4.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("     SMART JOB RECOMMENDATION ENGINE V4")
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
    user_experience = float(experience_input)
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


# ============================================================
# ROLE FILTER
# ============================================================

role_lower = role.lower()

role_jobs = df[
    df["title"]
    .astype(str)
    .str.lower()
    .str.contains(
        re.escape(role_lower),
        na=False
    )
].copy()


print("\n================================================")
print("SEARCH")
print("================================================")

print("Target Role:", role)
print("Jobs found:", len(role_jobs))


if len(role_jobs) == 0:

    print("\nNo jobs found.")
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
            market_skill_counts.get(skill, 0) + 1
        )


def skill_weight(skill):

    frequency = market_skill_counts.get(
        skill,
        1
    )

    ratio = frequency / len(role_jobs)

    return 1 + math.log1p(ratio * 100)


# ============================================================
# ROLE RELEVANCE
# ============================================================

def role_relevance(job_title, target_role):

    title = str(job_title).lower().strip()
    target = target_role.lower().strip()

    if title == target:
        return 100

    # Exact target phrase appears in title
    if target in title:
        return 95

    target_words = set(target.split())
    title_words = set(title.split())

    overlap = len(
        target_words & title_words
    )

    if len(target_words) == 0:
        return 0

    return min(
        90,
        (overlap / len(target_words)) * 100
    )


# ============================================================
# SENIORITY
# ============================================================

seniority_keywords = {

    "intern": -5,
    "trainee": -5,
    "fresher": -5,

    "junior": 0,

    "associate": 0,

    "senior": 20,
    "lead": 35,
    "manager": 45,
    "principal": 50,
    "architect": 50,
    "head": 60,
    "director": 60,
}


def get_seniority_penalty(job_title):

    title = str(job_title).lower()

    penalty = 0
    detected = "Standard"

    for keyword, value in seniority_keywords.items():

        if re.search(
            r"\b" + re.escape(keyword) + r"\b",
            title
        ):

            if value > penalty:
                penalty = value
                detected = keyword.title()

    return penalty, detected


# ============================================================
# EXPERIENCE MATCH
# ============================================================

def extract_experience_range(text):

    text = str(text).lower()

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    numbers = [
        float(number)
        for number in numbers
    ]

    if len(numbers) == 0:
        return None, None

    if len(numbers) == 1:

        return numbers[0], numbers[0]

    return min(numbers), max(numbers)


def experience_match(
    experience_text,
    user_years
):

    minimum, maximum = (
        extract_experience_range(
            experience_text
        )
    )

    if minimum is None:
        return 100

    # User falls within required range
    if (
        user_years >= minimum
        and user_years <= maximum
    ):
        return 100

    # Fresher applying to a job requiring experience
    if user_years < minimum:

        difference = minimum - user_years

        return max(
            0,
            100 - difference * 30
        )

    # User has more experience than required
    difference = user_years - maximum

    return max(
        0,
        100 - difference * 10
    )


# ============================================================
# LOCATION MATCH
# ============================================================

def location_match(
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

    preferred = preferred.lower().strip()

    # Direct location match
    if preferred in location:
        return 100

    # Bangalore / Bengaluru equivalence
    if preferred in {"bangalore", "bengaluru"}:

        if (
            "bangalore" in location
            or "bengaluru" in location
        ):
            return 100

    # Remote is useful regardless of city
    if "remote" in location:
        return 90

    # Hybrid is somewhat useful
    if "hybrid" in location:
        return 70

    return 30


# ============================================================
# FRESHNESS
# ============================================================

def freshness_score(days):

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
# SALARY AVAILABILITY
# ============================================================

def salary_score(row):

    if (
        row["currency"] == "INR"
        and row["salary_available"] == True
    ):
        return 100

    return 40


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

results = []


for _, row in role_jobs.iterrows():

    job_skills = row["normalized_skills"]

    if not job_skills:
        continue


    # --------------------------------------------------------
    # MATCHED / MISSING
    # --------------------------------------------------------

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

    role_score = role_relevance(
        row["title"],
        role
    )

    exp_score = experience_match(
        row["experience"],
        user_experience
    )

    loc_score = location_match(
        row["location"],
        preferred_location
    )

    fresh_score = freshness_score(
        row["days_ago"]
    )

    salary_availability = salary_score(
        row
    )

    seniority_penalty, seniority = (
        get_seniority_penalty(
            row["title"]
        )
    )


    # --------------------------------------------------------
    # BASE RECOMMENDATION SCORE
    # --------------------------------------------------------

    recommendation_score = (

        skill_score * 0.40

        + role_score * 0.20

        + exp_score * 0.15

        + loc_score * 0.15

        + fresh_score * 0.05

        + salary_availability * 0.05

    )


    # --------------------------------------------------------
    # SENIORITY PENALTY
    # --------------------------------------------------------

    # Strongly protect freshers from senior positions
    if user_experience == 0:

        recommendation_score -= (
            seniority_penalty * 0.50
        )

    else:

        recommendation_score -= (
            seniority_penalty * 0.20
        )


    recommendation_score = max(
        0,
        min(
            100,
            recommendation_score
        )
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


    # --------------------------------------------------------
    # FRESHER SUITABILITY
    # --------------------------------------------------------

    if user_experience == 0:

        if (
            seniority_penalty <= 5
            and exp_score >= 70
        ):

            fresher_suitable = "Yes"

        else:

            fresher_suitable = "No"

    else:

        fresher_suitable = "Not Applicable"


    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    results.append({

        "job_id": row["jobid"],

        "job_title": row["title"],

        "company": row["companyname"],

        "location": row["location"],

        "experience": row["experience"],

        "seniority": seniority,

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
            exp_score,
            2
        ),

        "location_match": round(
            loc_score,
            2
        ),

        "freshness_score": round(
            fresh_score,
            2
        ),

        "salary_score": round(
            salary_availability,
            2
        ),

        "seniority_penalty": seniority_penalty,

        "recommendation_score": round(
            recommendation_score,
            2
        ),

        "recommendation": recommendation,

        "fresher_suitable": fresher_suitable,

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
print("TOP SMART RECOMMENDATIONS")
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
        f"   Skill Match: "
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
        f"   Location Match: "
        f"{row['location_match']}%"
    )

    print(
        f"   Seniority: "
        f"{row['seniority']}"
    )

    print(
        f"   Fresher Suitable: "
        f"{row['fresher_suitable']}"
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

print(
    "Fresher-suitable jobs:",
    len(
        results_df[
            results_df[
                "fresher_suitable"
            ] == "Yes"
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
print("V4 COMPLETE")
print("================================================")