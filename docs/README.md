# Resume Summarizer

AI-powered resume analysis and intelligent job recommendation system powered by Groq API.

## Overview

Resume Summarizer is a comprehensive web application that analyzes resumes using advanced AI models to provide:
- Detailed resume parsing and structured data extraction
- Professional career analysis and insights
- AI-powered chat interface for resume questions
- LinkedIn profile integration and data merging
- Intelligent job recommendations based on profile

## Features

- **Resume Analysis**: Extract and analyze resume data using AI
- **Structured Extraction**: Convert unstructured resume text into organized JSON format
- **Career Insights**: Get detailed analysis including strengths, improvement areas, and career trajectory
- **Interactive Chat**: Ask questions about your resume with AI-powered responses
- **LinkedIn Integration**: Merge LinkedIn profile data with resume information
- **Job Recommendations**: Get personalized job recommendations based on your unified profile
- **Session Management**: Secure session handling for user data

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/LLM**: Groq API (openai/gpt-oss-120b model)
- **Web Scraping**: Selenium with ChromeDriver
- **PDF Processing**: PyPDF2
- **Frontend**: HTML5, CSS3, JavaScript
- **Server**: Uvicorn

## Project Structure

```
resume-summarizer/
├── config.py                 # Configuration and constants
├── models.py                 # Pydantic request/response models
├── services.py               # Business logic and AI operations
├── session_manager.py        # Session management utilities
├── handlers.py               # Route handlers for endpoints
├── main.py                   # FastAPI application entry point
├── app.py                    # Legacy main app (deprecated, use main.py)
│
├── src/
│   ├── scrapers/            # LinkedIn and web scraping
│   │   └── linkedin_scraper.py
│   ├── builders/            # Profile building and merging
│   │   └── profile_builder.py
│   ├── recommenders/        # Job recommendation engine
│   │   └── job_recommender.py
│   └── utils/               # Utility functions
│       ├── list_models.py
│       └── pdf_qa_system.py
│
├── static/                   # Frontend assets
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/                    # Test suite
│   └── test_system.py
│
├── docs/                     # Documentation
│   └── README.md
│
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── PROJECT_STRUCTURE.md      # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome/Chromium browser
- ChromeDriver (matching your Chrome version)
- Groq API key

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd resume-summarizer
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5: Verify Installation
```bash
python tests/test_system.py
```

All tests should pass with `[PASS]` status.

## Usage

### Starting the Application
```bash
python main.py
```

The application will start at: `http://localhost:8000`

### API Endpoints

#### 1. Upload Resume
```
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- session_id: unique session identifier

Response:
{
  "message": "Resume analyzed successfully",
  "resume_data": {...},
  "characters": 5234
}
```

#### 2. Get Analysis
```
POST /get-analysis
Content-Type: application/json

Request:
{
  "session_id": "your-session-id"
}

Response:
{
  "resume_data": {...},
  "analysis": {
    "overall_score": "...",
    "career_trajectory": "...",
    "key_strengths": "...",
    "improvement_areas": "...",
    "industry_fit": "...",
    "next_career_moves": "...",
    "suggested_job_summary": "..."
  }
}
```

#### 3. Chat
```
POST /chat
Content-Type: application/json

Request:
{
  "message": "What skills should I highlight?",
  "session_id": "your-session-id"
}

Response:
{
  "response": "Based on your resume..."
}
```

#### 4. Add LinkedIn Profile
```
POST /add-linkedin
Content-Type: application/json

Request:
{
  "linkedin_url": "https://linkedin.com/in/username",
  "session_id": "your-session-id"
}

Response:
{
  "message": "LinkedIn profile processed successfully",
  "unified_profile": {...},
  "info": "Merged data from resume + LinkedIn..."
}
```

#### 5. Skip LinkedIn
```
POST /skip-linkedin
Content-Type: application/json

Request:
{
  "session_id": "your-session-id"
}

Response:
{
  "message": "Profile created from resume only",
  "unified_profile": {...}
}
```

#### 6. Recommend Jobs
```
POST /recommend-jobs
Content-Type: application/json

Request:
{
  "session_id": "your-session-id"
}

Response:
{
  "message": "Job recommendations generated successfully",
  "recommendations": {...}
}
```

#### 7. Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "service": "Resume Summarizer"
}
```

## Configuration

### Environment Variables
Configure in `.env` file:

```
# Groq API Configuration
GROQ_API_KEY=your_api_key_here

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Session Settings
REQUEST_TIMEOUT=60  # seconds
```

### API Settings
Modify in `config.py`:
- `GROQ_MODEL`: Change the AI model (default: 'openai/gpt-oss-120b')
- `MAX_FILE_SIZE`: Maximum PDF file size in bytes
- `REQUEST_TIMEOUT`: Session timeout duration

## Testing

Run the complete system test:
```bash
python tests/test_system.py
```

Tests include:
- Import verification
- Environment configuration
- ChromeDriver availability
- Groq API connectivity
- Profile builder functionality

## Development

### Code Organization
- **config.py**: Configuration management
- **models.py**: Data validation (Pydantic)
- **services.py**: Core business logic
- **session_manager.py**: Session handling
- **handlers.py**: HTTP request handlers
- **main.py**: FastAPI application setup

### Adding New Features

1. Add request/response models in `models.py`
2. Implement business logic in `services.py`
3. Create handler class in `handlers.py`
4. Add route in `main.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include docstrings for all modules/functions/classes
- Use professional naming conventions

## Troubleshooting

### Issue: ChromeDriver Not Found
**Solution**: Install ChromeDriver matching your Chrome version
- Windows: `choco install chromedriver`
- Mac: `brew install chromedriver`
- Linux: `sudo apt-get install chromium-chromedriver`

### Issue: GROQ_API_KEY not found
**Solution**: Create `.env` file with valid API key
```
GROQ_API_KEY=your_actual_key_here
```

### Issue: Port 8000 Already in Use
**Solution**: Change port in `main.py`
```python
uvicorn.run(app, host="127.0.0.1", port=8001)
```

### Issue: LinkedIn Scraping Fails
**Solution**: LinkedIn structure may have changed
- Check if LinkedIn selectors are still valid
- Update selectors in `src/scrapers/linkedin_scraper.py`
- System automatically falls back to resume-only mode

## Performance Optimization

- **Session Cleanup**: Automatic cleanup of expired sessions every 60 seconds
- **File Upload**: Limit to 10MB per file
- **AI Requests**: Uses fast Groq API for low-latency responses
- **Caching**: Session data cached in memory

## Security Considerations

- API keys stored in environment variables (not in code)
- File uploads validated (PDF only)
- Session timeouts prevent memory leaks
- No sensitive data logged to console in production

## API Limits

- **Max File Size**: 10MB per resume
- **Max Requests**: 30 requests per minute (configurable)
- **Session Timeout**: 60 seconds of inactivity
- **Groq API**: Depends on Groq plan

## Support & Documentation

- Check `docs/README.md` for detailed documentation
- Review `PROJECT_STRUCTURE.md` for architecture details
- Run tests with: `python tests/test_system.py`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Changelog

### Version 1.0.0 (2025-12-31)
- Initial release
- Resume parsing and analysis
- LinkedIn profile integration
- Job recommendations
- Chat interface
