# ⚡ Israel Electrical Engineering Student Job Agent & Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Groq-Llama%203%20%2F%20GPT--OSS-orange" alt="Groq">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

An intelligent, full-stack job search agent and interactive dashboard built specifically for **Electrical Engineering (EE) students in Israel** seeking student positions, internships, and junior hardware/firmware roles.

---

## 🎯 Key Features

- **⚡ 10 Specialized EE Disciplines**:
  - **VLSI & Chip Design** (ASIC, RTL, Verilog, SystemVerilog, FPGA)
  - **Silicon Verification** (UVM, SystemVerilog, Coverage, Emulation)
  - **Board Design & Hardware Engineering** (Analog/Digital, Altium, High-Speed PCB, Power)
  - **Embedded Systems & Firmware** (C/C++, Microcontrollers, RTOS, Linux Device Drivers)
  - **RF, Antennas & Communications** (Microwave, Radar, Wireless, ADS/HFSS)
  - **Signal & Image Processing / DSP** (MATLAB, Python, Computer Vision, Algorithms)
  - **Electro-Optics & Applied Physics** (Lasers, Photonics, Sensors, Metrology)
  - **Hardware Validation & Lab** (Bring-up, Oscilloscopes, Post-Silicon, LabVIEW)
  - **Power, Energy & Control Systems** (High voltage, DC-DC, Inverters, PLC)
  - **General EE Student Roles**

- **📍 6 Israeli Geographical Regions**:
  - **Tel Aviv & Central (Gush Dan)** (Tel Aviv, Ramat Gan, Petah Tikva, Holon, etc.)
  - **Haifa & North** (Haifa / Matam, Yokneam, Karmiel, Migdal HaEmek)
  - **Sharon Area** (Herzliya Pituach, Ra'anana, Kfar Saba, Netanya)
  - **Jerusalem** (Har Hotzvim, Givat Ram)
  - **South & Shfela** (Beer Sheva, Kiryat Gat, Rehovot, Nes Ziona)
  - **Hybrid / Remote**

- **⏱️ Recency & Advertisement Time Filter**:
  - Filter postings by: Past 24h, Past 3 days, Past 7 days, Past 14 days, Past 30 days, or All Time.

- **🤖 AI Agent Sourcing & LLM Evaluation**:
  - Intelligent scraping & extraction across Israeli career portals and tech boards (LinkedIn Israel, Drushim, AllJobs, Greenhouse, Comeet, Workday).
  - Evaluates fit and assigns a **0–100% Relevance Match Score** with AI reasoning.
  - Extracts student requirements: target study year, minimum days/week commitment, and required tools/skills.

- **📋 Application Tracker & Custom Notes**:
  - Track application lifecycle: `New`, `⭐ Saved`, `📝 Applied`, `💬 Interviewing`, `🎉 Offered`, `❌ Archived`.
  - Add personal notes for interview prep.
  - 1-click export to CSV.

- **🏢 Direct Employer Hub**:
  - Fast 1-click direct links to career portals of major Israeli tech employers (Nvidia, Intel, Apple, Qualcomm, Broadcom, Marvell, Elbit Systems, IAI, Rafael, Mobileye, Cadence, Synopsys, Applied Materials, SolarEdge, Tower Semi, etc.).

---

## 🏗️ Project Architecture

```
student-job-agent/
│
├── app.py              # Modern Streamlit Web Dashboard
├── agent_engine.py     # AI Agent evaluation, LLM parsing, scoring & fallback heuristics
├── scraper.py          # Web search & scraper engine tailored for Israeli job boards
├── db_manager.py       # SQLite persistence, schema migrations, deduplication & tracking
├── config.py           # EE disciplines, Israeli regions, top employers & filter options
├── main.py             # Unified CLI entrypoint (launch Web UI or CLI scout)
├── test_system.py      # Full unit test suite
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore configuration
└── README.md           # Documentation
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/student-job-agent.git
cd student-job-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables (Optional but recommended)
Copy `.env.example` to `.env` and add your API key(s):
```bash
cp .env.example .env
```
*(Supports [Groq](https://console.groq.com/) for ultrafast LLM evaluation or [Google Gemini](https://aistudio.google.com/))*.

---

## 🖥️ Usage

### Launch the Web App
```bash
streamlit run app.py
```
*(Or simply run `python main.py`)*

### Run AI Scout via Command Line
```bash
# Scout recent VLSI jobs in Israel
python main.py --scout --discipline "VLSI & Chip Design" --count 5

# Scout Embedded / Firmware positions
python main.py --scout --discipline "Embedded Systems & Firmware" --count 3

# Scout with custom keywords
python main.py --scout --keywords "FPGA" --count 4
```

---

## 🧪 Running Tests

To run the full unit test suite:
```bash
python test_system.py
```

---

## 📄 License
This project is licensed under the MIT License.
