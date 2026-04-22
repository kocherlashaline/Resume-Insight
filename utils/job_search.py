import requests
from typing import List, Dict

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"

def search_jobs(
    title: str,
    app_id: str,
    app_key: str,
    country: str = "us",
    results: int = 10,
) -> List[Dict]:
    """Search for jobs on Adzuna and return list of job dicts."""
    url = f"{ADZUNA_BASE}/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results,
        "what": title,
        "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        for job in data.get("results", []):
            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company", {}).get("display_name", "Unknown"),
                "location": job.get("location", {}).get("display_name", ""),
                "description": job.get("description", "")[:3000],
                "url": job.get("redirect_url", ""),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
            })
        return jobs
    except Exception as e:
        return [{"error": str(e)}]
