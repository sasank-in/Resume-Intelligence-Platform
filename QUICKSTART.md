# 🚀 Quick Start Guide

Get your Resume Analyzer Pro running in 3 minutes!

## Step 1: Setup (2 minutes)

```bash
# Clone and enter directory
git clone <your-repo>
cd resume-analyzer

# Install requirements
pip install -r requirements.txt

# Get your free API key from https://console.groq.com
# Add it to .env file:
echo "GROQ_API_KEY=your_actual_key_here" > .env
```

## Step 2: Run (30 seconds)

```bash
python main.py
```

**Open:** `http://localhost:8000`

## Step 3: Use (30 seconds)

### **Option A: Analyze Your Resume**
1. Click **"Analyzer"** in navigation
2. **Upload your PDF resume**
3. **View AI analysis** and insights

### **Option B: Research Jobs**
1. Click **"Find Jobs"** in navigation  
2. **Paste job description** or **enter job role**
3. **Get market insights** and requirements

## 🎯 Two Powerful Tools

### **Analyzer Tool:**
- Upload resume → Get AI insights
- Chat with AI about your career
- LinkedIn integration available

### **Find Jobs Tool:**
- Analyze job descriptions (no resume needed)
- Get salary and market data
- Research career paths

## 🔧 Troubleshooting

**Not working?**

1. **API Key Issue**: Make sure your `.env` file has: `GROQ_API_KEY=your_key`
2. **Port Busy**: Change port in `main.py` from 8000 to 8001
3. **PDF Issues**: Use text-based PDFs (not scanned images)

## 🎉 Success!

If you see the analyzer page at `http://localhost:8000`, you're ready to go!

**Try both tools:**
- **Analyzer**: Upload a sample resume to test analysis features
- **Find Jobs**: Paste a job description to test market intelligence