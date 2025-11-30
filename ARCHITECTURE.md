# System Architecture

## Clean & Simple Design

This is a complete rewrite with a focus on simplicity and reliability.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PyPDF2** - PDF text extraction
- **Google Gemini AI** - Question answering and summarization
- **Python-dotenv** - Environment variable management

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks, just clean code
- **Modern CSS** - Gradients, animations, responsive design
- **Inter Font** - Clean, professional typography

## Architecture Decisions

### Why No Vector Databases?
- **Simplicity**: No complex setup or dependencies
- **Reliability**: Fewer moving parts = fewer failures
- **Cost**: No additional infrastructure needed
- **Speed**: Direct AI processing is fast enough for most use cases

### Why Contextual Memory Instead of RAG?
- **Easier to understand**: Simple chat history approach
- **Good enough**: Works well for most documents
- **No embeddings needed**: Avoids quota issues
- **Conversational**: Natural follow-up questions

### How It Works

```
1. PDF Upload
   ↓
2. Extract text with page numbers
   ↓
3. Generate summary (first 15k chars)
   ↓
4. Store in session memory
   ↓
5. User asks question
   ↓
6. Send to Gemini:
   - Document content (first 10k chars)
   - Last 3 Q&A pairs
   - Current question
   ↓
7. Get contextual answer
   ↓
8. Store in chat history
   ↓
9. Repeat from step 5
```

## File Structure

```
qa-summarizer/
├── app.py                 # FastAPI web application
├── pdf_qa_system.py       # CLI version
├── requirements.txt       # Python dependencies
├── .env                   # API keys (gitignored)
├── README.md             # User documentation
├── ARCHITECTURE.md       # This file
├── static/
│   ├── index.html        # Main HTML page
│   ├── style.css         # All styling
│   └── script.js         # Frontend logic
└── venv/                 # Virtual environment
```

## Session Management

```python
sessions = {
    "session_id": {
        "pdf_text": "Full PDF content with page markers",
        "chat_history": [
            {"question": "...", "answer": "..."},
            {"question": "...", "answer": "..."}
        ]
    }
}
```

## API Endpoints

### GET /
Returns the main HTML page

### POST /upload
- **Input**: PDF file + session_id
- **Process**: Extract text, generate summary
- **Output**: Summary + character count
- **Storage**: Saves to session

### POST /ask
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
