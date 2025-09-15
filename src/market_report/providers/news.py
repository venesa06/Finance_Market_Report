# src/market_report/providers/news.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_news(q="finance", page_size=6, language="en"):
    """
    Fetch top news articles from NewsAPI.
    Returns a dict with { "articles": [ ... ] }
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "pageSize": page_size,
        "language": language,
        "sortBy": "publishedAt",
        "apiKey": API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "articles": []}
