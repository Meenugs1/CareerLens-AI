import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

print("\n===== SKILL NORMALIZATION =====")


# ------------------------------------------------
# STEP 1: SPLIT SKILLS
# ------------------------------------------------

df["skill_list"] = df["tagsandskills"].apply(
    lambda x: [
        skill.strip()
        for skill in str(x).split(",")
        if skill.strip()
        and skill.strip().lower() != "not specified"
    ]
)


# ------------------------------------------------
# STEP 2: BASIC NORMALIZATION
# ------------------------------------------------

df["normalized_skill_list"] = df["skill_list"].apply(
    lambda skills: [
        skill.lower().strip()
        for skill in skills
    ]
)


# ------------------------------------------------
# STEP 3: HIGH-CONFIDENCE ALIASES
# ------------------------------------------------

skill_aliases = {

    # Programming
    "python programming": "python",
    "python scripting": "python",

    "java programming": "java",

    "java script": "javascript",
    "java-script": "javascript",

    "c sharp": "c#",
    "c-sharp": "c#",

    "c plus plus": "c++",
    "c-plus-plus": "c++",

    # SQL
    "structured query language": "sql",
    "sql server": "sql",

    # Power BI
    "powerbi": "power bi",
    "power bi desktop": "power bi",

    # Excel
    "ms excel": "excel",
    "microsoft excel": "excel",

    # AWS
    "amazon web services": "aws",

    # Machine Learning
    "machine learning": "machine learning",
    "machinelearning": "machine learning",

    # Artificial Intelligence
    "artificial intelligence": "artificial intelligence",
    "artificial intelligence ai": "artificial intelligence",

    # Databases
    "mysql database": "mysql",
    "microsoft sql server": "sql server",

    # Web
    "html5": "html",
    "css3": "css",

    # DevOps
    "continuous integration/continuous deployment": "ci/cd",
    "continuous integration and continuous deployment": "ci/cd",

}


# ------------------------------------------------
# STEP 4: APPLY ALIASES
# ------------------------------------------------

def normalize_skill(skill):

    skill = skill.lower().strip()

    return skill_aliases.get(skill, skill)


df["final_skill_list"] = df["normalized_skill_list"].apply(
    lambda skills: [
        normalize_skill(skill)
        for skill in skills
    ]
)


# ------------------------------------------------
# STEP 5: FLATTEN
# ------------------------------------------------

all_skills = []

for skills in df["final_skill_list"]:
    all_skills.extend(skills)


# ------------------------------------------------
# STEP 6: COUNT
# ------------------------------------------------

skill_counts = pd.Series(all_skills).value_counts()


print("\n===== FINAL UNIQUE SKILLS =====")
print("Unique skills:", len(skill_counts))


print("\n===== TOP 100 SKILLS =====")
print(skill_counts.head(100))


# ------------------------------------------------
# STEP 7: SAVE SKILL COUNTS
# ------------------------------------------------

skill_output = pd.DataFrame({
    "skill": skill_counts.index,
    "job_count": skill_counts.values
})

skill_output.to_csv(
    "data/processed/skill_counts.csv",
    index=False
)


print("\nSkill counts saved to:")
print("data/processed/skill_counts.csv")