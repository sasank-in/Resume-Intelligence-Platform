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
    """Request model for LinkedIn profile addition"""
    linkedin_url: str
    session_id: str

class JobRecommendationRequest(BaseModel):
    """Request model for job recommendations"""
    session_id: str

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
