import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_jd_from_url(url: str) -> str:
    """Scrape job description text from a URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try common JD containers first
        for selector in [
            "div[class*='job-description']",
            "div[class*='jobDescription']",
            "div[class*='description']",
            "div[id*='job-description']",
            "section[class*='description']",
            "article",
        ]:
            container = soup.select_one(selector)
            if container:
                text = container.get_text(separator="\n", strip=True)
                if len(text) > 200:
                    return text[:8000]

        # Fallback: grab all body text
        body = soup.find("body")
        if body:
            text = body.get_text(separator="\n", strip=True)
            return text[:8000]

        return ""

    except Exception as e:
        return f"ERROR: Could not scrape URL — {str(e)}"
