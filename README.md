# Resume Summarizer

AI-powered resume analysis and intelligent job recommendation system powered by Groq API.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GROQ_API_KEY=your_key_here" > .env

# Run application
python main.py
```

Open browser to `http://localhost:8000`

## Documentation

- **[Setup & Usage](docs/README.md)** - Installation, configuration, API reference
- **[Architecture](docs/PROJECT_STRUCTURE.md)** - Project structure, module descriptions, design patterns

## Features

- Resume analysis & parsing
- AI-powered insights
- Interactive chat about your resume
- LinkedIn profile integration
- Job recommendations

## Project Structure

```
resume-summarizer/
├── app/                    # Application modules
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   ├── services.py        # Business logic
│   ├── handlers.py        # Route handlers
│   └── session_manager.py # Session management
│
├── src/                   # Business logic modules
├── static/                # Frontend
├── tests/                 # Test suite
├── docs/                  # Documentation
│
├── main.py               # Application entry point
├── requirements.txt
└── .env                  # Configuration (create this)
```

## Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI**: Groq API (openai/gpt-oss-120b)
- **PDF Processing**: PyPDF2
- **Web Scraping**: Selenium
- **Frontend**: HTML5, CSS3, JavaScript

## License

[Add license information]

## Support

See [documentation](docs/) for detailed setup and troubleshooting guides.
