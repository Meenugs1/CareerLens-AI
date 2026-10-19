"""Dataset-derived career path exploration."""

import re
from collections import Counter, defaultdict

from backend.recommendation_service import _load_dataset, extract_skills
from backend.skill_gap_service import _build_role_analysis, _percentage


RELATED_ROLE_LIMIT = 8
KEY_SKILL_LIMIT = 10
MINIMUM_ROLE_JOBS = 2
SENIORITY_WORDS = {
    "associate", "chief", "director", "entry", "head", "intern", "jr",
    "junior", "lead", "manager", "principal", "senior", "sr", "staff",
    "trainee", "vice", "vp",
}
_title_profile_cache = {}


def _title_tokens(title):
    return set(re.findall(r"[a-z0-9]+", str(title).lower()))


def _title_family(title):
    tokens = _title_tokens(title)
    return " ".join(sorted(tokens - SENIORITY_WORDS))


def _build_title_profiles(df):
    cache_key = id(df)
    if cache_key in _title_profile_cache:
        return _title_profile_cache[cache_key]

    profiles = defaultdict(lambda: [0, Counter(), []])
    for title_value, tags_value in df[["title", "tagsandskills"]].itertuples(index=False, name=None):
        title = str(title_value).strip()
        if not title or title.lower() in {"nan", "none"}:
            continue
        profile = profiles[title]
        profile[0] += 1
        job_skills = extract_skills(tags_value)
        profile[1].update(job_skills)
        profile[2].append(job_skills)

    profiles = {
        title: {
            "job_count": profile[0],
            "skill_counts": profile[1],
            "job_skill_sets": profile[2],
        }
        for title, profile in profiles.items()
    }

    _title_profile_cache[cache_key] = dict(profiles)
    return _title_profile_cache[cache_key]


def _empty_result(role, message):
    return {
        "success": False,
        "role": role,
        "message": message,
        "analyzed_jobs": 0,
        "job_count": 0,
        "key_skills": [],
        "related_roles": [],
    }


def _relationship_evidence(shared_skills, title_overlap, target_skill_count):
    evidence = [f"Shares {len(shared_skills)} of the selected key skills."]
    if title_overlap:
        evidence.append("The role titles share observable terms.")
    if not target_skill_count:
        evidence = ["The role titles share observable terms."]
    return " ".join(evidence)


def _role_result(role, analysis, profiles):
    target_skills = set(
        sorted(
            analysis["skill_counts"],
            key=lambda skill: (-analysis["skill_counts"][skill], skill),
        )[:KEY_SKILL_LIMIT]
    )
    target_tokens = _title_tokens(role)
    target_family = _title_family(role)
    candidates = []

    for candidate_role, profile in profiles.items():
        if candidate_role.casefold() == role.casefold():
            continue
        if profile["job_count"] < MINIMUM_ROLE_JOBS:
            continue

        candidate_skills = set(profile["skill_counts"])
        shared_skills = target_skills & candidate_skills
        candidate_tokens = _title_tokens(candidate_role)
        title_intersection = target_tokens & candidate_tokens
        title_union = target_tokens | candidate_tokens
        title_similarity = (
            len(title_intersection) / len(title_union) if title_union else 0.0
        )
        skill_similarity = (
            len(shared_skills) / len(target_skills) if target_skills else 0.0
        )
        if not shared_skills and not title_intersection:
            continue

        candidate_key_skills = set(
            sorted(
                profile["skill_counts"],
                key=lambda skill: (-profile["skill_counts"][skill], skill),
            )[:KEY_SKILL_LIMIT]
        )
        shared_key_skills = target_skills & candidate_key_skills
        additional_skills = candidate_key_skills - target_skills
        score = (skill_similarity * 0.75) + (title_similarity * 0.25)
        if _title_family(candidate_role) == target_family:
            score *= 0.7

        candidates.append({
            "role": candidate_role,
            "job_count": int(profile["job_count"]),
            "shared_skills": sorted(shared_key_skills),
            "additional_observed_skills": sorted(additional_skills),
            "skill_overlap_percentage": _percentage(
                len(shared_key_skills), len(target_skills)
            ),
            "title_similarity_percentage": _percentage(
                len(title_intersection), len(title_union)
            ),
            "relationship_evidence": _relationship_evidence(
                shared_key_skills, title_intersection, len(target_skills)
            ),
            "_score": score,
            "_family": _title_family(candidate_role),
        })

    candidates.sort(
        key=lambda item: (-item["_score"], -len(item["shared_skills"]),
                          -item["job_count"], item["role"].casefold())
    )

    selected = []
    family_counts = Counter()
    for candidate in candidates:
        family = candidate["_family"]
        if family == target_family and family_counts[family] >= 1:
            continue
        if family != target_family and family_counts[family] >= 2:
            continue
        family_counts[family] += 1
        selected.append({key: value for key, value in candidate.items() if not key.startswith("_")})
        if len(selected) == RELATED_ROLE_LIMIT:
            break

    return {
        "success": True,
        "message": "These are dataset-based career exploration options, not guaranteed career progression paths.",
        "role": role,
        "analyzed_jobs": int(len(analysis["role_jobs"])),
        "job_count": int(len(analysis["role_jobs"])),
        "key_skills": sorted(target_skills),
        "related_roles": selected,
        "relationship_method": (
            "Roles are ranked using shared normalized key skills and Jaccard "
            "similarity between observed title tokens. Candidates need at least "
            "two observed jobs and are grouped to limit duplicate seniority variants."
        ),
    }


def explore_career_path(role):
    target_role = str(role or "").strip()
    if not target_role:
        return _empty_result(target_role, "Enter a role to explore.")

    df = _load_dataset()
    analysis = _build_role_analysis(df, target_role)
    if analysis["role_jobs"].empty:
        return _empty_result(
            target_role,
            "Insufficient data available for this role. No matching jobs were found.",
        )

    profiles = _build_title_profiles(df)
    result = _role_result(target_role, analysis, profiles)
    if not result["related_roles"]:
        result["message"] = (
            "Insufficient relationship evidence in the current dataset. "
            "No related roles were returned."
        )
    return result