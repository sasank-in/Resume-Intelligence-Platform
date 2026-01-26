"""
Resume Parser for Automated Job Application Screening
Extracts structured data from resumes and scores candidates
"""
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import PyPDF2
from pathlib import Path


class ResumeParser:
    """
    Advanced resume parser for extracting structured information
    """
    
    def __init__(self):
        self.skills_database = self._load_skills_database()
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'mba', 'bs', 'ms', 
            'ba', 'ma', 'associate', 'diploma', 'degree', 'university', 'college'
        ]
        
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load categorized skills database"""
        return {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
                'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            ],
            'web': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'fastapi', 'spring', 'asp.net', 'jquery'
            ],
            'database': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle',
                'cassandra', 'dynamodb', 'elasticsearch', 'sqlite'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'jenkins', 'ci/cd', 'devops', 'ansible', 'cloudformation'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'scikit-learn', 'pandas', 'numpy', 'data analysis', 'statistics',
                'nlp', 'computer vision', 'ai', 'neural networks'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving',
                'project management', 'agile', 'scrum', 'collaboration'
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information"""
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name (usually first line)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # First non-empty line is usually the name
            first_line = lines[0]
            # Remove common titles
            name = re.sub(r'\b(resume|cv|curriculum vitae)\b', '', first_line, flags=re.IGNORECASE)
            return name.strip() if len(name.split()) <= 4 else None
        return None
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills by category"""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.skills_database.items():
            category_skills = []
            for skill in skills:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    category_skills.append(skill)
            
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains education keywords
            if any(keyword in line_lower for keyword in self.education_keywords):
                edu_entry = {
                    'degree': line.strip(),
                    'institution': '',
                    'year': ''
                }
                
                # Try to find institution in nearby lines
                if i + 1 < len(lines):
                    edu_entry['institution'] = lines[i + 1].strip()
                
                # Extract year
                year_pattern = r'\b(19|20)\d{2}\b'
                year_match = re.search(year_pattern, line)
                if year_match:
                    edu_entry['year'] = year_match.group()
                elif i + 1 < len(lines):
                    year_match = re.search(year_pattern, lines[i + 1])
                    if year_match:
                        edu_entry['year'] = year_match.group()
                
                education.append(edu_entry)
        
        return education
    
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience"""
        experience = []
        
        # Find experience section
        exp_pattern = r'(experience|employment|work history)(.*?)(?=education|skills|projects|$)'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_match:
            exp_text = exp_match.group(2)
            
            # Split by common job entry patterns
            job_entries = re.split(r'\n(?=[A-Z][a-z]+ \d{4}|\d{4})', exp_text)
            
            for entry in job_entries:
                if entry.strip():
                    lines = [l.strip() for l in entry.split('\n') if l.strip()]
                    if lines:
                        exp_entry = {
                            'title': lines[0] if len(lines) > 0 else '',
                            'company': lines[1] if len(lines) > 1 else '',
                            'duration': '',
                            'description': ' '.join(lines[2:]) if len(lines) > 2 else ''
                        }
                        
                        # Extract duration
                        duration_pattern = r'\b(19|20)\d{2}\s*[-–]\s*((19|20)\d{2}|present|current)\b'
                        duration_match = re.search(duration_pattern, entry, re.IGNORECASE)
                        if duration_match:
                            exp_entry['duration'] = duration_match.group()
                        
                        experience.append(exp_entry)
        
        return experience
    
    def calculate_experience_years(self, experience: List[Dict[str, str]]) -> float:
        """Calculate total years of experience"""
        total_years = 0.0
        current_year = datetime.now().year
        
        for exp in experience:
            duration = exp.get('duration', '')
            years = re.findall(r'\b(19|20)\d{2}\b', duration)
            
            if len(years) >= 2:
                start_year = int(years[0])
                end_year = int(years[1])
                total_years += (end_year - start_year)
            elif len(years) == 1 and ('present' in duration.lower() or 'current' in duration.lower()):
                start_year = int(years[0])
                total_years += (current_year - start_year)
        
        return round(total_years, 1)
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """
        Parse resume and extract all information
        
        Args:
            pdf_path: Path to PDF resume file
            
        Returns:
            Dictionary with structured resume data
        """
        text = self.extract_text_from_pdf(pdf_path)
        
        parsed_data = {
            'name': self.extract_name(text),
            'contact': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience': self.extract_experience(text),
            'total_experience_years': 0.0,
            'raw_text': text,
            'parsed_at': datetime.now().isoformat()
        }
        
        # Calculate experience years
        parsed_data['total_experience_years'] = self.calculate_experience_years(
            parsed_data['experience']
        )
        
        return parsed_data


class CandidateScreener:
    """
    Automated candidate screening and ranking system
    """
    
    def __init__(self, job_requirements: Dict):
        """
        Initialize screener with job requirements
        
        Args:
            job_requirements: Dictionary with required skills, experience, education
        """
        self.job_requirements = job_requirements
        self.parser = ResumeParser()
    
    def score_skills_match(self, candidate_skills: Dict[str, List[str]]) -> Tuple[float, Dict]:
        """Score candidate skills against job requirements"""
        required_skills = self.job_requirements.get('required_skills', [])
        preferred_skills = self.job_requirements.get('preferred_skills', [])
        
        # Flatten candidate skills
        all_candidate_skills = []
        for skills_list in candidate_skills.values():
            all_candidate_skills.extend([s.lower() for s in skills_list])
        
        # Calculate matches
        required_matches = sum(1 for skill in required_skills 
                              if skill.lower() in all_candidate_skills)
        preferred_matches = sum(1 for skill in preferred_skills 
                               if skill.lower() in all_candidate_skills)
        
        # Calculate score (required skills weighted more)
        required_score = (required_matches / len(required_skills) * 70) if required_skills else 0
        preferred_score = (preferred_matches / len(preferred_skills) * 30) if preferred_skills else 0
        
        total_score = required_score + preferred_score
        
        details = {
            'required_matches': required_matches,
            'required_total': len(required_skills),
            'preferred_matches': preferred_matches,
            'preferred_total': len(preferred_skills),
            'matched_skills': [s for s in all_candidate_skills 
                             if s in [r.lower() for r in required_skills + preferred_skills]]
        }
        
        return round(total_score, 2), details
    
    def score_experience(self, years_experience: float) -> Tuple[float, str]:
        """Score candidate experience"""
        min_exp = self.job_requirements.get('min_experience_years', 0)
        max_exp = self.job_requirements.get('max_experience_years', 100)
        
        if years_experience < min_exp:
            score = (years_experience / min_exp) * 50 if min_exp > 0 else 0
            reason = f"Below minimum ({years_experience} < {min_exp} years)"
        elif years_experience > max_exp:
            score = 75
            reason = f"Overqualified ({years_experience} > {max_exp} years)"
        else:
            score = 100
            reason = f"Perfect fit ({min_exp}-{max_exp} years)"
        
        return round(score, 2), reason
    
    def score_education(self, education: List[Dict[str, str]]) -> Tuple[float, str]:
        """Score candidate education"""
        required_degree = self.job_requirements.get('required_degree', '').lower()
        
        if not required_degree:
            return 100.0, "No specific requirement"
        
        degree_hierarchy = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'mba': 4, 'ms': 4, 'ma': 4,
            'bachelor': 3, 'bs': 3, 'ba': 3,
            'associate': 2,
            'diploma': 1
        }
        
        required_level = 0
        for key, level in degree_hierarchy.items():
            if key in required_degree:
                required_level = level
                break
        
        candidate_level = 0
        for edu in education:
            degree = edu.get('degree', '').lower()
            for key, level in degree_hierarchy.items():
                if key in degree:
                    candidate_level = max(candidate_level, level)
        
        if candidate_level >= required_level:
            score = 100
            reason = "Meets or exceeds requirement"
        elif candidate_level > 0:
            score = (candidate_level / required_level) * 80
            reason = "Below required level"
        else:
            score = 0
            reason = "No relevant education found"
        
        return round(score, 2), reason
    
    def calculate_overall_score(self, parsed_resume: Dict) -> Dict:
        """Calculate overall candidate score"""
        
        # Score components
        skills_score, skills_details = self.score_skills_match(parsed_resume['skills'])
        exp_score, exp_reason = self.score_experience(parsed_resume['total_experience_years'])
        edu_score, edu_reason = self.score_education(parsed_resume['education'])
        
        # Weighted average (skills: 50%, experience: 30%, education: 20%)
        overall_score = (skills_score * 0.5) + (exp_score * 0.3) + (edu_score * 0.2)
        
        # Determine status
        if overall_score >= 80:
            status = "HIGHLY_RECOMMENDED"
        elif overall_score >= 60:
            status = "RECOMMENDED"
        elif overall_score >= 40:
            status = "MAYBE"
        else:
            status = "NOT_RECOMMENDED"
        
        return {
            'overall_score': round(overall_score, 2),
            'status': status,
            'breakdown': {
                'skills': {
                    'score': skills_score,
                    'weight': '50%',
                    'details': skills_details
                },
                'experience': {
                    'score': exp_score,
                    'weight': '30%',
                    'reason': exp_reason,
                    'years': parsed_resume['total_experience_years']
                },
                'education': {
                    'score': edu_score,
                    'weight': '20%',
                    'reason': edu_reason
                }
            }
        }
    
    def screen_candidate(self, pdf_path: str) -> Dict:
        """
        Screen a single candidate
        
        Args:
            pdf_path: Path to candidate's resume PDF
            
        Returns:
            Complete screening results
        """
        # Parse resume
        parsed_resume = self.parser.parse_resume(pdf_path)
        
        # Calculate scores
        scoring = self.calculate_overall_score(parsed_resume)
        
        return {
            'candidate_info': {
                'name': parsed_resume['name'],
                'email': parsed_resume['contact']['email'],
                'phone': parsed_resume['contact']['phone']
            },
            'scoring': scoring,
            'parsed_data': parsed_resume,
            'screened_at': datetime.now().isoformat()
        }
    
    def screen_batch(self, resume_paths: List[str]) -> List[Dict]:
        """
        Screen multiple candidates and rank them
        
        Args:
            resume_paths: List of paths to resume PDFs
            
        Returns:
            List of screening results, sorted by score
        """
        results = []
        
        for path in resume_paths:
            try:
                result = self.screen_candidate(path)
                result['file_path'] = path
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': path,
                    'error': str(e),
                    'status': 'FAILED'
                })
        
        # Sort by overall score (descending)
        results.sort(
            key=lambda x: x.get('scoring', {}).get('overall_score', 0),
            reverse=True
        )
        
        return results
    
    def export_results(self, results: List[Dict], output_path: str):
        """Export screening results to JSON"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to: {output_path}")


def create_job_requirements_template() -> Dict:
    """Create a template for job requirements"""
    return {
        'job_title': 'Software Engineer',
        'required_skills': [
            'python', 'javascript', 'sql', 'git'
        ],
        'preferred_skills': [
            'react', 'docker', 'aws', 'agile'
        ],
        'min_experience_years': 2,
        'max_experience_years': 5,
        'required_degree': 'bachelor'
    }


# Example usage
if __name__ == "__main__":
    # Define job requirements
    job_requirements = {
        'job_title': 'Senior Python Developer',
        'required_skills': ['python', 'django', 'sql', 'rest api'],
        'preferred_skills': ['docker', 'aws', 'redis', 'react'],
        'min_experience_years': 3,
        'max_experience_years': 8,
        'required_degree': 'bachelor'
    }
    
    # Initialize screener
    screener = CandidateScreener(job_requirements)
    
    # Screen single candidate
    # result = screener.screen_candidate('path/to/resume.pdf')
    # print(json.dumps(result, indent=2))
    
    # Screen multiple candidates
    # resume_paths = ['resume1.pdf', 'resume2.pdf', 'resume3.pdf']
    # results = screener.screen_batch(resume_paths)
    # screener.export_results(results, 'screening_results.json')
    
    print("Resume Parser and Screener initialized successfully!")
    print("Use CandidateScreener to automate your hiring process.")
