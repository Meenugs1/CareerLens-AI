import pandas as pd

# Load cleaned dataset
file_path = "data/processed/jobs_cleaned.xlsx"
df = pd.read_excel(file_path)

print("\n===== SKILLS INTELLIGENCE =====")

# ------------------------------------------------
# STEP 1: SPLIT SKILLS
# ------------------------------------------------

df["skill_list"] = df["tagsandskills"].apply(
    lambda x: [
        skill.strip()
        for skill in str(x).split(",")
        if skill.strip() and skill.strip().lower() != "not specified"
    ]
)


# ------------------------------------------------
# STEP 2: FLATTEN ALL SKILLS
# ------------------------------------------------

all_skills = []

for skill_list in df["skill_list"]:
    all_skills.extend(skill_list)


# ------------------------------------------------
# STEP 3: COUNT RAW SKILLS
# ------------------------------------------------

skill_counts = pd.Series(all_skills).value_counts()


print("\n===== RAW UNIQUE SKILLS =====")
print("Unique skill names:", len(skill_counts))


print("\n===== TOP 50 RAW SKILLS =====")
print(skill_counts.head(50))


# ------------------------------------------------
# STEP 4: NORMALIZE SKILL NAMES
# ------------------------------------------------

df["normalized_skill_list"] = df["skill_list"].apply(
    lambda skills: [
        skill.lower().strip()
        for skill in skills
    ]
)


# ------------------------------------------------
# STEP 5: FLATTEN NORMALIZED SKILLS
# ------------------------------------------------

normalized_skills = []

for skill_list in df["normalized_skill_list"]:
    normalized_skills.extend(skill_list)


# ------------------------------------------------
# STEP 6: COUNT NORMALIZED SKILLS
# ------------------------------------------------

normalized_skill_counts = pd.Series(
    normalized_skills
).value_counts()


print("\n===== NORMALIZED SKILLS =====")
print("Unique normalized skills:", len(normalized_skill_counts))


print("\n===== TOP 50 NORMALIZED SKILLS =====")
print(normalized_skill_counts.head(50))