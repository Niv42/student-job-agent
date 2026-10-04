import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# EE Disciplines / Sub-fields Definitions
# ==============================================================================
DISCIPLINES: Dict[str, Dict[str, any]] = {
    "VLSI & Chip Design": {
        "he": "תכנון שבבים ו-VLSI",
        "keywords": ["VLSI", "ASIC", "RTL", "Verilog", "SystemVerilog", "FPGA", "Digital Design", "Logic Design", "Synthesis", "Cadence", "Synopsys"],
        "icon": "⚡"
    },
    "Silicon Verification": {
        "he": "אימות חומרה (Verification)",
        "keywords": ["Verification", "UVM", "SystemVerilog", "Coverage", "Emulation", "Specman", "Formal Verification", "אימות חומרה"],
        "icon": "🔬"
    },
    "Board Design & Hardware": {
        "he": "עריכת מעגלים וחומרה (Board Design)",
        "keywords": ["Board Design", "Hardware Engineer", "Analog", "PCB", "Altium", "Power Electronics", "Schematics", "חומרה", "כרטיסים"],
        "icon": "🔌"
    },
    "Embedded Systems & Firmware": {
        "he": "מערכות משובצות וקושחה (Embedded / FW)",
        "keywords": ["Embedded", "Firmware", "RTOS", "Microcontroller", "ARM", "STM32", "C++", "Device Driver", "Linux Kernel", "קושחה", "משובץ מחשב"],
        "icon": "💻"
    },
    "RF, Antennas & Communications": {
        "he": "תקשורת אלחוטית, RF וראדאר",
        "keywords": ["RF", "Antenna", "Microwave", "Wireless", "Radar", "Signal Integrity", "EMC", "תקשורת", "גלי רדיו"],
        "icon": "📡"
    },
    "Signal & Image Processing / DSP": {
        "he": "עיבוד אותות ותמונה / DSP",
        "keywords": ["DSP", "Signal Processing", "Image Processing", "Computer Vision", "Algorithms", "MATLAB", "עיבוד אותות", "עיבוד תמונה"],
        "icon": "📊"
    },
    "Electro-Optics & Applied Physics": {
        "he": "אלקטרו-אופטיקה ופיזיקה יישומית",
        "keywords": ["Electro-Optics", "Photonics", "Laser", "Optics", "Sensors", "Applied Physics", "אופטיקה", "אלקטרואופטיקה", "פוטוניקה"],
        "icon": "💡"
    },
    "Hardware Validation & Lab": {
        "he": "מעבדת חומרה ובדיקות (Post-Silicon / Lab)",
        "keywords": ["Post-Silicon", "Validation", "Hardware Lab", "Oscilloscope", "LabVIEW", "Bring-up", "Test Engineer", "מעבדת חומרה", "בדיקות חומרה"],
        "icon": "🧪"
    },
    "Power, Energy & Control": {
        "he": "מערכות הספק, אנרגיה ובקרה",
        "keywords": ["Power Systems", "High Voltage", "Control Systems", "PLC", "Inverters", "SolarEdge", "זרם חזק", "הספק", "בקרה"],
        "icon": "🔋"
    },
    "General EE / Tech Student": {
        "he": "הנדסת חשמל כללי / סטודנט טכנולוגי",
        "keywords": ["Electrical Engineering", "EE Student", "סטודנט להנדסת חשמל", "סטודנט להנדסה"],
        "icon": "🎓"
    }
}

# ==============================================================================
# Israeli Geographical Regions
# ==============================================================================
REGIONS: Dict[str, Dict[str, any]] = {
    "Tel Aviv & Central": {
        "he": "תל אביב והמרכז (גוש דן)",
        "cities": ["Tel Aviv", "Ramat Gan", "Petah Tikva", "Holon", "Bnei Brak", "Bat Yam", "Givatayim", "Kiryat Ono", "תל אביב", "רמת גן", "פתח תקווה", "חולון"],
        "icon": "🏙️"
    },
    "Haifa & North": {
        "he": "חיפה והצפון (מת\"ם, יקנעם)",
        "cities": ["Haifa", "Matam", "Yokneam", "Karmiel", "Migdal HaEmek", "Nesher", "Acre", "Nazareth", "חיפה", "מתם", "יקנעם", "כרמיאל", "מגדל העמק", "נשר"],
        "icon": "🌲"
    },
    "Sharon Area": {
        "he": "אזור השרון (הרצליה, רעננה, נתניה)",
        "cities": ["Herzliya", "Herzliya Pituach", "Raanana", "Kfar Saba", "Netanya", "Hod Hasharon", "Kfar Netter", "הרצליה", "רעננה", "כפר סבא", "נתניה", "הוד השרון"],
        "icon": "🏖️"
    },
    "Jerusalem": {
        "he": "ירושלים (הר חוצבים, גבעת רם)",
        "cities": ["Jerusalem", "Har Hotzvim", "Givat Ram", "Beit Shemesh", "ירושלים", "הר חוצבים", "גבעת רם"],
        "icon": "🏛️"
    },
    "South & Shfela": {
        "he": "השפלה והדרום (רחובות, ב\"ש, קריית גת)",
        "cities": ["Beer Sheva", "Kiryat Gat", "Rehovot", "Nes Ziona", "Rishon LeZion", "Yavne", "Ashdod", "Ashkelon", "באר שבע", "קריית גת", "רחובות", "נס ציונה", "ראשון לציון", "יבנה"],
        "icon": "🏜️"
    },
    "Hybrid / Remote": {
        "he": "היברידי / מרחוק",
        "cities": ["Remote", "Hybrid", "Israel", "היברידי", "עבודה מהבית"],
        "icon": "🌐"
    }
}

# ==============================================================================
# Top Employers for EE Students in Israel
# ==============================================================================
TOP_EMPLOYERS: List[Dict[str, str]] = [
    {"name": "Nvidia (Mellanox)", "category": "Semiconductor / AI", "careers_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite", "locations": "Yokneam, Tel Aviv, Raanana, Beer Sheva, Jerusalem"},
    {"name": "Intel Israel", "category": "Semiconductor", "careers_url": "https://jobs.intel.com/en/search-jobs/Israel", "locations": "Haifa, Petah Tikva, Jerusalem, Kiryat Gat"},
    {"name": "Apple Israel", "category": "Silicon / HW", "careers_url": "https://jobs.apple.com/en-il/search?location=israel-ISR", "locations": "Herzliya, Haifa"},
    {"name": "Qualcomm Israel", "category": "Semiconductor / Wireless", "careers_url": "https://qualcomm.wd5.myworkdayjobs.com/External", "locations": "Haifa, Hod Hasharon"},
    {"name": "Broadcom Israel", "category": "Semiconductor / Networking", "careers_url": "https://broadcom.wd1.myworkdayjobs.com/External_Career", "locations": "Tel Aviv, Nazareth"},
    {"name": "Marvell Israel", "category": "Semiconductor / Storage", "careers_url": "https://marvell.wd1.myworkdayjobs.com/MarvellCareers", "locations": "Petah Tikva, Yokneam"},
    {"name": "Elbit Systems", "category": "Defense / Aerospace / HW", "careers_url": "https://elbitsystems.com/careers/", "locations": "Haifa, Netanya, Rehovot, Karmiel, Holon"},
    {"name": "IAI (Israel Aerospace)", "category": "Aerospace / Defense / RF", "careers_url": "https://www.iai.co.il/careers", "locations": "Lod, Yehud, Beer Yaakov"},
    {"name": "Rafael Advanced Defense", "category": "Defense / Electro-Optics / HW", "careers_url": "https://www.rafael.co.il/careers/", "locations": "Haifa, Tel Aviv, Shlomi"},
    {"name": "Mobileye", "category": "Automotive / Vision / HW", "careers_url": "https://careers.mobileye.com/", "locations": "Jerusalem, Petah Tikva"},
    {"name": "Cadence Design Systems", "category": "EDA / VLSI Tools", "careers_url": "https://cadence.wd1.myworkdayjobs.com/External_Careers", "locations": "Petah Tikva, Haifa"},
    {"name": "Synopsys Israel", "category": "EDA / Silicon IP", "careers_url": "https://synopsys.wd1.myworkdayjobs.com/SynopsysCareersSite", "locations": "Herzliya, Haifa"},
    {"name": "Applied Materials", "category": "Semiconductor Equipment", "careers_url": "https://appliedmaterials.wd1.myworkdayjobs.com/Applied_Materials_Careers", "locations": "Rehovot"},
    {"name": "Tower Semiconductor", "category": "Foundry / Analog", "careers_url": "https://towersemi.com/careers/", "locations": "Migdal HaEmek, Netanya"},
    {"name": "SolarEdge", "category": "Power Electronics / Energy", "careers_url": "https://www.solaredge.com/corporate/careers", "locations": "Herzliya, Modi'in"},
    {"name": "KLA Israel", "category": "Electro-Optics / Inspection", "careers_url": "https://kla.wd1.myworkdayjobs.com/Search", "locations": "Migdal HaEmek, Yavne"},
    {"name": "Nova Ltd", "category": "Metrology / Physics / HW", "careers_url": "https://www.novami.com/careers/", "locations": "Rehovot"},
    {"name": "Texas Instruments", "category": "Semiconductor / Analog", "careers_url": "https://careers.ti.com/", "locations": "Raanana"},
    {"name": "Sony Semiconductor", "category": "IoT / Cellular / RF", "careers_url": "https://altair-semi.com/careers/", "locations": "Hod Hasharon"},
    {"name": "Western Digital", "category": "Storage / VLSI / Firmware", "careers_url": "https://jobs.smartrecruiters.com/WesternDigital", "locations": "Kfar Saba, Omer (Beer Sheva)"}
]

# Recency Filter Options (in days)
RECENCY_OPTIONS = {
    "All Time": None,
    "Past 24 Hours": 1,
    "Past 3 Days": 3,
    "Past 7 Days (1 Week)": 7,
    "Past 14 Days (2 Weeks)": 14,
    "Past 30 Days (1 Month)": 30
}

# Status Options for Application Tracking
STATUS_OPTIONS = [
    "New",
    "⭐ Saved",
    "📝 Applied",
    "💬 Interviewing",
    "🎉 Offered",
    "❌ Passed / Archived"
]
