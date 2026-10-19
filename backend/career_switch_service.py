"""Dataset-derived career switch comparison."""

from backend.recommendation_service import _load_dataset
from backend.skill_gap_service import (
    _build_role_analysis,
    _normalize_current_skills,
    _percentage,
    _priority,
    _priority_thresholds,
)


TARGET_SKILL_LIMIT = 10


def _empty_result(current_role, current_skills, target_role, message):
    return {
        "success": False,
        "message": message,
        "current_profile": {
            "role": current_role,
            "skills": sorted(current_skills),
        },
        "target_role": {"role": target_role, "analyzed_jobs": 0, "top_skills": []},
        "skill_overlap": {"overlap_skills": [], "missing_skills": []},
        "switch_gap": {
            "target_role_jobs": 0,
            "matching_jobs": 0,
            "coverage": 0.0,
            "overlap_count": 0,
            "missing_count": 0,
        },
        "transition_skills": [],
    }


def _skill_item(skill, count, total_jobs, thresholds):
    percentage = _percentage(count, total_jobs)
    return {
        "skill": skill,
        "jobs_with_skill": int(count),
        "demand_percentage": percentage,
        "priority": _priority(percentage, thresholds),
        "evidence": f"Found in {count} of {total_jobs} analyzed jobs",
    }


def analyze_career_switch(current_role, current_skills, target_role):
    current_role = str(current_role or "").strip()
    target_role = str(target_role or "").strip()
    normalized_skills = _normalize_current_skills(current_skills)

    if not current_role:
        return _empty_result(
            current_role,
            normalized_skills,
            target_role,
            "Enter your current role.",
        )
    if not target_role:
        return _empty_result(
            current_role,
            normalized_skills,
            target_role,
            "Enter a target role.",
        )
    if not normalized_skills:
        return _empty_result(
            current_role,
            normalized_skills,
            target_role,
            "Enter at least one current skill.",
        )
    if current_role.casefold() == target_role.casefold():
        return _empty_result(
            current_role,
            normalized_skills,
            target_role,
            "Current and target roles are the same. Select a different target role to analyze a career switch.",
        )

    df = _load_dataset()
    analysis = _build_role_analysis(df, target_role)
    total_jobs = len(analysis["role_jobs"])
    if total_jobs == 0:
        return _empty_result(
            current_role,
            normalized_skills,
            target_role,
            "Insufficient data available for the selected target role.",
        )

    skill_counts = analysis["skill_counts"]
    thresholds = _priority_thresholds(skill_counts, total_jobs)
    top_skills = sorted(
        skill_counts,
        key=lambda skill: (-skill_counts[skill], skill),
    )[:TARGET_SKILL_LIMIT]
    target_skill_set = set(top_skills)
    overlap_skills = target_skill_set & normalized_skills
    missing_skills = target_skill_set - normalized_skills
    matching_jobs = sum(
        len(normalized_skills & job_skills) >= 2
        for job_skills in analysis["job_skill_sets"]
    )
    coverage = _percentage(matching_jobs, total_jobs)

    top_skill_items = [
        _skill_item(skill, skill_counts[skill], total_jobs, thresholds)
        for skill in top_skills
    ]
    overlap_items = [
        item for item in top_skill_items if item["skill"] in overlap_skills
    ]
    missing_items = [
        item for item in top_skill_items if item["skill"] in missing_skills
    ]

    return {
        "success": True,
        "message": "Results are based on the current dataset and do not guarantee employment or career outcomes.",
        "current_profile": {
            "role": current_role,
            "skills": sorted(normalized_skills),
        },
        "target_role": {
            "role": target_role,
            "analyzed_jobs": total_jobs,
            "top_skills": top_skill_items,
        },
        "skill_overlap": {
            "overlap_skills": overlap_items,
            "missing_skills": missing_items,
            "skill_set_definition": "The target skill set is the top 10 observed skills by job count in the selected target role.",
        },
        "switch_gap": {
            "target_role_jobs": total_jobs,
            "matching_jobs": matching_jobs,
            "coverage": coverage,
            "overlap_count": len(overlap_items),
            "missing_count": len(missing_items),
            "coverage_definition": "Percentage of target-role jobs containing at least two normalized current skills; all selected current skills are considered.",
        },
        "transition_skills": missing_items,
        "readiness_summary": (
            f"Your current skills overlap with {len(overlap_items)} of the "
            f"{len(top_skill_items)} commonly observed skills in the selected target role."
        ),
    }
