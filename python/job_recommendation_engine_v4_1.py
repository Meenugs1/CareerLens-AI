import pandas as pd
import math
import re

# ============================================================
# JOB RECOMMENDATION ENGINE V4.1
# Adds: min/max experience columns, stronger fresher protection,
# city normalization, work mode input, cleaner skill matching,
# "Why Recommended" explanations.
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/job_recommendations_v4_1.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("     SMART JOB RECOMMENDATION ENGINE V4.1")
print("================================================")


# ============================================================
# SKILL ALIASES
# Maps messy/variant skill text to one clean concept.
# Alias lookup always runs BEFORE the ignored-skill check,
# so short forms like "ml" or "aiml" get resolved to their
# full concept instead of being treated as noise.
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

    # Machine learning family
    "ml": "machine learning",
    "machinelearning": "machine learning",
    "machine-learning": "machine learning",
    "machine learning": "machine learning",

    # AI/ML combined tags
    "aiml": "artificial intelligence / machine learning",
    "ai/ml": "artificial intelligence / machine learning",
    "ai ml": "artificial intelligence / machine learning",
    "ai-ml": "artificial intelligence / machine learning",

    "nlp": "natural language processing",

    "tensorflow": "tensorflow",
    "pytorch": "pytorch",

    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    "nodejs": "node.js",
    "node js": "node.js",

    "angularjs": "angular",
}


# ============================================================
# GENERIC / NOISY / FRAGMENT TERMS
# These never show up as a "missing skill" to the user.
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
    "languages",
    # stray fragments that sometimes appear in messy tag data
    "machine",
    "al",
    "ml",
    "aiml",
}


# ============================================================
# NORMALIZE SKILL
# Order matters: alias lookup first, THEN the ignored check.
# This means "ml" / "aiml" resolve into their full concept
# and are never independently flagged as noise, while true
# fragments (leftover from bad splitting) still get dropped.
# ============================================================

def normalize_skill(skill):

    skill = str(skill).strip().lower()

    if not skill:
        return None

    if skill in skill_aliases:
        skill = skill_aliases[skill]

    if skill in ignored_skills:
        return None

    return skill


def extract_skills(skill_text):

    skills = set()

    for skill in str(skill_text).split(","):

        normalized = normalize_skill(skill)

        if normalized:
            skills.add(normalized)

    return skills


# ============================================================
# CITY NORMALIZATION
# ============================================================

city_aliases = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "madras": "chennai",
    "gurgaon": "gurugram",
}


def normalize_city(city):

    city = str(city).strip().lower()

    if city in city_aliases:
        return city_aliases[city]

    return city


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

print("\nWork Mode options: Any / On-site / Hybrid / Remote")
work_mode_input = input(
    "Enter preferred work mode: "
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


preferred_city = normalize_city(preferred_location)
preferred_is_any = (
    preferred_location == ""
    or preferred_location.strip().lower() == "any"
)

preferred_work_mode = work_mode_input.strip().lower()
if preferred_work_mode == "" or preferred_work_mode == "any":
    preferred_work_mode = "any"


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


role_jobs["normalized_skills"] = (
    role_jobs["tagsandskills"]
    .apply(extract_skills)
)


# ============================================================
# MARKET SKILL FREQUENCY (for weighting rarer skills higher)
# ============================================================

market_skill_counts = {}

for skills in role_jobs["normalized_skills"]:

    for skill in skills:

        market_skill_counts[skill] = (
            market_skill_counts.get(skill, 0) + 1
        )


def skill_weight(skill):

    frequency = market_skill_counts.get(skill, 1)
    ratio = frequency / len(role_jobs)

    return 1 + math.log1p(ratio * 100)


# ============================================================
# ROLE RELEVANCE (fully dynamic - works for any role text)
# ============================================================

def role_relevance(job_title, target_role):

    title = str(job_title).lower().strip()
    target = target_role.lower().strip()

    if title == target:
        return 100

    if target in title:
        return 95

    target_words = set(target.split())
    title_words = set(title.split())

    overlap = len(target_words & title_words)

    if len(target_words) == 0:
        return 0

    return min(90, (overlap / len(target_words)) * 100)


# ============================================================
# SENIORITY
# Negative keywords strongly hurt fresher suitability.
# Positive keywords are good signals for freshers.
# ============================================================

negative_seniority_keywords = {
    "senior": 20,
    "sr": 20,
    "lead": 35,
    "manager": 45,
    "principal": 50,
    "architect": 50,
    "head": 60,
    "director": 60,
    "staff": 30,
    "expert": 25,
}

positive_seniority_keywords = {
    "junior",
    "jr",
    "fresher",
    "trainee",
    "intern",
    "entry level",
}


def get_seniority_info(job_title):

    title = str(job_title).lower()

    penalty = 0
    detected = "Standard"
    is_positive = False

    for keyword in positive_seniority_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", title):
            is_positive = True
            detected = keyword.title()

    for keyword, value in negative_seniority_keywords.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", title):
            if value > penalty:
                penalty = value
                detected = keyword.title()

    return penalty, detected, is_positive


# ============================================================
# EXPERIENCE MATCH
# Prefers minimumexperience / maximumexperience columns.
# Falls back to parsing the raw experience text only if those
# columns are missing or blank for a row.
# ============================================================

def extract_experience_range_from_text(text):

    text = str(text).lower()
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    numbers = [float(n) for n in numbers]

    if len(numbers) == 0:
        return None, None

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers), max(numbers)


def get_experience_range(row):

    minimum = row.get("minimumexperience")
    maximum = row.get("maximumexperience")

    min_valid = pd.notna(minimum)
    max_valid = pd.notna(maximum)

    if min_valid and max_valid:
        return float(minimum), float(maximum)

    if min_valid and not max_valid:
        return float(minimum), float(minimum)

    # Fall back to parsing raw experience text
    return extract_experience_range_from_text(
        row.get("experience")
    )


def experience_match(minimum, maximum, user_years):

    if minimum is None:
        return 100

    if user_years >= minimum and user_years <= maximum:
        return 100

    if user_years < minimum:
        difference = minimum - user_years
        return max(0, 100 - difference * 30)

    difference = user_years - maximum
    return max(0, 100 - difference * 10)


# ============================================================
# LOCATION MATCH
# 100 = exact city
# 90  = preferred city appears among several cities in a listing
# 80  = remote, when remote is acceptable to the user
# 70  = hybrid involving a relevant city
# 30  = other city
# 0   = unknown / unusable location text
# ============================================================

def location_match(job_location, preferred_city, preferred_is_any):

    raw_location = str(job_location).strip()

    if raw_location == "" or raw_location.lower() in {"nan", "not specified"}:
        return 0

    location_lower = raw_location.lower()

    if preferred_is_any:
        return 50

    is_remote = "remote" in location_lower
    is_hybrid = "hybrid" in location_lower

    # Split multi-city listings on common separators
    city_parts = re.split(r"[\/,&|]| and ", location_lower)
    city_parts = [normalize_city(part.strip()) for part in city_parts if part.strip()]

    if preferred_city in city_parts:
        if len(city_parts) == 1 and not is_hybrid and not is_remote:
            return 100
        return 90

    if is_hybrid and preferred_city in location_lower:
        return 70

    if is_remote:
        return 80

    if is_hybrid:
        return 70

    return 30


# ============================================================
# WORK MODE MATCH
# Only uses a dedicated column if the dataset actually has one.
# Otherwise infers Remote/Hybrid from location text only -
# never invents "On-site" when the data doesn't say so.
# ============================================================

def get_job_work_mode(row):

    for column_name in row.index:
        if column_name.strip().lower() == "workmode":
            value = str(row[column_name]).strip().lower()
            if value and value != "nan":
                return value

    location_lower = str(row.get("location", "")).lower()

    if "remote" in location_lower:
        return "remote"

    if "hybrid" in location_lower:
        return "hybrid"

    return "not specified"


def work_mode_match(job_mode, preferred_mode):

    if preferred_mode == "any":
        return 100

    if job_mode == "not specified":
        return 50

    if job_mode == preferred_mode:
        return 100

    return 20


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
# WHY RECOMMENDED
# ============================================================

def build_why_recommended(
    matched_skills,
    preferred_city,
    preferred_is_any,
    loc_score,
    exp_score,
    fresher_suitable
):

    reasons = []

    for skill in sorted(matched_skills):
        reasons.append(f"{skill.title()} matched")

    if not preferred_is_any and loc_score >= 70:
        reasons.append(f"{preferred_city.title()} preference matched")

    if exp_score >= 70:
        reasons.append("Suitable experience level")

    if fresher_suitable == "Yes":
        reasons.append("Fresher-friendly role")

    if not reasons:
        reasons.append("Meets minimum skill overlap")

    return "; ".join(f"\u2713 {reason}" for reason in reasons)


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

results = []


for _, row in role_jobs.iterrows():

    job_skills = row["normalized_skills"]

    if not job_skills:
        continue

    matched = user_skills & job_skills
    missing = job_skills - user_skills

    if len(matched) < 2:
        continue

    # ---------------- Skill score ----------------

    total_weight = sum(skill_weight(s) for s in job_skills)
    matched_weight = sum(skill_weight(s) for s in matched)

    skill_score = (
        (matched_weight / total_weight * 100)
        if total_weight > 0 else 0
    )

    # ---------------- Role relevance ----------------

    role_score = role_relevance(row["title"], role)

    # ---------------- Experience ----------------

    min_exp, max_exp = get_experience_range(row)
    exp_score = experience_match(min_exp, max_exp, user_experience)

    # ---------------- Location ----------------

    loc_score = location_match(
        row["location"], preferred_city, preferred_is_any
    )

    # ---------------- Work mode ----------------

    job_work_mode = get_job_work_mode(row)
    mode_score = work_mode_match(job_work_mode, preferred_work_mode)

    # ---------------- Freshness ----------------

    fresh_score = freshness_score(row.get("days_ago"))

    # ---------------- Seniority ----------------

    seniority_penalty, seniority, is_positive_fit = (
        get_seniority_info(row["title"])
    )

    # ---------------- Base score (matches required weights) ----------------

    recommendation_score = (
        skill_score * 0.40
        + role_score * 0.20
        + exp_score * 0.20
        + loc_score * 0.10
        + fresh_score * 0.05
        + mode_score * 0.05
    )

    # ---------------- Fresher protection ----------------

    if user_experience == 0:
        recommendation_score -= seniority_penalty * 0.60
    else:
        recommendation_score -= seniority_penalty * 0.20

    recommendation_score = max(0, min(100, recommendation_score))

    # ---------------- Match level ----------------

    if recommendation_score >= 75:
        recommendation = "Excellent Match"
    elif recommendation_score >= 60:
        recommendation = "Strong Match"
    elif recommendation_score >= 45:
        recommendation = "Moderate Match"
    else:
        recommendation = "Low Match"

    # ---------------- Fresher suitability ----------------

    if user_experience == 0:
        if seniority_penalty == 0 or is_positive_fit:
            fresher_suitable = "Yes"
        else:
            fresher_suitable = "No"
    else:
        fresher_suitable = "Not Applicable"

    why_recommended = build_why_recommended(
        matched, preferred_city, preferred_is_any,
        loc_score, exp_score, fresher_suitable
    )

    results.append({
        "job_id": row["jobid"],
        "job_title": row["title"],
        "company": row["companyname"],
        "location": row["location"],
        "work_mode": job_work_mode.title(),
        "experience": row["experience"],
        "seniority": seniority,
        "salary_range": row.get("salary_range"),
        "currency": row.get("currency"),
        "job_uploaded": row.get("jobuploaded"),
        "days_ago": row.get("days_ago"),

        "skill_score": round(skill_score, 2),
        "role_relevance": round(role_score, 2),
        "experience_match": round(exp_score, 2),
        "location_match": round(loc_score, 2),
        "work_mode_match": round(mode_score, 2),
        "freshness_score": round(fresh_score, 2),

        "recommendation_score": round(recommendation_score, 2),
        "recommendation": recommendation,
        "fresher_suitable": fresher_suitable,

        "matched_skills": ", ".join(sorted(matched)),
        "missing_skills": ", ".join(sorted(missing)),
        "matched_skill_count": len(matched),
        "required_skill_count": len(job_skills),

        "why_recommended": why_recommended,
    })


# ============================================================
# RESULTS
# ============================================================

results_df = pd.DataFrame(results)

if len(results_df) == 0:
    print("\nNo suitable recommendations found.")
    exit()

results_df = results_df.sort_values(
    by=["recommendation_score", "skill_score"],
    ascending=[False, False]
).reset_index(drop=True)


# ============================================================
# DISPLAY TOP 20
# ============================================================

print("\n================================================")
print("TOP SMART RECOMMENDATIONS")
print("================================================")

for position, (_, row) in enumerate(
    results_df.head(20).iterrows(), start=1
):

    print(f"\n{position}. {row['job_title']}")
    print(f"   Company: {row['company']}")
    print(f"   Location: {row['location']}")
    print(f"   Recommendation Score: {row['recommendation_score']}%")
    print(f"   Match Level: {row['recommendation']}")
    print(f"   Skill Match: {row['skill_score']}%")
    print(f"   Role Relevance: {row['role_relevance']}%")
    print(f"   Experience Match: {row['experience_match']}%")
    print(f"   Location Match: {row['location_match']}%")
    print(f"   Work Mode Match: {row['work_mode_match']}%")
    print(f"   Freshness: {row['freshness_score']}%")
    print(f"   Seniority: {row['seniority']}")
    print(f"   Fresher Suitable: {row['fresher_suitable']}")
    print(f"   Matched Skills: {row['matched_skills']}")

    if row["missing_skills"]:
        print(f"   Missing Skills: {row['missing_skills']}")

    print(f"   Why Recommended: {row['why_recommended']}")


# ============================================================
# SUMMARY
# ============================================================

print("\n================================================")
print("RECOMMENDATION SUMMARY")
print("================================================")

print("Jobs analyzed:", len(role_jobs))
print("Jobs recommended:", len(results_df))

print(
    "Excellent matches:",
    len(results_df[results_df["recommendation_score"] >= 75])
)

print(
    "Strong matches:",
    len(results_df[
        (results_df["recommendation_score"] >= 60)
        & (results_df["recommendation_score"] < 75)
    ])
)

print(
    "Fresher-suitable jobs:",
    len(results_df[results_df["fresher_suitable"] == "Yes"])
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(output_file, index=False)

print("\n================================================")
print("REPORT SAVED")
print("================================================")
print(output_file)

print("\n================================================")
print("V4.1 COMPLETE")
print("================================================")
