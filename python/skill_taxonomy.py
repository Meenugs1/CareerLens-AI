import pandas as pd

# ============================================================
# SKILL TAXONOMY V2
# ============================================================

input_file = "data/processed/jobs_cleaned.xlsx"
output_file = "data/processed/skill_counts_v2.csv"

df = pd.read_excel(input_file)

print("\n================================================")
print("           SKILL TAXONOMY V2")
print("================================================")

# ------------------------------------------------------------
# STEP 1: Split skills
# ------------------------------------------------------------

df["skill_list"] = df["tagsandskills"].apply(
    lambda x: [
        skill.strip()
        for skill in str(x).split(",")
        if skill.strip()
        and skill.strip().lower() != "not specified"
    ]
)

# ------------------------------------------------------------
# STEP 2: Normalize text
# ------------------------------------------------------------

def normalize_skill(skill):

    skill = skill.lower().strip()

    aliases = {

        # Programming languages
        "python programming": "python",
        "python scripting": "python",

        "java programming": "java",

        "java script": "javascript",
        "java-script": "javascript",
        "javascript programming": "javascript",

        "c sharp": "c#",
        "c-sharp": "c#",

        "c plus plus": "c++",
        "c-plus-plus": "c++",

        # Web
        "html5": "html",
        "html 5": "html",

        "css3": "css",
        "css 3": "css",

        "reactjs": "react",
        "react js": "react",
        "react.js": "react",

        "nodejs": "node.js",
        "node js": "node.js",

        "angularjs": "angular",
        "angular.js": "angular",

        # Database
        "structured query language": "sql",

        "mysql database": "mysql",

        # Power BI
        "powerbi": "power bi",
        "power bi desktop": "power bi",

        # Excel
        "microsoft excel": "excel",
        "ms excel": "excel",

        # Cloud
        "amazon web services": "aws",

        # AI / ML
        "machinelearning": "machine learning",

        "artificial intelligence ai": "artificial intelligence",

        # DevOps
        "continuous integration": "ci/cd",
        "continuous integration and continuous deployment": "ci/cd",
        "continuous integration/continuous deployment": "ci/cd",

        # Version control
        "git version control": "git",
    }

    return aliases.get(skill, skill)


# Apply normalization

df["normalized_skill_list"] = df["skill_list"].apply(
    lambda skills: [normalize_skill(skill) for skill in skills]
)

# ------------------------------------------------------------
# STEP 3: Remove obvious non-skills
# ------------------------------------------------------------

non_skills = {

    # Job titles
    "developer",
    "engineer",
    "manager",
    "lead",
    "executive",
    "intern",
    "internship",

    # Experience terms
    "senior",
    "junior",
    "fresher",
    "experienced",
    "experience",

    # Generic words
    "job",
    "jobs",
    "work",
    "working",
    "employee",
    "candidate",
    "team",

    # Generic personality terms
    "hardworking",
    "motivated",
    "dedicated",
    "responsible",
    "quick learner",
    "positive attitude",
    "team player",
}


def remove_non_skills(skills):

    return [
        skill
        for skill in skills
        if skill not in non_skills
    ]


df["clean_skill_list"] = df["normalized_skill_list"].apply(
    remove_non_skills
)

# ------------------------------------------------------------
# STEP 4: Count skills
# ------------------------------------------------------------

all_skills = []

for skill_list in df["clean_skill_list"]:
    all_skills.extend(skill_list)

skill_counts = pd.Series(all_skills).value_counts()

# ------------------------------------------------------------
# STEP 5: Create final table
# ------------------------------------------------------------

skill_analysis = pd.DataFrame({
    "skill": skill_counts.index,
    "job_count": skill_counts.values
})

skill_analysis["percentage_of_jobs"] = (
    skill_analysis["job_count"]
    / len(df)
    * 100
)

# ------------------------------------------------------------
# STEP 6: Display results
# ------------------------------------------------------------

print("\nTotal jobs:", len(df))

print(
    "\nUnique skills after normalization:",
    len(skill_analysis)
)

print("\n================================================")
print("TOP 50 CLEANED SKILLS")
print("================================================")

print(
    skill_analysis
    .head(50)
    .to_string(index=False)
)

# ------------------------------------------------------------
# STEP 7: Save
# ------------------------------------------------------------

skill_analysis.to_csv(
    output_file,
    index=False
)

print("\n================================================")
print("SKILL TAXONOMY COMPLETE")
print("================================================")

print("Saved to:")
print(output_file)