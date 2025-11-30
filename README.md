# PDF Q&A System with Gemini AI

A clean, simple PDF question-answering system powered by Google's Gemini AI with contextual memory.

## Features

✨ **Simple & Reliable** - No complex dependencies, just works
🤖 **Gemini AI Powered** - Uses Google's latest Gemini 2.0 Flash model
💬 **Contextual Memory** - Remembers previous questions for better answers
🎨 **Beautiful UI** - Modern gradient design with smooth animations
📄 **Page References** - AI mentions which pages information comes from

## Tech Stack

- **Backend**: FastAPI + Python
- **AI**: Google Gemini 2.0 Flash
- **PDF Processing**: PyPDF2
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **No Vector Databases** - Direct AI processing for simplicity

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

Features:
- Upload PDF files directly
- Get AI-powered summaries
- Ask questions with contextual memory
- Beautiful, responsive interface

### CLI Version

Run the command-line version:
```bash
python pdf_qa_system.py
```

The CLI will:
1. Ask for a PDF file path
2. Extract all text from the PDF
3. Generate an AI summary
4. Enter Q&A mode with chat history

Type 'exit' or 'quit' to end the session.

## How It Works

1. **PDF Upload**: Extract text from PDF with page numbers
2. **Summary Generation**: Gemini AI creates a comprehensive summary
3. **Question Answering**: 
   - Sends document content + last 3 Q&A pairs to AI
   - AI generates contextual answers
   - Mentions page numbers when referencing content
   - Maintains conversation history

## Architecture

- **Simple & Direct**: No embeddings, no vector stores
- **Contextual**: Maintains chat history for follow-up questions
- **Efficient**: Only sends relevant context (first 10k chars + recent Q&A)
- **Scalable**: Session-based storage for multiple users

## Benefits

- ✅ No complex setup or dependencies
- ✅ Works immediately out of the box
- ✅ Free tier friendly (Gemini API)
- ✅ Contextual conversations
- ✅ Page number references
- ✅ Beautiful, modern UI

## Limitations

- Processes first ~10k characters of document for Q&A
- Keeps last 3 Q&A pairs in context
- Requires internet connection for Gemini API
- Free tier has rate limits

## Future Enhancements

- Add full document chunking for large PDFs
- Implement vector search for better retrieval
- Add multi-document support
- Export conversation history
- Add authentication

## License

MIT License - Feel free to use and modify!
