import sys
import os
import argparse
import subprocess
from dotenv import load_dotenv

# Ensure stdout and stderr handle utf-8 safely on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

import db_manager
import agent_engine
from config import DISCIPLINES, REGIONS

def run_app():
    """Launches the Streamlit Web Application."""
    print("Launching Israel Electrical Engineering Student Job Agent Web App...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.run(cmd)

def run_cli_scout(discipline=None, region=None, keywords=None, max_results=5):
    """Runs the AI agent to scout jobs and persist them into the local database."""
    print("==================================================================")
    print(">> ISRAEL ELECTRICAL ENGINEERING STUDENT JOB AGENT <<")
    print("==================================================================")
    print(f"* Target Discipline: {discipline or 'All EE Disciplines'}")
    print(f"* Target Region:     {region or 'All Regions (Israel)'}")
    print(f"* Custom Keywords:   {keywords or 'None'}")
    print("------------------------------------------------------------------")
    print("[*] Agent is querying Israeli tech boards and analyzing with AI...")
    
    db_manager.init_db()
    jobs = agent_engine.scout_and_save_jobs(
        discipline=discipline,
        region=region,
        keywords=keywords,
        max_results=max_results
    )
    
    print(f"\n[+] Scout Complete! Found and evaluated {len(jobs)} positions:\n")
    for i, job in enumerate(jobs, 1):
        print(f"[{i}] {job.get('company')} | {job.get('title')}")
        print(f"    * Domain:    {job.get('discipline')} (Region: {job.get('region')})")
        print(f"    * Match:     {job.get('relevance_score')}%")
        print(f"    * Reqs:      {job.get('study_year')} | {job.get('days_per_week')}")
        skills_str = ', '.join(job.get('skills', [])) if isinstance(job.get('skills'), list) else str(job.get('skills'))
        print(f"    * Skills:    {skills_str}")
        print(f"    * URL:       {job.get('url')}")
        print(f"    * Rationale: {job.get('relevance_reasons')}")
        print("-" * 66)

def main():
    parser = argparse.ArgumentParser(description="Israel EE Student Job Agent")
    parser.add_argument("--ui", action="store_true", help="Launch interactive Streamlit Web UI")
    parser.add_argument("--scout", action="store_true", help="Run AI scout agent in terminal")
    parser.add_argument("--discipline", type=str, choices=list(DISCIPLINES.keys()), help="Target EE sub-discipline")
    parser.add_argument("--region", type=str, choices=list(REGIONS.keys()), help="Target Israeli region")
    parser.add_argument("--keywords", type=str, help="Additional keywords to search")
    parser.add_argument("--count", type=int, default=5, help="Number of results to scout")
    
    args = parser.parse_args()
    
    if args.scout:
        run_cli_scout(
            discipline=args.discipline,
            region=args.region,
            keywords=args.keywords,
            max_results=args.count
        )
    else:
        # Default action: run the web UI
        run_app()

if __name__ == "__main__":
    main()