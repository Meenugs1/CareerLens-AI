import pandas as pd
import re

# ============================================================
# DYNAMIC SKILL GAP ANALYZER V4.1
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
taxonomy_file = "data/processed/skill_taxonomy_final.csv"
output_file = "data/processed/skill_gap_report_v4_1.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("     DYNAMIC SKILL GAP ANALYZER V4.1")
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

    # NLP
    "nlp": "natural language processing",

    # TensorFlow
    "tensorflow framework": "tensorflow",

    # PyTorch
    "pytorch framework": "pytorch",

    # Node
    "nodejs": "node.js",
    "node js": "node.js",

    # Angular
    "angularjs": "angular",
}


# ============================================================
# GENERIC / NOISE SKILLS
# ============================================================

ignored_skills = {

    "not specified",

    # Generic concepts
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

    # Generic HR/process words
    "candidate",
    "employee",
    "screening",
    "experience",
    "joining formalities",
    "responsibilities",
    "activities",
    "requirements",
    "process",

    # Role descriptions
    "data analyst",
    "business analyst",
    "frontend developer",
    "front end",
    "frontend development",

    # Obviously weak standalone terms
    "machine",
    "stack",
    "bi",
    "office",
    "microsoft",
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
# NORMALIZE ROLE NAME
# ============================================================

def normalize_role_name(role):

    role = role.lower().strip()

    replacements = {

        "developer": "development",
        "developers": "development",

        "engineer": "engineering",
        "engineers": "engineering",

        "analyst": "analysis",
        "analysts": "analysis",

        "scientist": "science",
        "scientists": "science",

        "manager": "management",
        "managers": "management",
    }

    words = role.split()

    normalized_words = []

    for word in words:

        normalized_words.append(
            replacements.get(word, word)
        )

    return " ".join(normalized_words)


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
    .fillna("")
    .str.lower()
    .str.contains(
        re.escape(role_lower),
        na=False
    )
].copy()


if len(role_jobs) == 0:

    print("\nNo matching jobs found.")

    print(
        "\nTry using a broader or more common job title."
    )

    exit()


print("\n================================================")
print("ROLE ANALYSIS")
print("================================================")

print("Target Role:", role)
print("Jobs Found:", len(role_jobs))


# ============================================================
# EXTRACT SKILLS
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
# REMOVE TARGET-ROLE DESCRIPTORS
# ============================================================

normalized_role = normalize_role_name(role)


def is_role_descriptor(skill):

    normalized_skill = normalize_role_name(skill)

    if normalized_skill == normalized_role:

        return True

    return False


skill_analysis = skill_analysis[
    ~skill_analysis["skill"].apply(
        is_role_descriptor
    )
].copy()


# ============================================================
# KEEP IMPORTANT SKILLS
# ============================================================
# Minimum 5% of matching jobs
# ============================================================

important_skills = skill_analysis[
    skill_analysis["percentage"] >= 5
].copy()


# ============================================================
# LOAD TAXONOMY
# ============================================================

try:

    taxonomy = pd.read_csv(
        taxonomy_file
    )

    taxonomy["skill"] = (
        taxonomy["skill"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    taxonomy_lookup = dict(
        zip(
            taxonomy["skill"],
            taxonomy["category"]
        )
    )

except Exception:

    taxonomy_lookup = {}


important_skills["category"] = (
    important_skills["skill"]
    .map(taxonomy_lookup)
    .fillna("Other")
)


# ============================================================
# USER SKILL MATCHING
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
# WEIGHTED MATCH SCORE
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

def get_priority(percentage):

    if percentage >= 30:

        return "HIGH"

    elif percentage >= 15:

        return "MEDIUM"

    else:

        return "LOW"


important_skills["priority"] = (
    important_skills["percentage"]
    .apply(get_priority)
)


# ============================================================
# STATUS
# ============================================================

important_skills["status"] = (
    important_skills["skill"]
    .apply(
        lambda x:
        "HAVE"
        if x in user_skills
        else "MISSING"
    )
)


# ============================================================
# SORT RESULTS
# ============================================================

important_skills = (
    important_skills
    .sort_values(
        "percentage",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# TOP REQUIRED SKILLS
# ============================================================

print("\n================================================")
print("TOP REQUIRED MARKET SKILLS")
print("================================================")

print(
    important_skills[
        [
            "skill",
            "category",
            "job_count",
            "percentage"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# MATCHED SKILLS
# ============================================================

print("\n================================================")
print("MATCHED SKILLS")
print("================================================")

matched_df = important_skills[
    important_skills["status"] == "HAVE"
]


if len(matched_df) > 0:

    for _, row in matched_df.iterrows():

        print(
            f"✓ {row['skill']} "
            f"- {row['percentage']:.2f}% "
            f"- {row['category']}"
        )

else:

    print("No important skills matched.")


# ============================================================
# MISSING SKILLS
# ============================================================

print("\n================================================")
print("SKILL GAPS")
print("================================================")

missing_df = important_skills[
    important_skills["status"] == "MISSING"
]


if len(missing_df) > 0:

    for _, row in missing_df.iterrows():

        print(
            f"✗ {row['skill']} "
            f"- {row['percentage']:.2f}% "
            f"- {row['priority']} "
            f"- {row['category']}"
        )

else:

    print("No important skill gaps found!")


# ============================================================
# SCORE
# ============================================================

print("\n================================================")
print("MARKET-WEIGHTED SKILL MATCH")
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
        "Excellent skill coverage for this role."
    )

elif match_score >= 60:

    print(
        "Good skill coverage. Focus on the remaining "
        "high-frequency skills."
    )

elif match_score >= 40:

    print(
        "Moderate skill coverage. Several important "
        "market skills are still missing."
    )

else:

    print(
        "Low skill coverage. Start with the highest-"
        "frequency missing skills."
    )


# ============================================================
# SAVE REPORT
# ============================================================

important_skills["target_role"] = role

important_skills["overall_match"] = round(
    match_score,
    2
)


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