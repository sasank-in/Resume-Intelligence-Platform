"""Business logic and service functions for resume analysis."""
import json
from typing import Dict, Optional

from pypdf import PdfReader
from groq import Groq

from .config import GROQ_API_KEY, GROQ_MODEL
from .logging_config import get_logger

log = get_logger(__name__)
client = Groq(api_key=GROQ_API_KEY)


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]
    return text.strip()


def _llm_json(prompt: str, *, max_tokens: int = 1500, temperature: float = 0.5) -> Dict:
    """Call the LLM and parse the response as JSON. Returns {} on failure."""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = _strip_code_fences(response.choices[0].message.content)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log.warning("llm_json_parse_failed", extra={"head": raw[:200]})
        return {}


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pieces = []
    for page_num, page in enumerate(reader.pages, 1):
        page_text = page.extract_text() or ""
        pieces.append(f"\n--- Page {page_num} ---\n{page_text}")
    return "".join(pieces)


def extract_resume_data(resume_text: str) -> Dict:
    """
    Extract structured resume data using Groq AI
    
    Args:
        resume_text: Raw text from resume PDF
        
    Returns:
        Dictionary with structured resume data
    """
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
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    try:
        json_str = response.choices[0].message.content.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        
        json_str = json_str.strip()
        return json.loads(json_str)
    except Exception as e:
        log.warning("resume_json_parse_failed", extra={"error": str(e), "head": json_str[:200]})
        return {"raw_analysis": json_str}


def generate_detailed_analysis(resume_data: Dict, resume_text: str) -> Dict:
    """
    Generate detailed career analysis using Groq AI
    
    Args:
        resume_data: Structured resume data
        resume_text: Raw resume text
        
    Returns:
        Dictionary with detailed analysis
    """
    # Extract key info for better context
    name = resume_data.get('name', 'Candidate')
    skills = ', '.join(resume_data.get('skills', [])[:10])
    experience_summary = ""
    if resume_data.get('experience'):
        exp = resume_data['experience'][0]
        experience_summary = f"{exp.get('title', '')} at {exp.get('company', '')}"
    
    analysis_prompt = f"""Analyze this resume and provide a comprehensive career analysis in JSON format.

CANDIDATE: {name}
KEY SKILLS: {skills}
CURRENT/RECENT ROLE: {experience_summary}

FULL RESUME:
{resume_text}

Generate a detailed analysis with these fields:

{{
    "overall_score": "Your assessment of overall professional profile (include score and reasoning)",
    "career_trajectory": "Analysis of career progression and growth pattern",
    "key_strengths": "Top 3 professional strengths identified from the resume (as a single paragraph)",
    "improvement_areas": "Areas for professional development and skill enhancement (as a single paragraph)",
    "industry_fit": "Industries and sectors best suited for this candidate (as a single paragraph)",
    "competitive_advantage": "What makes this candidate stand out",
    "next_career_moves": "3 recommended next career steps (as a single paragraph)",
    "salary_expectations": "Estimated salary range based on experience and skills",
    "recommendations_summary": "Comprehensive career recommendations and action items",
    "suggested_job_summary": "A concise 3-4 sentence job summary suitable for a job application based on the resume"
}}

CRITICAL INSTRUCTIONS:
- Generate ALL values based on the ACTUAL resume content
- Do NOT use generic templates or placeholder text
- Be SPECIFIC - reference actual skills, roles, companies, achievements from the resume
- ALL fields should be STRINGS (not arrays) - write as paragraphs or comma-separated text
- For suggested_job_summary: Write a unique, personalized summary that could be used on LinkedIn or job applications
- Make the summary compelling and highlight what makes this candidate valuable
- Return ONLY valid JSON, no other text"""
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    response_text = response.choices[0].message.content.strip()
    
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        
        # Convert any array values to strings for consistent display
        for key, value in analysis.items():
            if isinstance(value, list):
                analysis[key] = ', '.join(str(item) for item in value)
        
        # Ensure suggested_job_summary is not just the resume summary
        if analysis.get('suggested_job_summary') == resume_data.get('summary'):
            # Generate a better one if it's just copying
            analysis['suggested_job_summary'] = f"{name} is a {experience_summary} with expertise in {skills}. " + resume_data.get('summary', '')
        
        return analysis
    except json.JSONDecodeError as e:
        log.warning("analysis_json_parse_failed", extra={"error": str(e)})
        # Return better fallback with actual resume data
        return {
            "overall_score": "Strong professional profile",
            "career_trajectory": f"Experienced professional with background in {experience_summary}",
            "key_strengths": f"Expertise in {skills}",
            "improvement_areas": "Continuous learning and skill development recommended",
            "industry_fit": "Technology and related sectors",
            "competitive_advantage": f"Specialized experience in {experience_summary}",
            "next_career_moves": "Senior roles, leadership positions, or specialized consulting",
            "salary_expectations": "Competitive market rate based on experience level",
            "recommendations_summary": "Focus on building leadership skills, expanding technical expertise, and networking within the industry",
            "suggested_job_summary": f"{name} is an experienced professional currently working as {experience_summary}. With strong expertise in {skills}, they bring valuable technical knowledge and proven track record to any organization. Seeking opportunities to leverage skills in challenging roles."
        }


def generate_chat_response(resume_data: Dict, message: str, chat_history: list) -> str:
    """
    Generate AI response for chat interaction
    
    Args:
        resume_data: Structured resume data
        message: User message
        chat_history: Previous chat messages
        
    Returns:
        AI response text
    """
    history_context = ""
    if chat_history:
        history_context = "\nPrevious conversation:\n"
        for qa in chat_history[-3:]:
            history_context += f"User: {qa['user']}\nAssistant: {qa['assistant']}\n"
    
    prompt = f"""You are a friendly career coach. Answer the user's question about their resume.

        Candidate: {resume_data.get('name', 'Candidate')}
        Summary: {resume_data.get('summary', 'Professional')}
        Skills: {', '.join(resume_data.get('skills', [])[:10])}
        Roles: {', '.join([exp.get('title', '') for exp in resume_data.get('experience', [])[:3]])}

        {history_context}

        User: {message}

        Provide a helpful, conversational response (2-3 sentences). Be supportive and actionable."""
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def generate_job_analysis(
    job_description: str,
    target_role: Optional[str],
    analysis_type: str,
    job_requirements: Dict,
) -> Dict:
    """LLM-driven job description analysis. Replaces the hardcoded stub."""
    role = target_role or job_requirements.get("job_title") or "this role"
    prompt = f"""Analyze this job posting and produce a {analysis_type} analysis as JSON.

ROLE: {role}
EXTRACTED REQUIREMENTS: {json.dumps(job_requirements)[:1500]}
JOB DESCRIPTION:
{job_description[:4000]}

Return JSON with these fields, all values grounded in the description (not generic):
{{
  "role_title": "...",
  "analysis_type": "{analysis_type}",
  "required_skills": ["..."],
  "preferred_skills": ["..."],
  "experience_level": "e.g. 3-5 years",
  "education_requirements": ["..."],
  "key_responsibilities": ["..."],
  "company_insights": {{"size": "...", "culture": "...", "benefits": "..."}},
  "salary_range": "estimated range with currency",
  "ats_tips": ["specific keyword tips"],
  "market_insights": {{"demand": "...", "growth_outlook": "...", "top_locations": ["..."]}}
}}

Return ONLY JSON. If a field cannot be inferred, use "Not specified" or []."""
    result = _llm_json(prompt, max_tokens=1500)
    if not result:
        return {
            "role_title": role,
            "analysis_type": analysis_type,
            "error": "Analysis unavailable; please retry.",
        }
    result.setdefault("role_title", role)
    result.setdefault("analysis_type", analysis_type)
    return result


def extract_linkedin_from_text(linkedin_text: str) -> Dict:
    """Extract structured LinkedIn fields from raw pasted profile text."""
    prompt = f"""You are extracting LinkedIn profile data from text the user pasted.
Return ONLY valid JSON in this shape; use null/[] when a field is absent.

{{
  "name": "...",
  "headline": "...",
  "location": "...",
  "summary": "...",
  "skills": ["..."],
  "experience": [
    {{"title": "...", "company": "...", "duration": "...", "highlights": ["..."]}}
  ],
  "education": [
    {{"degree": "...", "institution": "...", "year": "...", "details": "..."}}
  ],
  "certifications": ["..."],
  "languages": ["..."]
}}

PROFILE TEXT (truncated to 8000 chars):
{linkedin_text[:8000]}
"""
    return _llm_json(prompt, max_tokens=1500)


def generate_market_insights(
    job_role: str,
    experience_level: Optional[str],
    industry: Optional[str],
    location: Optional[str],
) -> Dict:
    """LLM-driven market insights. Replaces the hardcoded stub."""
    prompt = f"""You are a labor-market analyst. Produce JSON insights for:
ROLE: {job_role}
EXPERIENCE LEVEL: {experience_level or 'unspecified'}
INDUSTRY: {industry or 'unspecified'}
LOCATION: {location or 'unspecified'}

Return JSON only:
{{
  "role": "{job_role}",
  "experience_level": "{experience_level or ''}",
  "industry": "{industry or ''}",
  "location": "{location or ''}",
  "salary_data": {{"min": int, "max": int, "median": int, "currency": "USD"}},
  "job_outlook": {{"demand": "...", "growth_rate": "...", "openings": "..."}},
  "top_skills": ["..."],
  "career_path": ["progression 1", "progression 2"],
  "top_companies": ["..."],
  "education_stats": {{"bachelor_required": "...", "master_preferred": "...", "bootcamp_accepted": "..."}},
  "notes": "brief caveat — these are estimates, not real-time market data"
}}

Use realistic ranges for the location/experience combo. If location is unspecified, assume US median."""
    result = _llm_json(prompt, max_tokens=1200)
    if not result:
        return {
            "role": job_role,
            "experience_level": experience_level,
            "industry": industry,
            "location": location,
            "error": "Market insights unavailable; please retry.",
        }
    return result
