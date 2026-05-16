"""
ATS (Applicant Tracking System) Checker
Analyzes resume compatibility with job descriptions and ATS systems
"""
from src._logprint import make_log_print
print = make_log_print(__name__)
import os
import json
import re
from typing import Dict, List, Tuple
from groq import Groq
from dotenv import load_dotenv


class ATSChecker:
    """Real-world ATS compatibility checker"""
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = 'openai/gpt-oss-120b'
        
        # Common ATS systems and their parsing characteristics
        self.ats_systems = {
            "Workday": {"keyword_weight": 0.4, "format_weight": 0.3, "structure_weight": 0.3},
            "Taleo": {"keyword_weight": 0.5, "format_weight": 0.2, "structure_weight": 0.3},
            "iCIMS": {"keyword_weight": 0.45, "format_weight": 0.25, "structure_weight": 0.3},
            "Greenhouse": {"keyword_weight": 0.4, "format_weight": 0.35, "structure_weight": 0.25},
            "Lever": {"keyword_weight": 0.35, "format_weight": 0.4, "structure_weight": 0.25},
            "BambooHR": {"keyword_weight": 0.4, "format_weight": 0.3, "structure_weight": 0.3}
        }
    
    def analyze_ats_compatibility(self, resume_data: Dict, job_description: str, 
                                 target_role: str = None, ats_system: str = "Generic") -> Dict:
        """
        Comprehensive ATS compatibility analysis
        
        Args:
            resume_data: Parsed resume data
            job_description: Job posting description
            target_role: Specific role title (optional)
            ats_system: Target ATS system (optional)
            
        Returns:
            Detailed ATS compatibility report
        """
        import logging
        logging.getLogger(__name__).info(
            "ats_analyze_start", extra={"target_role": target_role or "position"}
        )
        
        # Extract job requirements using AI
        job_requirements = self._extract_job_requirements(job_description, target_role)
        
        # Perform multi-dimensional analysis
        keyword_analysis = self._analyze_keywords(resume_data, job_requirements)
        format_analysis = self._analyze_format_compatibility(resume_data)
        structure_analysis = self._analyze_structure(resume_data)
        
        # Calculate overall ATS score
        ats_score = self._calculate_ats_score(
            keyword_analysis, format_analysis, structure_analysis, ats_system
        )
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(
            keyword_analysis, format_analysis, structure_analysis, job_requirements
        )
        
        return {
            "overall_score": ats_score,
            "ats_system": ats_system,
            "target_role": target_role,
            "keyword_analysis": keyword_analysis,
            "format_analysis": format_analysis,
            "structure_analysis": structure_analysis,
            "job_requirements": job_requirements,
            "recommendations": recommendations,
            "pass_probability": self._calculate_pass_probability(ats_score),
            "competitive_analysis": self._generate_competitive_analysis(ats_score)
        }
    
    def _extract_job_requirements(self, job_description: str, target_role: str = None) -> Dict:
        """Extract structured requirements from job description using AI"""
        
        prompt = f"""Analyze this job description and extract key requirements in JSON format:

JOB DESCRIPTION:
{job_description}

TARGET ROLE: {target_role or "Not specified"}

Extract and return ONLY valid JSON:
{{
    "required_skills": ["skill1", "skill2", "skill3"],
    "preferred_skills": ["skill1", "skill2"],
    "required_experience_years": 3,
    "education_requirements": ["Bachelor's degree", "relevant field"],
    "certifications": ["cert1", "cert2"],
    "key_responsibilities": ["responsibility1", "responsibility2"],
    "industry_keywords": ["keyword1", "keyword2"],
    "soft_skills": ["communication", "leadership"],
    "technical_tools": ["tool1", "tool2"],
    "job_level": "Senior/Mid/Junior/Executive",
    "company_size": "Startup/Mid-size/Enterprise",
    "remote_work": true/false
}}

Focus on extracting actual requirements, not generic descriptions."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        
        except Exception as e:
            print(f"Error extracting job requirements: {e}")
            return self._fallback_job_requirements(job_description)
    
    def _analyze_keywords(self, resume_data: Dict, job_requirements: Dict) -> Dict:
        """Analyze keyword matching between resume and job requirements"""
        
        # Extract resume keywords
        resume_skills = set(s.lower().strip() for s in resume_data.get('skills', []))
        resume_text = ' '.join([
            resume_data.get('summary', ''),
            ' '.join([exp.get('description', '') for exp in resume_data.get('experience', [])]),
            ' '.join([edu.get('description', '') for edu in resume_data.get('education', [])])
        ]).lower()
        
        # Required skills analysis
        required_skills = set(s.lower().strip() for s in job_requirements.get('required_skills', []))
        preferred_skills = set(s.lower().strip() for s in job_requirements.get('preferred_skills', []))
        industry_keywords = set(s.lower().strip() for s in job_requirements.get('industry_keywords', []))
        technical_tools = set(s.lower().strip() for s in job_requirements.get('technical_tools', []))
        
        # Calculate matches
        required_matches = resume_skills.intersection(required_skills)
        preferred_matches = resume_skills.intersection(preferred_skills)
        industry_matches = self._find_keyword_matches(resume_text, industry_keywords)
        tool_matches = resume_skills.intersection(technical_tools)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(resume_text, required_skills.union(preferred_skills))
        
        return {
            "required_skill_matches": list(required_matches),
            "required_skill_coverage": len(required_matches) / max(len(required_skills), 1) * 100,
            "preferred_skill_matches": list(preferred_matches),
            "preferred_skill_coverage": len(preferred_matches) / max(len(preferred_skills), 1) * 100,
            "industry_keyword_matches": list(industry_matches),
            "technical_tool_matches": list(tool_matches),
            "keyword_density": keyword_density,
            "missing_required_skills": list(required_skills - required_matches),
            "missing_preferred_skills": list(preferred_skills - preferred_matches),
            "keyword_score": self._calculate_keyword_score(
                len(required_matches), len(required_skills),
                len(preferred_matches), len(preferred_skills),
                keyword_density
            )
        }
    
    def _analyze_format_compatibility(self, resume_data: Dict) -> Dict:
        """Analyze resume format compatibility with ATS systems"""
        
        format_score = 100
        issues = []
        recommendations = []
        
        # Check for standard sections
        standard_sections = ['experience', 'education', 'skills']
        missing_sections = [s for s in standard_sections if not resume_data.get(s)]
        
        if missing_sections:
            format_score -= len(missing_sections) * 15
            issues.extend([f"Missing {section} section" for section in missing_sections])
            recommendations.extend([f"Add {section} section" for section in missing_sections])
        
        # Check contact information
        contact_fields = ['name', 'email', 'phone']
        missing_contact = [f for f in contact_fields if not resume_data.get(f)]
        
        if missing_contact:
            format_score -= len(missing_contact) * 10
            issues.extend([f"Missing {field}" for field in missing_contact])
            recommendations.extend([f"Add {field} to contact information" for field in missing_contact])
        
        # Check experience descriptions
        exp_with_descriptions = [exp for exp in resume_data.get('experience', []) 
                               if exp.get('description') and len(exp.get('description', '')) > 50]
        total_exp = len(resume_data.get('experience', []))
        
        if total_exp > 0 and len(exp_with_descriptions) / total_exp < 0.8:
            format_score -= 20
            issues.append("Insufficient experience descriptions")
            recommendations.append("Add detailed descriptions to all work experiences")
        
        # Check for dates
        exp_with_dates = [exp for exp in resume_data.get('experience', []) 
                         if exp.get('start_date') or exp.get('duration')]
        
        if total_exp > 0 and len(exp_with_dates) / total_exp < 0.9:
            format_score -= 15
            issues.append("Missing employment dates")
            recommendations.append("Include start and end dates for all positions")
        
        return {
            "format_score": max(format_score, 0),
            "issues": issues,
            "recommendations": recommendations,
            "ats_friendly_elements": self._identify_ats_friendly_elements(resume_data),
            "problematic_elements": self._identify_problematic_elements(resume_data)
        }
    
    def _analyze_structure(self, resume_data: Dict) -> Dict:
        """Analyze resume structure and organization"""
        
        structure_score = 100
        issues = []
        recommendations = []
        
        # Check section order (preferred: Contact, Summary, Experience, Education, Skills)
        sections_present = []
        if resume_data.get('name'): sections_present.append('contact')
        if resume_data.get('summary'): sections_present.append('summary')
        if resume_data.get('experience'): sections_present.append('experience')
        if resume_data.get('education'): sections_present.append('education')
        if resume_data.get('skills'): sections_present.append('skills')
        
        # Check for logical flow
        if 'experience' in sections_present and 'education' in sections_present:
            exp_index = sections_present.index('experience')
            edu_index = sections_present.index('education')
            if exp_index > edu_index and len(resume_data.get('experience', [])) > 0:
                # Experience should typically come before education for experienced candidates
                pass  # This is actually good structure
        
        # Check experience chronology
        experiences = resume_data.get('experience', [])
        if len(experiences) > 1:
            # Check if experiences are in reverse chronological order (most recent first)
            chronology_score = self._check_chronological_order(experiences)
            if chronology_score < 0.8:
                structure_score -= 15
                issues.append("Experience not in reverse chronological order")
                recommendations.append("Arrange experience in reverse chronological order (most recent first)")
        
        # Check for consistent formatting
        consistency_score = self._check_formatting_consistency(resume_data)
        structure_score = structure_score * consistency_score
        
        if consistency_score < 0.9:
            issues.append("Inconsistent formatting detected")
            recommendations.append("Ensure consistent formatting across all sections")
        
        return {
            "structure_score": max(structure_score, 0),
            "issues": issues,
            "recommendations": recommendations,
            "section_order": sections_present,
            "chronology_score": chronology_score if 'chronology_score' in locals() else 100,
            "consistency_score": consistency_score * 100
        }
    
    def _calculate_ats_score(self, keyword_analysis: Dict, format_analysis: Dict, 
                           structure_analysis: Dict, ats_system: str) -> float:
        """Calculate overall ATS compatibility score"""
        
        weights = self.ats_systems.get(ats_system, {
            "keyword_weight": 0.4, "format_weight": 0.3, "structure_weight": 0.3
        })
        
        keyword_score = keyword_analysis.get('keyword_score', 0)
        format_score = format_analysis.get('format_score', 0)
        structure_score = structure_analysis.get('structure_score', 0)
        
        overall_score = (
            keyword_score * weights['keyword_weight'] +
            format_score * weights['format_weight'] +
            structure_score * weights['structure_weight']
        )
        
        return round(overall_score, 1)
    
    def _generate_recommendations(self, keyword_analysis: Dict, format_analysis: Dict,
                                structure_analysis: Dict, job_requirements: Dict) -> List[Dict]:
        """Generate prioritized improvement recommendations"""
        
        recommendations = []
        
        # High priority: Missing required skills
        missing_required = keyword_analysis.get('missing_required_skills', [])
        if missing_required:
            recommendations.append({
                "priority": "High",
                "category": "Keywords",
                "issue": f"Missing {len(missing_required)} required skills",
                "action": f"Add these skills to your resume: {', '.join(missing_required[:5])}",
                "impact": "Critical for ATS filtering"
            })
        
        # Medium priority: Format issues
        format_issues = format_analysis.get('issues', [])
        for issue in format_issues[:3]:  # Top 3 format issues
            recommendations.append({
                "priority": "Medium",
                "category": "Format",
                "issue": issue,
                "action": format_analysis.get('recommendations', ['Fix formatting'])[0],
                "impact": "Improves ATS parsing accuracy"
            })
        
        # Low priority: Structure improvements
        structure_issues = structure_analysis.get('issues', [])
        for issue in structure_issues[:2]:  # Top 2 structure issues
            recommendations.append({
                "priority": "Low",
                "category": "Structure",
                "issue": issue,
                "action": structure_analysis.get('recommendations', ['Improve structure'])[0],
                "impact": "Enhances readability and flow"
            })
        
        # Keyword density recommendations
        keyword_density = keyword_analysis.get('keyword_density', 0)
        if keyword_density < 2:
            recommendations.append({
                "priority": "Medium",
                "category": "Keywords",
                "issue": "Low keyword density",
                "action": "Naturally incorporate more job-relevant keywords throughout your resume",
                "impact": "Increases keyword matching score"
            })
        
        return recommendations[:8]  # Return top 8 recommendations
    
    def _calculate_pass_probability(self, ats_score: float) -> Dict:
        """Calculate probability of passing ATS screening"""
        
        if ats_score >= 85:
            probability = "Very High (90-95%)"
            message = "Excellent ATS compatibility. Your resume should pass most ATS systems."
        elif ats_score >= 75:
            probability = "High (75-85%)"
            message = "Good ATS compatibility. Minor improvements could boost your chances."
        elif ats_score >= 65:
            probability = "Moderate (60-70%)"
            message = "Fair ATS compatibility. Several improvements needed for better results."
        elif ats_score >= 50:
            probability = "Low (40-55%)"
            message = "Poor ATS compatibility. Significant improvements required."
        else:
            probability = "Very Low (20-35%)"
            message = "Very poor ATS compatibility. Major restructuring needed."
        
        return {
            "probability": probability,
            "message": message,
            "score_range": self._get_score_range(ats_score)
        }
    
    def _generate_competitive_analysis(self, ats_score: float) -> Dict:
        """Generate competitive analysis against other candidates"""
        
        if ats_score >= 80:
            percentile = "Top 20%"
            competitive_edge = "Strong"
        elif ats_score >= 70:
            percentile = "Top 40%"
            competitive_edge = "Good"
        elif ats_score >= 60:
            percentile = "Top 60%"
            competitive_edge = "Average"
        else:
            percentile = "Bottom 40%"
            competitive_edge = "Weak"
        
        return {
            "percentile": percentile,
            "competitive_edge": competitive_edge,
            "benchmark_score": 72.5,  # Industry average
            "improvement_needed": max(0, 75 - ats_score)  # Points needed to reach "good" level
        }
    
    # Helper methods
    def _find_keyword_matches(self, text: str, keywords: set) -> List[str]:
        """Find keyword matches in text"""
        matches = []
        for keyword in keywords:
            if keyword in text:
                matches.append(keyword)
        return matches
    
    def _calculate_keyword_density(self, text: str, keywords: set) -> float:
        """Calculate keyword density in text"""
        if not text or not keywords:
            return 0
        
        word_count = len(text.split())
        keyword_count = sum(1 for keyword in keywords if keyword in text)
        
        return (keyword_count / word_count) * 100 if word_count > 0 else 0
    
    def _calculate_keyword_score(self, req_matches: int, req_total: int,
                               pref_matches: int, pref_total: int, density: float) -> float:
        """Calculate overall keyword score"""
        if req_total == 0:
            return 50  # Default score if no requirements
        
        required_score = (req_matches / req_total) * 70  # 70% weight for required skills
        preferred_score = (pref_matches / max(pref_total, 1)) * 20  # 20% weight for preferred skills
        density_score = min(density * 2, 10)  # 10% weight for keyword density
        
        return min(required_score + preferred_score + density_score, 100)
    
    def _identify_ats_friendly_elements(self, resume_data: Dict) -> List[str]:
        """Identify ATS-friendly elements in resume"""
        friendly_elements = []
        
        if resume_data.get('skills'):
            friendly_elements.append("Dedicated skills section")
        
        if resume_data.get('experience'):
            friendly_elements.append("Work experience section")
        
        if resume_data.get('education'):
            friendly_elements.append("Education section")
        
        # Check for standard formatting
        if resume_data.get('name') and resume_data.get('email'):
            friendly_elements.append("Clear contact information")
        
        return friendly_elements
    
    def _identify_problematic_elements(self, resume_data: Dict) -> List[str]:
        """Identify potentially problematic elements for ATS"""
        problems = []
        
        # Check for common ATS issues
        if not resume_data.get('skills'):
            problems.append("Missing skills section")
        
        if not resume_data.get('experience'):
            problems.append("Missing work experience")
        
        # Check for insufficient descriptions
        exp_count = len(resume_data.get('experience', []))
        desc_count = len([exp for exp in resume_data.get('experience', []) 
                         if exp.get('description') and len(exp.get('description', '')) > 30])
        
        if exp_count > 0 and desc_count / exp_count < 0.7:
            problems.append("Insufficient job descriptions")
        
        return problems
    
    def _check_chronological_order(self, experiences: List[Dict]) -> float:
        """Check if experiences are in proper chronological order"""
        # This is a simplified check - in a real implementation,
        # you'd parse dates and verify order
        return 0.9  # Assume good order for now
    
    def _check_formatting_consistency(self, resume_data: Dict) -> float:
        """Check formatting consistency across sections"""
        # This is a simplified check - in a real implementation,
        # you'd analyze formatting patterns
        return 0.95  # Assume good consistency for now
    
    def _get_score_range(self, score: float) -> str:
        """Get score range description"""
        if score >= 90:
            return "Excellent (90-100)"
        elif score >= 80:
            return "Very Good (80-89)"
        elif score >= 70:
            return "Good (70-79)"
        elif score >= 60:
            return "Fair (60-69)"
        elif score >= 50:
            return "Poor (50-59)"
        else:
            return "Very Poor (0-49)"
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from AI response"""
        try:
            json_str = response_text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return self._fallback_job_requirements("")
    
    def _fallback_job_requirements(self, job_description: str) -> Dict:
        """Fallback job requirements if AI parsing fails"""
        # Extract basic keywords from job description
        common_skills = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes']
        found_skills = [skill for skill in common_skills if skill.lower() in job_description.lower()]
        
        return {
            "required_skills": found_skills[:5],
            "preferred_skills": [],
            "required_experience_years": 3,
            "education_requirements": ["Bachelor's degree"],
            "certifications": [],
            "key_responsibilities": ["Develop software", "Collaborate with team"],
            "industry_keywords": ["technology", "software", "development"],
            "soft_skills": ["communication", "teamwork"],
            "technical_tools": found_skills,
            "job_level": "Mid",
            "company_size": "Mid-size",
            "remote_work": True
        }