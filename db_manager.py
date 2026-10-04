import sys
import os
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Ensure stdout handles utf-8 safely on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database table schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        region TEXT,
        discipline TEXT,
        description TEXT,
        skills TEXT,
        study_year TEXT,
        days_per_week TEXT,
        url TEXT,
        date_posted TEXT,
        source TEXT,
        relevance_score INTEGER DEFAULT 80,
        relevance_reasons TEXT,
        status TEXT DEFAULT 'New',
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def generate_job_id(company: str, title: str, url: str) -> str:
    """Generates a stable unique hash ID for deduplication."""
    key = f"{company.strip().lower()}_{title.strip().lower()}_{url.strip().lower()}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]

def save_job(job: Dict[str, Any]) -> str:
    """Inserts or updates a job. Preserves user status and notes if existing."""
    conn = get_connection()
    cursor = conn.cursor()
    
    url = job.get("url", "").strip()
    company = job.get("company", "").strip()
    title = job.get("title", "").strip()
    
    job_id = job.get("id") or generate_job_id(company, title, url)
    
    # Check if job already exists
    cursor.execute("SELECT status, notes FROM jobs WHERE id = ?", (job_id,))
    existing = cursor.fetchone()
    
    status = existing["status"] if existing else job.get("status", "New")
    notes = existing["notes"] if existing else job.get("notes", "")
    
    skills = job.get("skills", [])
    if isinstance(skills, list):
        skills_str = json.dumps(skills, ensure_ascii=False)
    else:
        skills_str = str(skills)
        
    date_posted = job.get("date_posted") or datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
    INSERT INTO jobs (
        id, title, company, location, region, discipline, 
        description, skills, study_year, days_per_week, url, 
        date_posted, source, relevance_score, relevance_reasons, status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        title = excluded.title,
        company = excluded.company,
        location = excluded.location,
        region = excluded.region,
        discipline = excluded.discipline,
        description = excluded.description,
        skills = excluded.skills,
        study_year = excluded.study_year,
        days_per_week = excluded.days_per_week,
        url = excluded.url,
        date_posted = excluded.date_posted,
        source = excluded.source,
        relevance_score = excluded.relevance_score,
        relevance_reasons = excluded.relevance_reasons
    """, (
        job_id,
        title,
        company,
        job.get("location", "Israel"),
        job.get("region", "Tel Aviv & Central"),
        job.get("discipline", "General EE / Tech Student"),
        job.get("description", ""),
        skills_str,
        job.get("study_year", "2nd/3rd Year"),
        job.get("days_per_week", "2-3 days / 20 hours"),
        url,
        date_posted,
        job.get("source", "Web"),
        int(job.get("relevance_score", 85)),
        job.get("relevance_reasons", ""),
        status,
        notes
    ))
    conn.commit()
    conn.close()
    return job_id

def get_jobs(
    disciplines: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    recency_days: Optional[int] = None,
    min_relevance: int = 0,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetches jobs matching filter criteria."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE relevance_score >= ?"
    params = [min_relevance]
    
    if disciplines and len(disciplines) > 0 and "All" not in disciplines:
        placeholders = ",".join(["?"] * len(disciplines))
        query += f" AND discipline IN ({placeholders})"
        params.extend(disciplines)
        
    if regions and len(regions) > 0 and "All" not in regions:
        placeholders = ",".join(["?"] * len(regions))
        query += f" AND region IN ({placeholders})"
        params.extend(regions)
        
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
        
    if recency_days:
        cutoff = (datetime.now() - timedelta(days=recency_days)).strftime("%Y-%m-%d")
        query += " AND date_posted >= ?"
        params.append(cutoff)
        
    if search_query:
        term = f"%{search_query.strip()}%"
        query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ? OR skills LIKE ? OR location LIKE ?)"
        params.extend([term, term, term, term, term])
        
    query += " ORDER BY date_posted DESC, relevance_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["skills"] = json.loads(item["skills"]) if item["skills"] else []
        except Exception:
            item["skills"] = [s.strip() for s in item["skills"].split(",") if s.strip()]
        results.append(item)
        
    conn.close()
    return results

def update_job_status(job_id: str, status: str, notes: Optional[str] = None):
    """Updates user application status and optional notes."""
    conn = get_connection()
    cursor = conn.cursor()
    if notes is not None:
        cursor.execute("UPDATE jobs SET status = ?, notes = ? WHERE id = ?", (status, notes, job_id))
    else:
        cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()

def delete_job(job_id: str):
    """Deletes a job from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def get_stats() -> Dict[str, Any]:
    """Returns aggregated stats for dashboard counters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT discipline, COUNT(*) FROM jobs GROUP BY discipline ORDER BY COUNT(*) DESC")
    by_discipline = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT region, COUNT(*) FROM jobs GROUP BY region ORDER BY COUNT(*) DESC")
    by_region = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return {
        "total_jobs": total_jobs,
        "by_discipline": by_discipline,
        "by_region": by_region,
        "by_status": by_status
    }

def seed_initial_data():
    """Seeds rich, realistic Israeli Electrical Engineering student positions across all fields."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        return  # already seeded

    now = datetime.now()
    
    sample_jobs = [
        {
            "title": "VLSI Logic Design Student",
            "company": "Nvidia (Mellanox)",
            "location": "Yokneam / Tel Aviv",
            "region": "Haifa & North",
            "discipline": "VLSI & Chip Design",
            "description": "Join our cutting-edge Networking Silicon team designing next-generation 800G/1.6T InfiniBand & Ethernet switches. Work with senior micro-architects on RTL coding (SystemVerilog), linting, clock domain crossing, and synthesis.",
            "skills": ["SystemVerilog", "RTL", "Digital Design", "Python", "Linux"],
            "study_year": "3rd or 4th year B.Sc. EE / Computer Engineering",
            "days_per_week": "At least 20 hours / week (2.5 days)",
            "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
            "date_posted": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
            "source": "Nvidia Careers",
            "relevance_score": 98,
            "relevance_reasons": "Direct RTL & Digital Logic design in top-tier tier-1 networking chip team.",
            "status": "New"
        },
        {
            "title": "Silicon Pre-Silicon Verification Student",
            "company": "Intel Israel",
            "location": "Haifa (Matam)",
            "region": "Haifa & North",
            "discipline": "Silicon Verification",
            "description": "Developing UVM-based simulation and verification environments for Intel next-gen Core processors. Writing test plans, coverage models, and tracking functional bugs in complex digital IP blocks.",
            "skills": ["UVM", "SystemVerilog", "OOP", "Perl/Python", "Git"],
            "study_year": "2nd or 3rd year B.Sc. Electrical Engineering",
            "days_per_week": "20-25 hours per week with exam flexibility",
            "url": "https://jobs.intel.com/en/search-jobs/Israel",
            "date_posted": (now - timedelta(days=2)).strftime("%Y-%m-%d"),
            "source": "Intel Israel Jobs",
            "relevance_score": 95,
            "relevance_reasons": "Core UVM / SystemVerilog verification role on flagship CPU architectures.",
            "status": "New"
        },
        {
            "title": "Hardware Board Design Student",
            "company": "Apple Israel",
            "location": "Herzliya Pituach",
            "region": "Sharon Area",
            "discipline": "Board Design & Hardware",
            "description": "Participate in designing, testing and debugging multi-layer high-speed PCB boards for Apple silicon validation systems. Hands-on schematic capture, board bring-up, signal integrity simulation and lab measurements.",
            "skills": ["Altium Designer", "High-Speed PCB", "Analog Circuits", "Oscilloscopes", "Signal Integrity"],
            "study_year": "3rd year EE Student with at least 1.5 years remaining",
            "days_per_week": "2-3 days / week (flexible during exams)",
            "url": "https://jobs.apple.com/en-il/search?location=israel-ISR",
            "date_posted": (now - timedelta(days=3)).strftime("%Y-%m-%d"),
            "source": "Apple Careers",
            "relevance_score": 96,
            "relevance_reasons": "High-speed board design & validation for custom Apple Silicon silicon systems.",
            "status": "⭐ Saved"
        },
        {
            "title": "Embedded & Firmware Engineering Student",
            "company": "Qualcomm Israel",
            "location": "Haifa",
            "region": "Haifa & North",
            "discipline": "Embedded Systems & Firmware",
            "description": "Developing low-level firmware for cellular modems and Wi-Fi 7/8 chips. Work on RTOS kernel services, device drivers (SPI, I2C, UART), memory management, and debugging using JTAG emulators.",
            "skills": ["C", "C++", "RTOS", "Microcontrollers", "ARM Architecture", "JTAG"],
            "study_year": "2nd or 3rd year in Electrical Engineering or Computer Engineering",
            "days_per_week": "20 hours / week",
            "url": "https://qualcomm.wd5.myworkdayjobs.com/External",
            "date_posted": (now - timedelta(days=4)).strftime("%Y-%m-%d"),
            "source": "Qualcomm Careers",
            "relevance_score": 94,
            "relevance_reasons": "Hands-on C/C++ firmware development on wireless connectivity chips.",
            "status": "New"
        },
        {
            "title": "RF & Microwave Engineering Student",
            "company": "Elbit Systems",
            "location": "Netanya / Haifa",
            "region": "Sharon Area",
            "discipline": "RF, Antennas & Communications",
            "description": "Join our Advanced Electronic Warfare & Radar engineering group. Assist in RF circuit simulations (ADS, CST, HFSS), testing RF power amplifiers, filters, mixers, and antenna arrays in anechoic chambers.",
            "skills": ["ADS", "CST / HFSS", "Spectrum Analyzer", "VNA", "Microwave Circuits", "MATLAB"],
            "study_year": "3rd or 4th year EE Student (RF / Electromagnetics track preferred)",
            "days_per_week": "Minimum 2 full days per week",
            "url": "https://elbitsystems.com/careers/",
            "date_posted": (now - timedelta(days=2)).strftime("%Y-%m-%d"),
            "source": "Elbit Careers",
            "relevance_score": 97,
            "relevance_reasons": "Comprehensive RF/Radar development with state-of-the-art lab and simulation tools.",
            "status": "New"
        },
        {
            "title": "Signal Processing & Algorithms Student",
            "company": "Mobileye",
            "location": "Jerusalem",
            "region": "Jerusalem",
            "discipline": "Signal & Image Processing / DSP",
            "description": "Developing signal processing and radar/LiDAR fusion algorithms for autonomous driving systems. Implementing real-time digital filtering, point-cloud clustering, and performance benchmarking on EyeQ chips.",
            "skills": ["Python", "C++", "MATLAB", "DSP Algorithms", "Linear Algebra"],
            "study_year": "B.Sc. / M.Sc. in Electrical Engineering / Applied Physics / CS",
            "days_per_week": "20 hours / week",
            "url": "https://careers.mobileye.com/",
            "date_posted": (now - timedelta(days=5)).strftime("%Y-%m-%d"),
            "source": "Mobileye Careers",
            "relevance_score": 93,
            "relevance_reasons": "Advanced autonomous vehicle perception and DSP algorithm engineering.",
            "status": "New"
        },
        {
            "title": "Electro-Optics & Laser Systems Student",
            "company": "Rafael Advanced Defense Systems",
            "location": "Haifa / Leshem",
            "region": "Haifa & North",
            "discipline": "Electro-Optics & Applied Physics",
            "description": "Integration and characterization of electro-optical sensor payloads, thermal cameras, and laser rangefinders. Designing optical test benches, optical alignment, and analyzing detector quantum efficiency.",
            "skills": ["Optics", "Lasers", "Zemax / MATLAB", "LabVIEW", "Optical Alignment"],
            "study_year": "3rd year EE / Applied Physics student with electro-optics track",
            "days_per_week": "2-3 days / week",
            "url": "https://www.rafael.co.il/careers/",
            "date_posted": (now - timedelta(days=3)).strftime("%Y-%m-%d"),
            "source": "Rafael Careers",
            "relevance_score": 95,
            "relevance_reasons": "Top-tier national electro-optics and laser systems division.",
            "status": "New"
        },
        {
            "title": "Hardware Validation & Post-Silicon Lab Student",
            "company": "Marvell Israel",
            "location": "Petah Tikva",
            "region": "Tel Aviv & Central",
            "discipline": "Hardware Validation & Lab",
            "description": "Perform silicon bring-up and physical layer validation on high-speed Ethernet PHY chips. Work with oscilloscopes, BERT (Bit Error Rate Testers), thermal chambers, and write Python test automation scripts.",
            "skills": ["Python Automation", "Oscilloscopes", "BERT", "Ethernet PHY", "Post-Silicon"],
            "study_year": "2nd, 3rd or 4th year Electrical Engineering student",
            "days_per_week": "20 hours weekly",
            "url": "https://marvell.wd1.myworkdayjobs.com/MarvellCareers",
            "date_posted": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
            "source": "Marvell Jobs",
            "relevance_score": 92,
            "relevance_reasons": "Direct silicon validation and Python test automation in high-speed networking.",
            "status": "New"
        },
        {
            "title": "Power Electronics & Control Engineering Student",
            "company": "SolarEdge Technologies",
            "location": "Herzliya Pituach / Modi'in",
            "region": "Sharon Area",
            "discipline": "Power, Energy & Control",
            "description": "Development and lab testing of solar PV power optimizers and grid-tied smart inverters. Design of DC-DC buck/boost converters, gate drivers, magnetic components, and analog control feedback loops.",
            "skills": ["Power Electronics", "DC-DC Converters", "LTspice / PSIM", "High Voltage Safety", "Control Loops"],
            "study_year": "3rd or 4th year EE student specializing in Power Electronics / Energy",
            "days_per_week": "2.5 days / week (flexible)",
            "url": "https://www.solaredge.com/corporate/careers",
            "date_posted": (now - timedelta(days=6)).strftime("%Y-%m-%d"),
            "source": "SolarEdge Careers",
            "relevance_score": 94,
            "relevance_reasons": "Industry leader in smart energy, high-power DC-DC and inverter electronics.",
            "status": "New"
        },
        {
            "title": "Analog / Mixed-Signal VLSI Student",
            "company": "Tower Semiconductor",
            "location": "Migdal HaEmek",
            "region": "Haifa & North",
            "discipline": "VLSI & Chip Design",
            "description": "Characterization of CMOS and SiGe BiCMOS analog cells (PLLs, bandgaps, LNAs, ADCs). Running SPICE / Spectre simulations, Monte Carlo variability analysis, and silicon wafer measurements.",
            "skills": ["Cadence Virtuoso", "Spectre / SPICE", "Analog Layout", "Semiconductor Physics"],
            "study_year": "3rd or 4th year B.Sc. / M.Sc. in Electrical Engineering",
            "days_per_week": "2 days per week",
            "url": "https://towersemi.com/careers/",
            "date_posted": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
            "source": "TowerSemi Careers",
            "relevance_score": 91,
            "relevance_reasons": "Authentic silicon foundry mixed-signal design & PDK modeling.",
            "status": "New"
        },
        {
            "title": "Hardware / Firmware Student - Cyber & Embedded",
            "company": "Check Point Software",
            "location": "Tel Aviv (near train station)",
            "region": "Tel Aviv & Central",
            "discipline": "Embedded Systems & Firmware",
            "description": "Developing firmware and hardware acceleration drivers for next-generation quantum-safe enterprise firewall appliances. Working on PCIe DMA, DPDK, Linux kernel drivers, and low-level C.",
            "skills": ["C", "Linux Kernel", "PCIe", "Networking Protocols", "Debugging"],
            "study_year": "2nd or 3rd year EE / CE student with at least 3 semesters left",
            "days_per_week": "20 hours / week",
            "url": "https://careers.checkpoint.com/",
            "date_posted": (now - timedelta(days=2)).strftime("%Y-%m-%d"),
            "source": "Check Point Careers",
            "relevance_score": 89,
            "relevance_reasons": "Combines network security hardware acceleration with low-level Linux systems.",
            "status": "New"
        },
        {
            "title": "Opto-Mechanical & Hardware Systems Student",
            "company": "Applied Materials",
            "location": "Rehovot",
            "region": "South & Shfela",
            "discipline": "Electro-Optics & Applied Physics",
            "description": "Working on advanced electron beam inspection and metrology machines for the world's most advanced chip fabs. Calibration of optical sensors, vacuum chambers, and high-precision motion stages.",
            "skills": ["Optics", "Sensors", "MATLAB", "Physics", "Motion Control"],
            "study_year": "3rd or 4th year EE / Physics student",
            "days_per_week": "2.5 days / week",
            "url": "https://appliedmaterials.wd1.myworkdayjobs.com/Applied_Materials_Careers",
            "date_posted": (now - timedelta(days=4)).strftime("%Y-%m-%d"),
            "source": "Applied Materials Careers",
            "relevance_score": 92,
            "relevance_reasons": "World-leading semiconductor metrology and physics equipment manufacturer.",
            "status": "New"
        }
    ]
    
    for job in sample_jobs:
        save_job(job)

if __name__ == "__main__":
    init_db()
    seed_initial_data()
    print("Database initialized and seeded successfully!")
