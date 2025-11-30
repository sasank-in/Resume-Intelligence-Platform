# Resume Analyzer - AI-Powered Candidate Assessment

An intelligent resume analysis system powered by Google's Gemini AI that extracts, structures, and evaluates candidate profiles with detailed assessments.

## Features

📄 **Instant Analysis** - Upload a PDF resume and get AI-powered insights instantly  
🤖 **Structured Extraction** - Automatically extracts name, skills, experience, education, and more  
📊 **Detailed Assessment** - Provides career trajectory, strengths, improvements, and industry fit  
🎯 **Skill Recognition** - Identifies and categorizes all technical and soft skills  
📈 **Career Insights** - Analyzes professional growth and recommends next steps  
🌍 **Multilingual** - Recognizes certifications and languages  
✨ **Beautiful UI** - Modern, responsive design with smooth animations  

## Tech Stack

- **Backend**: FastAPI + Python
- **AI**: Google Gemini 1.5 Flash
- **PDF Processing**: PyPDF2
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Architecture**: Simple, lightweight, no databases

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Get your free API key at: https://makersuite.google.com/app/apikey

## Usage

### Web Application (Recommended)

Run the FastAPI web app:
```bash
python app.py
```

Then open your browser to: http://localhost:8000

**Features:**
- Upload resume PDF
- View extracted candidate profile
- See skills organized by category
- Review professional experience timeline
- Check education background
- Read AI-generated assessments
- Get recommendations for improvement

### CLI Version

Run the command-line version:
```bash
python pdf_qa_system.py
```

The CLI will:
1. Ask for a resume PDF path
2. Extract and structure resume data
3. Display candidate profile
4. Show AI analysis and recommendations

## How It Works

### Resume Processing Pipeline

```
1. PDF Upload
   ↓
2. Extract text with page markers
   ↓
3. Structured Data Extraction
   - Name, contact, headline
   - Skills (categorized)
   - Professional experience
   - Education background
   - Certifications, languages
   ↓
4. AI Analysis
   - Overall score (1-10)
   - Career trajectory analysis
   - Key strengths identification
   - Improvement areas
   - Industry fit assessment
   - Next career steps
   ↓
5. Display in Beautiful UI
```

### Extraction Fields

**Personal Info**
- Full name
- Email & phone
- Location
- Professional headline

**Professional Data**
- Skills (all identified)
- Work experience with achievements
- Education (degree, institution, year)
- Certifications
- Languages

**AI Analysis**
- Overall score with justification
- Career progression assessment
- Top 3 strengths
- Areas for improvement
- Best-fit industries
- Recommended next moves

## Outputs

### Structured Resume Data
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "headline": "Senior Software Engineer",
  "skills": ["Python", "JavaScript", "React", ...],
  "experience": [
    {
      "title": "Senior Engineer",
      "company": "Tech Corp",
      "duration": "2020 - Present",
      "highlights": ["Led team of 5", "Increased performance by 40%", ...]
    }
  ],
  "education": [
    {
      "degree": "BS Computer Science",
      "institution": "State University",
      "year": "2016"
    }
  ]
}
```

### AI Assessment
- **Overall Score**: Rated out of 10 with justification
- **Career Trajectory**: Analysis of growth and progression
- **Strengths**: Top professional strengths
- **Improvements**: Areas for skill development
- **Industry Fit**: Best matching industries
- **Next Steps**: Recommended career moves

## Benefits

✅ Fast resume screening for recruiters  
✅ Automated candidate assessment  
✅ Structured data extraction  
✅ Objective scoring system  
✅ Professional development insights  
✅ No complex setup needed  
✅ Works with free Gemini API tier  

## Limitations

- Processes resumes up to 12,000 characters for analysis
- Accuracy depends on resume formatting
- Requires internet connection for Gemini API
- Subject to API rate limits

## Future Enhancements

- Batch resume processing
- Resume comparison tools
- ATS optimization suggestions
- Interview preparation tips
- Salary insights
- Job recommendation engine
- Resume scoring benchmarks

- Add full document chunking for large PDFs
- Implement vector search for better retrieval
- Add multi-document support
- Export conversation history
- Add authentication

## License

MIT License - Feel free to use and modify!
