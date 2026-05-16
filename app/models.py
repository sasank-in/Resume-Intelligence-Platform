"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List, Dict

class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    session_id: str

class ChatMessage(BaseModel):
    """Request model for chat interaction"""
    message: str
    session_id: str

class LinkedInProfileRequest(BaseModel):
    """Request model for LinkedIn profile addition via Selenium scrape."""
    linkedin_url: str
    session_id: str


class LinkedInPasteRequest(BaseModel):
    """Request model for LinkedIn profile via pasted text (preferred, no scraping)."""
    linkedin_text: str
    session_id: str

class JobRecommendationRequest(BaseModel):
    """Request model for job recommendations"""
    session_id: str

class ATSCheckRequest(BaseModel):
    """Request model for ATS compatibility check"""
    session_id: str
    job_description: str
    target_role: Optional[str] = None
    ats_system: Optional[str] = "Generic"

class ATSSuggestionsRequest(BaseModel):
    """Request model for ATS improvement suggestions"""
    session_id: str
    improvement_type: Optional[str] = "all"  # keywords/format/structure/all

class ResumeData(BaseModel):
    """Resume data model"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict] = []
    education: List[Dict] = []
    certifications: List[str] = []
    languages: List[str] = []

class AnalysisResponse(BaseModel):
    """Analysis response model"""
    resume_data: Dict
    analysis: Dict

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str

class ProfileResponse(BaseModel):
    """Unified profile response"""
    unified_profile: Dict
    message: Optional[str] = None
    info: Optional[str] = None
    warning: Optional[str] = None

class JobRequirements(BaseModel):
    """Job requirements model for candidate screening"""
    job_title: str
    required_skills: List[str]
    preferred_skills: List[str] = []
    min_experience_years: float = 0
    max_experience_years: float = 100
    required_degree: Optional[str] = None
    description: Optional[str] = None
