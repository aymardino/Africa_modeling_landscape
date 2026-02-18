"""AISESA Energy Models Africa — Home page."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data import load_countries, load_studies, load_tools, enrich_countries
from utils.ui import SIDEBAR_CSS

st.set_page_config(
    page_title="AISESA | African Energy Modelling Observatory",
    page_icon="assets/aisesa_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.html(SIDEBAR_CSS)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Platform</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:0.82rem; line-height:1.6;'>African Energy Modelling Observatory — inventory of energy modelling studies across 54 countries.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Quick stats</p>",
        unsafe_allow_html=True,
    )
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Countries", "54")
    col_s1.metric("Studies", "66")
    col_s2.metric("Tools", "28")
    col_s2.metric("2010–2025", "period")
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Views</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<ul style='font-size:0.82rem; line-height:2; padding-left:1rem;'>
        <li>🗺 <b>Map</b> — geographic coverage</li>
        <li>📊 <b>Gap Analysis</b> — under-served countries</li>
        <li>📈 <b>Readiness</b> — country readiness scores</li>
        <li>🔍 <b>Browse Studies</b> — filter all 66 studies</li>
        <li>🛠 <b>Recommender</b> — find the right tool</li>
        </ul>""",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.68rem; color:#6A9A82; font-style:italic; line-height:1.5;'>AISESA · MINES Paris-PSL<br/>Research Platform · 2025</p>",
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────────────────
_, col_logo_center, _ = st.columns([1, 1, 1])
with col_logo_center:
    try:
        st.image("assets/aisesa_logo.png", use_container_width=True)
    except Exception:
        pass

st.markdown(
    "<h1 style='text-align:center; font-family:Georgia,serif;'>African Energy Modelling Observatory</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#555; margin-top:-8px;'>A decision-support platform for energy modelling across 54 African countries. "
    "Use the sidebar to navigate between views.</p>",
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    countries = load_countries()
    studies = load_studies()
    tools = load_tools()
    enriched = enrich_countries(countries, studies)
    return enriched, studies, tools


countries, studies, tools = get_data()

st.divider()

# ── About ──────────────────────────────────────────────────────────────────────
st.markdown("### About this platform")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
This inventory covers **67 energy modelling studies** applied to Africa between 2010 and
2025, analysed across 35+ dimensions including:

- Technology coverage (solar, wind, biomass, hydro, nuclear...)
- African-specific features (informal economy, power reliability, urbanization)
- Institutional embedding and usage frequency
- Developer origin and local ownership
- Open-source vs proprietary licensing
- SDG 7 and SDG 13 alignment
""")
with col_b:
    st.markdown("""
**Key findings from the inventory:**

- **45%** of studies are led by non-African institutions
- Only **9%** explicitly model the informal economy
- **85%** are used *ad hoc* rather than for routine policy support
- Continental models dominate, masking national heterogeneity
- Coverage is skewed toward Nigeria, Kenya, South Africa

Use the **Gap Analysis** and **Readiness** views to explore country-level disparities,
or the **Recommender** to match tools to your policy context.
""")

st.divider()
st.markdown("### Navigate")
nav_cols = st.columns(5)
pages = [
    ("🗺 Interactive Map", "Geographic coverage across Africa"),
    ("📊 Gap Analysis", "Under-served countries & missing features"),
    ("📈 Readiness", "Country readiness scores"),
    ("🔍 Browse Studies", "Filter all 66 studies by approach, SDG, technology..."),
    ("🛠 Recommender", "Find the right modelling tool"),
]
for col, (title, desc) in zip(nav_cols, pages):
    with col:
        st.markdown(f"**{title}**")
        st.caption(desc)

st.markdown(
    "<p style='text-align:center; font-size:0.72rem; color:#aaa; margin-top:20px;'>"
    "AISESA &nbsp;·&nbsp; MINES Paris-PSL &nbsp;·&nbsp; Research Platform</p>",
    unsafe_allow_html=True,
)
