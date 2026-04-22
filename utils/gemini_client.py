from google import genai
from google.genai import errors as genai_errors
from typing import List, Dict
import json
import re

_client: genai.Client | None = None
MODEL = "gemini-2.0-flash"

def init_gemini(api_key: str):
    global _client
    _client = genai.Client(api_key=api_key)

def _get_client() -> genai.Client:
    if _client is None:
        raise RuntimeError("Gemini not initialised. Call init_gemini(api_key) first.")
    return _client

def _generate(prompt: str) -> str:
    client = _get_client()
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except genai_errors.ClientError as e:
        if e.code == 429:
            raise QuotaExceededError(str(e)) from e
        raise


class QuotaExceededError(Exception):
    pass


def _quota_error_dict() -> Dict:
    return {
        "error": "quota_exceeded",
        "raw": (
            "Your Gemini API free-tier quota is exhausted for today. "
            "Options: (1) wait until tomorrow for the quota to reset, "
            "(2) enable billing at https://ai.google.dev to get higher limits, "
            "or (3) use a different API key."
        ),
    }

def roast_resume(resume_text: str, jd_text: str) -> Dict:
    prompt = f"""
You are a brutally honest but helpful career coach and hiring manager with 15 years of experience.

Analyze this resume against the job description below. Be specific, direct, and actionable.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return ONLY valid JSON with this exact structure:
{{
  "match_score": <integer 0-100>,
  "verdict": "<2 sentence honest overall verdict>",
  "strengths": [
    {{"point": "<strength>", "detail": "<why this matters for this JD>"}}
  ],
  "roast": [
    {{"gap": "<missing skill or gap>", "severity": "critical|moderate|minor", "detail": "<why this matters>"}}
  ],
  "missing_keywords": ["<keyword1>", "<keyword2>"],
  "rewrites": [
    {{"original": "<existing bullet or section>", "improved": "<rewritten version with keywords>", "why": "<what changed>"}}
  ],
  "top_3_actions": ["<most important thing to do first>", "<second>", "<third>"]
}}
"""
    try:
        return _parse_json_response(_generate(prompt))
    except QuotaExceededError:
        return _quota_error_dict()


def analyze_jd_gaps(resume_text: str, jd_text: str, job_title: str = "", company: str = "") -> Dict:
    prompt = f"""
You are an expert ATS system and career coach.

Compare this resume to the job description and identify exactly what's missing.

RESUME:
{resume_text}

JOB DESCRIPTION ({job_title} at {company}):
{jd_text}

Return ONLY valid JSON:
{{
  "match_score": <integer 0-100>,
  "ats_keywords_missing": ["<keyword missing from resume but in JD>"],
  "ats_keywords_present": ["<keyword in both resume and JD>"],
  "skill_gaps": [
    {{"skill": "<skill>", "importance": "must-have|nice-to-have", "how_to_close": "<quick tip>"}}
  ],
  "experience_gaps": ["<experience mentioned in JD not evidenced in resume>"],
  "quick_wins": ["<change you can make to resume in under 10 mins to improve score>"],
  "summary": "<3 sentence honest summary of fit>"
}}
"""
    try:
        return _parse_json_response(_generate(prompt))
    except QuotaExceededError:
        return _quota_error_dict()


def rank_jobs_against_resume(resume_text: str, jobs: List[Dict]) -> List[Dict]:
    jobs_summary = ""
    for i, job in enumerate(jobs):
        jobs_summary += f"\nJOB {i+1}: {job['title']} at {job['company']}\n{job['description'][:1000]}\n---"

    prompt = f"""
You are a job matching AI. Score each job's fit with this resume.

RESUME:
{resume_text}

JOBS:
{jobs_summary}

Return ONLY valid JSON — an array ordered best match first:
[
  {{
    "job_index": <1-based index>,
    "match_score": <integer 0-100>,
    "top_3_reasons": ["<reason1>", "<reason2>", "<reason3>"],
    "top_3_gaps": ["<gap1>", "<gap2>", "<gap3>"]
  }}
]
"""
    try:
        rankings = _parse_json_response(_generate(prompt))
    except QuotaExceededError:
        return jobs
    if isinstance(rankings, list):
        enriched = []
        for r in rankings:
            idx = r.get("job_index", 1) - 1
            if 0 <= idx < len(jobs):
                enriched.append({**jobs[idx], **r})
        return sorted(enriched, key=lambda x: x.get("match_score", 0), reverse=True)
    return jobs


def generate_market_insights(resume_text: str, jobs: List[Dict]) -> str:
    all_descriptions = "\n---\n".join([j.get("description", "")[:500] for j in jobs[:10]])
    prompt = f"""
Analyze these job postings and compare against the resume. Give market intelligence.

RESUME SUMMARY (first 500 chars):
{resume_text[:500]}

JOB POSTINGS (sample):
{all_descriptions}

Write 4-5 bullet points of market insights:
- What skills appear in most job postings but are missing or weak in the resume
- What the candidate has that is in high demand
- Salary range observations if visible
- Overall market positioning advice

Be specific and actionable. Plain text, bullet points with dashes.
"""
    try:
        return _generate(prompt)
    except QuotaExceededError:
        return "Gemini quota exhausted. Please wait until tomorrow or enable billing at https://ai.google.dev."


def _parse_json_response(text: str) -> Dict:
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned)
    except Exception:
        return {"error": "Could not parse response", "raw": text[:500]}
