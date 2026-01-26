"""
API Handlers for Resume Screening System
"""
import tempfile
import os
import shutil
from pathlib import Path
from typing import Dict, List
from fastapi import HTTPException, UploadFile
from datetime import datetime

from src.parsers.resume_parser import CandidateScreener, ResumeParser
from src.parsers.batch_screener import BatchScreeningSystem


class ScreeningHandlers:
    """Handlers for resume screening endpoints"""
    
    def __init__(self):
        self.parser = ResumeParser()
        self.temp_dir = Path(tempfile.gettempdir()) / 'resume_screening'
        self.temp_dir.mkdir(exist_ok=True)
    
    async def parse_single_resume(self, file: UploadFile) -> Dict:
        """
        Parse a single resume and extract structured data
        
        Args:
            file: Uploaded PDF file
            
        Returns:
            Parsed resume data
        """
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        temp_path = None
        try:
            # Save uploaded file temporarily
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(content)
                temp_path = tmp.name
            
            # Parse resume
            parsed_data = self.parser.parse_resume(temp_path)
            
            return {
                'success': True,
                'data': parsed_data,
                'message': 'Resume parsed successfully'
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
        
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def screen_single_candidate(self, file: UploadFile, 
                                     job_requirements: Dict) -> Dict:
        """
        Screen a single candidate against job requirements
        
        Args:
            file: Uploaded resume PDF
            job_requirements: Job requirements dictionary
            
        Returns:
            Screening results with score and recommendations
        """
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        temp_path = None
        try:
            # Save uploaded file temporarily
            content = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(content)
                temp_path = tmp.name
            
            # Initialize screener
            screener = CandidateScreener(job_requirements)
            
            # Screen candidate
            result = screener.screen_candidate(temp_path)
            
            return {
                'success': True,
                'screening_result': result,
                'message': 'Candidate screened successfully'
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")
        
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def screen_batch(self, files: List[UploadFile], 
                          job_requirements: Dict) -> Dict:
        """
        Screen multiple candidates in batch
        
        Args:
            files: List of uploaded resume PDFs
            job_requirements: Job requirements dictionary
            
        Returns:
            Batch screening results with rankings
        """
        batch_dir = self.temp_dir / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_dir.mkdir(exist_ok=True)
        
        try:
            # Save all uploaded files
            saved_paths = []
            for file in files:
                if not file.filename.endswith('.pdf'):
                    continue
                
                file_path = batch_dir / file.filename
                content = await file.read()
                with open(file_path, 'wb') as f:
                    f.write(content)
                saved_paths.append(str(file_path))
            
            if not saved_paths:
                raise HTTPException(status_code=400, detail="No valid PDF files provided")
            
            # Initialize batch screening system
            batch_system = BatchScreeningSystem(
                job_requirements=job_requirements,
                output_dir=str(batch_dir / 'results')
            )
            
            # Process all resumes
            results = batch_system.process_applications(str(batch_dir))
            
            # Generate interview list
            interview_list = batch_system.generate_interview_list(
                results['results'], 
                top_n=min(10, len(results['results']))
            )
            
            return {
                'success': True,
                'summary': results['summary'],
                'top_candidates': interview_list,
                'total_processed': len(saved_paths),
                'message': 'Batch screening completed successfully'
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Batch screening failed: {str(e)}")
        
        finally:
            # Cleanup temporary files
            if batch_dir.exists():
                shutil.rmtree(batch_dir, ignore_errors=True)
    
    def get_job_requirements_template(self) -> Dict:
        """Get a template for job requirements"""
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
            'required_degree': 'bachelor',
            'description': 'Template for defining job requirements'
        }
    
    async def compare_candidates(self, files: List[UploadFile], 
                                job_requirements: Dict) -> Dict:
        """
        Compare multiple candidates side-by-side
        
        Args:
            files: List of resume PDFs (2-5 candidates)
            job_requirements: Job requirements dictionary
            
        Returns:
            Comparison matrix with scores and recommendations
        """
        if len(files) < 2 or len(files) > 5:
            raise HTTPException(
                status_code=400, 
                detail="Please provide 2-5 resumes for comparison"
            )
        
        temp_paths = []
        try:
            # Save uploaded files
            for file in files:
                if not file.filename.endswith('.pdf'):
                    continue
                
                content = await file.read()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(content)
                    temp_paths.append(tmp.name)
            
            # Screen all candidates
            screener = CandidateScreener(job_requirements)
            results = screener.screen_batch(temp_paths)
            
            # Build comparison matrix
            comparison = {
                'candidates': [],
                'winner': None,
                'comparison_date': datetime.now().isoformat()
            }
            
            for idx, result in enumerate(results):
                if 'error' in result:
                    continue
                
                comparison['candidates'].append({
                    'rank': idx + 1,
                    'name': result['candidate_info']['name'],
                    'overall_score': result['scoring']['overall_score'],
                    'status': result['scoring']['status'],
                    'skills_score': result['scoring']['breakdown']['skills']['score'],
                    'experience_score': result['scoring']['breakdown']['experience']['score'],
                    'education_score': result['scoring']['breakdown']['education']['score'],
                    'years_experience': result['scoring']['breakdown']['experience']['years'],
                    'matched_skills': result['scoring']['breakdown']['skills']['details']['matched_skills']
                })
            
            if comparison['candidates']:
                comparison['winner'] = comparison['candidates'][0]
            
            return {
                'success': True,
                'comparison': comparison,
                'message': 'Candidates compared successfully'
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
        
        finally:
            # Cleanup
            for path in temp_paths:
                if os.path.exists(path):
                    os.unlink(path)
