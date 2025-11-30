import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

class PDFQASystem:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # More stable, better quota
        self.pdf_content = ""
        self.chat_history = []
    
    def extract_pdf(self, pdf_path):
        """Extract text from PDF file"""
        print(f"📄 Extracting text from {pdf_path}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num} ---\n{page_text}"
        
        self.pdf_content = text
        print(f"✓ Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text
    
    def generate_summary(self):
        """Generate summary using Gemini AI"""
        if not self.pdf_content:
            return "No PDF content loaded. Please extract a PDF first."
        
        print("Generating summary with Gemini AI...")
        prompt = f"""Please provide a comprehensive summary of the following document:

{self.pdf_content[:15000]}

Summary:"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def ask_question(self, question):
        """Ask questions about the PDF content with chat history"""
        if not self.pdf_content:
            return "No PDF content loaded. Please extract a PDF first."
        
        # Build context with chat history
        context = f"Document Content:\n{self.pdf_content[:10000]}\n\n"
        
        if self.chat_history:
            context += "Previous Conversation:\n"
            for qa in self.chat_history[-3:]:  # Last 3 Q&A pairs
                context += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
        
        prompt = f"""{context}

Current Question: {question}

Please answer the question based on the document content above. If you reference specific information, mention which page it's from.

Answer:"""
        
        response = self.model.generate_content(prompt)
        answer = response.text
        
        # Store in chat history
        self.chat_history.append({
            "question": question,
            "answer": answer
        })
        
        return answer

def main():
    system = PDFQASystem()
    
    # Get PDF file path
    pdf_path = input("Enter the path to your PDF file: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File '{pdf_path}' not found")
        return
    
    # Extract PDF content
    system.extract_pdf(pdf_path)
    
    # Generate summary
    print("\n" + "="*50)
    print("📋 SUMMARY")
    print("="*50)
    summary = system.generate_summary()
    print(summary)
    
    # Q&A loop
    print("\n" + "="*50)
    print("💬 Q&A MODE - Ask questions about the document")
    print("Type 'exit' or 'quit' to end")
    print("="*50 + "\n")
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['exit', 'quit', '']:
            print("👋 Goodbye!")
            break
        
        print("\n💡 Answer:")
        answer = system.ask_question(question)
        print(answer)

if __name__ == "__main__":
    main()
