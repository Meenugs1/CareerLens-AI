import pandas as pd

# ============================================================
# SKILL CATEGORIES V2
# ============================================================

input_file = "data/processed/skill_counts_v2.csv"
output_file = "data/processed/skill_taxonomy_v2.csv"

df = pd.read_csv(input_file)

print("\n================================================")
print("             SKILL CATEGORIES V2")
print("================================================")


# ============================================================
# 1. SKILL CATEGORY MAP
# ============================================================

category_map = {

    # --------------------------------------------------------
    # PROGRAMMING
    # --------------------------------------------------------

    "python": "Programming",
    "java": "Programming",
    "javascript": "Programming",
    "c#": "Programming",
    "c++": "Programming",
    "r": "Programming",
    "scala": "Programming",
    "kotlin": "Programming",
    "php": "Programming",
    "ruby": "Programming",
    "go": "Programming",
    "coding": "Programming",


    # --------------------------------------------------------
    # WEB DEVELOPMENT
    # --------------------------------------------------------

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
    "web technologies": "Web Development",


    # --------------------------------------------------------
    # DATA ANALYTICS
    # --------------------------------------------------------

    "data analysis": "Data Analytics",
    "data analytics": "Data Analytics",
    "data visualization": "Data Analytics",
    "data modeling": "Data Analytics",
    "data mining": "Data Analytics",
    "data quality": "Data Analytics",
    "data management": "Data Analytics",
    "analytical": "Data Analytics",
    "statistics": "Data Analytics",
    "sas": "Data Analytics",
    "sas programming": "Data Analytics",
    "advanced excel": "Data Analytics",
    "macros": "Data Analytics",
    "excel": "Data Analytics",
    "etl": "Data Engineering",
    "data warehousing": "Data Engineering",


    # --------------------------------------------------------
    # BUSINESS INTELLIGENCE
    # --------------------------------------------------------

    "power bi": "Business Intelligence",
    "tableau": "Business Intelligence",
    "qlikview": "Business Intelligence",
    "looker": "Business Intelligence",
    "dashboard": "Business Intelligence",
    "dashboards": "Business Intelligence",


    # --------------------------------------------------------
    # DATABASES
    # --------------------------------------------------------

    "sql": "Databases",
    "mysql": "Databases",
    "oracle": "Databases",
    "postgresql": "Databases",
    "mongodb": "Databases",
    "sql server": "Databases",
    "database": "Databases",
    "database management": "Databases",


    # --------------------------------------------------------
    # AI / MACHINE LEARNING
    # --------------------------------------------------------

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
    "algorithms": "AI / Machine Learning",


    # --------------------------------------------------------
    # CLOUD
    # --------------------------------------------------------

    "aws": "Cloud",
    "microsoft azure": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",
    "google cloud": "Cloud",
    "cloud computing": "Cloud",
    "cloud": "Cloud",


    # --------------------------------------------------------
    # DEVOPS
    # --------------------------------------------------------

    "devops": "DevOps",
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "ci/cd": "DevOps",
    "jenkins": "DevOps",
    "terraform": "DevOps",
    "ansible": "DevOps",
    "linux": "DevOps",


    # --------------------------------------------------------
    # VERSION CONTROL
    # --------------------------------------------------------

    "git": "Version Control",
    "github": "Version Control",
    "gitlab": "Version Control",
    "bitbucket": "Version Control",


    # --------------------------------------------------------
    # SOFTWARE ENGINEERING
    # --------------------------------------------------------

    "software development": "Software Engineering",
    "application development": "Software Engineering",
    "microservices": "Software Engineering",
    "rest": "Software Engineering",
    "web services": "Software Engineering",
    "spring": "Software Engineering",
    "spring boot": "Software Engineering",
    "hibernate": "Software Engineering",
    ".net": "Software Engineering",
    "api": "Software Engineering",
    "application design": "Software Engineering",
    "architecture": "Software Engineering",
    "performance tuning": "Software Engineering",
    "debugging": "Software Engineering",
    "troubleshooting": "Software Engineering",
    "development methodologies": "Software Engineering",


    # --------------------------------------------------------
    # SOFTWARE TESTING
    # --------------------------------------------------------

    "software testing": "Software Testing",
    "automation testing": "Software Testing",
    "selenium": "Software Testing",
    "test cases": "Software Testing",
    "testing": "Software Testing",


    # --------------------------------------------------------
    # DATA ENGINEERING
    # --------------------------------------------------------

    "data engineering": "Data Engineering",
    "data pipeline": "Data Engineering",
    "data pipelines": "Data Engineering",
    "data integration": "Data Engineering",
    "big data": "Data Engineering",
    "hadoop": "Data Engineering",
    "spark": "Data Engineering",
    "apache spark": "Data Engineering",
    "kafka": "Data Engineering",


    # --------------------------------------------------------
    # PROJECT MANAGEMENT
    # --------------------------------------------------------

    "project management": "Project Management",
    "agile": "Project Management",
    "scrum": "Project Management",
    "jira": "Project Management",
    "kanban": "Project Management",


    # --------------------------------------------------------
    # BUSINESS & ANALYSIS
    # --------------------------------------------------------

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
    "documentation": "Business & Analysis",
    "root cause analysis": "Business & Analysis",


    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    "sales": "Sales",
    "business development": "Sales",
    "lead generation": "Sales",
    "b2b sales": "Sales",
    "channel sales": "Sales",
    "field sales": "Sales",
    "telesales": "Sales",
    "inside sales": "Sales",
    "direct sales": "Sales",
    "b2c sales": "Sales",
    "cold calling": "Sales",
    "sales management": "Sales",
    "sales and marketing": "Sales",


    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    "marketing": "Marketing",
    "digital marketing": "Marketing",
    "market research": "Marketing",
    "content writing": "Marketing",


    # --------------------------------------------------------
    # FINANCE & ACCOUNTING
    # --------------------------------------------------------

    "accounting": "Finance & Accounting",
    "finance": "Finance & Accounting",
    "accounts payable": "Finance & Accounting",
    "accounts receivable": "Finance & Accounting",
    "risk management": "Finance & Accounting",
    "financial analysis": "Finance & Accounting",
    "banking": "Finance & Accounting",
    "tds": "Finance & Accounting",
    "auditing": "Finance & Accounting",


    # --------------------------------------------------------
    # HUMAN RESOURCES
    # --------------------------------------------------------

    "recruitment": "Human Resources",
    "hiring": "Human Resources",
    "screening": "Human Resources",
    "talent acquisition": "Human Resources",
    "hr generalist activities": "Human Resources",


    # --------------------------------------------------------
    # CUSTOMER SERVICE
    # --------------------------------------------------------

    "customer service": "Customer Service",
    "customer support": "Customer Service",
    "customer care": "Customer Service",
    "voice process": "Customer Service",
    "international voice process": "Customer Service",
    "bpo": "Customer Service",
    "international bpo": "Customer Service",
    "non voice process": "Customer Service",
    "international call center": "Customer Service",
    "technical support": "Customer Service",


    # --------------------------------------------------------
    # OPERATIONS
    # --------------------------------------------------------

    "operations": "Operations",
    "procurement": "Operations",
    "supply chain": "Operations",
    "erp": "Operations",
    "operations management": "Operations",
    "production": "Operations",
    "process": "Operations",
    "administration": "Operations",


    # --------------------------------------------------------
    # ENTERPRISE SOFTWARE
    # --------------------------------------------------------

    "sap": "Enterprise Software",
    "sap hana": "Enterprise Software",
    "salesforce": "Enterprise Software",
    "servicenow": "Enterprise Software",


    # --------------------------------------------------------
    # ENGINEERING & DESIGN
    # --------------------------------------------------------

    "autocad": "Engineering & Design",
    "design": "Engineering & Design",
    "engineering": "Engineering & Design",


    # --------------------------------------------------------
    # IT INFRASTRUCTURE
    # --------------------------------------------------------

    "networking": "IT Infrastructure",
    "technical infrastructure": "IT Infrastructure",


    # --------------------------------------------------------
    # COMPLIANCE
    # --------------------------------------------------------

    "compliance": "Compliance",


    # --------------------------------------------------------
    # COMPUTER SCIENCE
    # --------------------------------------------------------

    "computer science": "Computer Science",


    # --------------------------------------------------------
    # SOFT SKILLS
    # --------------------------------------------------------

    "communication skills": "Soft Skills",
    "english": "Soft Skills",
    "presentation skills": "Soft Skills",
    "team management": "Soft Skills",
    "stakeholder management": "Soft Skills",
    "interpersonal skills": "Soft Skills",
    "team handling": "Soft Skills",
    "relationship": "Soft Skills",
    "relationship management": "Soft Skills",


    # --------------------------------------------------------
    # TRAINING / EDUCATION
    # --------------------------------------------------------

    "training": "Training & Education",
    "teaching": "Training & Education",
}


# ============================================================
# 2. ASSIGN CATEGORY
# ============================================================

df["category"] = df["skill"].map(category_map)

df["category"] = df["category"].fillna("Other")


# ============================================================
# 3. CATEGORY SUMMARY
# ============================================================

print("\n================================================")
print("CATEGORY SUMMARY")
print("================================================")

category_summary = (
    df.groupby("category")["job_count"]
    .sum()
    .sort_values(ascending=False)
)

print(category_summary.to_string())


# ============================================================
# 4. COVERAGE
# ============================================================

classified = df[df["category"] != "Other"]
unclassified = df[df["category"] == "Other"]

print("\n================================================")
print("TAXONOMY COVERAGE")
print("================================================")

print("Total unique skills:", len(df))
print("Classified skills:", len(classified))
print("Unclassified skills:", len(unclassified))

coverage = len(classified) / len(df) * 100

print("Unique skill coverage:", round(coverage, 2), "%")


# ============================================================
# 5. TOP UNCLASSIFIED SKILLS
# ============================================================

print("\n================================================")
print("TOP UNCLASSIFIED SKILLS")
print("================================================")

print(
    unclassified
    .head(100)
    .to_string(index=False)
)


# ============================================================
# 6. TOP SKILLS BY CATEGORY
# ============================================================

print("\n================================================")
print("TOP SKILLS BY CATEGORY")
print("================================================")

for category in sorted(df["category"].unique()):

    if category == "Other":
        continue

    category_df = (
        df[df["category"] == category]
        .sort_values("job_count", ascending=False)
        .head(10)
    )

    print(f"\n--- {category} ---")

    print(
        category_df[
            ["skill", "job_count"]
        ].to_string(index=False)
    )


# ============================================================
# 7. SAVE
# ============================================================

df.to_csv(
    output_file,
    index=False
)

print("\n================================================")
print("SKILL TAXONOMY V2 COMPLETE")
print("================================================")

print("Saved to:")
print(output_file)