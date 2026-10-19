import pandas as pd

# ============================================================
# SKILL GAP ANALYZER V3
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/skill_gap_report_v3.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("          SKILL GAP ANALYZER V3")
print("================================================")


# ============================================================
# ROLE SKILL FRAMEWORK
# ============================================================
# These are NOT hardcoded job results.
# They define how we interpret skills for the analyzer.
# Job percentages still come from the real dataset.
# ============================================================

role_framework = {

    "data analyst": {

        "core": [
            "python",
            "sql",
            "excel",
            "power bi",
            "tableau"
        ],

        "supporting": [
            "data visualization",
            "data modeling",
            "data quality",
            "data management",
            "etl",
            "business intelligence"
        ],

        "advanced": [
            "sas",
            "macros",
            "data warehousing"
        ]
    },

    "business analyst": {

        "core": [
            "business analysis",
            "sql",
            "excel",
            "power bi",
            "jira"
        ],

        "supporting": [
            "requirement gathering",
            "documentation",
            "user stories",
            "gap analysis",
            "agile",
            "stakeholder management"
        ],

        "advanced": [
            "business process modeling",
            "scrum",
            "tableau"
        ]
    },

    "frontend developer": {

        "core": [
            "html",
            "css",
            "javascript",
            "react",
            "git"
        ],

        "supporting": [
            "typescript",
            "redux",
            "bootstrap",
            "tailwind css",
            "angular"
        ],

        "advanced": [
            "nextjs",
            "vue.js",
            "micro frontend"
        ]
    },

    "full stack developer": {

        "core": [
            "javascript",
            "react",
            "java",
            "sql",
            "spring boot",
            "git"
        ],

        "supporting": [
            "node.js",
            "angular",
            "html",
            "css",
            "mongodb",
            "mysql",
            "postgresql",
            "microservices"
        ],

        "advanced": [
            "aws",
            "docker",
            "kubernetes",
            "typescript"
        ]
    },

    "ml engineer": {

        "core": [
            "python",
            "machine learning",
            "artificial intelligence",
            "tensorflow",
            "pytorch"
        ],

        "supporting": [
            "natural language processing",
            "deep learning",
            "statistics",
            "computer vision",
            "algorithms"
        ],

        "advanced": [
            "aws",
            "kubernetes",
            "generative ai",
            "langchain"
        ]
    }
}


# ============================================================
# SKILL ALIASES
# ============================================================

skill_aliases = {

    "powerbi": "power bi",
    "power bi desktop": "power bi",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "python programming": "python",
    "python scripting": "python",

    "structured query language": "sql",

    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    "html5": "html",
    "html 5": "html",

    "css3": "css",
    "css 3": "css",

    "java script": "javascript",
    "java-script": "javascript",

    "amazon web services": "aws",

    "machinelearning": "machine learning",
    "ml": "machine learning"
}


# ============================================================
# NOISE / NON-SKILLS
# ============================================================

ignored_skills = {

    "not specified",
    "data",
    "analysis",
    "analytical",
    "data analyst",
    "data analytics",
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
    "job",
    "jobs",
    "candidate",
    "employee",
    "joining formalities",
    "screening",
    "experience"
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

role_key = role.lower()

if role_key not in role_framework:

    print("\nThis role is not yet supported by the V3 framework.")

    print("\nCurrently supported roles:")

    for supported_role in role_framework:
        print("-", supported_role.title())

    print(
        "\nWe will make the framework dynamic for additional roles "
        "in a later version."
    )

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
# FIND JOBS FOR ROLE
# ============================================================

role_jobs = df[
    df["title"]
    .str.lower()
    .str.contains(role_key, na=False)
].copy()


if len(role_jobs) == 0:

    print("\nNo matching jobs found.")
    exit()


print("\n================================================")
print("ROLE ANALYSIS")
print("================================================")

print("Target Role:", role.title())
print("Jobs Analyzed:", len(role_jobs))


# ============================================================
# EXTRACT DATASET SKILLS
# ============================================================

all_skills = []

for skills in role_jobs["tagsandskills"]:

    for skill in str(skills).split(","):

        normalized = normalize_skill(skill)

        if normalized:

            all_skills.append(normalized)


skill_counts = pd.Series(all_skills).value_counts()


# ============================================================
# CREATE SKILL TABLE
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
# GET ROLE FRAMEWORK
# ============================================================

framework = role_framework[role_key]

core_skills = set(framework["core"])
supporting_skills = set(framework["supporting"])
advanced_skills = set(framework["advanced"])

all_framework_skills = (
    core_skills
    | supporting_skills
    | advanced_skills
)


# ============================================================
# MATCH SKILLS
# ============================================================

matched_core = core_skills & user_skills
missing_core = core_skills - user_skills

matched_supporting = (
    supporting_skills & user_skills
)

missing_supporting = (
    supporting_skills - user_skills
)

matched_advanced = (
    advanced_skills & user_skills
)

missing_advanced = (
    advanced_skills - user_skills
)


# ============================================================
# GET DATASET FREQUENCY FOR FRAMEWORK SKILLS
# ============================================================

skill_percentage_map = dict(
    zip(
        skill_analysis["skill"],
        skill_analysis["percentage"]
    )
)


def dataset_percentage(skill):

    return skill_percentage_map.get(skill, 0)


# ============================================================
# DISPLAY CORE SKILLS
# ============================================================

print("\n================================================")
print("CORE SKILLS")
print("================================================")

for skill in framework["core"]:

    percentage = dataset_percentage(skill)

    if skill in user_skills:

        print(
            f"✓ {skill} "
            f"- YOU HAVE IT "
            f"- {percentage:.2f}% of jobs"
        )

    else:

        print(
            f"✗ {skill} "
            f"- MISSING "
            f"- {percentage:.2f}% of jobs"
        )


# ============================================================
# DISPLAY SUPPORTING SKILLS
# ============================================================

print("\n================================================")
print("SUPPORTING SKILLS")
print("================================================")

for skill in framework["supporting"]:

    percentage = dataset_percentage(skill)

    if skill in user_skills:

        print(
            f"✓ {skill} "
            f"- YOU HAVE IT "
            f"- {percentage:.2f}% of jobs"
        )

    else:

        print(
            f"○ {skill} "
            f"- MISSING "
            f"- {percentage:.2f}% of jobs"
        )


# ============================================================
# DISPLAY ADVANCED SKILLS
# ============================================================

print("\n================================================")
print("ADVANCED / OPTIONAL SKILLS")
print("================================================")

for skill in framework["advanced"]:

    percentage = dataset_percentage(skill)

    if skill in user_skills:

        print(
            f"✓ {skill} "
            f"- YOU HAVE IT "
            f"- {percentage:.2f}% of jobs"
        )

    else:

        print(
            f"○ {skill} "
            f"- OPTIONAL "
            f"- {percentage:.2f}% of jobs"
        )


# ============================================================
# WEIGHTED CAREER SCORE
# ============================================================
# Core = 60%
# Supporting = 30%
# Advanced = 10%
# ============================================================

core_score = (
    len(matched_core)
    / len(core_skills)
    * 60
)

supporting_score = (
    len(matched_supporting)
    / len(supporting_skills)
    * 30
)

advanced_score = (
    len(matched_advanced)
    / len(advanced_skills)
    * 10
)

career_score = (
    core_score
    + supporting_score
    + advanced_score
)


# ============================================================
# SCORE DISPLAY
# ============================================================

print("\n================================================")
print("CAREER SKILL MATCH")
print("================================================")

print(
    f"Core Skills: "
    f"{len(matched_core)}/{len(core_skills)}"
)

print(
    f"Supporting Skills: "
    f"{len(matched_supporting)}/{len(supporting_skills)}"
)

print(
    f"Advanced Skills: "
    f"{len(matched_advanced)}/{len(advanced_skills)}"
)

print(
    f"\nOverall Skill Match: "
    f"{career_score:.2f}%"
)


# ============================================================
# PRIORITY GAPS
# ============================================================

print("\n================================================")
print("PRIORITY SKILL GAPS")
print("================================================")

priority_gaps = []

for skill in missing_core:

    priority_gaps.append({
        "skill": skill,
        "level": "HIGH",
        "job_percentage": dataset_percentage(skill)
    })


for skill in missing_supporting:

    priority_gaps.append({
        "skill": skill,
        "level": "MEDIUM",
        "job_percentage": dataset_percentage(skill)
    })


for skill in missing_advanced:

    priority_gaps.append({
        "skill": skill,
        "level": "LOW",
        "job_percentage": dataset_percentage(skill)
    })


priority_df = pd.DataFrame(priority_gaps)

if len(priority_df) > 0:

    priority_order = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    priority_df["sort_order"] = (
        priority_df["level"]
        .map(priority_order)
    )

    priority_df = priority_df.sort_values(
        ["sort_order", "job_percentage"],
        ascending=[True, False]
    )

    for _, row in priority_df.iterrows():

        print(
            f"{row['level']}: "
            f"{row['skill']} "
            f"- {row['job_percentage']:.2f}% of jobs"
        )

else:

    print("No skill gaps found!")


# ============================================================
# SAVE REPORT
# ============================================================

report_rows = []

for skill in framework["core"]:

    report_rows.append({
        "role": role.title(),
        "skill": skill,
        "level": "Core",
        "status": (
            "Have"
            if skill in user_skills
            else "Missing"
        ),
        "job_percentage": dataset_percentage(skill)
    })


for skill in framework["supporting"]:

    report_rows.append({
        "role": role.title(),
        "skill": skill,
        "level": "Supporting",
        "status": (
            "Have"
            if skill in user_skills
            else "Missing"
        ),
        "job_percentage": dataset_percentage(skill)
    })


for skill in framework["advanced"]:

    report_rows.append({
        "role": role.title(),
        "skill": skill,
        "level": "Advanced",
        "status": (
            "Have"
            if skill in user_skills
            else "Missing"
        ),
        "job_percentage": dataset_percentage(skill)
    })


report_df = pd.DataFrame(report_rows)

report_df["overall_match"] = career_score

report_df.to_csv(
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