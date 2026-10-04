import sys
import os
import unittest
import json
import sqlite3
from datetime import datetime, timedelta

# Ensure UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import config
import db_manager
import scraper
import agent_engine

class TestSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        db_manager.init_db()
        db_manager.seed_initial_data()

    def test_01_config_structures(self):
        """Verify configuration dictionaries and lists."""
        self.assertGreaterEqual(len(config.DISCIPLINES), 5)
        self.assertIn("VLSI & Chip Design", config.DISCIPLINES)
        self.assertIn("Embedded Systems & Firmware", config.DISCIPLINES)
        
        self.assertGreaterEqual(len(config.REGIONS), 4)
        self.assertIn("Tel Aviv & Central", config.REGIONS)
        self.assertIn("Haifa & North", config.REGIONS)
        
        self.assertGreaterEqual(len(config.TOP_EMPLOYERS), 10)
        for emp in config.TOP_EMPLOYERS:
            self.assertTrue(emp["name"])
            self.assertTrue(emp["careers_url"].startswith("http"))
            
        self.assertIn("All Time", config.RECENCY_OPTIONS)
        self.assertIn("⭐ Saved", config.STATUS_OPTIONS)

    def test_02_database_operations(self):
        """Test DB insert, update, query, deduplication, and stats."""
        test_job = {
            "title": "Unit Test RF Engineer",
            "company": "Test Defense Corp",
            "location": "Haifa",
            "region": "Haifa & North",
            "discipline": "RF, Antennas & Communications",
            "description": "Designing high-power RF amplifiers and antenna arrays.",
            "skills": ["ADS", "VNA", "MATLAB"],
            "study_year": "3rd Year B.Sc.",
            "days_per_week": "20 hrs / week",
            "url": "https://example.com/job/test-rf-123",
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "source": "UnitTest",
            "relevance_score": 95,
            "relevance_reasons": "Direct RF match for unit testing.",
            "status": "New"
        }
        
        # 1. Save Job
        job_id = db_manager.save_job(test_job)
        self.assertTrue(job_id)
        
        # 2. Query Job
        results = db_manager.get_jobs(
            disciplines=["RF, Antennas & Communications"],
            search_query="Unit Test RF"
        )
        self.assertTrue(any(j["id"] == job_id for j in results))
        saved = [j for j in results if j["id"] == job_id][0]
        self.assertEqual(saved["company"], "Test Defense Corp")
        self.assertIn("ADS", saved["skills"])
        
        # 3. Update Status & Notes
        db_manager.update_job_status(job_id, "⭐ Saved", notes="Interview on Sunday")
        updated = [j for j in db_manager.get_jobs() if j["id"] == job_id][0]
        self.assertEqual(updated["status"], "⭐ Saved")
        self.assertEqual(updated["notes"], "Interview on Sunday")
        
        # 4. Filter by Status
        saved_jobs = db_manager.get_jobs(status_filter="⭐ Saved")
        self.assertTrue(any(j["id"] == job_id for j in saved_jobs))
        
        # 5. Filter by Recency
        recent_jobs = db_manager.get_jobs(recency_days=7)
        self.assertTrue(any(j["id"] == job_id for j in recent_jobs))
        
        # 6. Test Stats
        stats = db_manager.get_stats()
        self.assertGreater(stats["total_jobs"], 0)
        self.assertIn("RF, Antennas & Communications", stats["by_discipline"])
        
        # 7. Clean up
        db_manager.delete_job(job_id)
        check_deleted = [j for j in db_manager.get_jobs() if j["id"] == job_id]
        self.assertEqual(len(check_deleted), 0)

    def test_03_scraper_heuristics(self):
        """Test scraper helper functions for title/company/location parsing."""
        comp = scraper.extract_company_from_title("NVIDIA hiring VLSI Student in Tel Aviv", "https://linkedin.com/jobs/view/123")
        self.assertEqual(comp, "Nvidia (Mellanox)")
        
        loc = scraper.extract_location_from_text("Job located in Haifa near Matam park")
        self.assertEqual(loc.lower(), "haifa")
        
        cleaned = scraper.clean_text("<b>Title</b>   with   extra spaces &amp; tags")
        self.assertEqual(cleaned, "Title with extra spaces &amp; tags")

    def test_04_agent_enrichment_fallback(self):
        """Test rule-based heuristic enrichment."""
        raw = {
            "title": "Board Design Student - Herzliya",
            "company": "Apple Israel",
            "location": "Herzliya",
            "region": "Sharon Area",
            "discipline": "Board Design & Hardware",
            "description": "Looking for 3rd year student with Altium and PCB experience.",
            "url": "https://example.com/apple-board"
        }
        enriched = agent_engine.heuristic_enrichment(raw)
        self.assertIn("Altium", enriched["skills"])
        self.assertIn("PCB", enriched["skills"])
        self.assertGreaterEqual(enriched["relevance_score"], 80)
        self.assertTrue(enriched["study_year"])

    def test_05_agent_live_evaluation(self):
        """Test AI agent evaluation and structured JSON output."""
        raw = {
            "title": "Silicon Verification Student (UVM/SystemVerilog)",
            "company": "Intel Israel",
            "location": "Haifa",
            "description": "Develop UVM simulation environments for next-gen Core CPUs. 20 hours per week for 2nd/3rd year EE students.",
            "url": "https://jobs.intel.com/sample"
        }
        analyzed = agent_engine.analyze_job_with_agent(raw)
        self.assertTrue(analyzed["title"])
        self.assertEqual(analyzed["discipline"], "Silicon Verification")
        self.assertEqual(analyzed["region"], "Haifa & North")
        self.assertIsInstance(analyzed["skills"], list)
        self.assertGreaterEqual(analyzed["relevance_score"], 70)

if __name__ == "__main__":
    unittest.main(verbosity=2)
