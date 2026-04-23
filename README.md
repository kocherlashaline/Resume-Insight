
# 🎯 ResumeIQ — AI Career Coach

An AI-powered resume analyzer and career coach built with Google Gemini, ChromaDB, Adzuna Jobs API, and Streamlit.

## Features

- **💥 Roast My Resume** — Score your resume vs any JD, get brutally honest gap analysis + AI-rewritten bullets
- **🔍 Find Matching Jobs** — Search live jobs via Adzuna, rank them against your resume with AI
- **🔗 Analyze JD URL** — Drop any job posting URL, get instant ATS keyword + skill gap analysis
- **🗂️ Chat with Multiple JDs** — Upload up to 20 JDs, embed them into ChromaDB via Google's text-embedding-004 model, then ask questions across all of them using semantic vector search + Gemini (genuine RAG pipeline)

## Tech Stack

- **LLM**: Google Gemini 2.0 Flash (free API via aistudio.google.com)
- **Embeddings**: Google text-embedding-004 (768-dim vectors, free tier)
- **Vector DB**: ChromaDB (in-memory, cosine similarity)
- **Job Search**: Adzuna API (free tier)
- **PDF Parsing**: pdfplumber
- **Web Scraping**: BeautifulSoup4
- **UI**: Streamlit

## How the RAG Pipeline Works

```
User question
     │
     ▼
text-embedding-004  ──►  768-dim query vector
                                │
                                ▼
                    ChromaDB cosine similarity search
                    across all embedded JDs
                                │
                                ▼
                    Top-5 most relevant JDs retrieved
                                │
                                ▼
                    Gemini 2.0 Flash generates answer
                    grounded in retrieved JD context
```

Each JD is embedded once at upload time and stored in an in-memory ChromaDB collection. Every question triggers a real vector retrieval — the app shows which JDs were retrieved and their cosine similarity scores, so the retrieval is fully transparent.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/kocherlashaline/Resume-Insight.git
cd Resume-Insight
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
Resume-Insight/
├── app.py                    # Main Streamlit app (4 tabs)
├── requirements.txt
├── utils/
│   ├── pdf_parser.py         # PDF text extraction
│   ├── jd_scraper.py         # URL scraping
│   ├── job_search.py         # Adzuna API
│   ├── gemini_client.py      # Gemini LLM + embedding calls
│   └── jd_vector_store.py    # ChromaDB vector store helpers
└── README.md
```

## Skills Demonstrated

- **RAG pipeline** — real vector retrieval with ChromaDB + Google embeddings, not just prompt stuffing
- **Vector embeddings** — text-embedding-004, cosine similarity search, transparent retrieval scores
- **LLM structured output** — JSON extraction with prompt engineering and regex cleanup
- **Multi-model resilience** — automatic fallback across Gemini models on rate limits
- **API integration** — Gemini, Adzuna Jobs API, web scraping with BeautifulSoup4
- **Full-stack AI app** — Streamlit UI, session state, multi-tab layout, progress tracking
