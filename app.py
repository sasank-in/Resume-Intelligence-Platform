import os
import tempfile
import json
import time
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import PyPDF2
import google.generativeai as genai

# Import custom modules
from src.scrapers import LinkedInScraper
from src.builders import ProfileBuilder
from src.recommenders import JobRecommender

load_dotenv()

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_REQUESTS_PER_MINUTE = 30
REQUEST_TIMEOUT = 60  # seconds

# Configure Gemini AI
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

app = FastAPI(title="Resume Summarizer")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store resume data per session
sessions = {}
session_timestamps = {}

class ResumeAnalysis(BaseModel):
    session_id: str

class ChatMessage(BaseModel):
    message: str
    session_id: str

class LinkedInProfile(BaseModel):
    linkedin_url: str
    session_id: str

class JobRecommendationRequest(BaseModel):
    session_id: str

def cleanup_old_sessions():
    """Remove sessions older than REQUEST_TIMEOUT seconds"""
    current_time = time.time()
    expired_sessions = [
        sid for sid, timestamp in session_timestamps.items()
        if current_time - timestamp > REQUEST_TIMEOUT
    ]
    for sid in expired_sessions:
        if sid in sessions:
            del sessions[sid]
        del session_timestamps[sid]
        print(f"Cleaned up expired session: {sid}")

def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num} ---\n{page_text}"
        return text

def extract_resume_data(resume_text):
    """Extract structured resume data using Gemini AI"""
    prompt = f"""Analyze the following resume and extract the information in JSON format with these exact fields:
{{
    "name": "Full name",
    "email": "Email address",
    "phone": "Phone number",
    "location": "City/Country",
    "headline": "Professional headline (2-3 words)",
    "summary": "Brief professional summary (2-3 sentences)",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "title": "Job title",
            "company": "Company name",
            "duration": "Start - End (e.g., Jan 2020 - Present)",
            "highlights": ["achievement1", "achievement2", "achievement3"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree name",
            "institution": "University/School",
            "year": "Graduation year",
            "details": "Additional details"
        }}
    ],
    "certifications": ["cert1", "cert2"],
    "languages": ["lang1", "lang2"],
    "strengths": ["key strength 1", "key strength 2", "key strength 3"],
    "recommendations": ["improvement 1", "improvement 2"]
}}

RESUME TEXT:
{resume_text}

Return ONLY the JSON, no other text. Ensure all arrays have at least one item."""
    
    response = model.generate_content(prompt)
    try:
        # Extract JSON from response
        json_str = response.text.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        
        json_str = json_str.strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON parsing error: {e}, raw response: {response.text[:200]}")
        return {"raw_analysis": response.text}

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), session_id: str = Form(...)):
    """Upload and analyze resume"""
    # Cleanup old sessions
    cleanup_old_sessions()
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_path = None
    try:
        print(f"Starting upload for session: {session_id}, file: {file.filename}")
        
        # Save uploaded file temporarily
        content = await file.read()
        file_size = len(content)
        print(f"File size: {file_size} bytes")
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            temp_path = tmp.name
        
        print(f"Temp file saved: {temp_path}")
        
        # Extract text from PDF
        resume_text = extract_pdf_text(temp_path)
        print(f"Extracted {len(resume_text)} characters from PDF")
        
        # Extract structured resume data
        resume_data = extract_resume_data(resume_text)
        print(f"Extracted resume data: {list(resume_data.keys())}")
        
        # Store session data
        sessions[session_id] = {
            "resume_text": resume_text,
            "resume_data": resume_data,
            "linkedin_data": None,
            "unified_profile": None
        }
        
        session_timestamps[session_id] = time.time()
        
        print(f"Session created: {session_id}, Total sessions: {len(sessions)}")
        
        return {
            "message": "Resume analyzed successfully",
            "resume_data": resume_data,
            "characters": len(resume_text)
        }
    
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                print(f"Cleaned up temp file: {temp_path}")
            except Exception as cleanup_error:
                print(f"Failed to clean up temp file: {cleanup_error}")

@app.post("/get-analysis")
async def get_analysis(analysis_request: ResumeAnalysis):
    """Get detailed analysis and recommendations"""
    session_id = analysis_request.session_id
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No resume uploaded for this session")
    
    try:
        resume_data = sessions[session_id]["resume_data"]
        
        # Get resume data
        resume_text = sessions[session_id]["resume_text"]
        
        analysis_prompt = f"""Analyze this resume and provide a comprehensive career analysis in JSON format.

RESUME CONTENT:
{resume_text}

Generate a detailed analysis with these fields. Let the AI determine all values based on the resume content:

{{
    "overall_score": "Your assessment of overall professional profile (include score and reasoning)",
    "career_trajectory": "Analysis of career progression and growth pattern",
    "key_strengths": "Top 3 professional strengths identified from the resume",
    "improvement_areas": "3 areas for professional development",
    "industry_fit": "Industries and sectors best suited for this candidate",
    "next_career_moves": "3 recommended next career steps",
    "suggested_job_summary": "A concise 3-4 sentence job summary suitable for a job application based on the resume"
}}

IMPORTANT:
- Generate ALL values based on the resume content
- Do NOT use any pre-defined values or templates
- Do NOT use any fixed context
- Analyze the ACTUAL resume and generate UNIQUE insights
- Be specific and reference actual skills, roles, companies, achievements
- Provide actionable, personalized recommendations
- Return ONLY valid JSON, no other text"""
        
        response = model.generate_content(analysis_prompt)
        response_text = response.text.strip()
        
        # Try to extract JSON
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback analysis if JSON fails
            analysis = {
                "overall_score": "Analysis generated",
                "career_trajectory": response_text[:150] if response_text else "See profile data above",
                "key_strengths": resume_data.get('summary', 'Professional expertise'),
                "improvement_areas": "Continuous learning recommended",
                "industry_fit": "Multiple sectors",
                "technical_skills_assessment": f"Skilled in {len(resume_data.get('skills', []))} technical areas",
                "soft_skills_assessment": "Leadership and collaboration evident",
                "achievement_highlights": "Check experience section",
                "gap_analysis": "Review skill gaps for growth",
                "salary_expectations": "Market competitive",
                "next_career_moves": "Senior progression or specialization",
                "competitive_advantage": "Unique background",
                "interview_talking_points": "Highlight key achievements",
                "recommendations_summary": "Continue professional development",
                "suggested_job_summary": resume_data.get('summary', 'Professional summary based on resume')
            }
        
        return {
            "resume_data": resume_data,
            "analysis": analysis
        }
    
    except Exception as e:
        print(f"Error in get_analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return basic analysis even on error
        return {
            "resume_data": sessions[session_id].get("resume_data", {}),
            "analysis": {
                "overall_score": "Analysis in progress",
                "career_trajectory": str(e)[:100],
                "key_strengths": "View profile above",
                "improvement_areas": "-",
                "industry_fit": "-",
                "technical_skills_assessment": "-",
                "soft_skills_assessment": "-",
                "achievement_highlights": "-",
                "gap_analysis": "-",
                "salary_expectations": "-",
                "next_career_moves": "-",
                "competitive_advantage": "-",
                "interview_talking_points": "-",
                "recommendations_summary": "-"
            }
        }

@app.post("/chat")
async def chat_with_ai(chat_request: ChatMessage):
    """Chat with AI about the resume"""
    session_id = chat_request.session_id
    message = chat_request.message
    
    print(f"Chat request - Session ID: {session_id}, Available sessions: {list(sessions.keys())}")
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No resume uploaded for this session. Please upload a resume first.")
    
    try:
        resume_data = sessions[session_id]["resume_data"]
        
        # Initialize chat history if not exists
        if "chat_history" not in sessions[session_id]:
            sessions[session_id]["chat_history"] = []
        
        chat_history = sessions[session_id]["chat_history"]
        
        # Build context from chat history
        history_context = ""
        if chat_history:
            history_context = "\nPrevious conversation:\n"
            for qa in chat_history[-3:]:  # Last 3 messages
                history_context += f"User: {qa['user']}\nAssistant: {qa['assistant']}\n"
        
        # Create AI prompt - simplified for reliability
        prompt = f"""You are a friendly career coach. Answer the user's question about their resume.

Candidate: {resume_data.get('name', 'Candidate')}
Summary: {resume_data.get('summary', 'Professional')}
Skills: {', '.join(resume_data.get('skills', [])[:10])}
Roles: {', '.join([exp.get('title', '') for exp in resume_data.get('experience', [])[:3]])}

{history_context}

User: {message}

Provide a helpful, conversational response (2-3 sentences). Be supportive and actionable."""
        
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        
        # Store in chat history
        chat_history.append({
            "user": message,
            "assistant": ai_response
        })
        
        return {
            "response": ai_response
        }
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/add-linkedin")
async def add_linkedin_profile(linkedin_request: LinkedInProfile):
    """Extract LinkedIn profile and merge with resume data"""
    session_id = linkedin_request.session_id
    linkedin_url = linkedin_request.linkedin_url
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No resume uploaded for this session")
    
    try:
        print(f"🔗 Processing LinkedIn profile: {linkedin_url}")
        
        # Extract LinkedIn data
        scraper = LinkedInScraper(headless=True)
        linkedin_data = scraper.extract_profile(linkedin_url)
        
        if not linkedin_data:
            raise HTTPException(status_code=400, detail="Failed to extract LinkedIn profile")
        
        # Store LinkedIn data
        sessions[session_id]["linkedin_data"] = linkedin_data
        
        # Build unified profile
        resume_data = sessions[session_id]["resume_data"]
        unified_profile = ProfileBuilder.merge_profiles(resume_data, linkedin_data)
        sessions[session_id]["unified_profile"] = unified_profile
        
        print(f"✓ Unified profile created with {len(unified_profile.get('skills', []))} skills")
        
        return {
            "message": "LinkedIn profile added successfully",
            "linkedin_data": linkedin_data,
            "unified_profile": unified_profile
        }
    
    except Exception as e:
        print(f"LinkedIn extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LinkedIn extraction failed: {str(e)}")

@app.post("/skip-linkedin")
async def skip_linkedin(analysis_request: ResumeAnalysis):
    """Build profile from resume only (skip LinkedIn)"""
    session_id = analysis_request.session_id
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No resume uploaded for this session")
    
    try:
        resume_data = sessions[session_id]["resume_data"]
        
        # Build unified profile from resume only
        unified_profile = ProfileBuilder.merge_profiles(resume_data, None)
        sessions[session_id]["unified_profile"] = unified_profile
        
        print(f"✓ Resume-only profile created")
        
        return {
            "message": "Profile created from resume only",
            "unified_profile": unified_profile
        }
    
    except Exception as e:
        print(f"Profile building error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Profile building failed: {str(e)}")

@app.post("/recommend-jobs")
async def recommend_jobs(job_request: JobRecommendationRequest):
    """Generate job recommendations based on unified profile"""
    session_id = job_request.session_id
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No profile found for this session")
    
    if not sessions[session_id].get("unified_profile"):
        raise HTTPException(status_code=400, detail="Please complete profile building first")
    
    try:
        unified_profile = sessions[session_id]["unified_profile"]
        
        print(f"🎯 Generating job recommendations for {unified_profile.get('name', 'candidate')}")
        
        # Generate recommendations
        recommender = JobRecommender()
        recommendations = recommender.recommend_jobs(unified_profile, num_recommendations=5)
        
        # Store recommendations in session
        sessions[session_id]["recommendations"] = recommendations
        
        print(f"✓ Generated {len(recommendations.get('recommendations', []))} job recommendations")
        
        return {
            "message": "Job recommendations generated successfully",
            "recommendations": recommendations
        }
    
    except Exception as e:
        print(f"Job recommendation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\nStarting Resume Summarizer...")
    print("Open your browser to: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
