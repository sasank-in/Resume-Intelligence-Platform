# Resume Screening System - Quick Start Guide

## Overview

The Resume Screening System automates the process of evaluating job applications by parsing resumes, scoring candidates against job requirements, and ranking them automatically.

## Quick Start

### 1. Access the Screening System

Navigate to: `http://localhost:8000/screening.html`

### 2. Define Job Requirements

Fill in the job requirements form:

- **Job Title**: e.g., "Senior Software Engineer"
- **Required Skills**: Comma-separated list (e.g., "python, javascript, sql, git")
- **Preferred Skills**: Comma-separated list (e.g., "react, docker, aws")
- **Min Experience**: Minimum years of experience (e.g., 2)
- **Max Experience**: Maximum years of experience (e.g., 5)
- **Required Degree**: Select from dropdown (Associate, Bachelor, Master, PhD)

### 3. Upload Resumes

- Click the upload area or drag and drop PDF files
- You can upload single or multiple resumes (up to 50)
- Only PDF format is supported

### 4. Screen Candidates

- Click "Screen Candidates" button
- Wait for processing (typically 5-10 seconds per resume)
- View results automatically

### 5. Review Results

The results page shows:

- **Summary Statistics**: Total processed, highly recommended, recommended, maybe, average score
- **Top Candidates**: Ranked list with detailed scores
- **Candidate Cards**: Individual analysis with:
  - Overall score (0-100)
  - Status classification
  - Matched skills
  - Contact information

## Scoring System

### Overall Score Calculation

```
Overall Score = (Skills × 50%) + (Experience × 30%) + (Education × 20%)
```

### Skills Scoring

- **Required Skills**: 70% weight
- **Preferred Skills**: 30% weight
- Matches are identified automatically from resume text

### Experience Scoring

- **Below Minimum**: Proportional score (0-50)
- **Within Range**: 100 points
- **Above Maximum**: 75 points (overqualified)

### Education Scoring

- **Meets or Exceeds**: 100 points
- **Below Requirement**: Proportional (0-80)
- **No Relevant Education**: 0 points

### Status Classification

- **80-100**: HIGHLY_RECOMMENDED (Green)
- **60-79**: RECOMMENDED (Blue)
- **40-59**: MAYBE (Orange)
- **0-39**: NOT_RECOMMENDED (Red)

## Example Job Requirements

### Software Engineer

```json
{
  "job_title": "Software Engineer",
  "required_skills": ["python", "javascript", "sql", "git"],
  "preferred_skills": ["react", "docker", "aws", "agile"],
  "min_experience_years": 2,
  "max_experience_years": 5,
  "required_degree": "bachelor"
}
```

### Data Scientist

```json
{
  "job_title": "Data Scientist",
  "required_skills": ["python", "machine learning", "statistics", "sql"],
  "preferred_skills": ["tensorflow", "pytorch", "aws", "spark"],
  "min_experience_years": 3,
  "max_experience_years": 7,
  "required_degree": "master"
}
```

### DevOps Engineer

```json
{
  "job_title": "DevOps Engineer",
  "required_skills": ["docker", "kubernetes", "aws", "ci/cd"],
  "preferred_skills": ["terraform", "ansible", "python", "monitoring"],
  "min_experience_years": 3,
  "max_experience_years": 8,
  "required_degree": "bachelor"
}
```

## API Usage

### Parse Single Resume

```bash
curl -X POST "http://localhost:8000/screening/parse-resume" \
  -F "file=@resume.pdf"
```

### Screen Single Candidate

```bash
curl -X POST "http://localhost:8000/screening/screen-candidate" \
  -F "file=@resume.pdf" \
  -F 'job_requirements={"job_title":"Software Engineer","required_skills":["python","javascript"],"min_experience_years":2,"required_degree":"bachelor"}'
```

### Screen Batch

```bash
curl -X POST "http://localhost:8000/screening/screen-batch" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F "files=@resume3.pdf" \
  -F 'job_requirements={"job_title":"Software Engineer","required_skills":["python","javascript"],"min_experience_years":2,"required_degree":"bachelor"}'
```

### Get Template

```bash
curl -X GET "http://localhost:8000/screening/job-requirements-template"
```

## Tips for Best Results

### Resume Format

- Use text-based PDFs (not scanned images)
- Include clear section headers (Experience, Education, Skills)
- List skills explicitly
- Include dates for work experience
- Provide complete contact information

### Job Requirements

- Be specific with required skills
- Use common skill names (e.g., "python" not "Python 3.x")
- Set realistic experience ranges
- Include both technical and soft skills
- Use preferred skills for nice-to-have qualifications

### Batch Processing

- Group similar positions together
- Use consistent job requirements
- Process 10-50 resumes at a time for optimal performance
- Review top 10-20% of candidates for interviews

## Troubleshooting

### No Candidates Found

- Check if required skills are too specific
- Verify resume PDFs are text-based
- Ensure experience range is reasonable
- Review education requirements

### Low Scores

- Adjust required vs preferred skills balance
- Widen experience range
- Lower education requirements
- Check skill name variations

### Processing Errors

- Verify PDF files are not corrupted
- Ensure files are under 10MB
- Check that PDFs contain extractable text
- Try processing files individually

## Advanced Features

### Candidate Comparison

Compare 2-5 candidates side-by-side:

```bash
curl -X POST "http://localhost:8000/screening/compare-candidates" \
  -F "files=@candidate1.pdf" \
  -F "files=@candidate2.pdf" \
  -F 'job_requirements={...}'
```

### Custom Filtering

Filter results programmatically:

```python
from src.parsers.batch_screener import BatchScreeningSystem

# Initialize system
batch_system = BatchScreeningSystem(job_requirements)

# Process resumes
results = batch_system.process_applications('resumes/')

# Filter by score
top_candidates = batch_system.filter_candidates(
    results['results'],
    min_score=70,
    status_filter=['HIGHLY_RECOMMENDED', 'RECOMMENDED']
)

# Generate interview list
interview_list = batch_system.generate_interview_list(
    results['results'],
    top_n=10
)
```

## Best Practices

1. **Define Clear Requirements**: Be specific about must-have vs nice-to-have skills
2. **Use Consistent Criteria**: Apply same requirements across all candidates
3. **Review Top Candidates**: Don't rely solely on scores, review top 10-20%
4. **Adjust Weights**: Customize scoring weights based on role importance
5. **Batch Process**: Screen multiple candidates together for efficiency
6. **Export Reports**: Save results for record-keeping and analysis
7. **Iterate**: Refine requirements based on candidate pool quality

## Support

For issues or questions:
- Check the main README.md
- Review API documentation
- Test with sample resumes first
- Verify job requirements format

## Next Steps

After screening:
1. Review top candidates
2. Schedule interviews with highly recommended candidates
3. Export results for hiring team
4. Refine job requirements based on candidate pool
5. Process additional batches as needed

---

Ready to streamline your hiring process? Start screening candidates now!
