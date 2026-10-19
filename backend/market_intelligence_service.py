"""Dataset-derived market intelligence calculations."""

import re
from collections import Counter

import pandas as pd

from backend.recommendation_service import _load_dataset


EXPERIENCE_BUCKETS = (
    ("0-1 years", 0, 1),
    ("2-3 years", 2, 3),
    ("4-5 years", 4, 5),
    ("6-8 years", 6, 8),
    ("9+ years", 9, None),
)


def _valid_dimension(value):
    if value is None or pd.isna(value):
        return None

    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() in {"nan", "none", "not specified", "unknown"}:
        return None

    return cleaned


def _skill_set(value):
    if value is None or pd.isna(value):
        return set()

    skills = set()
    for skill in str(value).split(","):
        cleaned = skill.strip().lower()
        if cleaned and cleaned not in {"nan", "none", "not specified"}:
            skills.add(cleaned)

    return skills


def _role_jobs(df, role):
    if not role:
        return df

    role_lower = role.strip().lower()
    if not role_lower:
        return df

    return df[
        df["title"]
        .astype(str)
        .str.lower()
        .str.contains(re.escape(role_lower), na=False)
    ].copy()


def _percentage(count, total):
    if not total:
        return 0.0
    return round(count / total * 100, 2)


def _top_locations(df):
    counts = Counter(
        location
        for location in (_valid_dimension(value) for value in df["location"])
        if location is not None
    )
    total = len(df)

    return [
        {
            "location": location,
            "job_count": count,
            "percentage_of_jobs": _percentage(count, total),
        }
        for location, count in counts.most_common(10)
    ]


def _top_companies(df):
    counts = Counter(
        company
        for company in (_valid_dimension(value) for value in df["companyname"])
        if company is not None
    )

    return [
        {"company": company, "job_count": count}
        for company, count in counts.most_common(10)
    ]


def _top_skills(df):
    counts = Counter()
    for tags in df["tagsandskills"]:
        counts.update(_skill_set(tags))

    total = len(df)
    return [
        {
            "skill": skill,
            "job_count": count,
            "percentage_of_jobs": _percentage(count, total),
        }
        for skill, count in counts.most_common(15)
    ]


def _experience_distribution(df):
    minimum_experience = pd.to_numeric(
        df["minimumexperience"], errors="coerce"
    )
    counts = []
    assigned = pd.Series(False, index=df.index)

    for label, lower_bound, upper_bound in EXPERIENCE_BUCKETS:
        mask = minimum_experience.ge(lower_bound)
        if upper_bound is not None:
            mask &= minimum_experience.le(upper_bound)
        mask &= ~assigned
        count = int(mask.sum())
        assigned |= mask
        counts.append({
            "experience_group": label,
            "job_count": count,
            "percentage_of_jobs": _percentage(count, len(df)),
        })

    unspecified_count = int((~assigned & minimum_experience.isna()).sum())
    if unspecified_count:
        counts.append({
            "experience_group": "Not Specified",
            "job_count": unspecified_count,
            "percentage_of_jobs": _percentage(unspecified_count, len(df)),
        })

    outside_bucket_count = int((~assigned & minimum_experience.notna()).sum())
    if outside_bucket_count:
        counts.append({
            "experience_group": "Other Numeric Range",
            "job_count": outside_bucket_count,
            "percentage_of_jobs": _percentage(outside_bucket_count, len(df)),
        })

    return counts


def _salary_intelligence(df):
    salary_mask = (
        df["currency"].astype(str).str.upper().eq("INR")
        & df["salary_available"].fillna(False).astype(bool)
        & df["average_salary"].notna()
    )
    salary_jobs = df.loc[salary_mask]

    if salary_jobs.empty:
        unavailable = "Insufficient data available"
        return {
            "average_salary": unavailable,
            "median_salary": unavailable,
            "minimum_salary": unavailable,
            "maximum_salary": unavailable,
            "salary_job_count": 0,
            "salary_range_distribution": [],
        }

    salary_values = salary_jobs["average_salary"]
    range_counts = salary_jobs["salary_range"].value_counts()

    return {
        "average_salary": round(float(salary_values.mean()), 2),
        "median_salary": round(float(salary_values.median()), 2),
        "minimum_salary": round(float(salary_values.min()), 2),
        "maximum_salary": round(float(salary_values.max()), 2),
        "salary_job_count": int(len(salary_jobs)),
        "salary_range_distribution": [
            {
                "salary_range": str(salary_range),
                "job_count": int(count),
                "percentage_of_salary_jobs": _percentage(
                    int(count), len(salary_jobs)
                ),
            }
            for salary_range, count in range_counts.items()
        ],
    }


def _top_roles(df):
    counts = Counter(
        title
        for title in (_valid_dimension(value) for value in df["title"])
        if title is not None
    )
    return [
        {"job_title": title, "job_count": count}
        for title, count in counts.most_common(15)
    ]


def _related_roles(df, role):
    if not role or not role.strip():
        return []

    role_tokens = set(re.findall(r"[a-z0-9]+", role.lower()))
    title_counts = Counter(
        title
        for title in (_valid_dimension(value) for value in df["title"])
        if title is not None
    )
    target = role.strip().lower()
    related = []

    for title, count in title_counts.items():
        title_tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
        overlap = len(role_tokens & title_tokens)
        if overlap and title.lower() != target:
            related.append((overlap, count, title))

    related.sort(key=lambda item: (-item[0], -item[1], item[2].lower()))
    return [
        {"job_title": title, "job_count": count}
        for _, count, title in related[:15]
    ]


def _overview(df):
    total_jobs = len(df)
    salary_jobs = int(df["salary_available"].fillna(False).astype(bool).sum())
    companies = {
        company
        for company in (_valid_dimension(value) for value in df["companyname"])
        if company is not None
    }
    locations = {
        location
        for location in (_valid_dimension(value) for value in df["location"])
        if location is not None
    }
    titles = {
        title
        for title in (_valid_dimension(value) for value in df["title"])
        if title is not None
    }

    return {
        "total_jobs": total_jobs,
        "jobs_with_salary": salary_jobs,
        "jobs_without_salary": total_jobs - salary_jobs,
        "unique_companies": len(companies),
        "unique_locations": len(locations),
        "unique_job_titles": len(titles),
    }


def get_market_intelligence(role=None):
    df = _load_dataset()
    role_jobs = _role_jobs(df, role)

    return {
        "success": True,
        "role": role.strip() if role and role.strip() else None,
        "overview": _overview(role_jobs),
        "top_locations": _top_locations(role_jobs),
        "top_companies": _top_companies(role_jobs),
        "top_skills": _top_skills(role_jobs),
        "experience_distribution": _experience_distribution(role_jobs),
        "salary_intelligence": _salary_intelligence(role_jobs),
        "top_roles": _top_roles(role_jobs),
        "related_roles": _related_roles(df, role),
    }
