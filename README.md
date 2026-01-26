# Resume Analyzer Pro

AI-powered resume analysis and job matching system. Upload your resume, get instant insights, and discover perfect job matches with comprehensive career analysis.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 3. Run the application
python main.py
```

Open your browser to: `http://localhost:8000`

## Overview

Resume Analyzer Pro is a comprehensive career intelligence platform that combines AI-powered resume analysis with job matching capabilities. The system provides detailed insights into your professional profile, identifies career opportunities, and offers actionable recommendations for career advancement.

### Core Capabilities

**Resume Analysis**
- Automated extraction of skills, experience, and education
- AI-generated career trajectory analysis
- Comprehensive strengths and development areas assessment
- Industry fit recommendations
- Salary insights based on experience and market data

**Job Intelligence**
- AI-powered job recommendations matched to your profile
- Skill gap analysis for target positions
- Career progression pathways
- Industry-specific insights

**Interactive Features**
- AI-powered chat interface for career guidance
- LinkedIn profile integration for enhanced analysis
- Session-based data management
- Responsive design for all devices

## Features

- Smart Resume Parsing: AI extracts all relevant information from PDF resumes
- Career Analysis: Detailed assessment of professional trajectory and strengths
- Job Matching: Intelligent recommendations based on skills and experience
- LinkedIn Integration: Enhance your profile with LinkedIn data
- AI Chat Assistant: Interactive career guidance and resume questions
- Mobile Responsive: Optimized experience across all devices

## Technical Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Engine**: Groq API (Llama models)
- **PDF Processing**: PyPDF2
- **Web Scraping**: Selenium (LinkedIn integration)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Session Management**: In-memory with automatic cleanup

## Requirements

- Python 3.8 or higher
- Groq API key (free tier available at groq.com)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 2GB RAM minimum
- Internet connection for AI processing

## Installation

### Standard Setup

```bash
git clone <repository-url>
cd resume-analyzer
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python main.py
```

### Virtual Environment Setup (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python main.py
```

## Configuration

### API Key Setup

1. Visit [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate a new API key
4. Add to `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-70b-versatile
MAX_FILE_SIZE=10485760
SESSION_TIMEOUT=3600
```

## Project Structure

```
resume-analyzer/
├── app/                    # Application core
│   ├── handlers.py        # API route handlers
│   ├── models.py          # Pydantic data models
│   ├── services.py        # Business logic and AI integration
│   ├── session_manager.py # Session management
│   └── config.py          # Configuration settings
├── src/                   # Business modules
│   ├── utils/             # Utility functions
│   │   └── pdf_qa_system.py
│   ├── recommenders/      # Job recommendation engine
│   │   └── job_recommender.py
│   ├── scrapers/          # Web scraping modules
│   │   └── linkedin_scraper.py
│   └── builders/          # Profile building
│       └── profile_builder.py
├── static/                # Frontend assets
│   ├── index.html         # Upload page
│   ├── analysis.html      # Analysis results page
│   ├── script.js          # Upload page logic
│   ├── analysis.js        # Analysis page logic
│   └── style.css          # Application styles
├── docs/                  # Documentation
├── tests/                 # Test suite
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (create this)
```

## API Endpoints

### Resume Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload and analyze resume PDF |
| `/get-analysis` | POST | Retrieve analysis for session |
| `/chat` | POST | Chat with AI about resume |

### Profile Enhancement

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add-linkedin` | POST | Add LinkedIn profile data |
| `/skip-linkedin` | POST | Skip LinkedIn integration |

### Job Recommendations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/recommend-jobs` | POST | Get personalized job recommendations |

## Usage Guide

### Basic Workflow

1. **Upload Resume**
   - Navigate to home page
   - Upload PDF resume (max 10MB)
   - Wait for processing (typically 5-10 seconds)

2. **Review Analysis**
   - Automatic redirect to analysis page
   - Review career trajectory and strengths
   - Examine development areas and recommendations

3. **LinkedIn Integration (Optional)**
   - Add LinkedIn profile URL
   - System merges data for enhanced analysis
   - Or skip to continue with resume data only

4. **Get Job Recommendations**
   - Click "Generate Job Recommendations"
   - Review matched positions
   - Analyze skill gaps and salary ranges

5. **Interactive Chat**
   - Use AI assistant for career questions
   - Get personalized guidance
   - Explore career options

### Best Practices

- Use text-based PDF resumes (not scanned images)
- Ensure resume includes complete work history
- Provide accurate LinkedIn profile URL if using integration
- Ask specific questions in the chat interface
- Review all recommendations before making career decisions

## Troubleshooting

### Common Issues

**API Key Errors**
```
Error: GROQ_API_KEY not found
Solution: Ensure .env file exists with valid API key
```

**Port Conflicts**
```
Error: Port 8000 already in use
Solution: Change port in main.py or terminate existing process
```

**PDF Processing Failures**
```
Error: Failed to extract text from PDF
Solution: Ensure PDF is text-based, not a scanned image
```

**Session Expired**
```
Error: No resume uploaded for this session
Solution: Upload resume again (sessions expire after 1 hour)
```

### Debug Mode

Enable detailed logging:

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

- Sessions automatically cleaned up after 1 hour
- PDF processing optimized for files up to 10MB
- AI responses cached per session
- Concurrent request handling via FastAPI

## Security Considerations

- API keys stored in environment variables
- File uploads validated for type and size
- Session data isolated per user
- Temporary files cleaned up automatically
- No persistent storage of sensitive data

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black app/ src/

# Lint code
pylint app/ src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is provided as-is for educational and professional use.

## Support

For technical issues or questions:
- Review documentation in `docs/` folder
- Check code comments for implementation details
- Test with sample resumes before production use

## Changelog

### Version 1.0.0
- Initial release
- Resume upload and analysis
- AI-powered career insights
- Job recommendations
- LinkedIn integration
- Interactive chat assistant
- Responsive web interface

---

Built with FastAPI and Groq AI. Designed for modern job seekers and career professionals.