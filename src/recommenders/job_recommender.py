from src._logprint import make_log_print
print = make_log_print(__name__)
import os
import json
from typing import Dict, List
from groq import Groq
from dotenv import load_dotenv

class JobRecommender:
    """AI-powered job recommendation engine using semantic similarity"""
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = 'openai/gpt-oss-120b'
    
    def recommend_jobs(self, unified_profile: Dict, num_recommendations: int = 5) -> Dict:
        """
        Generate job recommendations based on unified profile
        Uses AI to understand semantic similarity between profile and job requirements
        """
        print(f"🎯 Generating {num_recommendations} job recommendations...")
        
        # Build profile context
        profile_context = self._build_profile_context(unified_profile)
        
        # Generate recommendations using AI
        prompt = f"""Based on this candidate profile, recommend {num_recommendations} suitable job positions.

CANDIDATE PROFILE:
{profile_context}

Generate job recommendations in JSON format:
{{
    "recommendations": [
        {{
            "job_title": "Specific job title",
            "company_type": "Type of company (e.g., Tech Startup, Enterprise, Consulting)",
            "match_score": 85,
            "reasoning": "Why this job is a good fit (2-3 sentences)",
            "required_skills": ["skill1", "skill2", "skill3"],
            "matching_skills": ["candidate's matching skills"],
            "skill_gaps": ["skills to develop"],
            "salary_range": "$X - $Y",
            "growth_potential": "Career growth opportunities"
        }}
    ],
    "career_insights": {{
        "strongest_areas": "Top 3 areas where candidate excels",
        "recommended_industries": ["industry1", "industry2", "industry3"],
        "next_level_roles": ["role1", "role2"],
        "skill_development_priority": ["skill1", "skill2", "skill3"]
    }}
}}

IMPORTANT:
- Analyze the ACTUAL profile data provided
- Match based on skills, experience level, and career trajectory
- Provide realistic, actionable recommendations
- Consider both current capabilities and growth potential
- Return ONLY valid JSON, no other text"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            result = self._parse_json_response(response.choices[0].message.content)
            
            print(f"✓ Generated {len(result.get('recommendations', []))} recommendations")
            return result
        
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return self._fallback_recommendations(unified_profile)
    
    def _build_profile_context(self, profile: Dict) -> str:
        """Build a concise profile context for AI"""
        context = f"""
                Name: {profile.get('name', 'N/A')}
                Headline: {profile.get('headline', 'N/A')}
                Location: {profile.get('location', 'N/A')}

                Summary: {profile.get('summary', 'N/A')[:500]}

                Skills ({len(profile.get('skills', []))}): {', '.join(profile.get('skills', [])[:15])}

                Experience:
                """
        
        for exp in profile.get('experience', [])[:3]:
            context += f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})\n"
        
        context += f"\nEducation:\n"
        for edu in profile.get('education', [])[:2]:
            context += f"- {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')}\n"
        
        if profile.get('certifications'):
            context += f"\nCertifications: {', '.join(profile.get('certifications', [])[:5])}\n"
        
        return context
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from AI response"""
        try:
            # Extract JSON from markdown code blocks
            json_str = response_text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            raise
    
    def _fallback_recommendations(self, profile: Dict) -> Dict:
        """Fallback recommendations if AI fails"""
        return {
            "recommendations": [
                {
                    "job_title": "Senior Professional",
                    "company_type": "Growing Company",
                    "match_score": 75,
                    "reasoning": "Based on your experience and skills, you're well-suited for senior roles.",
                    "required_skills": profile.get('skills', [])[:5],
                    "matching_skills": profile.get('skills', [])[:3],
                    "skill_gaps": ["Leadership", "Strategic Planning"],
                    "salary_range": "Competitive",
                    "growth_potential": "High"
                }
            ],
            "career_insights": {
                "strongest_areas": "Technical expertise and professional experience",
                "recommended_industries": ["Technology", "Consulting", "Finance"],
                "next_level_roles": ["Senior Manager", "Director", "Principal"],
                "skill_development_priority": ["Leadership", "Communication", "Strategy"]
            }
        }
    
    def calculate_job_match_score(self, profile: Dict, job_requirements: Dict) -> float:
        """
        Calculate semantic similarity between profile and job requirements
        Returns match score 0-100
        """
        candidate_skills = set(s.lower() for s in profile.get('skills', []))
        required_skills = set(s.lower() for s in job_requirements.get('required_skills', []))
        
        if not required_skills:
            return 50.0
        
        # Calculate skill overlap
        matching_skills = candidate_skills.intersection(required_skills)
        skill_match_ratio = len(matching_skills) / len(required_skills)
        
        # Base score on skill match
        base_score = skill_match_ratio * 70  # Skills worth 70%
        
        # Add experience bonus (30%)
        exp_years = len(profile.get('experience', []))
        required_exp = job_requirements.get('years_experience', 3)
        exp_score = min(exp_years / required_exp, 1.0) * 30
        
        total_score = base_score + exp_score
        return round(min(total_score, 100), 1)
