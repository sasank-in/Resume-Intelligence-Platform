# Resume Analyzer - Architecture

## System Overview

A lightweight, AI-powered resume analysis system that extracts structured data from PDFs and provides intelligent candidate assessment.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PyPDF2** - PDF text extraction
- **Google Gemini 1.5 Flash** - AI analysis and extraction
- **Python-dotenv** - Environment variable management

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks, clean code
- **Modern CSS** - Gradients, animations, responsive design
- **Inter Font** - Professional typography

## Architecture Decisions

### Why Structured Data Extraction?
- **Reliable**: Consistent JSON output from AI
- **Scalable**: Easy to process and store
- **Queryable**: Supports future features like filtering and search
- **Integration-friendly**: Works with ATS systems

### Why Gemini AI?
- **Powerful**: Understands resume context and terminology
- **Fast**: 1.5 Flash model is optimized for speed
- **Affordable**: Free tier sufficient for development
- **Accurate**: Can extract and assess complex career data

### Why No Vector Databases?
- **Simplicity**: Fewer dependencies and moving parts
- **Speed**: Direct AI processing is fast enough
- **Cost**: No infrastructure overhead
- **Maintenance**: Easier to debug and maintain

## Data Flow

```
1. Resume Upload (PDF)
   ↓
2. Text Extraction
   (PyPDF2 extracts text with page markers)
   ↓
3. Structured Extraction (Gemini AI)
   - Parse personal information
   - Extract skills
   - Identify experience
   - Extract education
   - Find certifications
   ↓
4. Session Storage
   (In-memory dictionary per user)
   ↓
5. AI Analysis
   - Generate assessment
   - Identify strengths/weaknesses
   - Suggest improvements
   ↓
6. Display in UI
   (Formatted resume sections)
```

## API Endpoints

### GET /
- **Purpose**: Serve main HTML page
- **Response**: HTML page with UI

### POST /upload
- **Input**: PDF file + session_id
- **Process**: 
  - Extract text from PDF
  - Run AI extraction
  - Structure data
- **Output**: Structured resume data
- **Storage**: Saves to session

### POST /get-analysis
- **Input**: session_id
- **Process**: 
  - Retrieve stored resume data
  - Generate AI analysis
  - Structure assessment
- **Output**: Analysis report
- **Fields**: Score, trajectory, strengths, improvements, industry fit, next steps

## Data Structures

### Session Storage
```python
sessions = {
    "session_id": {
        "resume_text": "Full PDF content with page markers",
        "resume_data": {
            "name": "...",
            "email": "...",
            "skills": [...],
            "experience": [...],
            "education": [...]
        }
    }
}
```

### Resume Data Schema
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "headline": "string",
  "summary": "string",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {
      "title": "string",
      "company": "string",
      "duration": "string",
      "highlights": ["achievement1", ...]
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "year": "string",
      "details": "string"
    }
  ],
  "certifications": ["cert1", ...],
  "languages": ["lang1", ...],
  "strengths": ["strength1", ...],
  "recommendations": ["recommendation1", ...]
}
```

### Analysis Schema
```json
{
  "overall_score": "8/10 - Strong technical background with leadership experience",
  "career_trajectory": "Steady growth from junior to senior roles...",
  "key_strengths": "Excellent problem-solving, team leadership, technical expertise...",
  "improvement_areas": "Limited international experience, could expand soft skills...",
  "industry_fit": "Tech, finance, consulting, startups...",
  "next_steps": "Consider management track or specialized certifications..."
}
```

## File Structure

```
qa-summarizer/
├── app.py                 # FastAPI server + endpoints
├── pdf_qa_system.py       # CLI version
├── requirements.txt       # Python dependencies
├── .env                   # API keys (gitignored)
├── README.md             # Documentation
├── ARCHITECTURE.md       # This file
├── static/
│   ├── index.html        # Main UI
│   ├── style.css         # Styling (429+ lines)
│   └── script.js         # Frontend logic
└── venv/                 # Virtual environment
```

## Frontend Architecture

### HTML Structure
- Header section with branding
- Upload section for PDF files
- Collapsible resume sections:
  - Candidate profile
  - Skills grid
  - Experience timeline
  - Education cards
  - AI analysis dashboard
  - Certifications & languages

### CSS Features
- Gradient backgrounds
- Smooth animations
- Responsive grid layout
- Timeline visualization for experience
- Card-based UI for sections
- Mobile-friendly design

### JavaScript Flow
1. File selection handler
2. FormData creation for upload
3. API call to `/upload`
4. Resume data parsing and display
5. Async call to `/get-analysis`
6. Analysis results rendering

## Processing Flow

### Resume Extraction
1. PDF uploaded and saved temporarily
2. PyPDF2 extracts text with page numbers
3. Gemini AI receives first 12,000 chars
4. AI returns structured JSON
5. Data stored in session
6. Temp file deleted

### Analysis Generation
1. Retrieve stored resume data
2. Create Gemini prompt with resume data
3. AI generates assessment
4. Parse JSON response
5. Return to frontend
6. Display analysis cards

## Session Management

- **Session ID**: Generated from timestamp (Date.now())
- **Storage**: In-memory dictionary (lost on server restart)
- **Persistence**: Per-user session isolation
- **Cleanup**: Optional garbage collection on long intervals

## Performance Considerations

- **Text Limit**: 12,000 chars for extraction (balance accuracy vs speed)
- **API Calls**: 2 per resume (upload + analysis)
- **Response Time**: ~5-10 seconds typical
- **Memory**: Minimal footprint per session
- **Concurrency**: Handles multiple users independently

## Security Notes

- No authentication (consider adding for production)
- No file persistence (temp files auto-deleted)
- API key stored in environment variable
- CORS not configured (restrict for production)
- No input validation on file uploads (add in production)

## Future Enhancement Paths

### Phase 2: Storage & Persistence
- Add database (PostgreSQL) for history
- User authentication system
- Resume comparison tools

### Phase 3: Advanced Analytics
- Batch processing
- Industry benchmarking
- Salary insights
- ATS optimization scoring

### Phase 4: Integration
- Applicant Tracking System (ATS) connectors
- Interview prep suggestions
- Job recommendation engine
- LinkedIn integration### POST /ask
- **Input**: Question + session_id
- **Process**: Build context, query Gemini
- **Output**: Answer
- **Storage**: Adds to chat history

## Limitations & Trade-offs

### Current Limitations
1. **Document Size**: Only first 10k chars used for Q&A
2. **Context Window**: Last 3 Q&A pairs only
3. **No Persistence**: Sessions lost on restart
4. **Single User**: In-memory storage

### Why These Are OK
1. **10k chars** = ~5-7 pages, enough for most questions
2. **3 Q&A pairs** = sufficient context for follow-ups
3. **No persistence** = simpler, stateless design
4. **In-memory** = fast, no database needed

## Future Enhancements (If Needed)

### Easy Wins
- [ ] Increase context window to 20k chars
- [ ] Store more Q&A pairs (5-10)
- [ ] Add session timeout/cleanup
- [ ] Export conversation as PDF

### Medium Effort
- [ ] Add document chunking for large PDFs
- [ ] Implement Redis for session storage
- [ ] Add user authentication
- [ ] Multi-document support

### Complex (Only If Really Needed)
- [ ] Add vector database (FAISS/Chroma)
- [ ] Implement proper RAG pipeline
- [ ] Add semantic search
- [ ] Real-time collaboration

## Performance

### Typical Response Times
- PDF Upload: 2-5 seconds (depends on size)
- Summary Generation: 3-8 seconds
- Question Answering: 2-4 seconds

### Bottlenecks
1. **Gemini API**: Main bottleneck (network + processing)
2. **PDF Extraction**: Fast, not a concern
3. **Session Storage**: In-memory, very fast

## Security Considerations

### Current State
- ✅ API key in .env (not in code)
- ✅ File type validation (.pdf only)
- ✅ Temporary file cleanup
- ⚠️ No rate limiting
- ⚠️ No authentication
- ⚠️ No input sanitization

### For Production
- [ ] Add rate limiting
- [ ] Implement authentication
- [ ] Sanitize user inputs
- [ ] Add CORS configuration
- [ ] Use HTTPS
- [ ] Add file size limits

## Deployment

### Local Development
```bash
python app.py
```

### Production (Simple)
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Production (Better)
- Use Gunicorn with Uvicorn workers
- Add Nginx reverse proxy
- Use systemd for process management
- Add monitoring (Prometheus/Grafana)

## Monitoring

### What to Monitor
- API response times
- Error rates
- Session count
- Memory usage
- Gemini API quota

### Simple Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Cost Analysis

### Free Tier (Gemini)
- 60 requests per minute
- 1,500 requests per day
- Sufficient for personal use

### Estimated Costs (Paid)
- $0.00025 per 1k characters input
- $0.001 per 1k characters output
- ~$0.01 per document (typical)

## Conclusion

This architecture prioritizes:
1. **Simplicity** over complexity
2. **Reliability** over features
3. **Speed of development** over optimization
4. **Ease of understanding** over cleverness

Perfect for:
- Personal projects
- Prototypes
- Small teams
- Learning AI integration

Not ideal for:
- Large-scale production
- Multi-tenant SaaS
- High-volume processing
- Complex document analysis

**Remember**: Start simple, add complexity only when needed!
