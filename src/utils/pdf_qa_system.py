import os
import json
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

class ResumeAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.resume_text = ""
        self.resume_data = {}
    
    def extract_pdf(self, pdf_path):
        """Extract text from PDF file"""
        print(f"📄 Extracting resume from {pdf_path}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}"
        
        self.resume_text = text
        print(f"✓ Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text
    
    def extract_resume_data(self):
        """Extract structured resume data using Gemini AI"""
        if not self.resume_text:
            return "No resume content loaded. Please extract a resume first."
        
        print("🔍 Analyzing resume with Gemini AI...")
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
            "highlights": ["achievement1", "achievement2"]
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
{self.resume_text[:12000]}

Return ONLY the JSON, no other text."""
        
        response = self.model.generate_content(prompt)
        
        try:
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            self.resume_data = json.loads(json_str)
            return self.resume_data
        except:
            print("⚠️ Could not parse structured data, showing raw analysis...")
            return {"raw_analysis": response.text}
    
    def generate_detailed_analysis(self):
        """Generate detailed analysis and recommendations"""
        if not self.resume_data:
            return "Please analyze resume data first."
        
        print("📊 Generating detailed analysis...")
        prompt = f"""Based on this resume data, provide a detailed professional analysis:

Resume Data:
{json.dumps(self.resume_data, indent=2)}

Provide a JSON response with:
{{
    "overall_score": "Score out of 10 with brief justification",
    "career_trajectory": "Analysis of career progression (2-3 sentences)",
    "key_strengths": "Top 3 strengths for this candidate (2-3 sentences)",
    "improvement_areas": "Areas for improvement (2-3 sentences)",
    "industry_fit": "Best industries for this profile (2-3 sentences)",
    "next_steps": "Recommended next career moves (2-3 sentences)"
}}

Return ONLY the JSON, no other text."""
        
        response = self.model.generate_content(prompt)
        
        try:
            json_str = response.text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            
            return json.loads(json_str)
        except:
            return {"analysis": response.text}

def main():
    analyzer = ResumeAnalyzer()
    
    # Get PDF file path
    pdf_path = input("Enter the path to your resume PDF: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File '{pdf_path}' not found")
        return
    
    # Extract resume content
    analyzer.extract_pdf(pdf_path)
    
    # Extract structured data
    print("\n" + "="*60)
    print("📋 RESUME DATA EXTRACTION")
    print("="*60)
    resume_data = analyzer.extract_resume_data()
    
    if isinstance(resume_data, dict):
        # Display structured data
        if "name" in resume_data:
            print(f"\n👤 {resume_data.get('name', 'N/A')}")
            print(f"📍 {resume_data.get('location', 'N/A')} | {resume_data.get('headline', 'N/A')}")
            print(f"📧 {resume_data.get('email', 'N/A')} | {resume_data.get('phone', 'N/A')}")
            
            if resume_data.get('summary'):
                print(f"\n💼 {resume_data['summary']}")
            
            if resume_data.get('skills'):
                print(f"\n🎯 Skills: {', '.join(resume_data['skills'][:10])}")
            
            if resume_data.get('experience'):
                print("\n💻 Experience:")
                for exp in resume_data['experience'][:3]:
                    print(f"  • {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})")
            
            if resume_data.get('education'):
                print("\n🎓 Education:")
                for edu in resume_data['education']:
                    print(f"  • {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})")
    
    # Generate detailed analysis
    print("\n" + "="*60)
    print("📊 DETAILED ANALYSIS")
    print("="*60)
    analysis = analyzer.generate_detailed_analysis()
    
    if isinstance(analysis, dict):
        for key, value in analysis.items():
            if key != "raw_analysis":
                print(f"\n✨ {key.upper().replace('_', ' ')}:")
                print(f"{value}")

if __name__ == "__main__":
    main()
