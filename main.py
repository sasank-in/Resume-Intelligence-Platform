"""
Main FastAPI application entry point
Resume Summarizer - AI-powered resume analysis and job recommendation system
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, STATIC_DIR, REQUEST_TIMEOUT
from app.models import (
    ResumeAnalysisRequest, ChatMessage, LinkedInProfileRequest,
    JobRecommendationRequest, ATSCheckRequest, ATSSuggestionsRequest
)
from app.session_manager import SessionManager
from app.handlers import (
    ResumeHandlers, ChatHandlers, LinkedInHandlers, JobHandlers
)
from app.screening_routes import screening_router

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Initialize session manager
session_manager = SessionManager(timeout=REQUEST_TIMEOUT)

# Initialize handlers
resume_handlers = ResumeHandlers(session_manager)
chat_handlers = ChatHandlers(session_manager)
linkedin_handlers = LinkedInHandlers(session_manager)
job_handlers = JobHandlers(session_manager)

# Include screening router
app.include_router(screening_router)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve home page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Static files not found. Please ensure static/index.html exists."
        )


@app.get("/analysis.html", response_class=HTMLResponse)
async def analysis_page():
    """Serve analysis page"""
    try:
        with open("static/analysis.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Analysis page not found. Please ensure static/analysis.html exists."
        )


@app.get("/jobs.html", response_class=HTMLResponse)
async def jobs_page():
    """Serve jobs & ATS page"""
    try:
        with open("static/jobs.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Jobs page not found. Please ensure static/jobs.html exists."
        )


@app.get("/screening.html", response_class=HTMLResponse)
async def screening_page():
    """Serve resume screening page"""
    try:
        with open("static/screening.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Screening page not found. Please ensure static/screening.html exists."
        )


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), session_id: str = Form(...)):
    """
    Upload and analyze resume PDF
    
    - **file**: PDF file to upload
    - **session_id**: Unique session identifier
    """
    return await resume_handlers.upload_resume(file, session_id)


@app.post("/get-analysis")
async def get_analysis(request: ResumeAnalysisRequest):
    """
    Get detailed analysis of uploaded resume
    
    - **session_id**: Unique session identifier
    """
    return await resume_handlers.get_analysis(request)


@app.post("/chat")
async def chat(request: ChatMessage):
    """
    Chat with AI about the resume
    
    - **message**: User message/question
    - **session_id**: Unique session identifier
    """
    return await chat_handlers.chat(request)


@app.post("/add-linkedin")
async def add_linkedin_profile(request: LinkedInProfileRequest):
    """
    Extract and add LinkedIn profile data
    
    - **linkedin_url**: LinkedIn profile URL
    - **session_id**: Unique session identifier
    """
    return await linkedin_handlers.add_linkedin_profile(request)


@app.post("/skip-linkedin")
async def skip_linkedin(request: ResumeAnalysisRequest):
    """
    Skip LinkedIn and build profile from resume only
    
    - **session_id**: Unique session identifier
    """
    return await linkedin_handlers.skip_linkedin(request)


@app.post("/recommend-jobs")
async def recommend_jobs(request: JobRecommendationRequest):
    """
    Generate job recommendations based on unified profile
    
    - **session_id**: Unique session identifier
    """
    return await job_handlers.recommend_jobs(request)


@app.post("/check-ats")
async def check_ats_compatibility(session_id: str = Form(...), 
                                job_description: str = Form(...),
                                target_role: str = Form(None),
                                ats_system: str = Form("Generic")):
    """
    Check ATS compatibility against job description
    
    - **session_id**: Unique session identifier
    - **job_description**: Job posting description
    - **target_role**: Target role title (optional)
    - **ats_system**: Target ATS system (optional)
    """
    return await job_handlers.check_ats_compatibility(session_id, job_description, target_role, ats_system)


@app.post("/ats-suggestions")
async def get_ats_suggestions(request: ATSSuggestionsRequest):
    """
    Get specific ATS improvement suggestions
    
    - **session_id**: Unique session identifier
    - **improvement_type**: Type of improvements (keywords/format/structure/all)
    """
    return await job_handlers.get_ats_suggestions(request.session_id, request.improvement_type)


@app.post("/analyze-job")
async def analyze_job_description(job_description: str = Form(...),
                                target_role: str = Form(None),
                                analysis_type: str = Form("comprehensive")):
    """
    Analyze job description without resume (standalone)
    
    - **job_description**: Job posting description
    - **target_role**: Target role title (optional)
    - **analysis_type**: Type of analysis (comprehensive/skills/ats/market)
    """
    return await job_handlers.analyze_job_standalone(job_description, target_role, analysis_type)


@app.post("/market-insights")
async def get_market_insights(job_role: str = Form(...),
                            experience_level: str = Form(None),
                            industry: str = Form(None),
                            location: str = Form(None)):
    """
    Get job market insights for specific role
    
    - **job_role**: Job role/title to research
    - **experience_level**: Experience level (entry/mid/senior/lead)
    - **industry**: Industry sector (optional)
    - **location**: Location (optional)
    """
    return await job_handlers.get_market_data(job_role, experience_level, industry, location)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": APP_TITLE}


# Mount static files AFTER all routes are defined
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    print(f"\nStarting {APP_TITLE}...")
    print("Open your browser to: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
