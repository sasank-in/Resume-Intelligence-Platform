"""
API Routes for Resume Screening System
Add these routes to your main FastAPI application
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
import json

from .screening_handlers import ScreeningHandlers
from .models import JobRequirements


# Create router
screening_router = APIRouter(prefix="/screening", tags=["screening"])

# Initialize handlers
screening_handlers = ScreeningHandlers()


@screening_router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse a single resume and extract structured data
    
    Upload a PDF resume to extract:
    - Contact information
    - Skills by category
    - Work experience
    - Education
    - Total years of experience
    """
    return await screening_handlers.parse_single_resume(file)


@screening_router.post("/screen-candidate")
async def screen_candidate(
    file: UploadFile = File(...),
    job_requirements: str = Form(...)
):
    """
    Screen a single candidate against job requirements
    
    Provides:
    - Overall score (0-100)
    - Status (HIGHLY_RECOMMENDED, RECOMMENDED, MAYBE, NOT_RECOMMENDED)
    - Detailed breakdown by skills, experience, education
    - Matched skills and gaps
    """
    requirements = json.loads(job_requirements)
    return await screening_handlers.screen_single_candidate(file, requirements)


@screening_router.post("/screen-batch")
async def screen_batch(
    files: List[UploadFile] = File(...),
    job_requirements: str = Form(...)
):
    """
    Screen multiple candidates in batch
    
    Upload multiple resume PDFs to:
    - Score and rank all candidates
    - Generate summary statistics
    - Identify top candidates for interviews
    - Export detailed reports
    """
    requirements = json.loads(job_requirements)
    return await screening_handlers.screen_batch(files, requirements)


@screening_router.post("/compare-candidates")
async def compare_candidates(
    files: List[UploadFile] = File(...),
    job_requirements: str = Form(...)
):
    """
    Compare 2-5 candidates side-by-side
    
    Provides:
    - Comparison matrix with all scores
    - Winner identification
    - Skill match comparison
    - Experience comparison
    """
    requirements = json.loads(job_requirements)
    return await screening_handlers.compare_candidates(files, requirements)


@screening_router.get("/job-requirements-template")
async def get_job_requirements_template():
    """
    Get a template for job requirements
    
    Returns a sample job requirements structure that can be customized
    """
    return screening_handlers.get_job_requirements_template()


# Add these routes to your main.py:
"""
from app.screening_routes import screening_router

app.include_router(screening_router)
"""
