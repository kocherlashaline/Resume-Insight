# 🎯 ResumeIQ — AI Career Coach

A brutally honest AI-powered resume analyzer built with Gemini 1.5 Pro, Adzuna Jobs API, and Streamlit.

## Features

- **💥 Roast My Resume** — Score your resume vs any JD, get gap analysis + rewritten bullets
- **🔍 Find Matching Jobs** — Search live jobs via Adzuna, rank them against your resume with AI
- **🔗 Analyze JD URL** — Drop any job posting URL, get instant gap analysis

## Tech Stack

- **LLM**: Google Gemini 1.5 Pro (free API via aistudio.google.com)
- **Job Search**: Adzuna API (free tier — 250 calls/month)
- **PDF Parsing**: pdfplumber
- **Web Scraping**: BeautifulSoup4
- **UI**: Streamlit (free hosting on Streamlit Cloud)

## Setup

### 1. Clone and install

```bash
git clone https://github.com/yourusername/resume-roaster
cd resume-roaster
pip install -r requirements.txt
```

### 2. Get API Keys (both free)

- **Gemini**: https://aistudio.google.com → Get API Key
- **Adzuna**: https://developer.adzuna.com → Register → Get App ID + Key

### 3. Run locally

```bash
streamlit run app.py
```

### 4. Deploy to Streamlit Cloud (free)

1. Push to GitHub
2. Go to share.streamlit.io
3. Connect your repo → Deploy
4. Add API keys in Streamlit Secrets settings

## Project Structure

```
resume-roaster/
├── app.py                    # Main Streamlit app
├── requirements.txt
├── utils/
│   ├── pdf_parser.py         # PDF text extraction
│   ├── jd_scraper.py         # URL scraping
│   ├── job_search.py         # Adzuna API
│   └── gemini_client.py      # All Gemini LLM calls
└── README.md
```

## Skills Demonstrated

- RAG-aligned document comparison (resume vs JD)
- LLM structured output with Pydantic-style JSON validation
- API integration (Gemini, Adzuna, web scraping)
- Full-stack AI application deployment
- Streamlit UI with persistent session state
