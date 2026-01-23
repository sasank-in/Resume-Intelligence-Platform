"""
Business logic and service functions for resume analysis
"""
import json
import PyPDF2
from typing import Dict, Optional
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text from PDF
    """
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num} ---\n{page_text}"
    return text


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
        print(f"JSON parsing error: {e}, raw response: {json_str[:200]}")
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
    "key_strengths": "Top 3 professional strengths identified from the resume",
    "improvement_areas": "3 areas for professional development",
    "industry_fit": "Industries and sectors best suited for this candidate",
    "technical_skills_assessment": "Evaluation of technical competencies",
    "soft_skills_assessment": "Evaluation of soft skills and leadership",
    "competitive_advantage": "What makes this candidate stand out",
    "next_career_moves": "3 recommended next career steps",
    "salary_expectations": "Estimated salary range based on experience and skills",
    "suggested_job_summary": "Write a compelling 3-4 sentence professional summary for job applications that highlights: 1) Current role/expertise, 2) Key technical skills, 3) Years of experience, 4) Notable achievements or specializations. Make it specific to THIS candidate's actual background."
}}

CRITICAL INSTRUCTIONS:
- Generate ALL values based on the ACTUAL resume content
- Do NOT use generic templates or placeholder text
- Be SPECIFIC - reference actual skills, roles, companies, achievements from the resume
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
        
        # Ensure suggested_job_summary is not just the resume summary
        if analysis.get('suggested_job_summary') == resume_data.get('summary'):
            # Generate a better one if it's just copying
            analysis['suggested_job_summary'] = f"{name} is a {experience_summary} with expertise in {skills}. " + resume_data.get('summary', '')
        
        return analysis
    except json.JSONDecodeError as e:
        print(f"Analysis JSON parse error: {e}")
        # Return better fallback with actual resume data
        return {
            "overall_score": "Strong professional profile",
            "career_trajectory": f"Experienced professional with background in {experience_summary}",
            "key_strengths": f"Expertise in {skills}",
            "improvement_areas": "Continuous learning and skill development recommended",
            "industry_fit": "Technology and related sectors",
            "technical_skills_assessment": f"Proficient in {skills}",
            "soft_skills_assessment": "Strong communication and teamwork abilities",
            "competitive_advantage": f"Specialized experience in {experience_summary}",
            "next_career_moves": "Senior roles, leadership positions, or specialized consulting",
            "salary_expectations": "Competitive market rate based on experience level",
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
