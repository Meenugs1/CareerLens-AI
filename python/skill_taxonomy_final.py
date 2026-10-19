import pandas as pd

# ============================================================
# SKILL TAXONOMY FINAL CLEANUP
# ============================================================

input_file = "data/processed/skill_taxonomy_v2.csv"
output_file = "data/processed/skill_taxonomy_final.csv"

df = pd.read_csv(input_file)

print("\n================================================")
print("          SKILL TAXONOMY FINAL CLEANUP")
print("================================================")


# ============================================================
# FINAL CATEGORY CORRECTIONS
# ============================================================

corrections = {

    # ---------------- DATA ENGINEERING ----------------
    "pyspark": "Data Engineering",
    "hive": "Data Engineering",
    "etl": "Data Engineering",
    "data warehousing": "Data Engineering",
    "data pipeline": "Data Engineering",
    "data pipelines": "Data Engineering",

    # ---------------- DATABASES ----------------
    "dbms": "Databases",

    # ---------------- WEB / SOFTWARE ----------------
    "backend": "Software Engineering",
    "full stack": "Web Development",

    # ---------------- SOFTWARE TESTING ----------------
    "manual testing": "Software Testing",
    "quality assurance": "Software Testing",
    "quality control": "Software Testing",

    # ---------------- SOFTWARE ENGINEERING ----------------
    ".net core": "Software Engineering",
    "software": "Software Engineering",
    "software development life cycle": "Software Engineering",
    "sdlc": "Software Engineering",
    "application design": "Software Engineering",

    # ---------------- VERSION CONTROL ----------------
    "version control": "Version Control",

    # ---------------- ENTERPRISE SOFTWARE ----------------
    "crm": "Enterprise Software",
    "sap abap": "Enterprise Software",
    "sap s hana": "Enterprise Software",
    "sap sd": "Enterprise Software",

    # ---------------- PRODUCT MANAGEMENT ----------------
    "product management": "Product Management",

    # ---------------- PROJECT MANAGEMENT ----------------
    "program management": "Project Management",
    "change management": "Project Management",
    "process improvement": "Project Management",
    "continuous improvement": "Project Management",

    # ---------------- BUSINESS / ANALYSIS ----------------
    "research": "Business & Analysis",
    "forecasting": "Business & Analysis",
    "planning": "Business & Analysis",
    "analytics": "Data Analytics",

    # ---------------- FINANCE ----------------
    "budgeting": "Finance & Accounting",
    "taxation": "Finance & Accounting",
    "billing": "Finance & Accounting",
    "reconciliation": "Finance & Accounting",
    "financial reporting": "Finance & Accounting",
    "gst": "Finance & Accounting",

    # ---------------- HR ----------------
    "it recruitment": "Human Resources",

    # ---------------- SALES ----------------
    "insurance sales": "Sales",
    "retail sales": "Sales",
    "corporate sales": "Sales",
    "client acquisition": "Sales",
    "cross selling": "Sales",

    # ---------------- OPERATIONS ----------------
    "vendor management": "Operations",
    "inventory management": "Operations",
    "logistics": "Operations",
    "purchase": "Operations",
    "sourcing": "Operations",
    "maintenance": "Operations",

    # ---------------- SOFT SKILLS ----------------
    "negotiation": "Soft Skills",
    "leadership": "Soft Skills",
    "technical leadership": "Soft Skills",
    "problem solving": "Soft Skills",
    "relationship building": "Soft Skills",

    # ---------------- MARKETING ----------------
    "seo": "Marketing",
    "social media": "Marketing",

    # ---------------- IT INFRASTRUCTURE ----------------
    "monitoring": "IT Infrastructure",

    # ---------------- CLOUD ----------------
    "ms office": "Productivity Tools",
    "microsoft": "Productivity Tools",

    # ---------------- HEALTHCARE ----------------
    "healthcare": "Healthcare",

    # ---------------- DOMAIN ----------------
    "insurance": "Insurance",
    "financial services": "Finance & Accounting",
    "retail": "Retail",
    "hospitality": "Hospitality",
}


# ============================================================
# APPLY CORRECTIONS
# ============================================================

df["category"] = df["skill"].map(corrections).fillna(df["category"])


# ============================================================
# CREATE CATEGORY SUMMARY
# ============================================================

print("\n================================================")
print("FINAL CATEGORY SUMMARY")
print("================================================")

category_summary = (
    df.groupby("category")["job_count"]
    .sum()
    .sort_values(ascending=False)
)

print(category_summary.to_string())


# ============================================================
# COVERAGE BY UNIQUE SKILLS
# ============================================================

classified = df[df["category"] != "Other"]
unclassified = df[df["category"] == "Other"]

print("\n================================================")
print("FINAL TAXONOMY COVERAGE")
print("================================================")

print("Total unique skills:", len(df))
print("Classified skills:", len(classified))
print("Unclassified skills:", len(unclassified))

coverage = len(classified) / len(df) * 100

print("Unique skill coverage:", round(coverage, 2), "%")


# ============================================================
# JOB POSTING COVERAGE
# ============================================================

total_skill_occurrences = df["job_count"].sum()

classified_occurrences = classified["job_count"].sum()

job_coverage = (
    classified_occurrences
    / total_skill_occurrences
    * 100
)

print(
    "Skill occurrence coverage:",
    round(job_coverage, 2),
    "%"
)


# ============================================================
# TOP REMAINING UNCLASSIFIED SKILLS
# ============================================================

print("\n================================================")
print("TOP REMAINING UNCLASSIFIED SKILLS")
print("================================================")

print(
    unclassified
    .sort_values("job_count", ascending=False)
    .head(50)
    .to_string(index=False)
)


# ============================================================
# SAVE FINAL TAXONOMY
# ============================================================

df.to_csv(
    output_file,
    index=False
)

print("\n================================================")
print("FINAL TAXONOMY COMPLETE")
print("================================================")

print("Saved to:")
print(output_file)