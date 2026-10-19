"""Dataset-derived role matching for a user's normalized skills."""

from collections import Counter, defaultdict

from backend.career_path_service import (
    _build_title_profiles,
    _title_family,
)
from backend.career_simulator_service import _matching_jobs
from backend.recommendation_service import _load_dataset, normalize_skill
from backend.skill_gap_service import _percentage


MINIMUM_MATCHING_JOBS = 2
MINIMUM_ROLE_JOBS = 5
ROLE_RESULT_LIMIT = 10
MISSING_SKILL_LIMIT = 5
_matching_index_cache = {}


def _build_matching_index(df):
    cache_key = id(df)
    if cache_key in _matching_index_cache:
        return _matching_index_cache[cache_key]

    title_profiles = _build_title_profiles(df)
    role_profiles = defaultdict(
        lambda: {
            "title_counts": Counter(),
            "job_count": 0,
            "skill_counts": Counter(),
            "job_skill_sets": [],
        }
    )

    for title, title_profile in title_profiles.items():
        role_family = _title_family(title) or title.casefold()
        profile = role_profiles[role_family]
        profile["title_counts"][title] += title_profile["job_count"]
        profile["job_count"] += title_profile["job_count"]
        profile["skill_counts"].update(title_profile["skill_counts"])
        profile["job_skill_sets"].extend(title_profile["job_skill_sets"])

    index = {
        "role_profiles": dict(role_profiles),
        "all_job_skill_sets": [
            job_skill_set
            for profile in role_profiles.values()
            for job_skill_set in profile["job_skill_sets"]
        ],
        "observed_skills": {
            skill
            for profile in role_profiles.values()
            for skill in profile["skill_counts"]
        },
    }
    _matching_index_cache[cache_key] = index
    return index


def _normalize_skills(skills):
    normalized = set()
    for skill in skills or []:
        value = normalize_skill(skill)
        if value:
            normalized.add(value)
    return normalized


def _empty_result(skills, message, analyzed_jobs=0, unrecognized_skills=None):
    return {
        "success": False,
        "message": message,
        "skills": sorted(skills),
        "unrecognized_skills": sorted(unrecognized_skills or []),
        "analyzed_jobs": analyzed_jobs,
        "matching_jobs": 0,
        "roles": [],
    }


def _role_name(profile):
    return profile["title_counts"].most_common(1)[0][0]


def _role_match(profile, selected_skills):
    matching_jobs = _matching_jobs(profile["job_skill_sets"], selected_skills)
    missing_common_skills = [
        skill
        for skill, _ in sorted(
            profile["skill_counts"].items(),
            key=lambda item: (-item[1], item[0]),
        )
        if skill not in selected_skills
    ][:MISSING_SKILL_LIMIT]

    return {
        "role": _role_name(profile),
        "matching_jobs": int(matching_jobs),
        "role_total_jobs": int(profile["job_count"]),
        "match_percentage": _percentage(matching_jobs, profile["job_count"]),
        "matching_skills": sorted(
            selected_skills & set(profile["skill_counts"])
        ),
        "missing_common_skills": missing_common_skills,
        "evidence": (
            f"{matching_jobs} {_role_name(profile)} jobs in the dataset match "
            "at least two of your selected skills."
        ),
    }


def find_matching_roles(skills):
    requested_skills = _normalize_skills(skills)
    if not requested_skills:
        return _empty_result(
            requested_skills,
            "Select at least two recognized skills to analyze role matches.",
        )

    df = _load_dataset()
    index = _build_matching_index(df)
    recognized_skills = requested_skills & index["observed_skills"]
    unrecognized_skills = requested_skills - recognized_skills

    if len(recognized_skills) < 2:
        return _empty_result(
            recognized_skills,
            "Select at least two recognized skills to analyze role matches.",
            len(df),
            unrecognized_skills,
        )

    role_results = []
    total_matching_jobs = _matching_jobs(
        index["all_job_skill_sets"], recognized_skills
    )
    for profile in index["role_profiles"].values():
        if profile["job_count"] < MINIMUM_ROLE_JOBS:
            continue
        if len(recognized_skills & set(profile["skill_counts"])) < 2:
            continue
        role_result = _role_match(profile, recognized_skills)
        if (
            role_result["matching_jobs"] >= MINIMUM_MATCHING_JOBS
        ):
            role_results.append(role_result)

    role_results.sort(
        key=lambda result: (
            -result["matching_jobs"],
            -result["match_percentage"],
            -result["role_total_jobs"],
            result["role"].casefold(),
        )
    )
    role_results = role_results[:ROLE_RESULT_LIMIT]

    if not role_results:
        return _empty_result(
            recognized_skills,
            "No roles with sufficient dataset evidence matched your selected skills.",
            len(df),
            unrecognized_skills,
        ) | {"matching_jobs": total_matching_jobs}

    return {
        "success": True,
        "message": "These results show dataset-based skill matches, not guaranteed career outcomes.",
        "skills": sorted(recognized_skills),
        "unrecognized_skills": sorted(unrecognized_skills),
        "analyzed_jobs": int(len(df)),
        "matching_jobs": int(total_matching_jobs),
        "roles": role_results,
        "matching_rule": "A job matches when it contains at least two normalized selected skills.",
        "filter_rule": (
            f"Roles need at least {MINIMUM_ROLE_JOBS} total observed jobs and "
            f"{MINIMUM_MATCHING_JOBS} matching jobs; results are limited to the top "
            f"{ROLE_RESULT_LIMIT} roles."
        ),
        "ranking_method": "Matching job count descending, match percentage descending, then role job count descending.",
    }