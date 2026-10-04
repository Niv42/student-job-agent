import sys
import re
import time

# Ensure stdout handles utf-8 safely on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ddgs import DDGS
from config import DISCIPLINES, REGIONS, TOP_EMPLOYERS

def clean_text(text: str) -> str:
    """Removes weird markdown, extra spaces, and html artifacts."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_company_from_title(title: str, url: str) -> str:
    """Heuristic extractor for company name from search result title/URL."""
    # Check known employers
    for emp in TOP_EMPLOYERS:
        if emp["name"].lower() in title.lower() or emp["name"].split()[0].lower() in title.lower():
            return emp["name"]
        if emp["name"].lower().replace(" ", "") in url.lower():
            return emp["name"]
            
    # Check common patterns: "Company hiring Title" or "Title at Company"
    match_hiring = re.search(r'^(.*?)\s+hiring\s+', title, re.IGNORECASE)
    if match_hiring:
        return match_hiring.group(1).strip()
        
    match_at = re.search(r'at\s+(.*?)(?:\s+in\s+Israel|\s+[-|]|\s*$)', title, re.IGNORECASE)
    if match_at:
        return match_at.group(1).strip()
        
    # Check "|" or "-" separator
    if "|" in title:
        parts = [p.strip() for p in title.split("|")]
        if len(parts) >= 2 and len(parts[-1]) < 30:
            return parts[-1]
    if "-" in title:
        parts = [p.strip() for p in title.split("-")]
        if len(parts) >= 2 and len(parts[-1]) < 30:
            return parts[-1]
            
    return "Tech Company (Israel)"

def extract_location_from_text(text: str) -> str:
    """Detects Israeli city or region from text."""
    text_lower = text.lower()
    for region_name, data in REGIONS.items():
        for city in data["cities"]:
            if city.lower() in text_lower:
                return city.title()
    return "Israel"

def search_web_for_ee_jobs(
    discipline: Optional[str] = None,
    region: Optional[str] = None,
    custom_keywords: Optional[str] = None,
    max_results: int = 15
) -> List[Dict[str, Any]]:
    """
    Executes targeted DDGS searches for Israeli Electrical Engineering student positions.
    """
    queries = []
    
    # 1. Targeted discipline search
    if discipline and discipline in DISCIPLINES:
        disc_info = DISCIPLINES[discipline]
        main_kw = disc_info["keywords"][0]
        queries.append(f'"{main_kw}" student Israel (site:linkedin.com/jobs OR site:drushim.co.il OR site:greenhouse.io OR site:myworkdayjobs.com)')
        queries.append(f'"{disc_info["he"]}" משרת סטודנט')
    elif custom_keywords:
        queries.append(f'"{custom_keywords}" student Israel job (site:linkedin.com OR site:drushim.co.il OR site:alljobs.co.il)')
    else:
        # Broad high-yield queries
        queries = [
            '"VLSI" student Israel (site:linkedin.com/jobs OR site:myworkdayjobs.com)',
            '"Hardware" student Israel (site:linkedin.com/jobs OR site:greenhouse.io)',
            '"Verification" student Israel (site:linkedin.com/jobs OR site:myworkdayjobs.com)',
            '"Embedded" student Israel (site:linkedin.com/jobs OR site:drushim.co.il)',
            '"סטודנט להנדסת חשמל" משרה',
            '"RF" student Israel job',
            '"Electro-Optics" student Israel'
        ]
        
    raw_results = []
    seen_urls = set()
    
    ddgs = DDGS()
    
    for q in queries:
        try:
            results = list(ddgs.text(q, max_results=max_results))
            for item in results:
                href = item.get("href", "")
                if href and href not in seen_urls:
                    seen_urls.add(href)
                    raw_results.append(item)
            time.sleep(0.5) # respectful delay
        except Exception as e:
            print(f"Search warning for query '{q}': {e}")
            
    processed_jobs = []
    for item in raw_results:
        title = clean_text(item.get("title", ""))
        snippet = clean_text(item.get("body", ""))
        url = item.get("href", "")
        
        # Filter out obvious non-job or foreign domain hits
        lower_url = url.lower()
        if any(bad in lower_url for bad in [".pl/", ".de/", ".ru/", "wikipedia.org", "youtube.com", "facebook.com"]):
            continue
            
        company = extract_company_from_title(title, url)
        location = extract_location_from_text(f"{title} {snippet}")
        
        # Identify region
        matched_region = "Tel Aviv & Central"
        for r_name, r_data in REGIONS.items():
            if any(c.lower() in f"{location} {title} {snippet}".lower() for c in r_data["cities"]):
                matched_region = r_name
                break
                
        # Identify discipline
        matched_disc = "General EE / Tech Student"
        for d_name, d_data in DISCIPLINES.items():
            if any(kw.lower() in f"{title} {snippet}".lower() for kw in d_data["keywords"]):
                matched_disc = d_name
                break
                
        processed_jobs.append({
            "title": title.replace(" - LinkedIn", "").replace(" | LinkedIn", "").replace(" - Drushim", "").strip(),
            "company": company,
            "location": location,
            "region": matched_region,
            "discipline": matched_disc,
            "description": snippet,
            "url": url,
            "source": "Web Search (DDGS)",
            "date_posted": datetime.now().strftime("%Y-%m-%d")
        })
        
    return processed_jobs

if __name__ == "__main__":
    print("Testing search engine...")
    res = search_web_for_ee_jobs(discipline="VLSI & Chip Design", max_results=3)
    print(f"Found {len(res)} jobs:")
    for j in res[:3]:
        print(f"[*] [{j['company']}] {j['title']} -> {j['url']}")
