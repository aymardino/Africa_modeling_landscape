"""Gap Analysis page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.data import load_countries, load_studies, enrich_countries
from utils.ui import SIDEBAR_CSS

st.set_page_config(page_title="Gap Analysis | AISESA", layout="wide", page_icon="assets/aisesa_logo.png")
st.html(SIDEBAR_CSS)

REGION_COLORS = {"north":"#1565C0","west":"#2E7D32","east":"#6A1B9A","central":"#E65100","southern":"#37474F"}

@st.cache_data
def get_data():
    c = load_countries()
    s = load_studies()
    return enrich_countries(c, s), s

countries, studies = get_data()
n = len(studies)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Gap score explained</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:0.79rem; line-height:1.7;'>"
        "Gap score (0–100):<br>"
        "🔴 <b>African features</b> — 40%<br>"
        "🟠 <b>Institutional capacity</b> — 30%<br>"
        "🟡 <b>Data availability</b> — 20%<br>"
        "🟢 <b>Model density</b> — 10%<br>"
        "Higher = more under-served.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.78rem; color:#8FBCA8; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>Region filter</p>",
        unsafe_allow_html=True,
    )
    region_filter = st.multiselect(
        "Regions",
        sorted(countries["region"].unique().tolist()),
        default=[],
        placeholder="All regions",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.68rem; color:#6A9A82; font-style:italic; line-height:1.5;'>AISESA · MINES Paris-PSL<br/>Research Platform · 2025</p>",
        unsafe_allow_html=True,
    )

if region_filter:
    countries_view = countries[countries["region"].isin(region_filter)]
    studies_view = studies  # gap uses country-level, keep studies full
else:
    countries_view = countries

st.title("Gap Analysis")
st.markdown("Critical gaps in how energy models represent African realities.")

# ── KPIs ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Cover informal economy", f"{round(studies['informal_economy'].eq('yes').sum()/n*100)}%",
          delta=f"{studies['informal_economy'].eq('yes').sum()} of {n} studies", delta_color="off")
k2.metric("Ad hoc / occasional usage",
          f"{round(studies['frequency'].isin(['ad_hoc','occasional']).sum()/n*100)}%",
          delta="not routinely embedded in policy", delta_color="inverse")
k3.metric("No local ownership",
          f"{round(studies['local_ownership'].eq('no').sum()/n*100)}%",
          delta="non-African-led studies", delta_color="inverse")
k4.metric("Average gap score (filtered)",
          f"{int(countries_view['gap_score'].mean())}/100",
          delta="higher = more under-served", delta_color="inverse")

st.divider()

# ── African feature coverage ────────────────────────────────────────────────────
st.subheader("African-specific feature coverage")
st.caption("These four features are critical for realistic African energy modelling yet covered by fewer than 20% of studies.")

features = [
    ("Informal Economy", studies["informal_economy"].eq("yes").sum()),
    ("Biomass / Charcoal", studies["biomass_charcoal"].eq("yes").sum()),
    ("Power Reliability", studies["power_reliability"].eq("yes").sum()),
    ("Urbanization", studies["urbanization"].eq("yes").sum()),
]
feat_df = pd.DataFrame(features, columns=["Feature","Count"])
feat_df["Percentage"] = (feat_df["Count"]/n*100).round(1)
fig_feat = px.bar(feat_df, x="Feature", y="Percentage",
                  color_discrete_sequence=["#C62828"],
                  text=feat_df["Percentage"].apply(lambda v: f"{v}%"),
                  title="% of Studies Covering Each African Feature")
fig_feat.add_hline(y=20, line_dash="dot", line_color="#888", annotation_text="20% threshold")
fig_feat.update_traces(textposition="outside")
fig_feat.update_layout(yaxis=dict(range=[0,40],title="% of studies"), height=300, margin={"t":50,"b":0})
st.plotly_chart(fig_feat, use_container_width=True)

st.divider()

# ── SDG alignment ──────────────────────────────────────────────────────────────
st.subheader("SDG alignment")
col_sdg1, col_sdg2, col_sdg3 = st.columns(3)

with col_sdg1:
    sdg7 = studies["sdg_7"].eq("yes").sum() if "sdg_7" in studies.columns else 0
    sdg13 = studies["sdg_13"].eq("yes").sum() if "sdg_13" in studies.columns else 0
    sdg_df = pd.DataFrame({"SDG": ["SDG 7\n(Clean Energy)", "SDG 13\n(Climate Action)"],
                            "Count": [sdg7, sdg13], "Pct": [round(sdg7/n*100), round(sdg13/n*100)]})
    fig_sdg = px.bar(sdg_df, x="SDG", y="Pct",
                     color_discrete_sequence=["#1565C0"],
                     text=sdg_df["Pct"].apply(lambda v: f"{v}%"),
                     title="SDG 7 & SDG 13 Alignment (%)")
    fig_sdg.update_traces(textposition="outside")
    fig_sdg.update_layout(yaxis=dict(range=[0,110],title="% of studies"), height=240, margin={"t":50,"b":0})
    st.plotly_chart(fig_sdg, use_container_width=True)

with col_sdg2:
    ndc = studies["ndc_mention"].eq("yes").sum() if "ndc_mention" in studies.columns else 0
    ndc_df = pd.DataFrame({"Type": ["Mentions NDC", "No NDC mention"],
                            "Count": [ndc, n - ndc]})
    fig_ndc = px.pie(ndc_df, names="Type", values="Count", hole=0.4,
                     color_discrete_sequence=["#2E7D32","#9E9E9E"],
                     title="NDC Mention in Studies")
    fig_ndc.update_layout(height=240, margin={"t":50,"b":0,"l":0,"r":0},
                          legend=dict(font=dict(size=10)))
    st.plotly_chart(fig_ndc, use_container_width=True)

with col_sdg3:
    if "developer_origin" in studies.columns:
        african_isos = {"DZ","AO","BJ","BW","BF","BI","CV","CM","CF","TD","KM","CD","CG","DJ",
                        "EG","GQ","ER","SZ","ET","GA","GM","GN","GW","CI","KE","LS","LR",
                        "LY","MG","MW","ML","MR","MU","MA","MZ","NA","NE","NG","RW","ST","SN",
                        "SC","SL","SO","ZA","SS","SD","TZ","TG","TN","UG","ZM","ZW"}

        def classify_origin(dev):
            if not dev or str(dev).strip() == "":
                return "Non-African"
            codes = [x.strip()[:2].upper() for x in str(dev).replace(",",";").split(";") if x.strip()]
            has_african = any(c in african_isos for c in codes)
            has_non_african = any(c not in african_isos for c in codes)
            if has_african and has_non_african:
                return "Mixed"
            elif has_african:
                return "African-led"
            else:
                return "Non-African"

        studies["origin_category"] = studies["developer_origin"].apply(classify_origin)
        dev_df = studies["origin_category"].value_counts().reset_index()
        dev_df.columns = ["Origin","Count"]
        fig_dev = px.pie(dev_df, names="Origin", values="Count", hole=0.4,
                         color="Origin",
                         color_discrete_map={
                             "African-led": "#2E7D32",
                             "Non-African": "#9E9E9E",
                             "Mixed": "#1565C0",
                         },
                         title="Developer Origin")
        fig_dev.update_layout(height=240, margin={"t":50,"b":0,"l":0,"r":0},
                              legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_dev, use_container_width=True)

st.divider()

# ── Charts row ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**License type**")
    lic = studies["open_source"].value_counts().reset_index()
    lic.columns = ["License","Count"]
    lic["License"] = lic["License"].replace({"open":"Open source","proprietary":"Proprietary"})
    fig_lic = px.pie(lic, names="License", values="Count",
                     color_discrete_sequence=["#2E7D32","#9E9E9E","#1565C0"], hole=0.4)
    fig_lic.update_layout(height=220, margin={"t":10,"b":10,"l":0,"r":0},
                          legend=dict(font=dict(size=10)))
    st.plotly_chart(fig_lic, use_container_width=True)

with col2:
    st.markdown("**Usage frequency**")
    freq = studies["frequency"].value_counts().reset_index()
    freq.columns = ["Frequency","Count"]
    freq["Frequency"] = freq["Frequency"].str.replace("_"," ").str.capitalize()
    fig_freq = px.bar(freq, x="Frequency", y="Count", color_discrete_sequence=["#2E7D32"], text="Count")
    fig_freq.update_traces(textposition="outside")
    fig_freq.update_layout(height=220, margin={"t":10,"b":10,"l":0,"r":0}, yaxis_title="Studies", xaxis_title="")
    st.plotly_chart(fig_freq, use_container_width=True)

with col3:
    st.markdown("**Scale of studies**")
    scale = studies["scale"].replace("","unspecified").value_counts().reset_index()
    scale.columns = ["Scale","Count"]
    fig_scale = px.bar(scale, x="Scale", y="Count", color_discrete_sequence=["#1565C0"], text="Count")
    fig_scale.update_traces(textposition="outside")
    fig_scale.update_layout(height=220, margin={"t":10,"b":10,"l":0,"r":0}, yaxis_title="Studies", xaxis_title="")
    st.plotly_chart(fig_scale, use_container_width=True)

st.divider()

# ── Gap score map + box ─────────────────────────────────────────────────────────
st.subheader("Gap score by region")
col_map, col_box = st.columns([2,1])

with col_map:
    fig_map = px.choropleth(
        countries_view, locations="iso3", color="gap_score",
        color_continuous_scale=["#1B5E20","#FDD835","#B71C1C"],
        hover_name="country_name",
        hover_data={"gap_score":True,"nb_models_applied":True,"iso3":False},
        scope="africa", labels={"gap_score":"Gap score"},
        title="Gap Score Map (higher = more under-served)",
    )
    fig_map.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#ccc",
                        showland=True, landcolor="#F0F4F0", showocean=True, oceancolor="#E3EEF9",
                        showcountries=True, countrycolor="#ccc")
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=360)
    st.plotly_chart(fig_map, use_container_width=True)

with col_box:
    rg = countries_view.copy()
    rg["Region"] = rg["region"].str.capitalize()
    fig_box = px.box(rg, x="Region", y="gap_score", color="Region",
                     color_discrete_map={r.capitalize():c for r,c in REGION_COLORS.items()},
                     title="Distribution by Region")
    fig_box.update_layout(showlegend=False, height=360, margin={"t":40,"b":0,"l":0,"r":0},
                          yaxis_title="Gap score (0-100)")
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

st.subheader("15 highest-gap countries")
top_gap = countries_view.nlargest(15,"gap_score")[
    ["country_name","region","power_pool","nb_models_applied",
     "gap_score","data_availability","has_institutional_capacity","electrification_rate"]
].copy()
top_gap.columns = ["Country","Region","Power Pool","Studies","Gap Score","Data","Capacity","Electrification (%)"]
top_gap["Region"] = top_gap["Region"].str.capitalize()
st.dataframe(
    top_gap.reset_index(drop=True),
    use_container_width=True, hide_index=True,
    column_config={
        "Gap Score": st.column_config.ProgressColumn("Gap Score", min_value=0, max_value=100, format="%d"),
        "Electrification (%)": st.column_config.NumberColumn(format="%.0f%%"),
    },
)
