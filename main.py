"""FastAPI app entrypoint for Resume Summarizer."""
import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    CORS_ORIGINS,
    ENV,
    IS_PROD,
    RATE_LIMIT_DEFAULT,
    RATE_LIMIT_LLM,
    RATE_LIMIT_UPLOAD,
    STATIC_DIR,
)
from app.observability import init_sentry
from app import health
from app.handlers import (
    ChatHandlers,
    JobHandlers,
    LinkedInHandlers,
    ResumeHandlers,
)
from app.logging_config import get_logger, setup_logging
from app.models import (
    ATSSuggestionsRequest,
    ChatMessage,
    JobRecommendationRequest,
    LinkedInPasteRequest,
    LinkedInProfileRequest,
    ResumeAnalysisRequest,
)
from app.screening_routes import screening_router
from app.session_manager import build_session_manager, session_cleanup_loop
from src.recommenders import JobRecommender
from src.utils.ats_checker import ATSChecker

setup_logging()
log = get_logger(__name__)
init_sentry(release=APP_VERSION, environment=ENV)

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_manager = build_session_manager()
    job_recommender = JobRecommender()
    ats_checker = ATSChecker()

    app.state.session_manager = session_manager
    app.state.resume_handlers = ResumeHandlers(session_manager)
    app.state.chat_handlers = ChatHandlers(session_manager)
    app.state.linkedin_handlers = LinkedInHandlers(session_manager)
    app.state.job_handlers = JobHandlers(session_manager, job_recommender, ats_checker)

    cleanup_task = asyncio.create_task(session_cleanup_loop(session_manager))
    log.info("app_started", extra={"env": "prod" if IS_PROD else "dev"})
    try:
        yield
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        log.info("app_stopped")


OPENAPI_TAGS = [
    {"name": "pages", "description": "HTML pages served to the browser."},
    {"name": "resume", "description": "Resume upload, parsing, and AI analysis."},
    {"name": "chat", "description": "Conversational AI about the uploaded resume."},
    {"name": "linkedin", "description": "Optional LinkedIn profile merge."},
    {"name": "jobs", "description": "Job recommendations and ATS compatibility."},
    {"name": "job-tools", "description": "Standalone JD analyzer and market insights."},
    {"name": "screening", "description": "Recruiter-side batch resume screening."},
    {"name": "system", "description": "Health, liveness, version."},
]

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    # Hide docs in prod by default; expose via env if needed.
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        allow_credentials=True,
    )

app.include_router(screening_router)


def _serve_html(name: str) -> FileResponse:
    path = os.path.join(STATIC_DIR, name)
    if not os.path.isfile(path):
        return JSONResponse({"detail": f"{name} not found"}, status_code=404)
    return FileResponse(path, media_type="text/html")


@app.get("/", tags=["pages"], summary="Home page (upload UI)")
async def home():
    return _serve_html("index.html")


@app.get("/analysis.html", tags=["pages"], summary="Analysis results page")
async def analysis_page():
    return _serve_html("analysis.html")


@app.get("/jobs.html", tags=["pages"], summary="Job tools page")
async def jobs_page():
    return _serve_html("jobs.html")


@app.get("/screening.html", tags=["pages"], summary="Recruiter screening page")
async def screening_page():
    return _serve_html("screening.html")


@app.post(
    "/upload",
    tags=["resume"],
    summary="Upload and parse a resume PDF",
    description="Accepts a PDF (≤ MAX_FILE_SIZE), extracts text via pypdf, "
                "asks the LLM for structured fields, and stores the result in the session.",
)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    session_id: str = Form(...),
):
    return await request.app.state.resume_handlers.upload_resume(file, session_id)


@app.post(
    "/get-analysis",
    tags=["resume"],
    summary="Run AI career analysis for the uploaded resume",
)
@limiter.limit(RATE_LIMIT_LLM)
async def get_analysis(request: Request, payload: ResumeAnalysisRequest):
    return await request.app.state.resume_handlers.get_analysis(payload)


@app.post(
    "/chat",
    tags=["chat"],
    summary="Ask the AI a question about your resume",
)
@limiter.limit(RATE_LIMIT_LLM)
async def chat(request: Request, payload: ChatMessage):
    return await request.app.state.chat_handlers.chat(payload)


@app.post(
    "/add-linkedin",
    tags=["linkedin"],
    summary="Merge LinkedIn profile data (Selenium scrape)",
    description="Heavily rate-limited because each call spins up a headless Chrome.",
)
@limiter.limit("5/minute")
async def add_linkedin_profile(request: Request, payload: LinkedInProfileRequest):
    return await request.app.state.linkedin_handlers.add_linkedin_profile(payload)


@app.post(
    "/paste-linkedin",
    tags=["linkedin"],
    summary="Merge LinkedIn profile from pasted text (no scraping)",
    description="Preferred alternative to /add-linkedin. User pastes the visible "
                "text of their LinkedIn profile; we feed it to the LLM to extract "
                "structured data, then merge with resume.",
)
@limiter.limit(RATE_LIMIT_LLM)
async def paste_linkedin_profile(request: Request, payload: LinkedInPasteRequest):
    return await request.app.state.linkedin_handlers.paste_linkedin_profile(payload)


@app.post(
    "/skip-linkedin",
    tags=["linkedin"],
    summary="Build unified profile from resume only (skip LinkedIn)",
)
async def skip_linkedin(request: Request, payload: ResumeAnalysisRequest):
    return await request.app.state.linkedin_handlers.skip_linkedin(payload)


@app.post(
    "/recommend-jobs",
    tags=["jobs"],
    summary="AI-recommended job matches based on the unified profile",
)
@limiter.limit(RATE_LIMIT_LLM)
async def recommend_jobs(request: Request, payload: JobRecommendationRequest):
    return await request.app.state.job_handlers.recommend_jobs(payload)


@app.post(
    "/check-ats",
    tags=["jobs"],
    summary="ATS compatibility score against a job description",
)
@limiter.limit(RATE_LIMIT_LLM)
async def check_ats_compatibility(
    request: Request,
    session_id: str = Form(...),
    job_description: str = Form(...),
    target_role: str = Form(None),
    ats_system: str = Form("Generic"),
):
    return await request.app.state.job_handlers.check_ats_compatibility(
        session_id, job_description, target_role, ats_system
    )


@app.post(
    "/ats-suggestions",
    tags=["jobs"],
    summary="Targeted ATS improvement suggestions (requires prior /check-ats)",
)
@limiter.limit(RATE_LIMIT_LLM)
async def get_ats_suggestions(request: Request, payload: ATSSuggestionsRequest):
    return await request.app.state.job_handlers.get_ats_suggestions(
        payload.session_id, payload.improvement_type
    )


@app.post(
    "/analyze-job",
    tags=["job-tools"],
    summary="Analyze a job description on its own (no resume needed)",
)
@limiter.limit(RATE_LIMIT_LLM)
async def analyze_job_description(
    request: Request,
    job_description: str = Form(...),
    target_role: str = Form(None),
    analysis_type: str = Form("comprehensive"),
):
    return await request.app.state.job_handlers.analyze_job_standalone(
        job_description, target_role, analysis_type
    )


@app.post(
    "/market-insights",
    tags=["job-tools"],
    summary="Salary, demand, top skills for a given role",
)
@limiter.limit(RATE_LIMIT_LLM)
async def get_market_insights(
    request: Request,
    job_role: str = Form(...),
    experience_level: str = Form(None),
    industry: str = Form(None),
    location: str = Form(None),
):
    return await request.app.state.job_handlers.get_market_data(
        job_role, experience_level, industry, location
    )


@app.get(
    "/health",
    tags=["system"],
    summary="Liveness + dependency probes (Redis, Groq)",
    description="Returns 200 if the app is up. The `checks` field reports the "
                "status of each external dependency. Use this as a readiness probe.",
)
async def health_check(request: Request):
    return await health.run_checks(request.app.state)


if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    log.info(f"Starting {APP_TITLE}; open http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=not IS_PROD)
