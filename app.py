import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import PyPDF2
import google.generativeai as genai

load_dotenv()

# Configure Gemini AI
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')  # More stable, better quota

app = FastAPI(title="PDF Q&A System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store PDF content and chat history per session
sessions = {}

class Question(BaseModel):
    question: str
    session_id: str

def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num} ---\n{page_text}"
        return text

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default"):
    """Upload and process PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_path = None
    try:
        # Save uploaded file temporarily
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            temp_path = tmp.name
        
        # Extract text from PDF
        pdf_text = extract_pdf_text(temp_path)
        
        # Generate summary using Gemini
        summary_prompt = f"""Please provide a comprehensive summary of the following document:

{pdf_text[:15000]}  

Summary:"""
        
        response = model.generate_content(summary_prompt)
        summary = response.text
        
        # Store session data
        sessions[session_id] = {
            "pdf_text": pdf_text,
            "chat_history": []
        }
        
        return {
            "message": "PDF processed successfully",
            "summary": summary,
            "characters": len(pdf_text)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/ask")
async def ask_question(question_data: Question):
    """Ask a question about the uploaded PDF using chat context"""
    session_id = question_data.session_id
    question = question_data.question
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="No PDF uploaded for this session")
    
    try:
        session = sessions[session_id]
        pdf_text = session["pdf_text"]
        chat_history = session["chat_history"]
        
        # Build context with chat history
        context = f"Document Content:\n{pdf_text[:10000]}\n\n"
        
        if chat_history:
            context += "Previous Conversation:\n"
            for qa in chat_history[-3:]:  # Last 3 Q&A pairs
                context += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
        
        # Create prompt with context
        prompt = f"""{context}

Current Question: {question}

Please answer the question based on the document content above. If you reference specific information, mention which page it's from.

Answer:"""
        
        response = model.generate_content(prompt)
        answer = response.text
        
        # Store in chat history
        chat_history.append({
            "question": question,
            "answer": answer
        })
        
        return {
            "answer": answer
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting PDF Q&A System...")
    print("📍 Open your browser to: http://localhost:8000")
    print("Press CTRL+C to stop the server\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
