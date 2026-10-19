import pandas as pd

# ============================================================
# SKILL CATEGORIES V1
# ============================================================

input_file = "data/processed/skill_counts_v2.csv"
output_file = "data/processed/skill_taxonomy_final.csv"

df = pd.read_csv(input_file)

print("\n================================================")
print("             SKILL CATEGORIES V1")
print("================================================")

# ------------------------------------------------------------
# STEP 1: Define skill categories
# ------------------------------------------------------------

category_map = {

    # ---------------- PROGRAMMING ----------------
    "python": "Programming",
    "java": "Programming",
    "javascript": "Programming",
    "c#": "Programming",
    "c++": "Programming",
    "coding": "Programming",
    "r": "Programming",
    "scala": "Programming",
    "kotlin": "Programming",
    "php": "Programming",
    "ruby": "Programming",
    "go": "Programming",

    # ---------------- WEB DEVELOPMENT ----------------
    "html": "Web Development",
    "css": "Web Development",
    "react": "Web Development",
    "angular": "Web Development",
    "vue.js": "Web Development",
    "node.js": "Web Development",
    "bootstrap": "Web Development",
    "jquery": "Web Development",
    "typescript": "Web Development",
    "tailwind css": "Web Development",
    "nextjs": "Web Development",
    "frontend development": "Web Development",
    "front end": "Web Development",
    "web development": "Web Development",

    # ---------------- DATA ANALYTICS ----------------
    "data analysis": "Data Analytics",
    "data analytics": "Data Analytics",
    "data visualization": "Data Analytics",
    "data modeling": "Data Analytics",
    "data mining": "Data Analytics",
    "data quality": "Data Analytics",
    "data management": "Data Analytics",
    "business intelligence": "Data Analytics",
    "bi": "Data Analytics",
    "analytical": "Data Analytics",
    "statistics": "Data Analytics",
    "sas": "Data Analytics",
    "sas programming": "Data Analytics",
    "advanced excel": "Data Analytics",
    "macros": "Data Analytics",

    # ---------------- BUSINESS INTELLIGENCE ----------------
    "power bi": "Business Intelligence",
    "tableau": "Business Intelligence",
    "qlikview": "Business Intelligence",
    "looker": "Business Intelligence",
    "dashboard": "Business Intelligence",
    "dashboards": "Business Intelligence",

    # ---------------- DATABASES ----------------
    "sql": "Databases",
    "mysql": "Databases",
    "oracle": "Databases",
    "postgresql": "Databases",
    "mongodb": "Databases",
    "sql server": "Databases",
    "database": "Databases",
    "database management": "Databases",
    "data warehousing": "Databases",

    # ---------------- AI / MACHINE LEARNING ----------------
    "machine learning": "AI / Machine Learning",
    "artificial intelligence": "AI / Machine Learning",
    "deep learning": "AI / Machine Learning",
    "tensorflow": "AI / Machine Learning",
    "pytorch": "AI / Machine Learning",
    "natural language processing": "AI / Machine Learning",
    "nlp": "AI / Machine Learning",
    "computer vision": "AI / Machine Learning",
    "generative ai": "AI / Machine Learning",
    "data science": "AI / Machine Learning",
    "aiml": "AI / Machine Learning",
    "chatbot": "AI / Machine Learning",
    "image processing": "AI / Machine Learning",

    # ---------------- CLOUD ----------------
    "aws": "Cloud",
    "microsoft azure": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",
    "google cloud": "Cloud",
    "cloud computing": "Cloud",

    # ---------------- DEVOPS ----------------
    "devops": "DevOps",
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "ci/cd": "DevOps",
    "jenkins": "DevOps",
    "terraform": "DevOps",
    "ansible": "DevOps",
    "linux": "DevOps",

    # ---------------- VERSION CONTROL ----------------
    "git": "Version Control",
    "github": "Version Control",
    "gitlab": "Version Control",
    "bitbucket": "Version Control",

    # ---------------- SOFTWARE ENGINEERING ----------------
    "software development": "Software Engineering",
    "application development": "Software Engineering",
    "software testing": "Software Engineering",
    "automation testing": "Software Engineering",
    "debugging": "Software Engineering",
    "algorithms": "Software Engineering",
    "microservices": "Software Engineering",
    "rest": "Software Engineering",
    "web services": "Software Engineering",
    "spring": "Software Engineering",
    "spring boot": "Software Engineering",
    "hibernate": "Software Engineering",
    ".net": "Software Engineering",
    "api": "Software Engineering",

    # ---------------- PROJECT MANAGEMENT ----------------
    "project management": "Project Management",
    "agile": "Project Management",
    "scrum": "Project Management",
    "jira": "Project Management",
    "kanban": "Project Management",

    # ---------------- BUSINESS / ANALYSIS ----------------
    "business analysis": "Business & Analysis",
    "business analytics": "Business & Analysis",
    "requirement gathering": "Business & Analysis",
    "gap analysis": "Business & Analysis",
    "business process modeling": "Business & Analysis",
    "business requirement analysis": "Business & Analysis",
    "use cases": "Business & Analysis",
    "user stories": "Business & Analysis",
    "brd": "Business & Analysis",
    "frd": "Business & Analysis",

    # ---------------- SALES ----------------
    "sales": "Sales",
    "business development": "Sales",
    "lead generation": "Sales",
    "b2b sales": "Sales",
    "channel sales": "Sales",
    "field sales": "Sales",
    "telesales": "Sales",

    # ---------------- MARKETING ----------------
    "marketing": "Marketing",
    "digital marketing": "Marketing",
    "market research": "Marketing",

    # ---------------- FINANCE / ACCOUNTING ----------------
    "accounting": "Finance & Accounting",
    "finance": "Finance & Accounting",
    "accounts payable": "Finance & Accounting",
    "accounts receivable": "Finance & Accounting",
    "risk management": "Finance & Accounting",

    # ---------------- HR ----------------
    "recruitment": "Human Resources",
    "hiring": "Human Resources",
    "screening": "Human Resources",
    "hr generalist activities": "Human Resources",

    # ---------------- CUSTOMER SERVICE ----------------
    "customer service": "Customer Service",
    "customer support": "Customer Service",
    "customer care": "Customer Service",
    "voice process": "Customer Service",
    "international voice process": "Customer Service",
    "bpo": "Customer Service",
    "international bpo": "Customer Service",

    # ---------------- COMMUNICATION ----------------
    "communication skills": "Soft Skills",
    "english": "Soft Skills",
    "presentation skills": "Soft Skills",
    "team management": "Soft Skills",
    "stakeholder management": "Soft Skills",

    # ---------------- OPERATIONS ----------------
    "operations": "Operations",
    "procurement": "Operations",
    "supply chain": "Operations",
    "erp": "Operations",

    # ---------------- GENERAL TECHNICAL ----------------
    "networking": "IT Infrastructure",
    "troubleshooting": "IT Infrastructure",
    "oracle": "Databases",
}


# ------------------------------------------------------------
# STEP 2: Assign category
# ------------------------------------------------------------

df["category"] = df["skill"].map(category_map)

# Skills not yet classified
df["category"] = df["category"].fillna("Other")

# ------------------------------------------------------------
# STEP 3: Display category summary
# ------------------------------------------------------------

print("\n================================================")
print("CATEGORY SUMMARY")
print("================================================")

category_summary = (
    df.groupby("category")["job_count"]
    .sum()
    .sort_values(ascending=False)
)

print(category_summary.to_string())

# ------------------------------------------------------------
# STEP 4: Display unclassified skills
# ------------------------------------------------------------

unclassified = df[df["category"] == "Other"]

print("\n================================================")
print("UNCLASSIFIED SKILLS")
print("================================================")

print("Number of unclassified skills:", len(unclassified))

print("\nTop 50 unclassified skills:")

print(
    unclassified
    .head(50)
    .to_string(index=False)
)

# ------------------------------------------------------------
# STEP 5: Save final taxonomy
# ------------------------------------------------------------

df.to_csv(
    output_file,
    index=False
)

print("\n================================================")
print("SKILL TAXONOMY SAVED")
print("================================================")

print("Output:")
print(output_file)