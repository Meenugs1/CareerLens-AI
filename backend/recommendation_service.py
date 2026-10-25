"""
recommendation_service.py

A function-based version of the scoring logic from
python/job_recommendation_engine_v4_2.py.

This file does NOT use input() or print() - it exposes a single
function, get_recommendations(), that a FastAPI endpoint can call
directly and get back plain Python data (ready to convert to JSON).

The scoring rules themselves (skill match, role relevance,
experience match, location match, work mode match, freshness,
seniority, fresher suitability) are copied over unchanged from
V4.2 - nothing about the "brains" of the engine was redesigned.
"""
import math
import os
import pickle
import re
from html import unescape
from pathlib import Path

import pandas as pd
import requests


# ============================================================
# FILE PATHS (pathlib - works no matter where uvicorn is run from)
# This file lives in backend/, so the project root is one folder up.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "jobs_cleaned.xlsx"
CACHE_FILE = BASE_DIR / "data" / "processed" / "jobs_cleaned.cache.pkl"
_JOB_TYPE_CLASSIFIER_VERSION = 8

def ensure_dataset_exists():
    """Download the private dataset from Hugging Face if it is missing."""

    if DATA_FILE.exists():
        return

    hf_token = os.getenv("HF_TOKEN")
    dataset_repo = os.getenv(
        "HF_DATASET_REPO",
        "Meenugs1/careerlens-jobs-data",
    )

    if not hf_token:
        raise RuntimeError(
            "Dataset is missing and HF_TOKEN is not configured."
        )

    download_url = (
        f"https://huggingface.co/datasets/"
        f"{dataset_repo}/resolve/main/jobs_cleaned.xlsx"
    )

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".xlsx.tmp")

    try:
        with requests.get(
            download_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            stream=True,
            timeout=(30, 300),
        ) as response:
            response.raise_for_status()

            with temporary_file.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)

        temporary_file.replace(DATA_FILE)

    finally:
        if temporary_file.exists():
            temporary_file.unlink()

_INTERNSHIP_TEXT_PATTERN = (
    r"\binterns?\b|\binternships?\b|\bapprentices?\b|\bapprenticeships?\b"
)
_DIRECT_INTERNSHIP_DESCRIPTION_PATTERN = (
    r"\b(?:internship|apprenticeship)\s*(?:</?\w+[^>]*>\s*){0,2}(?:profile|position|role|opening|vacancy)\b"
    r"|\b(?:internship|apprenticeship)\s*(?:</?\w+[^>]*>\s*){0,2}(?:with\s+stipend|paid|stipend)\b"
    r"|\b(?:intern|apprentice)\s+(?:position|role|opening|opportunity)\b"
    r"|\b(?:looking for|seeking|hiring|recruiting)\b.{0,80}\b(?:intern|internship|apprentice|apprenticeship)\b"
    r"|\b(?:join|work)\s+(?:us\s+)?as\s+(?:an?\s+)?(?:intern|apprentice)\b"
)
_NON_INTERNSHIP_EVIDENCE_PATTERN = (
    r"\bnon[- ]internship\b|\bnot\s+an?\s+internship\b|\bno\s+internship\b"
)


# ============================================================
# DATASET CACHE
# The Excel file is read once during FastAPI startup. After that,
# the same data already in memory is reused for every search.
# ============================================================

_dataset_cache = None


def _build_inferred_job_types(df):
    def column_text(name):
        if name not in df.columns:
            return pd.Series("", index=df.index, dtype="string")
        return df[name].fillna("").astype("string")

    title = column_text("title")
    tags = column_text("tagsandskills")
    description = column_text("jobdescription")
    work_mode = column_text("workmode")
    inferred = pd.Series(None, index=df.index, dtype="object")

    def assign(pattern, value, text=title):
        mask = text.str.contains(pattern, case=False, regex=True, na=False)
        inferred.loc[mask & inferred.isna()] = value

    assign(_INTERNSHIP_TEXT_PATTERN, "Internship")
    assign(r"\bpart[- ]time\b|\bparttime\b", "Part-time")
    assign(r"\bcontract(?:ual)?\b", "Contract")
    assign(r"\bfull[- ]time\b|\bfulltime\b", "Full-time")

    internship_tag = tags.str.contains(
        r"(?:^|,)\s*(?:interns?|internships?|apprentices?|apprenticeships?)\s*(?:,|$)",
        case=False,
        regex=True,
        na=False,
    )
    inferred.loc[internship_tag & inferred.isna()] = "Internship"

    description_evidence = description.str.contains(
        _DIRECT_INTERNSHIP_DESCRIPTION_PATTERN,
        case=False,
        regex=True,
        na=False,
    )
    inferred.loc[description_evidence & inferred.isna()] = "Internship"

    other_text = title.str.cat(
        [tags, description, work_mode],
        sep=" ",
    )
    assign(r"\bpart[- ]time\b|\bparttime\b", "Part-time", other_text)
    assign(r"\bcontract(?:ual)?\b", "Contract", other_text)
    assign(r"\bfull[- ]time\b|\bfulltime\b", "Full-time", other_text)
    return inferred.tolist()


def _load_dataset():

    global _dataset_cache

    ensure_dataset_exists()

    if _dataset_cache is not None:
        return _dataset_cache

    source_mtime_ns = DATA_FILE.stat().st_mtime_ns

    if CACHE_FILE.exists():
        try:
            cached = pd.read_pickle(CACHE_FILE)
            if (
                isinstance(cached, dict)
                and cached.get("source_mtime_ns") == source_mtime_ns
                and isinstance(cached.get("dataframe"), pd.DataFrame)
            ):
                _dataset_cache = cached["dataframe"]
                if (
                    cached.get("job_type_classifier_version")
                    != _JOB_TYPE_CLASSIFIER_VERSION
                    or "_inferred_job_type" not in _dataset_cache.columns
                    or "_is_verified_internship" not in _dataset_cache.columns
                ):
                    _dataset_cache["_inferred_job_type"] = _build_inferred_job_types(
                        _dataset_cache
                    )
                    _dataset_cache["_is_verified_internship"] = (
                        _build_verified_internship_flags(_dataset_cache)
                    )
                    try:
                        pd.to_pickle(
                            {
                                "source_mtime_ns": source_mtime_ns,
                                "job_type_classifier_version": _JOB_TYPE_CLASSIFIER_VERSION,
                                "dataframe": _dataset_cache,
                            },
                            CACHE_FILE,
                        )
                    except OSError:
                        pass
                return _dataset_cache
        except (EOFError, OSError, pickle.UnpicklingError, TypeError, ValueError):
            pass

    _dataset_cache = pd.read_excel(DATA_FILE)
    _dataset_cache["_inferred_job_type"] = _build_inferred_job_types(
        _dataset_cache
    )
    _dataset_cache["_is_verified_internship"] = (
        _build_verified_internship_flags(_dataset_cache)
    )

    try:
        pd.to_pickle(
            {
                "source_mtime_ns": source_mtime_ns,
                "job_type_classifier_version": _JOB_TYPE_CLASSIFIER_VERSION,
                "dataframe": _dataset_cache,
            },
            CACHE_FILE,
        )
    except OSError:
        pass

    return _dataset_cache


def _build_verified_internship_flags(df):
    description = (
        df["jobdescription"].fillna("").astype("string")
        if "jobdescription" in df.columns
        else pd.Series("", index=df.index, dtype="string")
    )
    explicit_non_internship = description.str.contains(
        _NON_INTERNSHIP_EVIDENCE_PATTERN,
        case=False,
        regex=True,
        na=False,
    )
    return (
        df["_inferred_job_type"].eq("Internship")
        & ~explicit_non_internship
    )


# ============================================================
# SKILL ALIASES  (unchanged from V4.2)
# ============================================================

skill_aliases = {
    "python programming": "python",
    "python scripting": "python",

    "structured query language": "sql",

    "ms excel": "excel",
    "microsoft excel": "excel",

    "powerbi": "power bi",
    "power bi desktop": "power bi",

    "java script": "javascript",
    "java-script": "javascript",

    "react.js": "react",
    "reactjs": "react",
    "react js": "react",

    "html5": "html",
    "html 5": "html",

    "css3": "css",
    "css 3": "css",

    "amazon web services": "aws",

    # Machine learning family
    "ml": "machine learning",
    "machinelearning": "machine learning",
    "machine-learning": "machine learning",
    "machine learning": "machine learning",
    "machine learning algorithms": "machine learning",

    # AI/ML combined tags
    "aiml": "artificial intelligence / machine learning",
    "ai/ml": "artificial intelligence / machine learning",
    "ai ml": "artificial intelligence / machine learning",
    "ai-ml": "artificial intelligence / machine learning",

    "nlp": "natural language processing",

    "tensorflow": "tensorflow",
    "pytorch": "pytorch",

    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    "nodejs": "node.js",
    "node js": "node.js",

    "angularjs": "angular",
}


# ============================================================
# GENERIC / NOISY / FRAGMENT TERMS  (unchanged from V4.2)
# ============================================================

ignored_skills = {
    "not specified",
    "data",
    "analysis",
    "analytical",
    "analytics",
    "development",
    "technical",
    "software",
    "project",
    "management",
    "usage",
    "handling",
    "assistance",
    "generation",
    "calling",
    "voice",
    "candidate",
    "employee",
    "screening",
    "experience",
    "joining formalities",
    "responsibilities",
    "activities",
    "requirements",
    "process",
    "role",
    "office",
    "microsoft",
    "bi",
    "languages",
    "machine",
    "al",
    "ml",
    "aiml",
}


_INTERNSHIP_SKILL_ALIASES = {
    "python": "python",
    "python programming": "python",
    "python scripting": "python",
    "javascript": "javascript",
    "java script": "javascript",
    "java-script": "javascript",
    "js": "javascript",
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "html": "html",
    "html5": "html",
    "html 5": "html",
    "css": "css",
    "css3": "css",
    "css 3": "css",
    "typescript": "typescript",
    "angular": "angular",
    "angularjs": "angular",
    "vue": "vue.js",
    "vue.js": "vue.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "node.js": "node.js",
    "django": "django",
    "flask": "flask",
    "java": "java",
    "sql": "sql",
    "structured query language": "sql",
    "mysql": "sql",
    "microsoft sql server": "sql",
    "sql server": "sql",
    "postgresql": "sql",
    "postgres": "sql",
    "sqlite": "sql",
    "pl/sql": "sql",
    "excel": "excel",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "power bi": "power bi",
    "powerbi": "power bi",
    "power bi desktop": "power bi",
    "tableau": "tableau",
    "data analysis": "data analysis",
    "data analytics": "data analysis",
    "data visualization": "data visualization",
    "machine learning": "machine learning",
    "machine-learning": "machine learning",
    "machinelearning": "machine learning",
    "ml": "machine learning",
    "ml algorithms": "machine learning",
    "machine learning algorithms": "machine learning",
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "statistics": "statistics",
    "aws": "aws",
    "amazon web services": "aws",
    "azure": "azure",
    "git": "git",
    "docker": "docker",
    "rest api": "rest api",
    "rest apis": "rest api",
    "requirements gathering": "requirements gathering",
    "requirement gathering": "requirements gathering",
    "business analysis": "business analysis",
    "stakeholder management": "stakeholder management",
    "dashboarding": "dashboarding",
    "reporting": "reporting",
}
_INTERNSHIP_NON_SKILL_TERMS = {
    "intern",
    "internship",
    "apprentice",
    "apprenticeship",
    "full stack",
    "fresher",
    "program",
    "programming",
    "role intern",
    "software development",
    "software engineering",
    "coding",
    "cs",
}

_INTERNSHIP_SKILL_PHRASES = sorted(
    _INTERNSHIP_SKILL_ALIASES,
    key=len,
    reverse=True,
)
_INTERNSHIP_SKILL_PATTERN = re.compile(
    r"(?<![a-z0-9_])(?:"
    + "|".join(
        re.escape(phrase).replace(r"\ ", r"\s+")
        for phrase in _INTERNSHIP_SKILL_PHRASES
    )
    + r")(?![a-z0-9_])",
    re.IGNORECASE,
)

_INTERNSHIP_ROLE_PATTERNS = {
    "data analyst": re.compile(r"\bdata\s+analyst\b|\bdata\s+analytics?\b", re.I),
    "business analyst": re.compile(r"\bbusiness\s+analyst\b", re.I),
    "data scientist": re.compile(r"\bdata\s+scientist\b|\bdata\s+science\b", re.I),
    "python developer": re.compile(r"\bpython\s+(?:developer|engineer|programmer)\b", re.I),
    "software developer": re.compile(
        r"\bsoftware\s+(?:developer|engineer|development)\b|\bsde\b", re.I
    ),
    "frontend developer": re.compile(r"\bfront[- ]?end\b|\bfrontend\b", re.I),
}

_FRONTEND_SKILLS = {
    "javascript", "react", "html", "css", "typescript", "angular", "vue.js"
}
_DEVELOPER_TITLE_PATTERN = re.compile(
    r"\b(?:software|web|full[ -]?stack|backend|back[ -]?end|python)\b.{0,50}"
    r"\b(?:developer|engineer|programmer)\b|"
    r"\b(?:developer|engineer|programmer)\b.{0,50}"
    r"\b(?:software|web|full[ -]?stack|backend|back[ -]?end|python)\b",
    re.I,
)


def normalize_skill(skill):

    skill = str(skill).strip().lower()

    if not skill:
        return None

    if skill in skill_aliases:
        skill = skill_aliases[skill]

    if skill in ignored_skills:
        return None

    return skill


def extract_skills(skill_text):

    skills = set()

    for skill in str(skill_text).split(","):

        normalized = normalize_skill(skill)

        if normalized:
            skills.add(normalized)

    return skills


def _normalize_internship_skill(skill):
    value = re.sub(r"\s+", " ", str(skill or "").strip().casefold())
    if not value:
        return None
    if value in _INTERNSHIP_NON_SKILL_TERMS:
        return None
    if value in _INTERNSHIP_SKILL_ALIASES:
        return _INTERNSHIP_SKILL_ALIASES[value]
    return normalize_skill(value)


def _plain_text(value):
    text = unescape(str(value or ""))
    return re.sub(r"<[^>]+>", " ", text)


def _skill_mention_is_negated(text, start, end):
    sentence_start = max(
        text.rfind(mark, 0, start)
        for mark in (".", "!", "?", ";", "\n")
    ) + 1
    sentence_end_candidates = [
        position for mark in (".", "!", "?", ";", "\n")
        if (position := text.find(mark, end)) >= 0
    ]
    sentence_end = min(sentence_end_candidates) if sentence_end_candidates else len(text)
    before = text[max(sentence_start, start - 48):start].casefold().strip()
    after = text[end:min(sentence_end, end + 48)].casefold().strip()

    if re.match(
        r"^(?:(?:is|are)\s+)?(?:not\s+required|not\s+needed|not\s+necessary|"
        r"not\s+mandatory|not\s+a\s+requirement|not\s+expected)",
        after,
    ):
        return True
    if re.match(
        r"^(?:(?:is|are)\s+)?(?:preferred|optional|a\s+plus)[^.;!?]{0,24}"
        r"\bnot\s+required\b",
        after,
    ):
        return True
    if re.search(
        r"\b(?:not\s+required|not\s+needed|not\s+mandatory)\s*:?\s*$",
        before,
    ):
        return True
    if re.search(r"\b(?:no|without)\s*$", before) and re.match(
        r"\s*(?:required|needed|necessary|mandatory)\b",
        after,
    ):
        return True
    if re.search(
        r"\b(?:no|without)\s+(?:(?:prior|previous|any)\s+)?"
        r"(?:experience|knowledge|proficiency|familiarity|expertise)\s+"
        r"(?:in|with|of)?\s*$",
        before,
    ):
        return True
    if re.search(r"\b(?:not\s+required|not\s+needed|not\s+mandatory)\s*:?\s*$", before):
        return True
    return False


def _extract_catalog_skills(text, source, skill_sources):
    plain_text = _plain_text(text)
    for match in _INTERNSHIP_SKILL_PATTERN.finditer(plain_text):
        phrase = re.sub(r"\s+", " ", match.group().casefold())
        canonical = _INTERNSHIP_SKILL_ALIASES[phrase]
        if not _skill_mention_is_negated(
            plain_text,
            match.start(),
            match.end(),
        ):
            skill_sources.setdefault(canonical, set()).add(source)


def extract_internship_skill_evidence(row):
    skill_sources = {}
    tags = _plain_text(row.get("tagsandskills", ""))

    for tag in re.split(r"[,;|\n]+", tags):
        normalized = _normalize_internship_skill(tag)
        if normalized:
            skill_sources.setdefault(normalized, set()).add("tags")

    _extract_catalog_skills(tags, "tags", skill_sources)
    _extract_catalog_skills(row.get("title", ""), "title", skill_sources)
    _extract_catalog_skills(row.get("jobdescription", ""), "description", skill_sources)
    return skill_sources


def _serialize_skill_evidence(skill_sources, selected_skills=None):
    selected = set(selected_skills) if selected_skills is not None else None
    return [
        {"skill": skill, "sources": sorted(sources)}
        for skill, sources in sorted(skill_sources.items())
        if selected is None or skill in selected
    ]


def _internship_domain_key(target_role):
    role = re.sub(r"[^a-z0-9]+", " ", str(target_role or "").casefold()).strip()
    aliases = {
        "data analytics": "data analyst",
        "data science": "data scientist",
        "python engineer": "python developer",
        "software engineer": "software developer",
        "front end developer": "frontend developer",
        "front end": "frontend developer",
    }
    return aliases.get(role, role)


def _internship_role_match(row, target_role, skill_sources):
    title = _plain_text(row.get("title", ""))
    description = _plain_text(row.get("jobdescription", ""))
    tags = _plain_text(row.get("tagsandskills", ""))
    key = _internship_domain_key(target_role)
    title_match = False
    evidence = ""

    if key in _INTERNSHIP_ROLE_PATTERNS:
        title_match = bool(_INTERNSHIP_ROLE_PATTERNS[key].search(title))
        if key == "data analyst" and re.search(r"\bclinical\b", title, re.I):
            title_match = False
        if key == "python developer" and not title_match:
            has_python = "python" in skill_sources
            title_match = has_python and bool(_DEVELOPER_TITLE_PATTERN.search(title))
        elif key == "frontend developer" and not title_match:
            frontend_skill_count = len(_FRONTEND_SKILLS & set(skill_sources))
            title_match = bool(
                frontend_skill_count >= 2
                and re.search(r"\b(?:web|ui|full[ -]?stack|developer|engineer)\b", title, re.I)
                and not re.search(r"\b(?:devops|qa|testing|test engineer|reliability)\b", title, re.I)
            )
        if key == "software developer" and not title_match:
            title_match = bool(_DEVELOPER_TITLE_PATTERN.search(title))
        if key == "software developer" and re.search(
            r"\b(?:software\s+testing|qa\s+engineer|test\s+engineer|"
            r"reliability\s+engineer|network\s+engineer)\b",
            title,
            re.I,
        ):
            title_match = False
        if key == "business analyst" and re.search(
            r"\bbusiness\s+development\s+executive\b",
            title,
            re.I,
        ):
            title_match = False
        if title_match:
            evidence = f"Title supports the {target_role} domain."
    else:
        title_match = str(target_role or "").casefold() in title.casefold()
        if title_match:
            evidence = "Title contains the requested role."

    if not title_match:
        return False, ""

    if key == "python developer" and "python" in skill_sources and not re.search(
        r"\bpython\b",
        title,
        re.I,
    ):
        evidence = "Developer title with Python explicitly evidenced in listing skills."

    extracted_skills = sorted(
        skill
        for skill, sources in skill_sources.items()
        if "description" in sources
    )
    if extracted_skills:
        evidence += " Skills are also evidenced in the listing description: "
        evidence += ", ".join(extracted_skills[:5]) + "."
    elif tags:
        evidence += " Skill evidence is drawn from the supplied tags."
    return True, evidence


def _internship_evidence_rank(item):
    source_weight = {"tags": 3, "description": 2, "title": 1}
    matched_sources = item.get("matched_skill_evidence", [])
    evidence_weight = sum(
        max((source_weight.get(source, 0) for source in skill["sources"]), default=0)
        for skill in matched_sources
    )
    return (
        evidence_weight,
        len(item.get("available_skills", [])),
        item.get("job_title", "").casefold(),
    )


# ============================================================
# CITY NORMALIZATION  (unchanged from V4.2)
# ============================================================

city_aliases = {
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "calcutta": "kolkata",
    "madras": "chennai",
    "gurgaon": "gurugram",
}


def normalize_city(city):

    city = str(city).strip().lower()

    if city in city_aliases:
        return city_aliases[city]

    return city


def parse_location(job_location):

    raw_location = str(job_location).strip()
    location_lower = raw_location.lower()

    is_remote = "remote" in location_lower
    is_hybrid = "hybrid" in location_lower

    parts = re.split(r"[\/,&|\-]| and ", location_lower)

    city_parts = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part in {"remote", "hybrid"}:
            continue
        city_parts.append(normalize_city(part))

    return city_parts, is_remote, is_hybrid


def city_is_present(job_location, preferred_city):

    city_parts, _, _ = parse_location(job_location)
    return preferred_city in city_parts


# ============================================================
# ROLE RELEVANCE  (unchanged from V4.2 - works for ANY role text)
# ============================================================

def role_relevance(job_title, target_role):

    title = str(job_title).lower().strip()
    target = target_role.lower().strip()

    if title == target:
        return 100

    if target in title:
        return 95

    target_words = set(target.split())
    title_words = set(title.split())

    overlap = len(target_words & title_words)

    if len(target_words) == 0:
        return 0

    return min(90, (overlap / len(target_words)) * 100)


# ============================================================
# SENIORITY  (unchanged from V4.2)
# ============================================================

negative_seniority_keywords = {
    "senior": 20,
    "sr": 20,
    "lead": 35,
    "manager": 45,
    "principal": 50,
    "architect": 50,
    "head": 60,
    "director": 60,
    "staff": 30,
    "expert": 25,
}

positive_seniority_keywords = {
    "junior",
    "jr",
    "fresher",
    "trainee",
    "intern",
    "entry level",
}

positive_experience_phrases = (
    "0-1 year",
    "0-2 year",
    "0 to 1 year",
    "0 to 2 year",
)


def get_seniority_info(job_title):

    title = str(job_title).lower()

    penalty = 0
    detected = "Standard"
    is_positive = False

    for keyword in positive_seniority_keywords:
        if re.search(r"\b" + re.escape(keyword) + r"\b", title):
            is_positive = True
            detected = keyword.title()

    for phrase in positive_experience_phrases:
        if phrase in title:
            is_positive = True

    for keyword, value in negative_seniority_keywords.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", title):
            if value > penalty:
                penalty = value
                detected = keyword.title()

    return penalty, detected, is_positive


# ============================================================
# EXPERIENCE MATCH  (unchanged from V4.2)
# ============================================================

def extract_experience_range_from_text(text):

    text = str(text).lower()
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    numbers = [float(n) for n in numbers]

    if len(numbers) == 0:
        return None, None

    if len(numbers) == 1:
        return numbers[0], numbers[0]

    return min(numbers), max(numbers)


def get_experience_range(row):

    minimum = row.get("minimumexperience")
    maximum = row.get("maximumexperience")

    min_valid = pd.notna(minimum)
    max_valid = pd.notna(maximum)

    if min_valid and max_valid:
        return float(minimum), float(maximum)

    if min_valid and not max_valid:
        return float(minimum), float(minimum)

    return extract_experience_range_from_text(row.get("experience"))


def experience_match(minimum, maximum, user_years, is_fresher_friendly_title):

    if user_years == 0:

        if minimum is None or minimum == 0 or is_fresher_friendly_title:
            return 100

        difference = minimum
        return max(0, 100 - difference * 40)

    if minimum is None:
        return 100

    if user_years >= minimum and user_years <= maximum:
        return 100

    if user_years < minimum:
        difference = minimum - user_years
        return max(0, 100 - difference * 30)

    difference = user_years - maximum
    return max(0, 100 - difference * 10)


# ============================================================
# LOCATION MATCH  (unchanged from V4.2)
# ============================================================

def location_match(job_location, preferred_city, preferred_is_any):

    raw_location = str(job_location).strip()

    if raw_location == "" or raw_location.lower() in {"nan", "not specified"}:
        return 0

    if preferred_is_any:
        return 50

    city_parts, is_remote, is_hybrid = parse_location(job_location)
    city_present = preferred_city in city_parts

    if is_hybrid:
        return 90 if city_present else 60

    if is_remote:
        return 80

    if city_present:
        return 100 if len(city_parts) == 1 else 90

    return 20


# ============================================================
# WORK MODE MATCH  (unchanged from V4.2)
# ============================================================

def get_job_work_mode(row):

    for column_name in row.index:
        if column_name.strip().lower() == "workmode":
            value = str(row[column_name]).strip().lower()
            if value and value != "nan":
                return value

    location_lower = str(row.get("location", "")).lower()

    if "remote" in location_lower:
        return "remote"

    if "hybrid" in location_lower:
        return "hybrid"

    return "not specified"


def work_mode_match(job_mode, preferred_mode):

    if preferred_mode == "any":
        return 100

    if job_mode == "not specified":
        return 50

    if job_mode == preferred_mode:
        return 100

    return 20


# ============================================================
# JOB TYPE FILTERING
# ============================================================

def normalize_job_type(value):

    if value is None:
        return "any"

    normalized = str(value).strip().lower()
    if not normalized or normalized == "any":
        return "any"

    normalized = normalized.replace("_", " ").replace("-", " ")
    normalized = " ".join(normalized.split())

    if normalized in {"internship", "intern"}:
        return "internship"
    if normalized in {"contract", "contractual"}:
        return "contract"
    if normalized in {"part time", "parttime"}:
        return "part-time"
    if normalized in {"full time", "fulltime"}:
        return "full-time"

    return normalized


def classify_job_type_from_text(text):

    raw_text = str(text or "").lower()
    if not raw_text or raw_text == "nan":
        return None

    if re.search(
        _INTERNSHIP_TEXT_PATTERN,
        raw_text,
    ):
        return "Internship"

    if re.search(r"\bpart[- ]time\b|\bparttime\b", raw_text):
        return "Part-time"

    if re.search(r"\bcontract(ual)?\b", raw_text):
        return "Contract"

    if re.search(r"\bfull[- ]time\b|\bfulltime\b", raw_text):
        return "Full-time"

    return None


def _has_internship_tag(tags):
    internship_tags = {
        "intern",
        "interns",
        "internship",
        "internships",
        "apprentice",
        "apprentices",
        "apprenticeship",
        "apprenticeships",
    }
    return any(
        tag.strip().casefold() in internship_tags
        for tag in str(tags or "").split(",")
    )


def _has_direct_internship_description_evidence(description):
    text = str(description or "").lower()
    if not text or text == "nan":
        return False

    return bool(re.search(_DIRECT_INTERNSHIP_DESCRIPTION_PATTERN, text))


def _classify_non_internship_job_type(text):
    raw_text = str(text or "").lower()
    if re.search(r"\bpart[- ]time\b|\bparttime\b", raw_text):
        return "Part-time"
    if re.search(r"\bcontract(ual)?\b", raw_text):
        return "Contract"
    if re.search(r"\bfull[- ]time\b|\bfulltime\b", raw_text):
        return "Full-time"
    return None


def _classify_job_type_from_fields(title, tags, description, work_mode):
    title_type = classify_job_type_from_text(title)
    if title_type:
        return title_type

    if _has_internship_tag(tags):
        return "Internship"

    if _has_direct_internship_description_evidence(description):
        return "Internship"

    other_text = " ".join(
        str(value)
        for value in (tags, description, work_mode)
        if value is not None and str(value).strip() not in {"", "nan", "NaN"}
    )
    return _classify_non_internship_job_type(other_text)


def filter_jobs_by_job_type(df, requested_job_type):

    normalized_request = normalize_job_type(requested_job_type)
    if normalized_request == "any":
        return df.copy()

    job_type_candidates = [
        "jobtype",
        "job_type",
        "employmenttype",
        "employment_type",
        "employmenttypefinal",
        "employment_type_final",
    ]

    for col_name in job_type_candidates:
        if col_name in df.columns:
            col = df[col_name].fillna("")
            text_values = col.astype(str).str.lower()

            if normalized_request == "internship":
                mask = text_values.str.contains(r"intern(ship)?|apprentice(ship)?", na=False)
            elif normalized_request == "part-time":
                mask = text_values.str.contains(r"part[- ]time|parttime", na=False)
            elif normalized_request == "contract":
                mask = text_values.str.contains(r"contract(ual)?", na=False)
            elif normalized_request == "full-time":
                mask = text_values.str.contains(r"full[- ]time|fulltime", na=False)
            else:
                mask = pd.Series(False, index=df.index)

            if mask.any():
                return df[mask].copy()

    inferred_job_type = df["_inferred_job_type"]

    if normalized_request == "internship":
        if "_is_verified_internship" in df.columns:
            return df[df["_is_verified_internship"]].copy()
        return df[inferred_job_type == "Internship"].copy()
    if normalized_request == "part-time":
        return df[inferred_job_type == "Part-time"].copy()
    if normalized_request == "contract":
        return df[inferred_job_type == "Contract"].copy()
    if normalized_request == "full-time":
        return df[inferred_job_type == "Full-time"].copy()

    fallback_mask = []

    for _, row in df.iterrows():
        inferred = classify_job_type_from_text(
            " ".join(
                str(value)
                for value in [
                    row.get("title", ""),
                    row.get("tagsandskills", ""),
                    row.get("jobdescription", ""),
                    row.get("workmode", ""),
                ]
                if value is not None and str(value).strip() not in {"", "nan", "NaN"}
            )
        )

        if normalized_request == "internship":
            fallback_mask.append(inferred == "Internship")
        elif normalized_request == "part-time":
            fallback_mask.append(inferred == "Part-time")
        elif normalized_request == "contract":
            fallback_mask.append(inferred == "Contract")
        elif normalized_request == "full-time":
            fallback_mask.append(inferred == "Full-time")
        else:
            fallback_mask.append(False)

    return df[pd.Series(fallback_mask, index=df.index)].copy()


# ============================================================
# FRESHNESS  (unchanged from V4.2)
# ============================================================

def freshness_score(days):

    if pd.isna(days):
        return 50

    try:
        days = float(days)
    except:
        return 50

    if days <= 1:
        return 100
    if days <= 7:
        return 90
    if days <= 14:
        return 80
    if days <= 30:
        return 65
    if days <= 60:
        return 50

    return 30


# ============================================================
# WHY RECOMMENDED  (unchanged from V4.2)
# ============================================================

def build_why_recommended(
    matched_skills,
    preferred_city,
    preferred_is_any,
    city_matched,
    exp_score,
    fresher_suitable
):

    reasons = []

    for skill in sorted(matched_skills):
        reasons.append(f"{skill.title()} matched")

    if not preferred_is_any and city_matched:
        reasons.append(f"{preferred_city.title()} preference matched")

    if exp_score >= 70:
        reasons.append("Suitable experience level")

    if fresher_suitable == "Yes":
        reasons.append("Fresher-friendly role")

    if not reasons:
        reasons.append("Meets minimum skill overlap")

    return "; ".join(f"\u2713 {reason}" for reason in reasons)


# ============================================================
# MAIN ENTRY POINT
# This is the function a FastAPI endpoint will call.
# It takes plain values (no input(), no print()) and returns
# a plain Python dict - easy to turn into a JSON response.
# ============================================================

def get_recommendations(
    target_role,
    skills,
    experience,
    preferred_location,
    work_mode,
    job_type="Any"
):

    no_fallback = []

    empty_summary = {
        "jobs_analyzed": 0,
        "jobs_recommended": 0,
        "excellent_matches": 0,
        "strong_matches": 0,
        "fresher_suitable_jobs": 0,
    }

    # ---------------- Safe input handling ----------------

    target_role = str(target_role or "").strip()

    # skills can arrive as a comma-separated string OR a list
    if isinstance(skills, (list, tuple, set)):
        skills_text = ", ".join(str(s) for s in skills)
    else:
        skills_text = str(skills or "")

    try:
        user_experience = float(experience)
    except (TypeError, ValueError):
        user_experience = 0

    preferred_location = str(preferred_location or "").strip()
    preferred_city = normalize_city(preferred_location)
    preferred_is_any = (
        preferred_location == ""
        or preferred_location.lower() == "any"
    )

    work_mode = str(work_mode or "").strip().lower()
    preferred_work_mode = "any" if work_mode in ("", "any") else work_mode
    is_internship_request = normalize_job_type(job_type) == "internship"

    # Nothing to search with -> return an empty, safe result
    if not target_role or (not skills_text.strip() and not is_internship_request):
        return {
            "recommendations": [],
            "other_relevant_internships": no_fallback,
            "limited_skill_overlap_internships": [],
            "summary": empty_summary,
        }

    user_skills = set()
    for skill in skills_text.split(","):
        normalized = (
            _normalize_internship_skill(skill)
            if is_internship_request
            else normalize_skill(skill)
        )
        if normalized:
            user_skills.add(normalized)

    if not user_skills and not is_internship_request:
        return {
            "recommendations": [],
            "other_relevant_internships": no_fallback,
            "limited_skill_overlap_internships": [],
            "summary": empty_summary,
        }

    # ---------------- Job type filter (before scoring) ----------------

    df = _load_dataset()
    df = filter_jobs_by_job_type(df, job_type)

    # ---------------- Role filter ----------------

    if is_internship_request:
        domain_key = _internship_domain_key(target_role)
        domain_pattern = _INTERNSHIP_ROLE_PATTERNS.get(domain_key)
        if domain_key == "python developer":
            title_prefilter = df["title"].astype(str).str.contains(
                r"\bpython\s+(?:developer|engineer|programmer)\b|"
                r"\b(?:developer|engineer|programmer)\b",
                case=False,
                regex=True,
                na=False,
            )
        elif domain_key == "frontend developer":
            title_prefilter = df["title"].astype(str).str.contains(
                r"\bfront[- ]?end\b|\bfrontend\b|\b(?:web|ui|full[ -]?stack)\b",
                case=False,
                regex=True,
                na=False,
            )
        elif domain_key == "software developer":
            title_prefilter = df["title"].astype(str).str.contains(
                r"\bsoftware\b|\bsde\b|\b(?:web|full[ -]?stack)\b",
                case=False,
                regex=True,
                na=False,
            )
        elif domain_pattern is not None:
            title_prefilter = df["title"].astype(str).str.contains(
                domain_pattern,
                na=False,
            )
        else:
            title_prefilter = df["title"].astype(str).str.contains(
                re.escape(target_role),
                case=False,
                regex=True,
                na=False,
            )
        candidate_jobs = df[title_prefilter].copy()
        evidence_by_index = {}
        role_evidence_by_index = {}
        role_mask = []
        for index, row in candidate_jobs.iterrows():
            skill_sources = extract_internship_skill_evidence(row)
            is_relevant, role_evidence = _internship_role_match(
                row,
                target_role,
                skill_sources,
            )
            evidence_by_index[index] = skill_sources
            role_evidence_by_index[index] = role_evidence
            role_mask.append(is_relevant)

        role_jobs = candidate_jobs.loc[
            pd.Series(role_mask, index=candidate_jobs.index)
        ].copy()
        role_jobs["_skill_sources"] = role_jobs.index.map(evidence_by_index)
        role_jobs["_role_evidence"] = role_jobs.index.map(role_evidence_by_index)
        role_jobs["normalized_skills"] = role_jobs["_skill_sources"].map(
            lambda sources: set(sources)
        )
    else:
        role_lower = target_role.lower()
        role_jobs = df[
            df["title"]
            .astype(str)
            .str.lower()
            .str.contains(re.escape(role_lower), na=False)
        ].copy()

    if len(role_jobs) == 0:
        return {
            "recommendations": [],
            "other_relevant_internships": no_fallback,
            "limited_skill_overlap_internships": [],
            "summary": empty_summary,
        }

    role_jobs["normalized_skills"] = (
        role_jobs["_skill_sources"].map(lambda sources: set(sources))
        if is_internship_request
        else role_jobs["tagsandskills"].apply(extract_skills)
    )

    other_relevant_internships = []
    limited_skill_overlap_internships = []
    internship_coverage = None
    if is_internship_request:
        incomplete_skill_rows = role_jobs[
            role_jobs["_is_verified_internship"]
            & role_jobs["normalized_skills"].map(len).lt(2)
            & role_jobs.apply(
                lambda row: len(user_skills & row["normalized_skills"]) != 1,
                axis=1,
            )
        ]
        other_relevant_internships = [
            {
                "job_id": str(row.get("jobid", "")),
                "job_title": str(row.get("title", "")),
                "company": str(row.get("companyname", "")),
                "location": str(row.get("location", "")),
                "available_skills": sorted(row["normalized_skills"]),
                "skill_evidence": _serialize_skill_evidence(row["_skill_sources"]),
                "classification": "Internship",
                "label": "Skill data incomplete",
                "match_status": "A reliable skills match cannot be calculated because fewer than two normalized skills are available.",
                "role_evidence": row["_role_evidence"],
            }
            for _, row in incomplete_skill_rows.iterrows()
        ]

    # ---------------- Market skill frequency ----------------

    market_skill_counts = {}

    for skills_set in role_jobs["normalized_skills"]:
        for skill in skills_set:
            market_skill_counts[skill] = market_skill_counts.get(skill, 0) + 1

    def skill_weight(skill):
        frequency = market_skill_counts.get(skill, 1)
        ratio = frequency / len(role_jobs)
        return 1 + math.log1p(ratio * 100)

    # ---------------- Score every job ----------------

    results = []

    for _, row in role_jobs.iterrows():

        job_skills = row["normalized_skills"]

        if not job_skills:
            continue

        matched = user_skills & job_skills
        missing = job_skills - user_skills

        if is_internship_request and len(matched) == 1:
            limited_skill_overlap_internships.append({
                "job_id": str(row.get("jobid", "")),
                "job_title": str(row.get("title", "")),
                "company": str(row.get("companyname", "")),
                "location": str(row.get("location", "")),
                "available_skills": sorted(job_skills),
                "matched_skills": sorted(matched),
                "skill_evidence": _serialize_skill_evidence(row["_skill_sources"]),
                "matched_skill_evidence": _serialize_skill_evidence(
                    row["_skill_sources"],
                    matched,
                ),
                "role_evidence": row["_role_evidence"],
                "overlap_count": 1,
                "classification": "Internship",
                "label": "Limited skill overlap",
                "match_status": "Only one selected skill overlaps. This is a weaker match than the standard recommendations.",
            })
            continue

        if len(matched) < 2:
            continue

        total_weight = sum(skill_weight(s) for s in job_skills)
        matched_weight = sum(skill_weight(s) for s in matched)

        skill_score = (
            (matched_weight / total_weight * 100)
            if total_weight > 0 else 0
        )

        role_score = role_relevance(row["title"], target_role)

        seniority_penalty, seniority, is_positive_fit = (
            get_seniority_info(row["title"])
        )

        min_exp, max_exp = get_experience_range(row)
        exp_score = experience_match(
            min_exp, max_exp, user_experience, is_positive_fit
        )

        loc_score = location_match(
            row["location"], preferred_city, preferred_is_any
        )
        city_matched = (
            not preferred_is_any
            and city_is_present(row["location"], preferred_city)
        )

        job_work_mode = get_job_work_mode(row)
        mode_score = work_mode_match(job_work_mode, preferred_work_mode)

        fresh_score = freshness_score(row.get("days_ago"))

        recommendation_score = (
            skill_score * 0.40
            + role_score * 0.20
            + exp_score * 0.20
            + loc_score * 0.10
            + fresh_score * 0.05
            + mode_score * 0.05
        )

        if user_experience == 0:
            recommendation_score -= seniority_penalty * 0.60
        else:
            recommendation_score -= seniority_penalty * 0.20

        recommendation_score = max(0, min(100, recommendation_score))

        if recommendation_score >= 75:
            match_level = "Excellent Match"
        elif recommendation_score >= 60:
            match_level = "Strong Match"
        elif recommendation_score >= 45:
            match_level = "Moderate Match"
        else:
            match_level = "Low Match"

        if user_experience == 0:
            if seniority_penalty > 0:
                fresher_suitable = "No"
            elif is_positive_fit or min_exp is None or min_exp == 0:
                fresher_suitable = "Yes"
            else:
                fresher_suitable = "No"
        else:
            fresher_suitable = "Not Applicable"

        why_recommended = build_why_recommended(
            matched, preferred_city, preferred_is_any,
            city_matched, exp_score, fresher_suitable
        )

        recommendation = {
            "job_id": str(row.get("jobid", "")),
            "job_title": str(row.get("title", "")),
            "company": str(row.get("companyname", "")),
            "location": str(row.get("location", "")),
            "work_mode": job_work_mode.title(),

            "recommendation_score": round(float(recommendation_score), 2),
            "match_level": match_level,

            "skill_match": round(float(skill_score), 2),
            "role_relevance": round(float(role_score), 2),
            "experience_match": round(float(exp_score), 2),
            "location_match": round(float(loc_score), 2),
            "work_mode_match": round(float(mode_score), 2),
            "freshness_score": round(float(fresh_score), 2),

            "seniority": seniority,
            "fresher_suitable": fresher_suitable,

            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),

            "why_recommended": why_recommended,
        }
        if is_internship_request:
            recommendation["classification"] = "Internship"
            recommendation["skill_evidence"] = _serialize_skill_evidence(
                row["_skill_sources"]
            )
            recommendation["matched_skill_evidence"] = _serialize_skill_evidence(
                row["_skill_sources"],
                matched,
            )
            recommendation["role_evidence"] = row["_role_evidence"]
        results.append(recommendation)

    if is_internship_request:
        results.sort(
            key=lambda item: (item["recommendation_score"], item["skill_match"]),
            reverse=True,
        )
        limited_skill_overlap_internships.sort(
            key=_internship_evidence_rank,
            reverse=True,
        )
        other_relevant_internships.sort(
            key=_internship_evidence_rank,
            reverse=True,
        )
        standard_match_count = len(results)
        limited_match_count = len(limited_skill_overlap_internships)
        incomplete_match_count = len(other_relevant_internships)
        results = results[:7]
        remaining_slots = max(0, 7 - len(results))
        limited_skill_overlap_internships = limited_skill_overlap_internships[
            :remaining_slots
        ]
        remaining_slots -= len(limited_skill_overlap_internships)
        other_relevant_internships = other_relevant_internships[:remaining_slots]

        source_sets = role_jobs["_skill_sources"].tolist()
        internship_coverage = {
            "verified_internship_listings": int(len(role_jobs)),
            "listings_with_explicit_skills": sum(
                any("tags" in sources for sources in skill_map.values())
                for skill_map in source_sets
            ),
            "listings_with_text_extracted_skills": sum(
                any(
                    "description" in sources or "title" in sources
                    for sources in skill_map.values()
                )
                for skill_map in source_sets
            ),
            "standard_skill_matches": standard_match_count,
            "limited_overlap_matches": limited_match_count,
            "incomplete_skill_records": incomplete_match_count,
            "displayed_listings": (
                len(results)
                + len(limited_skill_overlap_internships)
                + len(other_relevant_internships)
            ),
            "display_limit": 7,
            "coverage_limited": (
                standard_match_count
                + limited_match_count
                + incomplete_match_count
            ) < 5,
            "coverage_message": (
                f"The dataset contains {standard_match_count + limited_match_count + incomplete_match_count} suitable verified role-relevant internships."
                if standard_match_count + limited_match_count + incomplete_match_count < 5
                else ""
            ),
        }

    if not results:
        no_match_summary = empty_summary.copy()
        no_match_summary["jobs_analyzed"] = len(role_jobs)
        response = {
            "recommendations": [],
            "other_relevant_internships": other_relevant_internships,
            "limited_skill_overlap_internships": limited_skill_overlap_internships,
            "summary": no_match_summary,
        }
        if internship_coverage is not None:
            response["internship_coverage"] = internship_coverage
        return response

    # ---------------- Sort (same order as V4.2) ----------------

    if not is_internship_request:
        results.sort(
            key=lambda item: (item["recommendation_score"], item["skill_match"]),
            reverse=True
        )

    # ---------------- Summary (counted across ALL matches) ----------------

    summary = {
        "jobs_analyzed": len(role_jobs),
        "jobs_recommended": len(results),
        "excellent_matches": sum(
            1 for r in results if r["recommendation_score"] >= 75
        ),
        "strong_matches": sum(
            1 for r in results if 60 <= r["recommendation_score"] < 75
        ),
        "fresher_suitable_jobs": sum(
            1 for r in results if r["fresher_suitable"] == "Yes"
        ),
    }

    # ---------------- Return top 20 + summary ----------------

    response = {
        "recommendations": results[:20],
        "other_relevant_internships": other_relevant_internships,
        "limited_skill_overlap_internships": limited_skill_overlap_internships,
        "summary": summary,
    }
    if internship_coverage is not None:
        response["internship_coverage"] = internship_coverage
    return response
