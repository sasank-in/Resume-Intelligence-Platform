# Resume Analyzer with Job Recommendations

An intelligent resume analysis and job recommendation system powered by Google's Gemini AI. Upload your resume, optionally add your LinkedIn profile, and get AI-powered job recommendations based on semantic similarity matching.

## Features

📄 **Resume Analysis** - Upload PDF resume for instant AI-powered extraction  
🔗 **LinkedIn Integration** - Optional LinkedIn profile scraping for enhanced data  
🤝 **Profile Merging** - Combines resume + LinkedIn into unified profile  
🎯 **Job Recommendations** - AI-powered job matching with semantic similarity  
📊 **Match Scoring** - See how well you match each recommended position  
💡 **Career Insights** - Get personalized career development recommendations  
✨ **Beautiful UI** - Modern, responsive design with smooth animations  

## User Flow

```
1. Upload Resume (PDF)
   ↓
2. Ask: "Do you want to share LinkedIn profile?"
   ↓
   Yes → LinkedIn Extraction → Profile Merger
   No  → Resume-Only Processing
   ↓
3. Unified Profile Builder
   ↓
4. Job Recommendations (AI-powered semantic matching)
```

## Tech Stack

- **Backend**: FastAPI + Python
- **AI**: Google Gemini 2.0 Flash
- **Web Scraping**: Selenium WebDriver
- **PDF Processing**: PyPDF2
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Architecture**: Modular, scalable design

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Chrome WebDriver for Selenium:
   - Download ChromeDriver: https://chromedriver.chromium.org/
   - Or install via package manager:
     ```bash
     # Windows (chocolatey)
     choco install chromedriver
     
     # Mac
     brew install chromedriver
     
     # Linux
     sudo apt-get install chromium-chromedriver
     ```

3. Create `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Get your free API key at: https://makersuite.google.com/app/apikey

## Usage

### Web Application

Run the FastAPI web app:
```bash
python app.py
```

Then open your browser to: http://localhost:8000

**Complete Flow:**
1. Upload your resume (PDF)
2. Choose to add LinkedIn profile or skip
3. View your unified profile
4. Get AI-powered job recommendations
5. See match scores and career insights

### Features in Detail

**Resume Upload**
- Extracts text from PDF
- AI structures data (name, skills, experience, education)
- Displays professional profile

**LinkedIn Integration (Optional)**
- Scrapes public LinkedIn profile
- Extracts additional skills and experience
- Merges with resume data for complete profile

**Job Recommendations**
- AI analyzes your complete profile
- Generates 5 personalized job recommendations
- Shows match scores (0-100%)
- Identifies matching skills and gaps
- Provides salary ranges and growth potential
- Offers career development insights

## How It Works

### System Architecture

```
┌─────────────────┐
│  Resume Upload  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  PDF Extraction │      │ LinkedIn Scraper │
│   (PyPDF2)      │      │   (Selenium)     │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Profile Builder│
         │  (Merge Data)  │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Job Recommender│
         │  (Gemini AI)   │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Recommendations│
         │  + Insights    │
         └────────────────┘
```

### Processing Pipeline

1. **Resume Extraction**
   - Upload PDF file
   - Extract text with PyPDF2
   - AI structures data into JSON

2. **LinkedIn Integration** (Optional)
   - User provides LinkedIn URL
   - Selenium scrapes public profile
   - Extracts skills, experience, education

3. **Profile Merging**
   - Combines resume + LinkedIn data
   - Removes duplicates
   - Prioritizes most complete information
   - Creates unified profile

4. **Job Recommendation**
   - AI analyzes unified profile
   - Semantic similarity matching
   - Generates 5 personalized recommendations
   - Calculates match scores
   - Identifies skill gaps

5. **Career Insights**
   - Strongest areas analysis
   - Industry recommendations
   - Next-level role suggestions
   - Skill development priorities

## API Endpoints

### POST /upload
Upload and analyze resume PDF
- **Input**: PDF file + session_id
- **Output**: Structured resume data

### POST /add-linkedin
Add LinkedIn profile to session
- **Input**: linkedin_url + session_id
- **Output**: LinkedIn data + unified profile

### POST /skip-linkedin
Build profile from resume only
- **Input**: session_id
- **Output**: Unified profile (resume-only)

### POST /recommend-jobs
Generate job recommendations
- **Input**: session_id
- **Output**: 5 job recommendations + career insights

### POST /get-analysis
Get detailed career analysis
- **Input**: session_id
- **Output**: Career assessment and recommendations

### POST /chat
Chat with AI career coach
- **Input**: message + session_id
- **Output**: AI response

## Benefits

✅ Complete career profile from multiple sources  
✅ AI-powered job matching with semantic similarity  
✅ Personalized recommendations based on your profile  
✅ Skill gap analysis for career development  
✅ Match scores to prioritize opportunities  
✅ Industry and role recommendations  
✅ Optional LinkedIn integration for richer data  
✅ Fast, automated candidate assessment  
✅ No complex setup or databases needed  

## Modules

### linkedin_scraper.py
- Selenium-based LinkedIn profile scraper
- Extracts name, headline, skills, experience, education
- Headless browser support
- Error handling and fallbacks

### profile_builder.py
- Merges resume and LinkedIn data
- Removes duplicates intelligently
- Prioritizes most complete information
- Handles resume-only mode

### job_recommender.py
- AI-powered job recommendation engine
- Semantic similarity matching
- Match score calculation
- Career insights generation
- Skill gap analysis

### app.py
- FastAPI web server
- Session management
- API endpoints for complete flow
- Integration of all modules  

## Limitations

- LinkedIn scraping requires public profiles
- Selenium needs ChromeDriver installed
- Rate limits on Gemini API (free tier: 60 req/min)
- Resume processing limited to first 12,000 characters
- Session data stored in memory (lost on restart)

## Future Enhancements

- Job board integration (Indeed, LinkedIn Jobs)
- Real-time job matching with live postings
- Resume optimization suggestions
- Interview preparation based on job match
- Salary negotiation insights
- Application tracking system
- Email notifications for new matches
- Multi-user support with database
- Resume comparison tools
- ATS compatibility scoring

## License

MIT License - Feel free to use and modify!
