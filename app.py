import streamlit as st
import os
from utils.pdf_parser import extract_text_from_pdf
from utils.jd_scraper import scrape_jd_from_url
from utils.job_search import search_jobs
from utils.gemini_client import (
    init_gemini,
    roast_resume,
    analyze_jd_gaps,
    rank_jobs_against_resume,
    generate_market_insights,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Career Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .score-box { padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem; }
  .score-high { background: #d4edda; color: #155724; }
  .score-mid  { background: #fff3cd; color: #856404; }
  .score-low  { background: #f8d7da; color: #721c24; }
  .gap-critical { border-left: 4px solid #dc3545; padding-left: 10px; margin: 6px 0; }
  .gap-moderate { border-left: 4px solid #ffc107; padding-left: 10px; margin: 6px 0; }
  .gap-minor    { border-left: 4px solid #28a745; padding-left: 10px; margin: 6px 0; }
  .keyword-pill { display: inline-block; background: #e9ecef; border-radius: 20px;
                  padding: 3px 12px; margin: 3px; font-size: 13px; }
  .keyword-missing { background: #f8d7da; color: #721c24; }
  .keyword-present { background: #d4edda; color: #155724; }
  .job-card { border: 1px solid #dee2e6; border-radius: 10px; padding: 1rem;
              margin-bottom: 1rem; background: white; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar — API Keys ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎯 ResumeIQ")
    st.caption("AI-powered career coach")
    st.divider()

    st.subheader("🔑 API Keys")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get free key at aistudio.google.com",
        placeholder="AIza...",
    )
    adzuna_id = st.text_input(
        "Adzuna App ID",
        help="Free at developer.adzuna.com",
        placeholder="your_app_id",
    )
    adzuna_key = st.text_input(
        "Adzuna App Key",
        type="password",
        placeholder="your_app_key",
    )

    st.divider()
    st.caption("📄 **Get API keys:**")
    st.caption("• [Gemini — aistudio.google.com](https://aistudio.google.com)")
    st.caption("• [Adzuna — developer.adzuna.com](https://developer.adzuna.com)")

    if gemini_key:
        init_gemini(gemini_key)
        st.success("Gemini connected ✓")

# ── Resume Upload (persistent across tabs) ───────────────────────────────────
st.title("🎯 ResumeIQ — AI Career Coach")

with st.expander("📄 Upload Your Resume (required for all features)", expanded=True):
    uploaded_resume = st.file_uploader("Upload Resume PDF", type=["pdf"], key="resume_upload")
    if uploaded_resume:
        if "resume_text" not in st.session_state or st.session_state.get("resume_name") != uploaded_resume.name:
            with st.spinner("Parsing resume..."):
                st.session_state.resume_text = extract_text_from_pdf(uploaded_resume)
                st.session_state.resume_name = uploaded_resume.name
        st.success(f"✓ Resume loaded: {uploaded_resume.name}")
        with st.expander("Preview extracted text"):
            st.text(st.session_state.resume_text[:1000] + "...")

resume_text = st.session_state.get("resume_text", "")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "💥 Roast My Resume",
    "🔍 Find Matching Jobs",
    "🔗 Analyze JD URL",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ROAST MY RESUME
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("💥 Roast My Resume vs a Job Description")
    st.caption("Paste a JD or drop a URL — get a brutal honest gap analysis + rewritten bullets")

    col1, col2 = st.columns([1, 1])

    with col1:
        jd_input_method = st.radio("JD Input Method", ["Paste JD text", "Scrape from URL"], horizontal=True)

    with col2:
        if jd_input_method == "Scrape from URL":
            jd_url = st.text_input("Job Posting URL", placeholder="https://careers.company.com/job/123")
            if jd_url and st.button("Fetch JD", key="fetch_jd_roast"):
                with st.spinner("Scraping job description..."):
                    scraped = scrape_jd_from_url(jd_url)
                    if scraped.startswith("ERROR"):
                        st.error(scraped)
                    else:
                        st.session_state.jd_text_roast = scraped
                        st.success("JD fetched!")

    jd_text = ""
    if jd_input_method == "Paste JD text":
        jd_text = st.text_area("Paste Job Description", height=200, placeholder="Paste the full job description here...")
    else:
        jd_text = st.session_state.get("jd_text_roast", "")
        if jd_text:
            st.text_area("Fetched JD (preview)", value=jd_text[:500] + "...", height=120, disabled=True)

    if st.button("💥 Roast My Resume", type="primary", disabled=not (resume_text and jd_text and gemini_key)):
        if not resume_text:
            st.warning("Please upload your resume first.")
        elif not jd_text:
            st.warning("Please provide a job description.")
        elif not gemini_key:
            st.warning("Please add your Gemini API key in the sidebar.")
        else:
            with st.spinner("Gemini is reviewing your resume... brace yourself 😬"):
                result = roast_resume(resume_text, jd_text)

            if "error" in result:
                st.error(f"Something went wrong: {result.get('raw', result['error'])}")
            else:
                # Score
                score = result.get("match_score", 0)
                score_class = "score-high" if score >= 70 else "score-mid" if score >= 45 else "score-low"
                score_emoji = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"
                st.markdown(f"""
                <div class="score-box {score_class}">
                  <h1>{score_emoji} {score}/100</h1>
                  <p>{result.get('verdict', '')}</p>
                </div>""", unsafe_allow_html=True)

                col_a, col_b = st.columns(2)

                with col_a:
                    # Strengths
                    st.markdown("### ✅ What's Working")
                    for s in result.get("strengths", []):
                        with st.container():
                            st.markdown(f"**{s.get('point', '')}**")
                            st.caption(s.get("detail", ""))

                    # Missing Keywords
                    st.markdown("### 🏷️ Missing Keywords")
                    st.caption("Add these to your resume to pass ATS filters:")
                    keywords_html = ""
                    for kw in result.get("missing_keywords", []):
                        keywords_html += f'<span class="keyword-pill keyword-missing">{kw}</span>'
                    st.markdown(keywords_html, unsafe_allow_html=True)

                with col_b:
                    # Gaps / Roast
                    st.markdown("### 🔥 The Roast (Gaps)")
                    for gap in result.get("roast", []):
                        severity = gap.get("severity", "minor")
                        icon = "🔴" if severity == "critical" else "🟡" if severity == "moderate" else "🟢"
                        st.markdown(
                            f'<div class="gap-{severity}">{icon} <strong>{gap.get("gap","")}</strong><br>'
                            f'<small>{gap.get("detail","")}</small></div>',
                            unsafe_allow_html=True
                        )

                # Top Actions
                st.markdown("### ⚡ Top 3 Actions Right Now")
                for i, action in enumerate(result.get("top_3_actions", []), 1):
                    st.info(f"**{i}.** {action}")

                # Rewrites
                st.markdown("### ✏️ Rewritten Bullets")
                st.caption("Copy these directly into your resume:")
                for rw in result.get("rewrites", []):
                    with st.expander(f"🔄 {rw.get('original', '')[:80]}..."):
                        st.markdown("**Before:**")
                        st.text(rw.get("original", ""))
                        st.markdown("**After:**")
                        st.success(rw.get("improved", ""))
                        st.caption(f"Why: {rw.get('why', '')}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FIND MATCHING JOBS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔍 Find Jobs That Match Your Resume")
    st.caption("Search live job postings and get AI-ranked matches with gap analysis")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        job_title_query = st.text_input("Job Title to Search", placeholder="AI Engineer", value="AI Engineer")
    with col2:
        country = st.selectbox("Country", ["us", "gb", "ca", "au"], index=0)
    with col3:
        num_results = st.slider("Results to fetch", 5, 20, 10)

    can_search = resume_text and gemini_key and adzuna_id and adzuna_key

    if not (adzuna_id and adzuna_key):
        st.info("💡 Add your free Adzuna API keys in the sidebar to enable job search. Sign up at developer.adzuna.com")

    if st.button("🔍 Find & Rank Jobs", type="primary", disabled=not can_search):
        with st.spinner(f"Searching for '{job_title_query}' jobs..."):
            jobs = search_jobs(job_title_query, adzuna_id, adzuna_key, country, num_results)

        if jobs and "error" in jobs[0]:
            st.error(f"Job search failed: {jobs[0]['error']}")
        else:
            st.success(f"Found {len(jobs)} jobs. Ranking against your resume...")

            with st.spinner("Gemini is ranking matches..."):
                ranked = rank_jobs_against_resume(resume_text, jobs)
                insights = generate_market_insights(resume_text, jobs)

            # Market insights
            with st.expander("📊 Market Intelligence", expanded=True):
                st.markdown(insights)

            # Ranked jobs
            st.markdown(f"### 🏆 Top Matches for Your Resume")
            for i, job in enumerate(ranked[:10], 1):
                score = job.get("match_score", 0)
                score_color = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"

                with st.expander(f"{score_color} #{i} — {job.get('title','')} at {job.get('company','')} | {score}/100 match"):
                    col_l, col_r = st.columns([1, 1])
                    with col_l:
                        st.markdown(f"**Company:** {job.get('company','')}")
                        st.markdown(f"**Location:** {job.get('location','')}")
                        if job.get("salary_min"):
                            st.markdown(f"**Salary:** ${job.get('salary_min',0):,.0f} – ${job.get('salary_max',0):,.0f}")
                        if job.get("url"):
                            st.markdown(f"[🔗 View Job Posting]({job.get('url')})")

                        st.markdown("**Why you're a good fit:**")
                        for reason in job.get("top_3_reasons", []):
                            st.markdown(f"✅ {reason}")

                    with col_r:
                        st.markdown("**Gaps to address:**")
                        for gap in job.get("top_3_gaps", []):
                            st.markdown(f"⚠️ {gap}")

                        if st.button(f"Deep analyze this JD", key=f"deep_{i}"):
                            with st.spinner("Running deep gap analysis..."):
                                deep = analyze_jd_gaps(
                                    resume_text,
                                    job.get("description", ""),
                                    job.get("title", ""),
                                    job.get("company", ""),
                                )
                            st.session_state[f"deep_result_{i}"] = deep

                    deep_result = st.session_state.get(f"deep_result_{i}")
                    if deep_result and "error" not in deep_result:
                        st.divider()
                        st.markdown("**🔑 ATS Keywords — Present:**")
                        present_html = "".join([f'<span class="keyword-pill keyword-present">{k}</span>' for k in deep_result.get("ats_keywords_present", [])])
                        st.markdown(present_html, unsafe_allow_html=True)

                        st.markdown("**🔑 ATS Keywords — Missing:**")
                        missing_html = "".join([f'<span class="keyword-pill keyword-missing">{k}</span>' for k in deep_result.get("ats_keywords_missing", [])])
                        st.markdown(missing_html, unsafe_allow_html=True)

                        st.markdown("**⚡ Quick Wins:**")
                        for qw in deep_result.get("quick_wins", []):
                            st.success(qw)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYZE JD URL
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔗 Analyze Any Job Posting URL")
    st.caption("Drop any job link — get a focused gap analysis against your resume")

    jd_url_input = st.text_input(
        "Job Posting URL",
        placeholder="https://www.linkedin.com/jobs/view/... or any job board URL",
        key="jd_url_tab3"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        fetch_btn = st.button("🔗 Fetch & Analyze", type="primary",
                              disabled=not (resume_text and gemini_key and jd_url_input))

    if fetch_btn:
        if not resume_text:
            st.warning("Upload your resume first.")
        elif not gemini_key:
            st.warning("Add Gemini API key in sidebar.")
        else:
            with st.spinner("Fetching job description..."):
                jd_scraped = scrape_jd_from_url(jd_url_input)

            if jd_scraped.startswith("ERROR"):
                st.error(f"{jd_scraped}")
                st.info("💡 Try copying and pasting the JD text in Tab 1 instead.")
            else:
                st.success(f"Fetched {len(jd_scraped)} characters from the job posting.")

                with st.expander("Preview fetched JD"):
                    st.text(jd_scraped[:600] + "...")

                with st.spinner("Running gap analysis..."):
                    result = analyze_jd_gaps(resume_text, jd_scraped)

                if "error" in result:
                    st.error(result.get("raw", result["error"]))
                else:
                    score = result.get("match_score", 0)
                    score_emoji = "🟢" if score >= 70 else "🟡" if score >= 45 else "🔴"

                    st.markdown(f"## {score_emoji} Match Score: {score}/100")
                    st.info(result.get("summary", ""))

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("### ✅ Keywords You Already Have")
                        present_html = "".join([f'<span class="keyword-pill keyword-present">{k}</span>'
                                                for k in result.get("ats_keywords_present", [])])
                        st.markdown(present_html or "_None detected_", unsafe_allow_html=True)

                        st.markdown("### 💼 Experience Gaps")
                        for eg in result.get("experience_gaps", []):
                            st.warning(eg)

                    with col_b:
                        st.markdown("### ❌ Missing Keywords (Add to Resume)")
                        missing_html = "".join([f'<span class="keyword-pill keyword-missing">{k}</span>'
                                                for k in result.get("ats_keywords_missing", [])])
                        st.markdown(missing_html or "_None detected_", unsafe_allow_html=True)

                        st.markdown("### 🎯 Skill Gaps")
                        for sg in result.get("skill_gaps", []):
                            icon = "🔴" if sg.get("importance") == "must-have" else "🟡"
                            with st.container():
                                st.markdown(f"{icon} **{sg.get('skill','')}** _{sg.get('importance','')}_")
                                st.caption(f"How to close: {sg.get('how_to_close','')}")

                    st.markdown("### ⚡ Quick Wins — Do These Today")
                    for i, qw in enumerate(result.get("quick_wins", []), 1):
                        st.success(f"**{i}.** {qw}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built with Gemini 1.5 Pro · Adzuna Jobs API · Streamlit · ChromaDB")
