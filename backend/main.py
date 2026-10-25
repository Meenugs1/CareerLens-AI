from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from backend.market_intelligence_service import get_market_intelligence
from backend.recommendation_service import _load_dataset, get_recommendations
from backend.skill_gap_service import analyze_skill_gap
from backend.career_simulator_service import simulate_skill_change
from backend.career_switch_service import analyze_career_switch
from backend.career_path_service import _build_title_profiles, explore_career_path
from backend.what_can_i_become_service import (
    _build_matching_index,
    find_matching_roles,
)
from backend.company_intelligence_service import (
    _build_company_index,
    get_company_intelligence,
    search_companies,
)


app = FastAPI(
    title="CareerLens AI API",
    description="AI-powered job recommendation and skill gap analysis API",
    version="1.0.0"
)


@app.on_event("startup")
def preload_recommendation_dataset():
    dataframe = _load_dataset()
    _build_title_profiles(dataframe)
    _build_matching_index(dataframe)
    _build_company_index(dataframe)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://career-lens-ai-khaki.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class RecommendationRequest(BaseModel):
    role: str
    skills: List[str]
    experience: float = 0
    location: str = "Any"
    work_mode: str = "Any"
    job_type: str = "Any"


class SkillGapRequest(BaseModel):
    role: str
    skills: List[str]


class CareerSimulatorRequest(BaseModel):
    role: str
    skills: List[str]
    add_skill: str


class CareerSwitchRequest(BaseModel):
    current_role: str
    current_skills: List[str]
    target_role: str


class WhatCanIBecomeRequest(BaseModel):
    skills: List[str]


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "message": "CareerLens AI API is running!",
        "version": "1.0"
    }


# ============================================================
# JOB RECOMMENDATION ENDPOINT
# ============================================================

@app.post("/recommend")
def recommend_jobs(request: RecommendationRequest):

    results = get_recommendations(
        target_role=request.role,
        skills=request.skills,
        experience=request.experience,
        preferred_location=request.location,
        work_mode=request.work_mode,
        job_type=request.job_type
    )

    return {
        "success": True,
        "role": request.role,
        "results": results
    }


@app.get("/market-intelligence")
def market_intelligence(role: str | None = None):
    return get_market_intelligence(role)


@app.post("/skill-gap")
def skill_gap(request: SkillGapRequest):
    return analyze_skill_gap(request.role, request.skills)


@app.post("/career-simulator")
def career_simulator(request: CareerSimulatorRequest):
    return simulate_skill_change(
        request.role,
        request.skills,
        request.add_skill,
    )


@app.post("/career-switch")
def career_switch(request: CareerSwitchRequest):
    return analyze_career_switch(
        request.current_role,
        request.current_skills,
        request.target_role,
    )


@app.get("/career-path")
def career_path(role: str | None = None):
    return explore_career_path(role)


@app.post("/what-can-i-become")
def what_can_i_become(request: WhatCanIBecomeRequest):
    return find_matching_roles(request.skills)


@app.get("/companies")
def companies(query: str | None = None):
    return search_companies(query)


@app.get("/company-intelligence")
def company_intelligence(company: str | None = None):
    return get_company_intelligence(company)