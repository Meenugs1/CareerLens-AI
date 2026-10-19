import pandas as pd

# Load normalized skill counts
file_path = "data/processed/skill_counts.csv"
df = pd.read_csv(file_path)

print("\n===== SKILL CLEANING =====")

print("Skills before cleaning:", len(df))


# ------------------------------------------------
# SKILLS THAT ARE NOT ACTUAL SKILLS
# ------------------------------------------------

non_skills = {
    "senior",
    "junior",
    "fresher",
    "experienced",
    "experience",
    "developer",
    "engineer",
    "manager",
    "lead",
    "executive",
    "intern",
    "internship",
    "job",
    "jobs",
    "work",
    "working",
    "employee",
    "candidate",
    "team player",
    "good communication",
    "hardworking",
    "responsible",
    "motivated",
    "dedicated",
    "quick learner",
    "positive attitude",
}


# ------------------------------------------------
# REMOVE NON-SKILLS
# ------------------------------------------------

df["skill"] = df["skill"].str.strip().str.lower()

cleaned_df = df[
    ~df["skill"].isin(non_skills)
].copy()


# ------------------------------------------------
# SORT BY JOB COUNT
# ------------------------------------------------

cleaned_df = cleaned_df.sort_values(
    "job_count",
    ascending=False
)


# ------------------------------------------------
# SAVE
# ------------------------------------------------

output_file = "data/processed/skill_counts_cleaned.csv"

cleaned_df.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------
# REPORT
# ------------------------------------------------

print("Skills after cleaning:", len(cleaned_df))

print(
    "Skills removed:",
    len(df) - len(cleaned_df)
)


print("\n===== TOP 100 CLEANED SKILLS =====")

print(
    cleaned_df.head(100).to_string(index=False)
)


print("\nSaved to:")
print(output_file)