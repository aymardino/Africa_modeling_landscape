"""Shared UI components: sidebar CSS, theming, common widgets."""

# Sidebar colour: dark slate-teal — readable, less visually heavy than pure dark green
SIDEBAR_CSS = """
<style>
  [data-testid="stSidebarContent"] {
    background: #2f7314 !important;
  }
  /* All text in sidebar */
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarContent"] p,
  [data-testid="stSidebarContent"] span,
  [data-testid="stSidebarContent"] div,
  [data-testid="stSidebarContent"] label {
    color: #D4E8D0 !important;
    font-size: 0.95rem !important;
  }
  /* Page navigation links */
  [data-testid="stSidebarNav"] a span {
    color: #ffffff !important;
    font-size: 0.98rem;
  }
  [data-testid="stSidebarNav"] a:hover span {
    color: #ffffff !important;
  }
  [data-testid="stSidebarNav"] [aria-current="page"] span {
    color: #ffffff !important;
    font-weight: 700;
  }
  /* Sidebar selectbox / input borders */
  [data-testid="stSidebarContent"] .stSelectbox > div > div {
    background: #3A5C4E !important;
    border-color: #4A7A62 !important;
    color: #D4E8D0 !important;
  }
  [data-testid="stSidebarContent"] .stMultiSelect > div {
    background: #3A5C4E !important;
  }
  /* Sidebar divider */
  [data-testid="stSidebarContent"] hr {
    border-color: #4A7A62 !important;
  }
  /* Sidebar metric */
  [data-testid="stSidebarContent"] [data-testid="stMetric"] label {
    color: #D4E8D0 !important;
    font-size: 0.82rem !important;
  }
  [data-testid="stSidebarContent"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #D4E8D0 !important;
    font-size: 1.3rem !important;
  }
  /* Global typography */
  h1, h2, h3 { font-family: Georgia, serif !important; }
  /* Reduce top padding */
  .block-container { padding-top: 2.5rem !important; }
</style>
"""
