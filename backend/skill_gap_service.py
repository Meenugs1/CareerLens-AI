"""Dataset-derived target-role skill gap analysis."""

import re
from collections import Counter

import pandas as pd

from backend.recommendation_service import _load_dataset, extract_skills, normalize_skill


_role_skill_cache = {}


def _role_jobs(df, role):
    role_lower = role.strip().lower()
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


def _normalize_current_skills(skills):
    normalized = set()
    for skill in skills or []:
        value = normalize_skill(skill)
        if value:
            normalized.add(value)
    return normalized


def _build_role_analysis(df, role):
    cache_key = (id(df), role.strip().lower())
    if cache_key in _role_skill_cache:
        return _role_skill_cache[cache_key]

    role_jobs = _role_jobs(df, role)
    job_skill_sets = [
        set() if pd.isna(value) else extract_skills(value)
        for value in role_jobs["tagsandskills"]
    ]
    skill_counts = Counter()
    for skill_set in job_skill_sets:
        skill_counts.update(skill_set)

    analysis = {
        "role_jobs": role_jobs,
        "job_skill_sets": job_skill_sets,
        "skill_counts": skill_counts,
    }
    _role_skill_cache[cache_key] = analysis
    return analysis


def _priority_thresholds(skill_counts, total_jobs):
    if total_jobs < 5 or not skill_counts:
        return None

    shares = pd.Series([
        count / total_jobs * 100 for count in skill_counts.values()
    ])
    return {
        "high": float(shares.quantile(0.75)),
        "medium": float(shares.quantile(0.50)),
    }


def _priority(percentage, thresholds):
    if thresholds is None:
        return "Insufficient data available"
    if percentage >= thresholds["high"]:
        return "High"
    if percentage >= thresholds["medium"]:
        return "Medium"
    return "Low"


def _skill_items(skills, counts, total_jobs, thresholds):
    return [
        {
            "skill": skill,
            "job_count": int(counts[skill]),
            "percentage": _percentage(counts[skill], total_jobs),
            "priority": _priority(
                _percentage(counts[skill], total_jobs), thresholds
            ),
            "evidence": f"Found in {counts[skill]} of {total_jobs} analyzed jobs",
        }
        for skill in sorted(skills, key=lambda item: (-counts[item], item))
    ]


def analyze_skill_gap(role, skills):
    target_role = str(role or "").strip()
    current_skills = _normalize_current_skills(skills)

    if not target_role:
        return {
            "success": True,
            "role": target_role,
            "current_skills": sorted(current_skills),
            "matching_jobs": 0,
            "skill_coverage": 0.0,
            "skill_coverage_definition": "Percentage of target-role jobs containing at least two of the selected skills.",
            "matched_skills": [],
            "missing_skills": [],
            "summary": {"target_role_jobs": 0, "analyzed_jobs": 0},
            "priority_method": "Insufficient data available",
        }

    df = _load_dataset()
    analysis = _build_role_analysis(df, target_role)
    role_jobs = analysis["role_jobs"]
    job_skill_sets = analysis["job_skill_sets"]
    skill_counts = analysis["skill_counts"]
    total_jobs = len(role_jobs)

    thresholds = _priority_thresholds(skill_counts, total_jobs)
    matched_skills = set(skill_counts) & current_skills
    missing_skills = set(skill_counts) - current_skills
    matching_jobs = sum(
        len(current_skills & job_skills) >= 2 for job_skills in job_skill_sets
    )

    coverage = _percentage(matching_jobs, total_jobs)
    priority_method = (
        "High is at or above the role skill-demand 75th percentile; "
        "Medium is at or above the median; Low is below the median."
        if thresholds is not None
        else "Insufficient data available"
    )

    return {
        "success": True,
        "role": target_role,
        "current_skills": sorted(current_skills),
        "matching_jobs": matching_jobs,
        "skill_coverage": coverage,
        "skill_coverage_definition": "Percentage of target-role jobs containing at least two of the selected skills.",
        "matched_skills": _skill_items(
            matched_skills, skill_counts, total_jobs, thresholds
        ),
        "missing_skills": _skill_items(
            missing_skills, skill_counts, total_jobs, thresholds
        ),
        "summary": {
            "target_role_jobs": total_jobs,
            "analyzed_jobs": total_jobs,
            "jobs_matching_current_skills": matching_jobs,
            "matched_skill_count": len(matched_skills),
            "missing_skill_count": len(missing_skills),
        },
        "priority_method": priority_method,
    }
