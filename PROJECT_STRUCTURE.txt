Resume Analyzer - Professional Project Structure
================================================

resume-summarizer/
│
├── app.py                          # Main FastAPI application (entry point)
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (API keys)
├── .gitignore                     # Git ignore rules
├── PROJECT_STRUCTURE.txt          # This file
│
├── src/                           # Source code modules
│   ├── __init__.py
│   │
│   ├── scrapers/                  # Web scraping modules
│   │   ├── __init__.py
│   │   └── linkedin_scraper.py    # LinkedIn profile extraction
│   │
│   ├── builders/                  # Data processing modules
│   │   ├── __init__.py
│   │   └── profile_builder.py     # Resume + LinkedIn merger
│   │
│   ├── recommenders/              # AI recommendation modules
│   │   ├── __init__.py
│   │   └── job_recommender.py     # Job matching engine
│   │
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       ├── pdf_qa_system.py       # CLI version (legacy)
│       └── list_models.py         # Model listing utility
│
├── static/                        # Frontend assets
│   ├── index.html                 # Main UI
│   ├── script.js                  # Frontend logic
│   └── style.css                  # Styling
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_system.py             # System tests
│
├── docs/                          # Documentation
│   ├── README.md                  # Project overview
│   ├── ARCHITECTURE.md            # Technical architecture
│   ├── SETUP.md                   # Setup instructions
│   ├── FLOW_DIAGRAM.md            # System flow diagrams
│   ├── PROJECT_COMPLETE.md        # Completion summary
│   ├── QUICKSTART.md              # Quick start guide
│   └── IMPLEMENTATION_SUMMARY.md  # Implementation details
│
└── venv/                          # Virtual environment (not in git)


Module Organization
===================

src/scrapers/
  - LinkedInScraper: Selenium-based profile extraction
  - Handles browser automation and data scraping

src/builders/
  - ProfileBuilder: Merges resume and LinkedIn data
  - Deduplicates skills, experience, education
  - Implements smart merging logic

src/recommenders/
  - JobRecommender: AI-powered job matching
  - Calculates match scores
  - Generates personalized recommendations

src/utils/
  - pdf_qa_system: CLI version for testing
  - list_models: Utility to list available AI models


Import Structure
================

From app.py:
  from src.scrapers import LinkedInScraper
  from src.builders import ProfileBuilder
  from src.recommenders import JobRecommender

From tests:
  from src.scrapers import LinkedInScraper
  from src.builders import ProfileBuilder
  from src.recommenders import JobRecommender


Running the Application
=======================

1. Install dependencies:
   pip install -r requirements.txt

2. Configure environment:
   Create .env file with GEMINI_API_KEY

3. Run tests:
   python tests/test_system.py

4. Start server:
   python app.py

5. Open browser:
   http://localhost:8000


File Purposes
=============

Core Application:
  app.py              - FastAPI server with all endpoints
  requirements.txt    - Python package dependencies
  .env               - API keys and secrets

Source Modules:
  linkedin_scraper.py - Extracts LinkedIn profiles
  profile_builder.py  - Merges resume + LinkedIn data
  job_recommender.py  - Generates job recommendations
  pdf_qa_system.py    - CLI version for testing
  list_models.py      - Lists available AI models

Frontend:
  index.html         - UI structure and layout
  script.js          - Frontend logic and API calls
  style.css          - Styling and animations

Tests:
  test_system.py     - Verifies all components working

Documentation:
  README.md          - Project overview and features
  ARCHITECTURE.md    - Technical architecture details
  SETUP.md           - Detailed setup instructions
  FLOW_DIAGRAM.md    - System flow visualizations
  QUICKSTART.md      - Quick start guide
  PROJECT_COMPLETE.md - Completion summary
  IMPLEMENTATION_SUMMARY.md - Implementation details


Benefits of This Structure
===========================

✓ Clear separation of concerns
✓ Easy to navigate and understand
✓ Scalable for future additions
✓ Professional organization
✓ Follows Python best practices
✓ Modular and maintainable
✓ Easy to test individual components
✓ Documentation centralized in docs/
✓ Source code organized by function
✓ Clean import paths


Adding New Features
===================

New scraper:
  → Add to src/scrapers/

New data processor:
  → Add to src/builders/

New recommendation engine:
  → Add to src/recommenders/

New utility:
  → Add to src/utils/

New test:
  → Add to tests/

New documentation:
  → Add to docs/
