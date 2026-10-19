"""Dataset-derived what-if skill simulation."""

from backend.recommendation_service import _load_dataset, normalize_skill
from backend.skill_gap_service import _build_role_analysis, _percentage


COVERAGE_DEFINITION = (
    "Percentage of target-role jobs containing at least two normalized selected skills."
)


def _matching_jobs(job_skill_sets, skills):
    return sum(
        len(skills & job_skills) >= 2
        for job_skills in job_skill_sets
    )


def _normalized_skills(skills):
    if not isinstance(skills, (list, tuple, set)):
        return set()

    return {
        normalized
        for skill in skills or []
        if isinstance(skill, str)
        for normalized in [normalize_skill(skill)]
        if normalized
    }


def _empty_result(role, skills, message):
    return {
        "success": False,
        "role": role,
        "message": message,
        "before": {"skills": sorted(skills), "matching_jobs": 0, "coverage": 0.0},
        "after": {"skills": sorted(skills), "matching_jobs": 0, "coverage": 0.0},
        "impact": {"matching_jobs_change": 0, "coverage_change": 0.0},
        "summary": {"target_role_jobs": 0, "analyzed_jobs": 0},
    }


def simulate_skill_change(role, skills, add_skill):
    target_role = str(role or "").strip()
    current_skills = _normalized_skills(skills)
    normalized_add_skill = (
        normalize_skill(add_skill)
        if isinstance(add_skill, str)
        else None
    )

    if not target_role:
        return _empty_result(target_role, current_skills, "Enter a target role.")
    if not current_skills:
        return _empty_result(target_role, current_skills, "Enter at least one current skill.")
    if not normalized_add_skill:
        return _empty_result(target_role, current_skills, "Enter a skill to add.")
    df = _load_dataset()
    analysis = _build_role_analysis(df, target_role)
    total_jobs = len(analysis["role_jobs"])
    if total_jobs == 0:
        return _empty_result(
            target_role,
            current_skills,
            "Insufficient data available for this target role.",
        )

    job_skill_sets = analysis["job_skill_sets"]
    updated_skills = current_skills | {normalized_add_skill}
    before_matching = 0
    after_matching = 0
    for job_skills in job_skill_sets:
        if len(current_skills & job_skills) >= 2:
            before_matching += 1
        if len(updated_skills & job_skills) >= 2:
            after_matching += 1
    before_coverage = _percentage(before_matching, total_jobs)
    after_coverage = _percentage(after_matching, total_jobs)

    if normalized_add_skill in current_skills:
        return {
            "success": False,
            "role": target_role,
            "message": "Skill is already included in your current skills.",
            "before": {
                "skills": sorted(current_skills),
                "matching_jobs": before_matching,
                "coverage": before_coverage,
            },
            "after": {
                "skills": sorted(current_skills),
                "matching_jobs": after_matching,
                "coverage": after_coverage,
            },
            "impact": {
                "matching_jobs_change": 0,
                "coverage_change": 0.0,
            },
            "summary": {
                "target_role_jobs": total_jobs,
                "analyzed_jobs": total_jobs,
            },
        }

    return {
        "success": True,
        "role": target_role,
        "message": "Results are dataset-based and do not guarantee employment.",
        "before": {
            "skills": sorted(current_skills),
            "matching_jobs": before_matching,
            "coverage": before_coverage,
        },
        "after": {
            "skills": sorted(updated_skills),
            "added_skill": normalized_add_skill,
            "matching_jobs": after_matching,
            "coverage": after_coverage,
        },
        "impact": {
            "matching_jobs_change": after_matching - before_matching,
            "coverage_change": round(after_coverage - before_coverage, 2),
        },
        "summary": {
            "target_role_jobs": total_jobs,
            "analyzed_jobs": total_jobs,
        },
        "coverage_definition": COVERAGE_DEFINITION,
    }
