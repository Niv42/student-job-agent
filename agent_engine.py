import sys
import os
import json
import re

# Ensure stdout handles utf-8 safely on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import DISCIPLINES, REGIONS
import db_manager
import scraper

# Try importing LLM libraries if available
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

def call_llm(prompt: str) -> Optional[str]:
    """Attempts to call available LLM API with fallback."""
    # 1. Try Groq (using working model)
    if GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert tech recruiter and Electrical Engineering career analyst in Israel. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq primary model warning: {e}")
            try:
                # Fallback to secondary groq model
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an expert tech recruiter and Electrical Engineering career analyst in Israel. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    model="openai/gpt-oss-20b",
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return chat_completion.choices[0].message.content
            except Exception as e2:
                print(f"Groq fallback model warning: {e2}")

    # 2. Try Gemini
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            for m in ["gemini-3.6-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
        except Exception as e:
            print(f"Gemini API call warning: {e}")

    return None

def heuristic_enrichment(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """Rule-based fallback when LLM is unavailable or for rapid processing."""
    text = f"{raw_job.get('title', '')} {raw_job.get('description', '')}".lower()
    
    # Match skills
    found_skills = []
    known_skills = [
        "SystemVerilog", "Verilog", "VHDL", "RTL", "UVM", "Altium", "PCB", 
        "C++", "C", "Python", "Linux", "RTOS", "ARM", "Microcontroller", 
        "MATLAB", "LabVIEW", "Oscilloscope", "ADS", "CST", "HFSS", "FPGA", 
        "Cadence", "Synopsys", "Optics", "Spectre", "SPICE"
    ]
    for skill in known_skills:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text):
            found_skills.append(skill)
            
    if not found_skills:
        found_skills = ["Hardware", "Electrical Engineering", "Lab"]
        
    # Match study year
    study_year = "2nd or 3rd year B.Sc."
    if "m.sc" in text or "master" in text:
        study_year = "M.Sc. / Advanced B.Sc."
    elif "4th year" in text or "last year" in text or "graduating" in text:
        study_year = "3rd / 4th Year (Graduating)"
    elif "1st year" in text:
        study_year = "1st or 2nd Year"

    # Match commitment
    days = "2-3 days / 20 hours per week"
    if "part time" in text or "20 hours" in text or "20 שעות" in text:
        days = "20 hours / week (Part-time)"
        
    # Calculate score
    score = 80
    if any(k in text for k in ["student", "intern", "internship", "סטודנט"]):
        score += 10
    if any(k in text for k in ["vlsi", "uvm", "rtl", "board", "embedded", "rf", "optics"]):
        score += 8
    score = min(score, 99)
    
    return {
        **raw_job,
        "skills": found_skills,
        "study_year": study_year,
        "days_per_week": days,
        "relevance_score": score,
        "relevance_reasons": f"Relevant for EE students specializing in {raw_job.get('discipline', 'Electrical Engineering')}."
    }

def analyze_job_with_agent(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """Uses LLM agent to parse, evaluate, and categorize an Israeli EE student job."""
    prompt = f"""
    Analyze this raw job listing for an Electrical Engineering student in Israel:
    Title: {raw_job.get('title')}
    Company: {raw_job.get('company')}
    Location: {raw_job.get('location')}
    Description: {raw_job.get('description')}
    URL: {raw_job.get('url')}
    
    Allowed Disciplines:
    {json.dumps(list(DISCIPLINES.keys()))}
    
    Allowed Regions:
    {json.dumps(list(REGIONS.keys()))}
    
    Return a JSON object with exactly these keys:
    {{
        "title": "Clean concise job title",
        "company": "Company Name",
        "location": "City or specific location in Israel",
        "region": "One of the Allowed Regions",
        "discipline": "One of the Allowed Disciplines",
        "description": "2-3 sentence clear summary of the role",
        "skills": ["List", "of", "3-6", "Key", "Technical", "Skills"],
        "study_year": "e.g. 2nd/3rd Year B.Sc. EE / 1.5+ years remaining",
        "days_per_week": "e.g. 2-3 days / 20 hours per week",
        "relevance_score": 85,
        "relevance_reasons": "1-2 sentences explaining why this fits an EE student"
    }}
    """
    
    llm_output = call_llm(prompt)
    if llm_output:
        try:
            # Extract JSON block if wrapped in markdown
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return {
                    **raw_job,
                    **parsed,
                    "url": raw_job.get("url"),
                    "source": raw_job.get("source", "Agent Scout"),
                    "date_posted": raw_job.get("date_posted", datetime.now().strftime("%Y-%m-%d"))
                }
        except Exception as e:
            print(f"Error parsing LLM JSON: {e}")
            
    # Fallback to heuristic analysis
    return heuristic_enrichment(raw_job)

def scout_and_save_jobs(
    discipline: Optional[str] = None,
    region: Optional[str] = None,
    keywords: Optional[str] = None,
    max_results: int = 6
) -> List[Dict[str, Any]]:
    """Runs the full agent pipeline: Scrapes web -> Analyzes with LLM -> Saves to SQLite DB."""
    raw_jobs = scraper.search_web_for_ee_jobs(
        discipline=discipline,
        region=region,
        custom_keywords=keywords,
        max_results=max_results
    )
    
    analyzed_jobs = []
    for raw in raw_jobs:
        analyzed = analyze_job_with_agent(raw)
        db_manager.save_job(analyzed)
        analyzed_jobs.append(analyzed)
        
    return analyzed_jobs

if __name__ == "__main__":
    db_manager.init_db()
    print("Testing agent analysis with Groq openai/gpt-oss-120b...")
    test_raw = {
        "title": "VLSI Design Student - Haifa",
        "company": "Qualcomm Israel",
        "location": "Haifa",
        "description": "Looking for 3rd year EE student to work on RTL SystemVerilog coding and synthesis.",
        "url": "https://qualcomm.wd5.myworkdayjobs.com/test",
        "source": "Test"
    }
    result = analyze_job_with_agent(test_raw)
    print(json.dumps(result, indent=2))
