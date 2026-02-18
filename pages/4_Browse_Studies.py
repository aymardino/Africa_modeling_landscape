"""Browse Studies — comprehensive filter & explore page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data import load_studies, load_countries
from utils.ui import SIDEBAR_CSS

st.set_page_config(page_title="Browse Studies | AISESA", layout="wide", page_icon="assets/aisesa_logo.png")
st.html(SIDEBAR_CSS)

@st.cache_data
def get_data():
    return load_studies(), load_countries()

studies, countries = get_data()

# ── Sidebar filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Filters</p>",
        unsafe_allow_html=True,
    )

    year_range = st.slider("Publication year", 2010, 2025, (2010, 2025))

    scale_opts = sorted([s for s in studies["scale"].dropna().unique() if s])
    scales = st.multiselect("Scale", scale_opts, default=[], placeholder="All", label_visibility="visible")

    approach_opts = sorted([a for a in studies["approach"].dropna().unique() if a])
    approaches = st.multiselect("Approach", approach_opts, default=[], placeholder="All")

    method_opts = sorted([m for m in studies["method"].dropna().unique() if m])
    methods = st.multiselect("Method", method_opts, default=[], placeholder="All")

    freq_opts = sorted([f for f in studies["frequency"].dropna().unique() if f])
    freqs = st.multiselect("Usage frequency", freq_opts, default=[], placeholder="All")

    lic_opts = sorted([l for l in studies["open_source"].dropna().unique() if l])
    lics = st.multiselect("License", lic_opts, default=[], placeholder="All")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>African features</p>",
        unsafe_allow_html=True,
    )
    f_informal = st.checkbox("Covers informal economy")
    f_biomass  = st.checkbox("Covers biomass/charcoal")
    f_reliability = st.checkbox("Covers power reliability")
    f_urban    = st.checkbox("Covers urbanization")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>SDG & policy</p>",
        unsafe_allow_html=True,
    )
    f_sdg7  = st.checkbox("SDG 7 aligned")
    f_sdg13 = st.checkbox("SDG 13 aligned")
    f_ndc   = st.checkbox("Mentions NDC")
    f_local = st.checkbox("Local ownership (African-led)")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Technology</p>",
        unsafe_allow_html=True,
    )
    tech_cols = ["solar","wind","hydro","biomass","nuclear","geothermal","fossil","h2","coal"]
    tech_avail = [t for t in tech_cols if t in studies.columns]
    selected_techs = st.multiselect("Must include technology", tech_avail, default=[], placeholder="Any")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.68rem; color:#6A9A82; font-style:italic; line-height:1.5;'>AISESA · MINES Paris-PSL<br/>Research Platform · 2025</p>",
        unsafe_allow_html=True,
    )

# ── Apply filters ───────────────────────────────────────────────────────────────
filt = studies[studies["year"].between(year_range[0], year_range[1], inclusive="both")].copy()
if scales:       filt = filt[filt["scale"].isin(scales)]
if approaches:   filt = filt[filt["approach"].isin(approaches)]
if methods:      filt = filt[filt["method"].isin(methods)]
if freqs:        filt = filt[filt["frequency"].isin(freqs)]
if lics:         filt = filt[filt["open_source"].isin(lics)]
if f_informal:   filt = filt[filt["informal_economy"].eq("yes")]
if f_biomass:    filt = filt[filt["biomass_charcoal"].eq("yes")]
if f_reliability:filt = filt[filt["power_reliability"].eq("yes")]
if f_urban:      filt = filt[filt["urbanization"].eq("yes")]
if f_sdg7 and "sdg_7" in filt.columns:    filt = filt[filt["sdg_7"].eq("yes")]
if f_sdg13 and "sdg_13" in filt.columns:  filt = filt[filt["sdg_13"].eq("yes")]
if f_ndc and "ndc_mention" in filt.columns: filt = filt[filt["ndc_mention"].eq("yes")]
if f_local:      filt = filt[filt["local_ownership"].eq("yes")]
for tech in selected_techs:
    if tech in filt.columns:
        filt = filt[filt[tech].eq("yes")]

# ── Header ──────────────────────────────────────────────────────────────────────
st.title("Browse Studies")
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown(
        f"Showing **{len(filt)}** of **{len(studies)}** studies matching your filters."
    )
with col_h2:
    search_text = st.text_input("Search model / author", placeholder="e.g. LEAP, OSeMOSYS...", label_visibility="collapsed")
if search_text:
    mask = (
        filt["model_name"].str.lower().str.contains(search_text.lower(), na=False) |
        filt["authors"].str.lower().str.contains(search_text.lower(), na=False)
    )
    filt = filt[mask]
    st.caption(f"After text search: {len(filt)} results")

st.divider()

# ── Summary charts ───────────────────────────────────────────────────────────────
if len(filt) > 0:
    chart_cols = st.columns(2)
    chart_cols2 = st.columns(2)

    with chart_cols[0]:
        yr = filt["year"].value_counts().sort_index().reset_index()
        yr.columns = ["Year","Count"]
        fig_yr = px.bar(yr, x="Year", y="Count", color_discrete_sequence=["#2E7D32"],
                        title="By Year", height=180)
        fig_yr.update_layout(margin={"t":40,"b":0,"l":0,"r":0}, showlegend=False,
                             xaxis=dict(tickmode="linear", dtick=5))
        st.plotly_chart(fig_yr, use_container_width=True)

    with chart_cols[1]:
        sc = filt["scale"].replace("","unspecified").value_counts().reset_index()
        sc.columns = ["Scale","Count"]
        fig_sc = px.pie(sc, names="Scale", values="Count", hole=0.4,
                        title="By Scale", height=180,
                        color_discrete_sequence=px.colors.qualitative.Set2)
        fig_sc.update_layout(margin={"t":40,"b":0,"l":0,"r":0},
                             legend=dict(font=dict(size=9)))
        st.plotly_chart(fig_sc, use_container_width=True)

    with chart_cols2[0]:
        ap = filt["approach"].replace("","unspecified").value_counts().reset_index()
        ap.columns = ["Approach","Count"]
        fig_ap = px.pie(ap, names="Approach", values="Count", hole=0.4,
                        title="By Approach", height=180,
                        color_discrete_sequence=["#2E7D32","#1565C0","#E65100","#9E9E9E"])
        fig_ap.update_layout(margin={"t":40,"b":0,"l":0,"r":0},
                             legend=dict(font=dict(size=9)))
        st.plotly_chart(fig_ap, use_container_width=True)

    with chart_cols2[1]:
        freq = filt["frequency"].value_counts().reset_index()
        freq.columns = ["Frequency","Count"]
        freq["Frequency"] = freq["Frequency"].str.replace("_"," ").str.capitalize()
        fig_fr = px.bar(freq, x="Frequency", y="Count", color_discrete_sequence=["#1565C0"],
                        title="By Frequency", height=180, text="Count")
        fig_fr.update_traces(textposition="outside")
        fig_fr.update_layout(margin={"t":40,"b":0,"l":0,"r":0},
                             xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_fr, use_container_width=True)

    # Technology heatmap
    st.markdown("#### Technology coverage in filtered studies")
    tech_avail_full = [t for t in ["solar","wind","hydro","biomass","nuclear","geothermal","fossil","h2","coal"] if t in filt.columns]
    if tech_avail_full:
        tech_pct = {t: round(filt[t].eq("yes").sum()/len(filt)*100,1) for t in tech_avail_full}
        tech_df = pd.DataFrame(list(tech_pct.items()), columns=["Technology","Coverage (%)"])
        tech_df = tech_df.sort_values("Coverage (%)", ascending=True)
        fig_tech = px.bar(
            tech_df, x="Coverage (%)", y="Technology", orientation="h",
            color="Coverage (%)", color_continuous_scale=["#C8E6C9","#1B5E20"],
            text=tech_df["Coverage (%)"].apply(lambda v: f"{v}%"),
            height=280,
        )
        fig_tech.update_traces(textposition="outside")
        fig_tech.update_layout(margin={"t":10,"b":0,"l":0,"r":40},
                               showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_tech, use_container_width=True)

    st.divider()

    # ── Studies table ───────────────────────────────────────────────────────────
    st.markdown("#### Studies table")

    display_cols = [c for c in [
        "id","model_name","authors","year","scale","approach","method",
        "open_source","frequency","informal_economy","biomass_charcoal",
        "power_reliability","urbanization","sdg_7","sdg_13","ndc_mention",
        "local_ownership","developer_origin","countries",
    ] if c in filt.columns]

    rename = {
        "id":"ID","model_name":"Model","authors":"Authors","year":"Year",
        "scale":"Scale","approach":"Approach","method":"Method",
        "open_source":"License","frequency":"Frequency",
        "informal_economy":"Informal Econ.","biomass_charcoal":"Biomass",
        "power_reliability":"Reliability","urbanization":"Urban",
        "sdg_7":"SDG 7","sdg_13":"SDG 13","ndc_mention":"NDC",
        "local_ownership":"Local","developer_origin":"Developer",
        "countries":"Countries",
    }

    disp = filt[display_cols].rename(columns=rename).reset_index(drop=True)
    # Truncate authors and countries for readability
    if "Authors" in disp.columns:
        disp["Authors"] = disp["Authors"].str.slice(0,40)
    if "Countries" in disp.columns:
        disp["Countries"] = disp["Countries"].str.slice(0,60) + "…"

    st.dataframe(
        disp,
        use_container_width=True,
        hide_index=True,
        height=450,
        column_config={
            "Year": st.column_config.NumberColumn(format="%d"),
        },
    )
    st.caption(f"{len(filt)} studies shown. Use sidebar filters to narrow down.")

else:
    st.warning("No studies match the current filters. Try relaxing some constraints.")
