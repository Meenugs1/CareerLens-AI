"""Dataset-derived company search and intelligence."""

from collections import Counter, defaultdict
import math

import pandas as pd

from backend.career_path_service import _title_family
from backend.market_intelligence_service import (
    _percentage,
    _valid_dimension,
)
from backend.recommendation_service import _load_dataset, extract_skills


COMPANY_SEARCH_LIMIT = 15
ROLE_LIMIT = 10
LOCATION_LIMIT = 10
SKILL_LIMIT = 15
_company_index_cache = {}


def _numeric_value(value):
    if value is None or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _new_company_profile():
    return {
        "names": Counter(),
        "company_ids": Counter(),
        "job_count": 0,
        "role_titles": defaultdict(Counter),
        "locations": Counter(),
        "skill_counts": Counter(),
        "salary_values": [],
        "salary_ranges": Counter(),
        "ratings": [],
        "review_counts": [],
    }


def _build_company_index(df):
    cache_key = id(df)
    if cache_key in _company_index_cache:
        return _company_index_cache[cache_key]

    profiles = defaultdict(_new_company_profile)
    selected_columns = [
        "companyname",
        "companyid",
        "title",
        "location",
        "tagsandskills",
        "currency",
        "salary_available",
        "average_salary",
        "salary_range",
        "aggregaterating",
        "reviewscount",
    ]

    for row in df[selected_columns].itertuples(index=False, name=None):
        (
            company_value,
            company_id,
            title_value,
            location_value,
            tags,
            currency,
            salary_available,
            average_salary,
            salary_range,
            rating,
            review_count,
        ) = row
        company = _valid_dimension(company_value)
        if company is None:
            continue

        profile = profiles[company.casefold()]
        profile["names"][company] += 1
        valid_company_id = _valid_dimension(company_id)
        if valid_company_id is not None:
            profile["company_ids"][valid_company_id] += 1
        profile["job_count"] += 1

        title = _valid_dimension(title_value)
        if title is not None:
            role_family = _title_family(title) or title.casefold()
            profile["role_titles"][role_family][title] += 1

        location = _valid_dimension(location_value)
        if location is not None:
            profile["locations"][location] += 1

        profile["skill_counts"].update(extract_skills(tags))

        is_salary_record = (
            str(currency).upper() == "INR"
            and pd.notna(salary_available)
            and bool(salary_available)
        )
        salary_value = _numeric_value(average_salary)
        if is_salary_record and salary_value is not None:
            profile["salary_values"].append(salary_value)
            valid_range = _valid_dimension(salary_range)
            if valid_range is not None:
                profile["salary_ranges"][valid_range] += 1

        rating_value = _numeric_value(rating)
        if rating_value is not None:
            profile["ratings"].append(rating_value)
        review_value = _numeric_value(review_count)
        if review_value is not None:
            profile["review_counts"].append(review_value)

    _company_index_cache[cache_key] = dict(profiles)
    return _company_index_cache[cache_key]


def _index():
    return _build_company_index(_load_dataset())


def _empty_result(company, message):
    return {
        "success": False,
        "company": company,
        "message": message,
    }


def search_companies(query=None):
    normalized_query = str(query or "").strip().casefold()
    profiles = _index()
    matches = []

    for profile in profiles.values():
        company = profile["names"].most_common(1)[0][0]
        if normalized_query and normalized_query not in company.casefold():
            continue
        matches.append({"company": company, "job_count": profile["job_count"]})

    matches.sort(key=lambda item: (-item["job_count"], item["company"].casefold()))
    return {
        "success": True,
        "query": str(query or "").strip(),
        "companies": matches[:COMPANY_SEARCH_LIMIT],
    }


def _roles(profile):
    role_items = []
    for titles in profile["role_titles"].values():
        role, count = titles.most_common(1)[0]
        role_items.append({"role": role, "job_count": int(sum(titles.values()))})
    return sorted(
        role_items,
        key=lambda item: (-item["job_count"], item["role"].casefold()),
    )[:ROLE_LIMIT]


def _locations(profile):
    return [
        {"location": location, "job_count": int(count)}
        for location, count in profile["locations"].most_common(LOCATION_LIMIT)
    ]


def _skills(profile):
    total_jobs = profile["job_count"]
    return [
        {
            "skill": skill,
            "jobs_with_skill": int(count),
            "demand_percentage": _percentage(count, total_jobs),
        }
        for skill, count in profile["skill_counts"].most_common(SKILL_LIMIT)
    ]


def _salary(profile):
    values = profile["salary_values"]
    if not values:
        return {
            "available": False,
            "salary_jobs": 0,
            "message": "Salary data is not available for this company in the current dataset.",
            "salary_range_distribution": [],
        }

    return {
        "available": True,
        "salary_jobs": len(values),
        "average_salary": round(float(pd.Series(values).mean()), 2),
        "median_salary": round(float(pd.Series(values).median()), 2),
        "minimum_salary": round(min(values), 2),
        "maximum_salary": round(max(values), 2),
        "salary_range_distribution": [
            {"salary_range": salary_range, "job_count": int(count)}
            for salary_range, count in profile["salary_ranges"].most_common()
        ],
        "message": "Salary statistics use only job records with available salary data.",
    }


def _ratings(profile):
    ratings = profile["ratings"]
    reviews = profile["review_counts"]
    if not ratings and not reviews:
        return {
            "available": False,
            "message": "Rating and review data are not available for this company in the current dataset.",
        }

    result = {
        "available": True,
        "message": "Ratings are dataset-listed values and are not an independent company review.",
    }
    if ratings:
        result.update({
            "rating_records": len(ratings),
            "average_dataset_listed_rating": round(sum(ratings) / len(ratings), 2),
            "minimum_dataset_listed_rating": round(min(ratings), 2),
            "maximum_dataset_listed_rating": round(max(ratings), 2),
        })
    if reviews:
        result.update({
            "review_count_records": len(reviews),
            "average_dataset_listed_review_count": round(sum(reviews) / len(reviews), 2),
            "maximum_dataset_listed_review_count": int(max(reviews)),
        })
    return result


def get_company_intelligence(company):
    target_company = str(company or "").strip()
    if not target_company:
        return _empty_result(target_company, "Enter a company to explore.")

    profile = _index().get(target_company.casefold())
    if profile is None:
        return _empty_result(
            target_company,
            "No company records matched this name in the current dataset.",
        )

    company_name = profile["names"].most_common(1)[0][0]
    salary = _salary(profile)
    return {
        "success": True,
        "company": company_name,
        "job_count": int(profile["job_count"]),
        "unique_roles": len(profile["role_titles"]),
        "unique_locations": len(profile["locations"]),
        "salary_data_jobs": salary["salary_jobs"],
        "roles": _roles(profile),
        "locations": _locations(profile),
        "skills": _skills(profile),
        "salary": salary,
        "ratings": _ratings(profile),
        "message": "Company information shown here is derived from the current job-market dataset and may not represent the company's complete or current hiring activity.",
    }