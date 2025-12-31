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
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.7
    )
    response_text = response.choices[0].message.content.strip()
    
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "overall_score": "Analysis generated",
            "career_trajectory": response_text[:150] if response_text else "See profile data above",
            "key_strengths": resume_data.get('summary', 'Professional expertise'),
            "improvement_areas": "Continuous learning recommended",
            "industry_fit": "Multiple sectors",
            "next_career_moves": "Senior progression or specialization",
            "suggested_job_summary": resume_data.get('summary', 'Professional summary based on resume')
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
