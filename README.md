# Resume Analyzer Pro

🚀 **AI-powered resume analysis and job matching system** - Upload your resume, get instant insights, check ATS compatibility, and discover perfect job matches.

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 3. Run the application
python main.py
```

**Open your browser to:** `http://localhost:8000`

## 🎯 What This Does

### **Upload & Analyze**
- Upload PDF resume → Get instant AI analysis
- Extract skills, experience, education automatically
- Interactive chat about your resume

### **Find Perfect Jobs**
- AI-powered job recommendations
- Match jobs to your exact skills and experience
- Get salary estimates and growth potential

### **ATS Compatibility Check**
- Test your resume against real job descriptions
- Get compatibility scores (0-100%)
- Receive specific improvement recommendations
- Support for major ATS systems (Workday, Taleo, iCIMS, etc.)

## 🛠 Features

✅ **Smart Resume Parsing** - AI extracts all relevant information  
✅ **Job Matching** - Find jobs that fit your profile perfectly  
✅ **ATS Checker** - Test compatibility with applicant tracking systems  
✅ **LinkedIn Integration** - Enhance your profile with LinkedIn data  
✅ **AI Chat** - Ask questions about your resume and career  
✅ **Mobile Friendly** - Works perfectly on all devices  

## 📱 How to Use

### **Simple 2-Step Process:**

1. **Analyzer** → Upload your PDF resume and get comprehensive AI analysis
2. **Find Jobs** → Analyze job descriptions and get market insights independently

### **Two Powerful Tools:**
- **Resume Analyzer**: Upload resume → Get AI insights, skills analysis, and improvement recommendations
- **Job Market Intelligence**: Analyze job postings → Get requirements breakdown and market data

## 🔧 Technical Stack

- **Backend**: FastAPI, Python 3.8+
- **AI**: Groq API (Llama models)
- **PDF Processing**: PyPDF2
- **Web Scraping**: Selenium (LinkedIn)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: In-memory sessions

## 📋 Requirements

- Python 3.8 or higher
- Groq API key (free at [groq.com](https://groq.com))
- Modern web browser

## 🚀 Installation

### **Option 1: Quick Setup**
```bash
git clone <your-repo>
cd resume-analyzer
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python main.py
```

### **Option 2: Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
python main.py
```

## 🔑 Getting Your API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create new API key
4. Add to `.env` file: `GROQ_API_KEY=your_key_here`

## 📁 Project Structure

```
resume-analyzer/
├── app/                    # Application core
│   ├── handlers.py        # API route handlers
│   ├── models.py          # Data models
│   ├── services.py        # Business logic
│   └── config.py          # Configuration
├── src/                   # Business modules
│   ├── utils/             # Utilities (ATS checker, etc.)
│   ├── recommenders/      # Job recommendation engine
│   └── scrapers/          # LinkedIn scraper
├── static/                # Frontend files
│   ├── index.html         # Home page
│   ├── analysis.html      # Resume analysis page
│   ├── jobs.html          # Jobs & ATS page
│   └── *.js, *.css        # Scripts and styles
└── main.py               # Application entry point
```

## 🎯 API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /upload` | Upload and analyze resume |
| `POST /check-ats` | Check ATS compatibility |
| `POST /recommend-jobs` | Get job recommendations |
| `POST /chat` | Chat with AI about resume |

## 🔧 Troubleshooting

**Common Issues:**

- **"GROQ_API_KEY not found"** → Add your API key to `.env` file
- **"Port 8000 already in use"** → Change port in `main.py` or kill existing process
- **"PDF parsing failed"** → Ensure PDF is text-based (not scanned image)

## 📞 Support

- Check [docs/](docs/) folder for detailed guides
- Review code comments for technical details
- Test with sample resumes first

## 🎉 Success Tips

1. **Use text-based PDFs** (not scanned images)
2. **Include complete job descriptions** for ATS checking
3. **Try different ATS systems** to see variations
4. **Ask specific questions** in the AI chat
5. **Update your resume** based on recommendations

---

**Ready to optimize your job search? Upload your resume and discover your potential!** 🚀