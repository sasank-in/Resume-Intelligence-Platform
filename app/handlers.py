"""Route handlers for FastAPI endpoints."""
import json
import os
import tempfile
from typing import Dict, List

from fastapi import Form, UploadFile

from . import services
from .config import ALLOWED_FILE_TYPES, MAX_FILE_SIZE
from .errors import bad_request, server_error
from .logging_config import get_logger
from .models import (
    ChatMessage,
    JobRecommendationRequest,
    LinkedInProfileRequest,
    ResumeAnalysisRequest,
)
from .session_manager import is_valid_session_id, validate_file_upload

from src.builders import ProfileBuilder
from src.recommenders import JobRecommender
from src.scrapers import LinkedInScraper
from src.utils.ats_checker import ATSChecker

log = get_logger(__name__)


def _require_session(session_manager, session_id: str) -> Dict:
    if not is_valid_session_id(session_id):
        raise bad_request("Invalid session id format")
    data = session_manager.get_session(session_id)
    if not data:
        raise bad_request("No resume uploaded for this session")
    return data


class ResumeHandlers:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    async def upload_resume(self, file: UploadFile, session_id: str) -> Dict:
        if not is_valid_session_id(session_id):
            raise bad_request("Invalid session id format")
        if not validate_file_upload(file.filename, ALLOWED_FILE_TYPES):
            raise bad_request("Only PDF files are allowed")

        temp_path = None
        try:
            content = await file.read()
            file_size = len(content)
            log.info("upload_received", extra={"session": session_id, "bytes": file_size})

            if file_size == 0:
                raise bad_request("File is empty")
            if file_size > MAX_FILE_SIZE:
                raise bad_request(
                    f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                temp_path = tmp.name

            resume_text = services.extract_pdf_text(temp_path)
            log.info("pdf_extracted", extra={"chars": len(resume_text)})

            resume_data = services.extract_resume_data(resume_text)

            self.session_manager.create_session(session_id, {
                "resume_text": resume_text,
                "resume_data": resume_data,
                "linkedin_data": None,
                "unified_profile": None,
            })

            return {
                "message": "Resume analyzed successfully",
                "resume_data": resume_data,
                "characters": len(resume_text),
            }
        except Exception as e:
            if hasattr(e, "status_code"):  # already an HTTPException
                raise
            raise server_error("Upload failed", e, session=session_id)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    log.warning("temp_cleanup_failed", extra={"path": temp_path})

    async def get_analysis(self, request: ResumeAnalysisRequest) -> Dict:
        data = _require_session(self.session_manager, request.session_id)
        try:
            analysis = services.generate_detailed_analysis(
                data["resume_data"], data["resume_text"]
            )
            return {"resume_data": data["resume_data"], "analysis": analysis}
        except Exception as e:
            raise server_error("Analysis failed", e, session=request.session_id)


class ChatHandlers:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    async def chat(self, request: ChatMessage) -> Dict:
        data = _require_session(self.session_manager, request.session_id)
        try:
            chat_history = data.get("chat_history", [])
            ai_response = services.generate_chat_response(
                data["resume_data"], request.message, chat_history
            )
            chat_history.append({"user": request.message, "assistant": ai_response})
            self.session_manager.update_session(
                request.session_id, {"chat_history": chat_history}
            )
            return {"response": ai_response}
        except Exception as e:
            raise server_error("Chat error", e, session=request.session_id)


class LinkedInHandlers:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    async def add_linkedin_profile(self, request: LinkedInProfileRequest) -> Dict:
        data = _require_session(self.session_manager, request.session_id)
        try:
            log.info("linkedin_extract_start", extra={"url": request.linkedin_url})
            scraper = LinkedInScraper(headless=True)
            linkedin_data = scraper.extract_profile(request.linkedin_url)

            linkedin_data_clean = {
                k: v for k, v in linkedin_data.items() if v is not None and v != []
            }
            unified = ProfileBuilder.merge_profiles(
                data["resume_data"],
                linkedin_data_clean if linkedin_data_clean else None,
            )
            unified_clean = self._clean_profile_data(unified)

            self.session_manager.update_session(request.session_id, {
                "linkedin_data": linkedin_data_clean,
                "unified_profile": unified_clean,
            })

            return {
                "message": "LinkedIn profile processed successfully",
                "linkedin_data": linkedin_data_clean,
                "unified_profile": unified_clean,
                "info": "Merged data from resume + LinkedIn",
            }
        except Exception as e:
            log.warning(
                "linkedin_extract_failed_using_resume_only",
                extra={"error": str(e), "session": request.session_id},
            )
            try:
                unified = ProfileBuilder.merge_profiles(data["resume_data"], None)
                unified_clean = self._clean_profile_data(unified)
                self.session_manager.update_session(
                    request.session_id, {"unified_profile": unified_clean}
                )
                return {
                    "message": "LinkedIn extraction unavailable; built profile from resume only",
                    "unified_profile": unified_clean,
                    "warning": "LinkedIn data could not be retrieved",
                }
            except Exception as inner:
                raise server_error("Profile build failed", inner, session=request.session_id)

    @staticmethod
    def _is_valid(value) -> bool:
        return value is not None and value != "" and value != "N/A"

    def _clean_profile_data(self, profile: Dict) -> Dict:
        """Drop None / 'N/A' placeholders for UI display."""
        cleaned: Dict = {}
        list_dict_keys = {"experience": "title", "education": "degree"}
        list_str_keys = {"skills", "certifications", "languages"}
        passthrough = {"data_sources"}

        for key, value in profile.items():
            if key in list_dict_keys:
                primary = list_dict_keys[key]
                cleaned[key] = [
                    item for item in (value or [])
                    if isinstance(item, dict) and self._is_valid(item.get(primary))
                ]
            elif key in list_str_keys:
                cleaned[key] = [s for s in (value or []) if self._is_valid(s)]
            elif key in passthrough:
                cleaned[key] = value
            elif self._is_valid(value):
                cleaned[key] = value
        return cleaned

    async def skip_linkedin(self, request: ResumeAnalysisRequest) -> Dict:
        data = _require_session(self.session_manager, request.session_id)
        try:
            unified = ProfileBuilder.merge_profiles(data["resume_data"], None)
            unified_clean = self._clean_profile_data(unified)
            self.session_manager.update_session(
                request.session_id, {"unified_profile": unified_clean}
            )
            return {
                "message": "Profile created from resume only",
                "unified_profile": unified_clean,
            }
        except Exception as e:
            raise server_error("Profile build failed", e, session=request.session_id)


class JobHandlers:
    def __init__(self, session_manager, job_recommender: JobRecommender, ats_checker: ATSChecker):
        self.session_manager = session_manager
        self.job_recommender = job_recommender
        self.ats_checker = ats_checker

    async def recommend_jobs(self, request: JobRecommendationRequest) -> Dict:
        data = _require_session(self.session_manager, request.session_id)
        if not data.get("unified_profile"):
            raise bad_request("Please complete profile building first")
        try:
            recommendations = self.job_recommender.recommend_jobs(
                data["unified_profile"], num_recommendations=5
            )
            self.session_manager.update_session(
                request.session_id, {"recommendations": recommendations}
            )
            return {
                "message": "Job recommendations generated successfully",
                "recommendations": recommendations,
            }
        except Exception as e:
            raise server_error("Job recommendation failed", e, session=request.session_id)

    async def check_ats_compatibility(
        self,
        session_id: str,
        job_description: str,
        target_role: str = None,
        ats_system: str = "Generic",
    ) -> Dict:
        data = _require_session(self.session_manager, session_id)
        try:
            analysis = self.ats_checker.analyze_ats_compatibility(
                data["resume_data"], job_description, target_role, ats_system
            )
            self.session_manager.update_session(session_id, {"ats_analysis": analysis})
            return {
                "message": "ATS compatibility analysis completed",
                "analysis": analysis,
            }
        except Exception as e:
            raise server_error("ATS analysis failed", e, session=session_id)

    async def get_ats_suggestions(self, session_id: str, improvement_type: str = "all") -> Dict:
        data = _require_session(self.session_manager, session_id)
        if not data.get("ats_analysis"):
            raise bad_request("Please run ATS analysis first")
        try:
            ats_analysis = data["ats_analysis"]
            recs = ats_analysis.get("recommendations", [])
            if improvement_type != "all":
                recs = [
                    r for r in recs
                    if r.get("category", "").lower() == improvement_type.lower()
                ]
            improvement_text = self._generate_improvement_text(
                data["resume_data"], recs, improvement_type
            )
            return {
                "message": f"ATS improvement suggestions for {improvement_type}",
                "improvement_type": improvement_type,
                "recommendations": recs,
                "improvement_text": improvement_text,
                "current_score": ats_analysis.get("overall_score", 0),
            }
        except Exception as e:
            raise server_error("ATS suggestions failed", e, session=session_id)

    def _generate_improvement_text(
        self, resume_data: Dict, recommendations: List[Dict], improvement_type: str
    ) -> str:
        if not recommendations:
            return "Your resume looks good in this area! No major improvements needed."
        prompt = (
            f"Based on these ATS analysis recommendations, provide specific, "
            f"actionable improvement text for a resume.\n\n"
            f"IMPROVEMENT TYPE: {improvement_type}\n"
            f"CURRENT RESUME DATA: {str(resume_data)[:1000]}...\n\n"
            f"RECOMMENDATIONS:\n{json.dumps(recommendations, indent=2)}\n\n"
            f"Provide a concise, actionable paragraph (2-3 sentences) covering "
            f"what to change, why it improves ATS compatibility, and next steps. "
            f"Focus on {improvement_type} improvements."
        )
        try:
            response = self.ats_checker.client.chat.completions.create(
                model=self.ats_checker.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            log.exception("improvement_text_generation_failed")
            return (
                f"Focus on addressing the {len(recommendations)} key issues identified "
                f"in your {improvement_type} analysis to improve ATS compatibility."
            )

    async def analyze_job_standalone(
        self, job_description: str, target_role: str = None,
        analysis_type: str = "comprehensive",
    ) -> Dict:
        try:
            job_requirements = self.ats_checker._extract_job_requirements(
                job_description, target_role
            )
            analysis = services.generate_job_analysis(
                job_description, target_role, analysis_type, job_requirements
            )
            return {
                "message": "Job analysis completed successfully",
                "analysis": analysis,
                "job_requirements": job_requirements,
            }
        except Exception as e:
            raise server_error("Job analysis failed", e)

    async def get_market_data(
        self, job_role: str, experience_level: str = None,
        industry: str = None, location: str = None,
    ) -> Dict:
        try:
            insights = services.generate_market_insights(
                job_role, experience_level, industry, location
            )
            return {
                "message": "Market insights generated successfully",
                "insights": insights,
            }
        except Exception as e:
            raise server_error("Market insights failed", e)
