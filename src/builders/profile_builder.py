import json
from typing import Dict, List, Optional

class ProfileBuilder:
    """Merge LinkedIn and Resume data into unified profile"""
    
    @staticmethod
    def merge_profiles(resume_data: Dict, linkedin_data: Optional[Dict] = None) -> Dict:
        """
        Merge resume and LinkedIn data with priority to most complete information
        Prefers resume data when LinkedIn scraping fails (returns None values)
        """
        if not linkedin_data:
            # Resume-only mode
            return ProfileBuilder._build_from_resume(resume_data)
        
        # Filter out None values from LinkedIn data - they indicate failed extraction
        linkedin_data_clean = {k: v for k, v in linkedin_data.items() if v is not None}
        
        # Merge both sources with smart fallback
        unified_profile = {
            "name": linkedin_data_clean.get("name") or resume_data.get("name") or "N/A",
            "email": resume_data.get("email") or "N/A",
            "phone": resume_data.get("phone") or "N/A",
            "location": linkedin_data_clean.get("location") or resume_data.get("location") or "N/A",
            "headline": linkedin_data_clean.get("headline") or resume_data.get("headline") or "N/A",
            "summary": ProfileBuilder._merge_summaries(
                resume_data.get("summary"),
                linkedin_data_clean.get("about")
            ),
            "skills": ProfileBuilder._merge_lists(
                resume_data.get("skills", []),
                linkedin_data_clean.get("skills") or []
            ),
            "experience": ProfileBuilder._merge_experience(
                resume_data.get("experience", []),
                linkedin_data_clean.get("experience") or []
            ),
            "education": ProfileBuilder._merge_education(
                resume_data.get("education", []),
                linkedin_data_clean.get("education") or []
            ),
            "certifications": ProfileBuilder._merge_lists(
                resume_data.get("certifications", []),
                linkedin_data_clean.get("certifications") or []
            ),
            "languages": resume_data.get("languages", []),
            "data_sources": ["resume", "linkedin"] if linkedin_data_clean else ["resume"]
        }
        
        return unified_profile
    
    @staticmethod
    def _build_from_resume(resume_data: Dict) -> Dict:
        """Build profile from resume only"""
        return {
            **resume_data,
            "data_sources": ["resume"]
        }
    
    @staticmethod
    def _merge_summaries(resume_summary: Optional[str], linkedin_about: Optional[str]) -> str:
        """Merge summary/about sections"""
        if linkedin_about and resume_summary:
            # Prefer longer, more detailed version
            return linkedin_about if len(linkedin_about) > len(resume_summary) else resume_summary
        return linkedin_about or resume_summary or "N/A"
    
    @staticmethod
    def _merge_lists(list1: List[str], list2: List[str]) -> List[str]:
        """Merge two lists, removing duplicates while preserving order"""
        seen = set()
        merged = []
        
        for item in list1 + list2:
            item_lower = item.lower().strip()
            if item_lower not in seen and item_lower:
                seen.add(item_lower)
                merged.append(item)
        
        return merged
    
    @staticmethod
    def _merge_experience(resume_exp: List[Dict], linkedin_exp: List[Dict]) -> List[Dict]:
        """Merge experience from both sources"""
        # Use resume experience as primary (more detailed)
        # Add LinkedIn experience if not already present
        merged = list(resume_exp)
        
        for li_exp in linkedin_exp:
            # Check if this experience already exists in resume
            exists = any(
                ProfileBuilder._similar_experience(li_exp, r_exp)
                for r_exp in resume_exp
            )
            
            if not exists:
                merged.append({
                    "title": li_exp.get("title", "N/A"),
                    "company": li_exp.get("company", "N/A"),
                    "duration": li_exp.get("duration", "N/A"),
                    "highlights": []
                })
        
        return merged
    
    @staticmethod
    def _similar_experience(exp1: Dict, exp2: Dict) -> bool:
        """Check if two experience entries are similar"""
        company1 = exp1.get("company", "").lower()
        company2 = exp2.get("company", "").lower()
        title1 = exp1.get("title", "").lower()
        title2 = exp2.get("title", "").lower()
        
        return company1 in company2 or company2 in company1 or title1 in title2 or title2 in title1
    
    @staticmethod
    def _merge_education(resume_edu: List[Dict], linkedin_edu: List[Dict]) -> List[Dict]:
        """Merge education from both sources"""
        merged = list(resume_edu)
        
        for li_edu in linkedin_edu:
            exists = any(
                ProfileBuilder._similar_education(li_edu, r_edu)
                for r_edu in resume_edu
            )
            
            if not exists:
                merged.append({
                    "degree": li_edu.get("degree", "N/A"),
                    "institution": li_edu.get("institution", "N/A"),
                    "year": "N/A",
                    "details": ""
                })
        
        return merged
    
    @staticmethod
    def _similar_education(edu1: Dict, edu2: Dict) -> bool:
        """Check if two education entries are similar"""
        inst1 = edu1.get("institution", "").lower()
        inst2 = edu2.get("institution", "").lower()
        
        return inst1 in inst2 or inst2 in inst1
    
    @staticmethod
    def generate_profile_summary(unified_profile: Dict) -> str:
        """Generate a text summary of the unified profile"""
        name = unified_profile.get("name", "Candidate")
        headline = unified_profile.get("headline", "Professional")
        skills_count = len(unified_profile.get("skills", []))
        exp_count = len(unified_profile.get("experience", []))
        
        summary = f"{name} - {headline}\n"
        summary += f"Skills: {skills_count} identified | Experience: {exp_count} roles\n"
        summary += f"Data sources: {', '.join(unified_profile.get('data_sources', []))}"
        
        return summary
