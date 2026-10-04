import streamlit as st
import pandas as pd
import json
from datetime import datetime
import db_manager
import agent_engine
from config import DISCIPLINES, REGIONS, TOP_EMPLOYERS, RECENCY_OPTIONS, STATUS_OPTIONS

# ==============================================================================
# Page Configuration & Styling
# ==============================================================================
st.set_page_config(
    page_title="Israel EE Student Job Scout",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, polished UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5, #00C853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #616161;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .job-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .job-card:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .company-tag {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E88E5;
    }
    .pill-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .pill-discipline {
        background-color: #E3F2FD;
        color: #1565C0;
    }
    .pill-location {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    .pill-date {
        background-color: #FFF3E0;
        color: #E65100;
    }
    .pill-score-high {
        background-color: #C8E6C9;
        color: #1B5E20;
    }
    .pill-score-med {
        background-color: #FFF9C4;
        color: #F57F17;
    }
    .skill-chip {
        display: inline-block;
        background-color: rgba(128, 128, 128, 0.15);
        color: inherit;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-size: 0.78rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Ensure DB is initialized
db_manager.init_db()
db_manager.seed_initial_data()

# ==============================================================================
# Header & Stats Section
# ==============================================================================
col_title, col_actions = st.columns([3, 1])

with col_title:
    st.markdown('<div class="main-header">⚡ Israel EE Student Job Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">משרות סטודנט להנדסת חשמל, אלקטרוניקה, שבבים ומערכות משובצות בישראל</div>', unsafe_allow_html=True)

# Load database statistics
stats = db_manager.get_stats()

m1, m2, m3, m4 = st.columns(4)
m1.metric("💼 Total Positions", stats["total_jobs"])
m2.metric("⭐ Saved / Target", stats["by_status"].get("⭐ Saved", 0))
m3.metric("📝 Applied", stats["by_status"].get("📝 Applied", 0))
m4.metric("💬 In Interview", stats["by_status"].get("💬 Interviewing", 0))

# ==============================================================================
# Sidebar - Smart Filters
# ==============================================================================
st.sidebar.header("🔍 Job Filters & Search")

# 1. Sub-Discipline Filter
discipline_options = ["All Disciplines"] + list(DISCIPLINES.keys())
selected_disciplines = st.sidebar.multiselect(
    "⚡ EE Sub-Discipline / התמחות",
    options=discipline_options,
    default=["All Disciplines"]
)
if "All Disciplines" in selected_disciplines or not selected_disciplines:
    filter_disciplines = None
else:
    filter_disciplines = selected_disciplines

# 2. Location / Region Filter
region_options = ["All Regions"] + list(REGIONS.keys())
selected_regions = st.sidebar.multiselect(
    "📍 Location Region / אזור בארץ",
    options=region_options,
    default=["All Regions"]
)
if "All Regions" in selected_regions or not selected_regions:
    filter_regions = None
else:
    filter_regions = selected_regions

# 3. Recency / Posting Time Filter
recency_choice = st.sidebar.selectbox(
    "⏱️ Time of Advertisement / מועד פרסום",
    options=list(RECENCY_OPTIONS.keys()),
    index=0
)
filter_recency = RECENCY_OPTIONS[recency_choice]

# 4. Relevance Score Slider
min_relevance = st.sidebar.slider(
    "🎯 Min Match / Relevance Score",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
    help="Scores above 90% indicate highly tailored roles for Electrical Engineering undergraduates."
)

# 5. Application Status Filter
status_choice = st.sidebar.selectbox(
    "📋 Application Status",
    options=["All Statuses"] + STATUS_OPTIONS,
    index=0
)
filter_status = None if status_choice == "All Statuses" else status_choice

# 6. Free text search
search_term = st.sidebar.text_input(
    "🔎 Search Keywords / Company / Skill",
    placeholder="e.g. Verilog, Altium, Nvidia, Haifa, C++...",
    help="Search directly in job titles, company names, skills, or descriptions."
)

st.sidebar.markdown("---")

# ==============================================================================
# AI Agent Live Scout Tool
# ==============================================================================
with st.sidebar.expander("🤖 **Run AI Agent Live Scout**", expanded=False):
    st.write("Search the live web and Israeli career boards with our AI agent to find and analyze fresh positions.")
    scout_disc = st.selectbox("Target Discipline", ["All"] + list(DISCIPLINES.keys()), key="scout_disc")
    scout_region = st.selectbox("Target Region", ["All"] + list(REGIONS.keys()), key="scout_region")
    scout_kw = st.text_input("Extra Keywords (Optional)", placeholder="e.g., Apple, FPGA, Radar", key="scout_kw")
    scout_count = st.slider("Max jobs to scout", min_value=2, max_value=10, value=4, key="scout_count")
    
    if st.button("🚀 Scout Now", use_container_width=True):
        with st.spinner("Agent is scraping Israeli tech boards and analyzing with AI..."):
            try:
                scout_disc_val = None if scout_disc == "All" else scout_disc
                scout_region_val = None if scout_region == "All" else scout_region
                new_jobs = agent_engine.scout_and_save_jobs(
                    discipline=scout_disc_val,
                    region=scout_region_val,
                    keywords=scout_kw if scout_kw.strip() else None,
                    max_results=scout_count
                )
                st.success(f"Agent successfully scouted and processed {len(new_jobs)} jobs!")
                st.rerun()
            except Exception as e:
                st.error(f"Agent scouting error: {e}")

# ==============================================================================
# Main View Tabs
# ==============================================================================
tab_jobs, tab_employers, tab_analytics, tab_add = st.tabs([
    "📋 Job Feed & Opportunities",
    "🏢 Top Israeli EE Employers",
    "📊 Insights & Analytics",
    "➕ Add Custom Job"
])

# Fetch filtered jobs
jobs = db_manager.get_jobs(
    disciplines=filter_disciplines,
    regions=filter_regions,
    recency_days=filter_recency,
    min_relevance=min_relevance,
    status_filter=filter_status,
    search_query=search_term if search_term.strip() else None
)

# ------------------------------------------------------------------------------
# TAB 1: Job Feed & Opportunities
# ------------------------------------------------------------------------------
with tab_jobs:
    col_filter_info, col_export = st.columns([3, 1])
    with col_filter_info:
        st.write(f"Showing **{len(jobs)}** matching positions")
    with col_export:
        if jobs:
            df_export = pd.DataFrame(jobs)
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name=f"israel_ee_student_jobs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    if not jobs:
        st.info("No jobs matched your filter criteria. Try relaxing your filters or run the **AI Agent Live Scout** in the sidebar!")
    else:
        for job in jobs:
            job_id = job["id"]
            relevance = job.get("relevance_score", 80)
            score_class = "pill-score-high" if relevance >= 90 else "pill-score-med"
            
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span class="company-tag">{job['company']}</span> &nbsp;
                            <span style="font-size: 1.25rem; font-weight: 600;">{job['title']}</span>
                        </div>
                        <div>
                            <span class="pill-badge {score_class}">🎯 Match: {relevance}%</span>
                        </div>
                    </div>
                    <div style="margin-top: 0.4rem; margin-bottom: 0.6rem;">
                        <span class="pill-badge pill-discipline">{job.get('discipline', 'General EE')}</span>
                        <span class="pill-badge pill-location">📍 {job.get('location', 'Israel')} ({job.get('region', 'Central')})</span>
                        <span class="pill-badge pill-date">📅 Posted: {job.get('date_posted', 'Recent')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Card Details in clean Streamlit components
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**Overview**: {job.get('description', 'No description available.')}")
                    
                    # Student constraints
                    req_col1, req_col2 = st.columns(2)
                    with req_col1:
                        st.caption(f"🎓 **Target Study Level**: {job.get('study_year', '2nd/3rd Year B.Sc.')}")
                    with req_col2:
                        st.caption(f"⏰ **Time Commitment**: {job.get('days_per_week', '2-3 days / 20 hrs')}")
                        
                    # Skills chips
                    skills = job.get("skills", [])
                    if skills:
                        chips_html = "".join([f'<span class="skill-chip">🛠️ {s}</span>' for s in skills])
                        st.markdown(f"<div>{chips_html}</div>", unsafe_allow_html=True)
                        
                    if job.get("relevance_reasons"):
                        st.info(f"💡 **AI Match Analysis**: {job['relevance_reasons']}")
                        
                with c2:
                    # Direct Apply Button
                    if job.get("url"):
                        st.link_button("🔗 Apply Directly", job["url"], use_container_width=True)
                    
                    # Status updater
                    current_status = job.get("status", "New")
                    status_idx = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0
                    new_status = st.selectbox(
                        "Status",
                        options=STATUS_OPTIONS,
                        index=status_idx,
                        key=f"status_{job_id}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != current_status:
                        db_manager.update_job_status(job_id, new_status)
                        st.rerun()
                        
                    # Notes popup expander
                    with st.expander("📝 Personal Notes"):
                        note_text = st.text_area("Notes", value=job.get("notes", ""), key=f"notes_{job_id}", label_visibility="collapsed")
                        if st.button("Save Note", key=f"btn_note_{job_id}"):
                            db_manager.update_job_status(job_id, new_status, notes=note_text)
                            st.toast("Note saved!")
                            
                st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1.2rem; border: none; border-top: 1px dashed rgba(128,128,128,0.3);'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: Top Israeli EE Employers
# ------------------------------------------------------------------------------
with tab_employers:
    st.subheader("🏢 Leading Employers Hiring EE Students in Israel")
    st.write("Direct career portal links and company hubs for chipmakers, defense giants, and hardware engineering leaders:")
    
    emp_cols = st.columns(2)
    for i, emp in enumerate(TOP_EMPLOYERS):
        col = emp_cols[i % 2]
        with col:
            with st.container():
                st.markdown(f"### {emp['name']}")
                st.caption(f"**Domain**: {emp['category']} | **Israel Hubs**: {emp['locations']}")
                st.link_button(f"🌐 Visit {emp['name']} Careers", emp["careers_url"], use_container_width=True)
                st.markdown("<br/>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: Insights & Analytics
# ------------------------------------------------------------------------------
with tab_analytics:
    st.subheader("📊 Israeli EE Student Market Insights")
    
    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.write("#### Openings by EE Sub-Discipline")
        if stats["by_discipline"]:
            df_disc = pd.DataFrame(list(stats["by_discipline"].items()), columns=["Discipline", "Count"]).set_index("Discipline")
            st.bar_chart(df_disc, color="#1E88E5")
        else:
            st.info("No data yet.")
            
    with col_ch2:
        st.write("#### Openings by Geographical Region")
        if stats["by_region"]:
            df_reg = pd.DataFrame(list(stats["by_region"].items()), columns=["Region", "Count"]).set_index("Region")
            st.bar_chart(df_reg, color="#00C853")
        else:
            st.info("No data yet.")
            
    st.write("#### Application Funnel & Status")
    if stats["by_status"]:
        df_stat = pd.DataFrame(list(stats["by_status"].items()), columns=["Status", "Count"]).set_index("Status")
        st.dataframe(df_stat, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: Add Custom Job
# ------------------------------------------------------------------------------
with tab_add:
    st.subheader("➕ Add a Custom Job Listing")
    st.write("Found a student job on Telegram, WhatsApp, or university career boards? Add it to your tracker!")
    
    with st.form("custom_job_form"):
        c_title = st.text_input("Job Title *", placeholder="e.g. ASIC RTL Design Student")
        c_comp = st.text_input("Company Name *", placeholder="e.g. Nvidia, Rafael, Startup")
        c_loc = st.text_input("Location / City", placeholder="e.g. Tel Aviv, Haifa, Remote")
        c_reg = st.selectbox("Region", options=list(REGIONS.keys()))
        c_disc = st.selectbox("Discipline", options=list(DISCIPLINES.keys()))
        c_desc = st.text_area("Job Description", placeholder="Short summary of job requirements...")
        c_skills = st.text_input("Key Skills (comma-separated)", placeholder="Verilog, Altium, C++, Python")
        c_url = st.text_input("Job Application Link / URL", placeholder="https://...")
        c_year = st.text_input("Study Year Requirement", placeholder="e.g. 3rd year B.Sc. EE")
        c_days = st.text_input("Expected Days/Hours", placeholder="e.g. 20 hours / 2.5 days")
        c_status = st.selectbox("Initial Status", options=STATUS_OPTIONS, index=0)
        
        submit = st.form_submit_button("Save Job", use_container_width=True)
        if submit:
            if not c_title or not c_comp:
                st.error("Please provide at least a Job Title and Company Name.")
            else:
                skills_list = [s.strip() for s in c_skills.split(",") if s.strip()]
                new_job = {
                    "title": c_title.strip(),
                    "company": c_comp.strip(),
                    "location": c_loc.strip() if c_loc.strip() else "Israel",
                    "region": c_reg,
                    "discipline": c_disc,
                    "description": c_desc.strip(),
                    "skills": skills_list,
                    "url": c_url.strip(),
                    "study_year": c_year.strip() if c_year.strip() else "2nd/3rd Year",
                    "days_per_week": c_days.strip() if c_days.strip() else "20 hours / week",
                    "status": c_status,
                    "relevance_score": 90,
                    "relevance_reasons": "Manually added by user.",
                    "source": "Custom Entry",
                    "date_posted": datetime.now().strftime("%Y-%m-%d")
                }
                db_manager.save_job(new_job)
                st.success("Custom job saved successfully!")
                st.rerun()
