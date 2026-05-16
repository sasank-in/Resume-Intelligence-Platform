"""
Batch Resume Screening System
Process multiple resumes and generate screening reports
"""
from src._logprint import make_log_print
print = make_log_print(__name__)
import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import csv

from .resume_parser import CandidateScreener, ResumeParser


class BatchScreeningSystem:
    """
    System for processing multiple resumes and generating reports
    """
    
    def __init__(self, job_requirements: Dict, output_dir: str = 'screening_results'):
        """
        Initialize batch screening system
        
        Args:
            job_requirements: Job requirements dictionary
            output_dir: Directory to save results
        """
        self.screener = CandidateScreener(job_requirements)
        self.job_requirements = job_requirements
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def find_resumes(self, directory: str) -> List[str]:
        """Find all PDF resumes in directory"""
        resume_dir = Path(directory)
        pdf_files = list(resume_dir.glob('*.pdf'))
        return [str(f) for f in pdf_files]
    
    def process_applications(self, resume_directory: str) -> Dict:
        """
        Process all applications in directory
        
        Args:
            resume_directory: Directory containing resume PDFs
            
        Returns:
            Processing summary and results
        """
        print(f"\n{'='*60}")
        print(f"BATCH RESUME SCREENING")
        print(f"{'='*60}")
        print(f"Job Title: {self.job_requirements.get('job_title', 'N/A')}")
        print(f"Resume Directory: {resume_directory}")
        
        # Find all resumes
        resume_paths = self.find_resumes(resume_directory)
        print(f"\nFound {len(resume_paths)} resumes to process")
        
        if not resume_paths:
            print("No PDF files found in directory!")
            return {'error': 'No resumes found'}
        
        # Screen all candidates
        print("\nProcessing resumes...")
        results = self.screener.screen_batch(resume_paths)
        
        # Generate summary
        summary = self._generate_summary(results)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._save_json_report(results, f'screening_results_{timestamp}.json')
        self._save_csv_report(results, f'screening_summary_{timestamp}.csv')
        self._save_text_report(results, summary, f'screening_report_{timestamp}.txt')
        
        print(f"\n{'='*60}")
        print("SCREENING COMPLETE")
        print(f"{'='*60}")
        print(f"Total Processed: {summary['total_processed']}")
        print(f"Highly Recommended: {summary['highly_recommended']}")
        print(f"Recommended: {summary['recommended']}")
        print(f"Maybe: {summary['maybe']}")
        print(f"Not Recommended: {summary['not_recommended']}")
        print(f"Failed: {summary['failed']}")
        print(f"\nResults saved to: {self.output_dir}")
        
        return {
            'summary': summary,
            'results': results
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate screening summary statistics"""
        summary = {
            'total_processed': len(results),
            'highly_recommended': 0,
            'recommended': 0,
            'maybe': 0,
            'not_recommended': 0,
            'failed': 0,
            'average_score': 0.0,
            'top_candidates': []
        }
        
        scores = []
        for result in results:
            if 'error' in result:
                summary['failed'] += 1
                continue
            
            status = result.get('scoring', {}).get('status', '')
            score = result.get('scoring', {}).get('overall_score', 0)
            scores.append(score)
            
            if status == 'HIGHLY_RECOMMENDED':
                summary['highly_recommended'] += 1
            elif status == 'RECOMMENDED':
                summary['recommended'] += 1
            elif status == 'MAYBE':
                summary['maybe'] += 1
            else:
                summary['not_recommended'] += 1
        
        if scores:
            summary['average_score'] = round(sum(scores) / len(scores), 2)
        
        # Get top 5 candidates
        valid_results = [r for r in results if 'error' not in r]
        summary['top_candidates'] = [
            {
                'name': r['candidate_info']['name'],
                'score': r['scoring']['overall_score'],
                'status': r['scoring']['status']
            }
            for r in valid_results[:5]
        ]
        
        return summary
    
    def _save_json_report(self, results: List[Dict], filename: str):
        """Save detailed JSON report"""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump({
                'job_requirements': self.job_requirements,
                'screening_date': datetime.now().isoformat(),
                'results': results
            }, f, indent=2)
        print(f"JSON report saved: {output_path}")
    
    def _save_csv_report(self, results: List[Dict], filename: str):
        """Save CSV summary report"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Rank', 'Name', 'Email', 'Phone', 'Overall Score',
                'Status', 'Skills Score', 'Experience Score', 'Education Score',
                'Years Experience', 'File Path'
            ])
            
            # Data rows
            for idx, result in enumerate(results, 1):
                if 'error' in result:
                    writer.writerow([
                        idx, 'ERROR', '', '', 0, 'FAILED', 0, 0, 0, 0,
                        result.get('file_path', '')
                    ])
                    continue
                
                info = result['candidate_info']
                scoring = result['scoring']
                breakdown = scoring['breakdown']
                
                writer.writerow([
                    idx,
                    info.get('name', 'N/A'),
                    info.get('email', 'N/A'),
                    info.get('phone', 'N/A'),
                    scoring['overall_score'],
                    scoring['status'],
                    breakdown['skills']['score'],
                    breakdown['experience']['score'],
                    breakdown['education']['score'],
                    breakdown['experience']['years'],
                    result.get('file_path', '')
                ])
        
        print(f"CSV report saved: {output_path}")
    
    def _save_text_report(self, results: List[Dict], summary: Dict, filename: str):
        """Save human-readable text report"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("RESUME SCREENING REPORT\n")
            f.write("="*80 + "\n\n")
            
            # Job details
            f.write(f"Job Title: {self.job_requirements.get('job_title', 'N/A')}\n")
            f.write(f"Screening Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Applications: {summary['total_processed']}\n\n")
            
            # Summary statistics
            f.write("-"*80 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Highly Recommended: {summary['highly_recommended']}\n")
            f.write(f"Recommended: {summary['recommended']}\n")
            f.write(f"Maybe: {summary['maybe']}\n")
            f.write(f"Not Recommended: {summary['not_recommended']}\n")
            f.write(f"Failed to Process: {summary['failed']}\n")
            f.write(f"Average Score: {summary['average_score']}\n\n")
            
            # Top candidates
            f.write("-"*80 + "\n")
            f.write("TOP CANDIDATES\n")
            f.write("-"*80 + "\n")
            for idx, candidate in enumerate(summary['top_candidates'], 1):
                f.write(f"{idx}. {candidate['name']} - Score: {candidate['score']} ({candidate['status']})\n")
            f.write("\n")
            
            # Detailed results
            f.write("-"*80 + "\n")
            f.write("DETAILED CANDIDATE ANALYSIS\n")
            f.write("-"*80 + "\n\n")
            
            for idx, result in enumerate(results, 1):
                if 'error' in result:
                    f.write(f"{idx}. ERROR - {result.get('file_path', 'Unknown')}\n")
                    f.write(f"   Error: {result['error']}\n\n")
                    continue
                
                info = result['candidate_info']
                scoring = result['scoring']
                breakdown = scoring['breakdown']
                
                f.write(f"{idx}. {info.get('name', 'N/A')}\n")
                f.write(f"   Email: {info.get('email', 'N/A')}\n")
                f.write(f"   Phone: {info.get('phone', 'N/A')}\n")
                f.write(f"   Overall Score: {scoring['overall_score']}/100\n")
                f.write(f"   Status: {scoring['status']}\n\n")
                
                f.write(f"   Skills Match: {breakdown['skills']['score']}/100\n")
                f.write(f"     - Required: {breakdown['skills']['details']['required_matches']}/{breakdown['skills']['details']['required_total']}\n")
                f.write(f"     - Preferred: {breakdown['skills']['details']['preferred_matches']}/{breakdown['skills']['details']['preferred_total']}\n")
                f.write(f"     - Matched: {', '.join(breakdown['skills']['details']['matched_skills'][:5])}\n\n")
                
                f.write(f"   Experience: {breakdown['experience']['score']}/100\n")
                f.write(f"     - Years: {breakdown['experience']['years']}\n")
                f.write(f"     - Assessment: {breakdown['experience']['reason']}\n\n")
                
                f.write(f"   Education: {breakdown['education']['score']}/100\n")
                f.write(f"     - Assessment: {breakdown['education']['reason']}\n\n")
                
                f.write("-"*80 + "\n\n")
        
        print(f"Text report saved: {output_path}")
    
    def filter_candidates(self, results: List[Dict], 
                         min_score: float = 60,
                         status_filter: List[str] = None) -> List[Dict]:
        """
        Filter candidates by score and status
        
        Args:
            results: Screening results
            min_score: Minimum overall score
            status_filter: List of acceptable statuses
            
        Returns:
            Filtered results
        """
        filtered = []
        
        for result in results:
            if 'error' in result:
                continue
            
            score = result['scoring']['overall_score']
            status = result['scoring']['status']
            
            if score >= min_score:
                if status_filter is None or status in status_filter:
                    filtered.append(result)
        
        return filtered
    
    def generate_interview_list(self, results: List[Dict], 
                               top_n: int = 10) -> List[Dict]:
        """
        Generate list of candidates to interview
        
        Args:
            results: Screening results
            top_n: Number of top candidates to select
            
        Returns:
            List of interview candidates
        """
        # Filter out errors
        valid_results = [r for r in results if 'error' not in r]
        
        # Get top N
        interview_list = valid_results[:top_n]
        
        # Format for output
        formatted_list = []
        for idx, result in enumerate(interview_list, 1):
            info = result['candidate_info']
            scoring = result['scoring']
            
            formatted_list.append({
                'rank': idx,
                'name': info.get('name', 'N/A'),
                'email': info.get('email', 'N/A'),
                'phone': info.get('phone', 'N/A'),
                'score': scoring['overall_score'],
                'status': scoring['status'],
                'key_strengths': scoring['breakdown']['skills']['details']['matched_skills'][:5]
            })
        
        return formatted_list


# Example usage
if __name__ == "__main__":
    # Define job requirements
    job_requirements = {
        'job_title': 'Senior Full Stack Developer',
        'required_skills': ['python', 'javascript', 'react', 'sql', 'rest api'],
        'preferred_skills': ['docker', 'aws', 'redis', 'typescript', 'agile'],
        'min_experience_years': 3,
        'max_experience_years': 8,
        'required_degree': 'bachelor'
    }
    
    # Initialize batch screening system
    batch_system = BatchScreeningSystem(
        job_requirements=job_requirements,
        output_dir='screening_results'
    )
    
    # Process all resumes in directory
    # results = batch_system.process_applications('path/to/resumes')
    
    # Generate interview list
    # interview_list = batch_system.generate_interview_list(results['results'], top_n=10)
    # print(json.dumps(interview_list, indent=2))
    
    print("Batch Screening System initialized successfully!")
    print("Place resume PDFs in a directory and run process_applications()")
