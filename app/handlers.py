"""
Route handlers for FastAPI endpoints
"""
import tempfile
import os
from fastapi import HTTPException, UploadFile, Form
from typing import Dict

from . import services
from .models import (
    ResumeAnalysisRequest, ChatMessage, LinkedInProfileRequest,
    JobRecommendationRequest
)
from .session_manager import SessionManager, validate_file_upload
from .config import MAX_FILE_SIZE, ALLOWED_FILE_TYPES

from src.scrapers import LinkedInScraper
from src.builders import ProfileBuilder
from src.recommenders import JobRecommender


class ResumeHandlers:
    """Handlers for resume-related endpoints"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def upload_resume(self, file: UploadFile, session_id: str) -> Dict:
        """
        Upload and analyze resume PDF
        
        Args:
            file: Uploaded PDF file
            session_id: Unique session identifier
            
        Returns:
            Dictionary with resume data
        """
        self.session_manager.cleanup_old_sessions()
        
        if not validate_file_upload(file.filename, ALLOWED_FILE_TYPES):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        temp_path = None
        try:
            print(f"[INFO] Processing upload for session: {session_id}, file: {file.filename}")
            
            content = await file.read()
            file_size = len(content)
            print(f"[INFO] File size: {file_size} bytes")
            
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
            
            print(f"[INFO] Temp file saved: {temp_path}")
            
            resume_text = services.extract_pdf_text(temp_path)
            print(f"[INFO] Extracted {len(resume_text)} characters from PDF")
            
            resume_data = services.extract_resume_data(resume_text)
            print(f"[INFO] Extracted resume data: {list(resume_data.keys())}")
            
            self.session_manager.create_session(session_id, {
                "resume_text": resume_text,
                "resume_data": resume_data,
                "linkedin_data": None,
                "unified_profile": None
            })
            
            print(f"[INFO] Session created: {session_id}")
            
            return {
                "message": "Resume analyzed successfully",
                "resume_data": resume_data,
                "characters": len(resume_text)
            }
        
        except Exception as e:
            print(f"[ERROR] Upload error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print(f"[INFO] Cleaned up temp file: {temp_path}")
                except Exception as e:
                    print(f"[WARNING] Failed to clean up temp file: {e}")
    
    async def get_analysis(self, request: ResumeAnalysisRequest) -> Dict:
        """
        Get detailed analysis of resume
        
        Args:
            request: Analysis request with session_id
            
        Returns:
            Dictionary with resume data and analysis
        """
        session_id = request.session_id
        session_data = self.session_manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=400, detail="No resume uploaded for this session")
        
        try:
            resume_data = session_data["resume_data"]
            resume_text = session_data["resume_text"]
            
            analysis = services.generate_detailed_analysis(resume_data, resume_text)
            
            return {
                "resume_data": resume_data,
                "analysis": analysis
            }
        
        except Exception as e:
            print(f"[ERROR] Analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


class ChatHandlers:
    """Handlers for chat-related endpoints"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def chat(self, request: ChatMessage) -> Dict:
        """
        Chat with AI about resume
        
        Args:
            request: Chat message with session_id
            
        Returns:
            Dictionary with AI response
        """
        session_id = request.session_id
        message = request.message
        
        print(f"[INFO] Chat request - Session ID: {session_id}")
        
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=400,
                detail="No resume uploaded for this session. Please upload a resume first."
            )
        
        try:
            resume_data = session_data["resume_data"]
            
            if "chat_history" not in session_data:
                session_data["chat_history"] = []
            
            chat_history = session_data["chat_history"]
            
            ai_response = services.generate_chat_response(
                resume_data, message, chat_history
            )
            
            chat_history.append({
                "user": message,
                "assistant": ai_response
            })
            
            self.session_manager.update_session(session_id, {"chat_history": chat_history})
            
            return {"response": ai_response}
        
        except Exception as e:
            print(f"[ERROR] Chat error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


class LinkedInHandlers:
    """Handlers for LinkedIn-related endpoints"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def add_linkedin_profile(self, request: LinkedInProfileRequest) -> Dict:
        """
        Extract and add LinkedIn profile
        
        Args:
            request: LinkedIn profile request with session_id and URL
            
        Returns:
            Dictionary with unified profile
        """
        session_id = request.session_id
        linkedin_url = request.linkedin_url
        
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=400, detail="No resume uploaded for this session")
        
        try:
            print(f"[INFO] Processing LinkedIn profile: {linkedin_url}")
            
            scraper = LinkedInScraper(headless=True)
            linkedin_data = scraper.extract_profile(linkedin_url)
            
            # Filter out None values from LinkedIn data
            linkedin_data_clean = {k: v for k, v in linkedin_data.items() if v is not None and v != []}
            
            resume_data = session_data["resume_data"]
            unified_profile = ProfileBuilder.merge_profiles(resume_data, linkedin_data_clean if linkedin_data_clean else None)
            
            # Clean up None and "N/A" values from unified profile for UI display
            unified_profile_clean = self._clean_profile_data(unified_profile)
            
            self.session_manager.update_session(session_id, {
                "linkedin_data": linkedin_data_clean,
                "unified_profile": unified_profile_clean
            })
            
            skills_count = len([s for s in unified_profile_clean.get('skills', []) if s and s != "N/A"])
            exp_count = len([e for e in unified_profile_clean.get('experience', []) if e.get('title') and e.get('title') != "N/A"])
            
            print(f"[INFO] Unified profile created with {skills_count} skills and {exp_count} experiences")
            
            return {
                "message": "LinkedIn profile processed successfully",
                "linkedin_data": linkedin_data_clean,
                "unified_profile": unified_profile_clean,
                "info": "Merged data from resume + LinkedIn (Resume data used where LinkedIn extraction was incomplete)"
            }
        
        except Exception as e:
            print(f"[ERROR] LinkedIn extraction error: {str(e)}")
            
            try:
                resume_data = session_data["resume_data"]
                unified_profile = ProfileBuilder.merge_profiles(resume_data, None)
                unified_profile_clean = self._clean_profile_data(unified_profile)
                self.session_manager.update_session(session_id, {"unified_profile": unified_profile_clean})
                
                return {
                    "message": "LinkedIn scraping encountered issues, using resume data instead",
                    "unified_profile": unified_profile_clean,
                    "warning": f"Could not extract LinkedIn data: {str(e)}"
                }
            except:
                raise HTTPException(status_code=500, detail=f"LinkedIn extraction failed: {str(e)}")
    
    
    def _clean_profile_data(self, profile: Dict) -> Dict:
        """Remove None and 'N/A' values from profile for UI display"""
        cleaned = {}
        
        for key, value in profile.items():
            if key == "experience" or key == "education":
                # Filter out entries with None/N/A titles
                cleaned[key] = [
                    item for item in (value or [])
                    if item and item.get(list(item.keys())[0]) and item.get(list(item.keys())[0]) != "N/A"
                ]
            elif key == "skills" or key == "certifications" or key == "languages":
                # Filter out None/"N/A" from lists
                cleaned[key] = [s for s in (value or []) if s and s != "N/A"]
            elif key == "data_sources":
                cleaned[key] = value
            elif value and value != "N/A":
                # Keep non-None, non-"N/A" values
                cleaned[key] = value
        
        return cleaned
    
    async def skip_linkedin(self, request: ResumeAnalysisRequest) -> Dict:
        """
        Skip LinkedIn and build profile from resume only
        
        Args:
            request: Analysis request with session_id
            
        Returns:
            Dictionary with profile data
        """
        session_id = request.session_id
        
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=400, detail="No resume uploaded for this session")
        
        try:
            resume_data = session_data["resume_data"]
            
            unified_profile = ProfileBuilder.merge_profiles(resume_data, None)
            unified_profile_clean = self._clean_profile_data(unified_profile)
            self.session_manager.update_session(session_id, {"unified_profile": unified_profile_clean})
            
            print("[INFO] Resume-only profile created")
            
            return {
                "message": "Profile created from resume only",
                "unified_profile": unified_profile_clean
            }
        
        except Exception as e:
            print(f"[ERROR] Profile building error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Profile building failed: {str(e)}")


class JobHandlers:
    """Handlers for job recommendation endpoints"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def recommend_jobs(self, request: JobRecommendationRequest) -> Dict:
        """
        Generate job recommendations
        
        Args:
            request: Job recommendation request with session_id
            
        Returns:
            Dictionary with job recommendations
        """
        session_id = request.session_id
        
        session_data = self.session_manager.get_session(session_id)
        if not session_data or not session_data.get("unified_profile"):
            raise HTTPException(
                status_code=400,
                detail="Please complete profile building first"
            )
        
        try:
            unified_profile = session_data["unified_profile"]
            
            print(f"[INFO] Generating job recommendations for {unified_profile.get('name', 'candidate')}")
            
            recommender = JobRecommender()
            recommendations = recommender.recommend_jobs(unified_profile, num_recommendations=5)
            
            self.session_manager.update_session(session_id, {"recommendations": recommendations})
            
            print(f"[INFO] Generated {len(recommendations.get('recommendations', []))} job recommendations")
            
            return {
                "message": "Job recommendations generated successfully",
                "recommendations": recommendations
            }
        
        except Exception as e:
            print(f"[ERROR] Job recommendation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Job recommendation failed: {str(e)}")
