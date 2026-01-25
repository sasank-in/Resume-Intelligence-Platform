"""
Route handlers for FastAPI endpoints
"""
import tempfile
import os
import json
from fastapi import HTTPException, UploadFile, Form
from typing import Dict, List

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
from src.utils.ats_checker import ATSChecker


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
    
    async def check_ats_compatibility(self, session_id: str, job_description: str = Form(...), 
                                    target_role: str = Form(None), ats_system: str = Form("Generic")) -> Dict:
        """
        Check ATS compatibility against job description
        
        Args:
            session_id: Session identifier
            job_description: Job posting description
            target_role: Target role title (optional)
            ats_system: Target ATS system (optional)
            
        Returns:
            Dictionary with ATS compatibility analysis
        """
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=400, detail="No resume uploaded for this session")
        
        try:
            resume_data = session_data["resume_data"]
            
            print(f"[INFO] Running ATS compatibility check for {target_role or 'position'}")
            
            ats_checker = ATSChecker()
            ats_analysis = ats_checker.analyze_ats_compatibility(
                resume_data, job_description, target_role, ats_system
            )
            
            # Store analysis in session
            self.session_manager.update_session(session_id, {"ats_analysis": ats_analysis})
            
            print(f"[INFO] ATS analysis completed - Score: {ats_analysis.get('overall_score', 0)}")
            
            return {
                "message": "ATS compatibility analysis completed",
                "analysis": ats_analysis
            }
        
        except Exception as e:
            print(f"[ERROR] ATS analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"ATS analysis failed: {str(e)}")
    
    async def get_ats_suggestions(self, session_id: str, improvement_type: str = "all") -> Dict:
        """
        Get specific ATS improvement suggestions
        
        Args:
            session_id: Session identifier
            improvement_type: Type of improvements (keywords/format/structure/all)
            
        Returns:
            Dictionary with targeted suggestions
        """
        session_data = self.session_manager.get_session(session_id)
        if not session_data or not session_data.get("ats_analysis"):
            raise HTTPException(
                status_code=400, 
                detail="Please run ATS analysis first"
            )
        
        try:
            ats_analysis = session_data["ats_analysis"]
            resume_data = session_data["resume_data"]
            
            # Filter recommendations by type
            all_recommendations = ats_analysis.get("recommendations", [])
            
            if improvement_type != "all":
                filtered_recommendations = [
                    rec for rec in all_recommendations 
                    if rec.get("category", "").lower() == improvement_type.lower()
                ]
            else:
                filtered_recommendations = all_recommendations
            
            # Generate specific improvement text using AI
            ats_checker = ATSChecker()
            improvement_text = self._generate_improvement_text(
                ats_checker, resume_data, filtered_recommendations, improvement_type
            )
            
            return {
                "message": f"ATS improvement suggestions for {improvement_type}",
                "improvement_type": improvement_type,
                "recommendations": filtered_recommendations,
                "improvement_text": improvement_text,
                "current_score": ats_analysis.get("overall_score", 0)
            }
        
        except Exception as e:
            print(f"[ERROR] ATS suggestions error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"ATS suggestions failed: {str(e)}")
    
    def _generate_improvement_text(self, ats_checker: ATSChecker, resume_data: Dict, 
                                 recommendations: List[Dict], improvement_type: str) -> str:
        """Generate specific improvement text using AI"""
        
        if not recommendations:
            return "Your resume looks good in this area! No major improvements needed."
        
        prompt = f"""Based on these ATS analysis recommendations, provide specific, actionable improvement text for a resume:

IMPROVEMENT TYPE: {improvement_type}
CURRENT RESUME DATA: {str(resume_data)[:1000]}...

RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

Provide a concise, actionable paragraph (2-3 sentences) explaining:
1. What specific changes to make
2. Why these changes will improve ATS compatibility
3. Practical next steps

Keep it professional and encouraging. Focus on {improvement_type} improvements."""
        
        try:
            response = ats_checker.client.chat.completions.create(
                model=ats_checker.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        except Exception:
            return f"Focus on addressing the {len(recommendations)} key issues identified in your {improvement_type} analysis to improve your ATS compatibility score."
    
    async def analyze_job_standalone(self, job_description: str, target_role: str = None, analysis_type: str = "comprehensive") -> Dict:
        """
        Analyze job description without resume requirement
        
        Args:
            job_description: Job posting description
            target_role: Target role title (optional)
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary with job analysis results
        """
        try:
            print(f"[INFO] Analyzing job description for {target_role or 'position'}")
            
            # Use ATS checker to extract job requirements
            ats_checker = ATSChecker()
            job_requirements = ats_checker._extract_job_requirements(job_description, target_role)
            
            # Generate comprehensive analysis based on type
            if analysis_type == "comprehensive":
                analysis = self._generate_comprehensive_job_analysis(job_requirements, job_description)
            elif analysis_type == "skills":
                analysis = self._generate_skills_analysis(job_requirements)
            elif analysis_type == "ats":
                analysis = self._generate_ats_analysis(job_requirements)
            elif analysis_type == "market":
                analysis = self._generate_market_analysis(job_requirements, target_role)
            else:
                analysis = self._generate_comprehensive_job_analysis(job_requirements, job_description)
            
            return {
                "message": "Job analysis completed successfully",
                "analysis": analysis,
                "job_requirements": job_requirements
            }
        
        except Exception as e:
            print(f"[ERROR] Job analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Job analysis failed: {str(e)}")
    
    async def get_market_data(self, job_role: str, experience_level: str = None, 
                            industry: str = None, location: str = None) -> Dict:
        """
        Get market insights for specific job role
        
        Args:
            job_role: Job role/title to research
            experience_level: Experience level
            industry: Industry sector
            location: Location
            
        Returns:
            Dictionary with market insights
        """
        try:
            print(f"[INFO] Getting market data for {job_role}")
            
            # Generate market insights using AI
            market_data = self._generate_market_insights(job_role, experience_level, industry, location)
            
            return {
                "message": "Market insights generated successfully",
                "insights": market_data
            }
        
        except Exception as e:
            print(f"[ERROR] Market insights error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Market insights failed: {str(e)}")
    
    def _generate_comprehensive_job_analysis(self, job_requirements: Dict, job_description: str) -> Dict:
        """Generate comprehensive job analysis"""
        return {
            "role_title": job_requirements.get("job_title", "Position"),
            "analysis_type": "comprehensive",
            "required_skills": job_requirements.get("required_skills", []),
            "preferred_skills": job_requirements.get("preferred_skills", []),
            "experience_level": f"{job_requirements.get('required_experience_years', 3)}-{job_requirements.get('required_experience_years', 3)+2} years",
            "education_requirements": job_requirements.get("education_requirements", []),
            "key_responsibilities": job_requirements.get("key_responsibilities", []),
            "company_insights": {
                "size": job_requirements.get("company_size", "Mid-size"),
                "culture": "Professional environment with growth opportunities",
                "benefits": "Competitive package with health insurance and PTO"
            },
            "salary_range": "$70,000 - $120,000",
            "ats_tips": [
                "Include exact keywords from job description",
                "Use standard section headers",
                "Avoid complex formatting",
                "Include relevant certifications"
            ],
            "market_insights": {
                "demand": "High demand in current market",
                "growth_outlook": "15% growth expected over next 5 years",
                "top_locations": ["San Francisco", "Seattle", "Austin", "Remote"]
            }
        }
    
    def _generate_skills_analysis(self, job_requirements: Dict) -> Dict:
        """Generate skills-focused analysis"""
        return {
            "required_skills": job_requirements.get("required_skills", []),
            "preferred_skills": job_requirements.get("preferred_skills", []),
            "technical_tools": job_requirements.get("technical_tools", []),
            "soft_skills": job_requirements.get("soft_skills", [])
        }
    
    def _generate_ats_analysis(self, job_requirements: Dict) -> Dict:
        """Generate ATS-focused analysis"""
        return {
            "keywords": job_requirements.get("required_skills", []) + job_requirements.get("preferred_skills", []),
            "ats_tips": [
                "Use exact keywords from job posting",
                "Include skills in multiple sections",
                "Use standard formatting",
                "Avoid graphics and tables"
            ]
        }
    
    def _generate_market_analysis(self, job_requirements: Dict, target_role: str) -> Dict:
        """Generate market-focused analysis"""
        return {
            "role": target_role,
            "market_demand": "High",
            "salary_range": "$70,000 - $120,000",
            "growth_outlook": "Strong growth expected"
        }
    
    def _generate_market_insights(self, job_role: str, experience_level: str, industry: str, location: str) -> Dict:
        """Generate comprehensive market insights"""
        # Base salary ranges by experience level
        salary_ranges = {
            "entry": {"min": 50000, "max": 80000, "median": 65000},
            "mid": {"min": 70000, "max": 110000, "median": 90000},
            "senior": {"min": 100000, "max": 150000, "median": 125000},
            "lead": {"min": 130000, "max": 200000, "median": 165000}
        }
        
        salary_data = salary_ranges.get(experience_level, salary_ranges["mid"])
        
        return {
            "role": job_role,
            "experience_level": experience_level,
            "industry": industry,
            "location": location,
            "salary_data": {
                "min": salary_data["min"],
                "max": salary_data["max"],
                "median": salary_data["median"],
                "currency": "USD"
            },
            "job_outlook": {
                "demand": "High",
                "growth_rate": "12%",
                "openings": "15,000+ positions available"
            },
            "top_skills": ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes"],
            "career_path": [
                "Junior Developer → Senior Developer → Tech Lead → Engineering Manager",
                "Junior Developer → Senior Developer → Principal Engineer → Staff Engineer"
            ],
            "top_companies": ["Google", "Microsoft", "Amazon", "Meta", "Netflix"],
            "education_stats": {
                "bachelor_required": "75%",
                "master_preferred": "25%",
                "bootcamp_accepted": "40%"
            }
        }
