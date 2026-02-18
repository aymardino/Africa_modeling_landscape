"""Interactive Map page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data import load_countries, load_studies, enrich_countries, get_country_studies
from utils.ui import SIDEBAR_CSS

st.set_page_config(page_title="Map | AISESA", layout="wide", page_icon="assets/aisesa_logo.png")
st.html(SIDEBAR_CSS)

REGION_COLORS = {"north":"#1565C0","west":"#2E7D32","east":"#6A1B9A","central":"#E65100","southern":"#37474F"}
POOL_COLORS   = {"COMELEC":"#0277BD","WAPP":"#2E7D32","EAPP":"#6A1B9A","CAPP":"#BF360C","SAPP":"#37474F"}

@st.cache_data
def get_data():
    c = load_countries()
    s = load_studies()
    return enrich_countries(c, s), s

countries_full, studies = get_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Map filters</p>",
        unsafe_allow_html=True,
    )
    year_range = st.slider("Study year range", 2010, 2025, (2010, 2025))
    scales = st.multiselect(
        "Study scale",
        ["continental", "regional", "national", "subnational"],
        default=[],
        placeholder="All scales",
    )
    approaches = st.multiselect(
        "Modelling approach",
        ["bottom-up", "top-down", "hybrid"],
        default=[],
        placeholder="All approaches",
    )

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Map legend</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:0.78rem; line-height:1.8;'>"
        "🟢 High model coverage<br>"
        "🟡 Medium coverage<br>"
        "🔴 Low / gap countries<br>"
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.68rem; color:#6A9A82; font-style:italic; line-height:1.5;'>AISESA · MINES Paris-PSL<br/>Research Platform · 2025</p>",
        unsafe_allow_html=True,
    )

# ── Filter studies ─────────────────────────────────────────────────────────────
filt = studies[
    studies["year"].between(year_range[0], year_range[1], inclusive="both")
]
if scales:
    filt = filt[filt["scale"].isin(scales)]
if approaches:
    filt = filt[filt["approach"].isin(approaches)]

# Recompute country model counts based on filtered studies
import re
countries = countries_full.copy()
def count_filtered(iso):
    pat = r"\b" + re.escape(iso) + r"\b"
    return filt["countries"].str.contains(pat, regex=True, na=False).sum()
countries["nb_models_applied"] = countries["iso_code"].apply(count_filtered)

st.title("Interactive Map")
st.markdown(
    f"Showing **{len(filt)}** studies ({year_range[0]}–{year_range[1]})"
    + (f" · scale: {', '.join(scales)}" if scales else "")
    + (f" · approach: {', '.join(approaches)}" if approaches else "")
)

mode = st.radio(
    "Map layer",
    ["Model Density", "National Only", "By Region", "By Power Pool", "Gap Score", "Readiness Score"],
    horizontal=True,
    label_visibility="collapsed",
)

def make_choropleth(df, color_col, color_scale, label, color_discrete_map=None):
    hover = {
        "country_name": True, "iso3": False,
        color_col: True, "nb_models_applied": True,
        "electrification_rate": True, "data_availability": True,
        "has_institutional_capacity": True,
    }
    if color_discrete_map:
        fig = px.choropleth(
            df, locations="iso3", color=color_col,
            color_discrete_map=color_discrete_map,
            hover_name="country_name", hover_data=hover, scope="africa",
        )
    else:
        fig = px.choropleth(
            df, locations="iso3", color=color_col,
            color_continuous_scale=color_scale,
            hover_name="country_name", hover_data=hover, scope="africa",
            labels={color_col: label},
        )
    fig.update_geos(
        showframe=False, showcoastlines=True, coastlinecolor="#ccc",
        showland=True, landcolor="#F0F4F0", showocean=True, oceancolor="#E3EEF9",
        showcountries=True, countrycolor="#ccc",
    )
    fig.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, height=500,
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig

if mode == "Model Density":
    fig = make_choropleth(countries, "nb_models_applied", ["#C8E6C9","#1B5E20"], "Studies applied")
    
elif mode == "National Only":
    fig = make_choropleth(countries, "nb_models_national", ["#C8E6C9","#1B5E20"], "National studies")

elif mode == "By Region":
    fig = make_choropleth(countries, "region", None, "Region",
                          color_discrete_map=REGION_COLORS)
elif mode == "By Power Pool":
    fig = make_choropleth(countries, "power_pool", None, "Power Pool",
                          color_discrete_map=POOL_COLORS)
elif mode == "Gap Score":
    fig = make_choropleth(countries, "gap_score", ["#1B5E20","#FDD835","#B71C1C"], "Gap score (0-100)")
else:
    fig = make_choropleth(countries, "readiness_score", ["#B71C1C","#FDD835","#1B5E20"], "Readiness (0-10)")

st.plotly_chart(fig, use_container_width=True)

if mode == "Gap Score":
    st.caption("Gap score 0–100: higher = more under-served (accounts for African feature coverage, institutional capacity, data availability, model density)")

st.divider()

col1, col2 = st.columns(2)

with col1:
    pool_counts = {}
    for _, row in filt.iterrows():
        pools = [p.strip() for p in str(row.get("power_pool","")).split(",") if p.strip()]
        seen = set()
        for pool in pools:
            if pool and pool not in seen:
                pool_counts[pool] = pool_counts.get(pool, 0) + 1
                seen.add(pool)
    pool_agg = pd.DataFrame(list(pool_counts.items()), columns=["Power Pool","Studies"])
    pool_agg = pool_agg[pool_agg["Power Pool"].isin(POOL_COLORS.keys())]
    fig_r = px.bar(
        pool_agg.sort_values("Studies"),
        x="Studies", y="Power Pool", orientation="h",
        color="Power Pool",
        color_discrete_map=POOL_COLORS,
        title="Studies by Power Pool (including continental and regional scale)",
    )
    fig_r.update_layout(showlegend=False, height=260, margin={"t":40,"b":0,"l":0,"r":0})
    st.plotly_chart(fig_r, use_container_width=True)

with col2:
    from utils.data import load_tools
    tools = load_tools()
    model_counts = tools[["tool_name","nb_studies_in_inventory"]].copy()
    model_counts.columns = ["Model","Studies"]
    model_counts = model_counts[model_counts["Studies"] > 0].nlargest(10,"Studies")
    model_counts["Model"] = model_counts["Model"].str.slice(0,22)
    fig_m = px.bar(
        model_counts.sort_values("Studies"),
        x="Studies", y="Model", orientation="h",
        color_discrete_sequence=["#2E7D32"],
        title="Top 10 Most-Applied Models",
    )
    fig_m.update_layout(height=260, margin={"t":40,"b":0,"l":0,"r":0})
    st.plotly_chart(fig_m, use_container_width=True)

st.divider()

st.subheader("Country detail")
selected = st.selectbox(
    "Select a country",
    sorted(countries_full["country_name"].tolist()),
    index=None,
    placeholder="Choose a country..."
)

if selected:
    row = countries_full[countries_full["country_name"]==selected].iloc[0]
    iso = row["iso_code"]
    c_studies = get_country_studies(filt, iso)

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Studies (filtered)", len(c_studies))
    m2.metric("Electrification", f"{row['electrification_rate']}%")
    m3.metric("Gap score", f"{int(row['gap_score'])}/100")
    m4.metric("Readiness", f"{row['readiness_score']}/10")
    m5.metric("Data", row["data_availability"].title())

    info_cols = st.columns(4)
    info_cols[0].caption(f"**Region:** {row['region'].capitalize()}")
    info_cols[1].caption(f"**Power pool:** {row['power_pool']}")
    info_cols[2].caption(f"**NDC:** {'Yes' if row['has_ndc']=='yes' else 'No'}")
    info_cols[3].caption(f"**Long-term strategy:** {'Yes' if row['has_lts']=='yes' else 'No'}")

    if not c_studies.empty:
        st.markdown(f"**{len(c_studies)} studies** cover {selected} in this period:")
        dcols = [c for c in ["model_name","year","scale","approach","method","open_source","frequency","informal_economy","local_ownership","sdg_7","sdg_13"] if c in c_studies.columns]
        st.dataframe(c_studies[dcols].reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("No studies match the current filters for this country.")
