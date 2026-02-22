"""
Free web enrichment tools - no paid APIs needed.
"""

import requests
from bs4 import BeautifulSoup
import json
import time


def search_web(query: str, num_results: int = 5) -> list:
    """
    Simple web search using DuckDuckGo (no API key needed).
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        url = f"https://html.duckduckgo.com/html/?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        for result in soup.find_all("a", class_="result__a")[:num_results]:
            results.append({
                "title": result.get_text(),
                "url": result.get("href", "")
            })
        
        return results
    except Exception as e:
        return [{"error": str(e)}]


def get_google_trends(keyword: str) -> dict:
    """
    Check Google Trends interest for a keyword.
    """
    try:
        import pandas as pd
        pd.set_option('future.no_silent_downcasting', True)

        from pytrends.request import TrendReq

        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword], timeframe='today 12-m')

        interest = pytrends.interest_over_time()

        if not interest.empty:
            recent_avg = interest[keyword].tail(4).mean()
            older_avg = interest[keyword].head(4).mean()

            trend = "Growing" if recent_avg > older_avg * 1.1 else \
                    "Declining" if recent_avg < older_avg * 0.9 else "Stable"

            return {
                "keyword": keyword,
                "trend_direction": trend,
                "current_interest": int(recent_avg),
                "historical_interest": int(older_avg),
            }

        return {"keyword": keyword, "trend_direction": "No data"}

    except Exception as e:
        return {"keyword": keyword, "error": str(e)}

def enrich_company(company_name: str, sector: str = "") -> dict:
    """
    Aggregate free enrichment data about a company.
    """
    enrichment = {
        "company": company_name,
        "web_results": [],
        "news": [],
        "trend_data": {},
    }
    
    # 1. Web search for company info
    enrichment["web_results"] = search_web(f"{company_name} startup funding")
    time.sleep(1)  # Be polite with requests
    
    # 2. Search for recent news
    enrichment["news"] = search_web(f"{company_name} startup news 2024")
    time.sleep(1)
    
    # 3. Google Trends for sector
    if sector:
        enrichment["trend_data"] = get_google_trends(sector)
    
    return enrichment


def format_enrichment_for_llm(enrichment: dict) -> str:
    """
    Format enrichment data into readable text for LLM consumption.
    """
    output = f"\n## Web Enrichment Data for: {enrichment['company']}\n"
    
    output += "\n### Web Search Results:\n"
    for r in enrichment.get("web_results", []):
        if "error" not in r:
            output += f"- {r.get('title', 'N/A')}: {r.get('url', 'N/A')}\n"
    
    output += "\n### Recent News:\n"
    for r in enrichment.get("news", []):
        if "error" not in r:
            output += f"- {r.get('title', 'N/A')}\n"
    
    trend = enrichment.get("trend_data", {})
    if trend and "error" not in trend:
        output += f"\n### Google Trends:\n"
        output += f"- Keyword: {trend.get('keyword', 'N/A')}\n"
        output += f"- Trend: {trend.get('trend_direction', 'N/A')}\n"
        output += f"- Current Interest: {trend.get('current_interest', 'N/A')}\n"
    
    return output