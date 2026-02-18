"""Data loading and computation utilities for AISESA Energy Models Africa."""

import re
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent / "data"

# ISO alpha-2 → ISO alpha-3 mapping for African countries (for Plotly choropleth)
ISO2_TO_ISO3 = {
    "DZ": "DZA", "AO": "AGO", "BJ": "BEN", "BW": "BWA", "BF": "BFA",
    "BI": "BDI", "CV": "CPV", "CM": "CMR", "CF": "CAF", "TD": "TCD",
    "KM": "COM", "CD": "COD", "CG": "COG", "DJ": "DJI", "EG": "EGY",
    "GQ": "GNQ", "ER": "ERI", "SZ": "SWZ", "ET": "ETH", "GA": "GAB",
    "GM": "GMB", "GH": "GHA", "GN": "GIN", "GW": "GNB", "CI": "CIV",
    "KE": "KEN", "LS": "LSO", "LR": "LBR", "LY": "LBY", "MG": "MDG",
    "MW": "MWI", "ML": "MLI", "MR": "MRT", "MU": "MUS", "MA": "MAR",
    "MZ": "MOZ", "NA": "NAM", "NE": "NER", "NG": "NGA", "RW": "RWA",
    "ST": "STP", "SN": "SEN", "SC": "SYC", "SL": "SLE", "SO": "SOM",
    "ZA": "ZAF", "SS": "SSD", "SD": "SDN", "TZ": "TZA", "TG": "TGO",
    "TN": "TUN", "UG": "UGA", "ZM": "ZMB", "ZW": "ZWE", "RE": "REU",
}


@pd.api.extensions.register_dataframe_accessor("_")
class _Dummy:
    pass


def load_countries() -> pd.DataFrame:
    df = pd.read_csv(
        BASE / "countries.csv",
        sep=";",
        encoding="latin-1",
        keep_default_na=False,
    )
    # Fix decimal comma → dot
    df["electrification_rate"] = (
        df["electrification_rate"].astype(str).str.replace(",", ".").astype(float)
    )
    df["iso3"] = df["iso_code"].map(ISO2_TO_ISO3)
    return df


def load_studies() -> pd.DataFrame:
    df = pd.read_csv(
        BASE / "studies.csv",
        sep=";",
        encoding="latin-1",
        keep_default_na=False,
    )
    # Drop unnamed columns
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    # Drop empty rows
    df = df[df["id"].astype(str).str.strip() != ""]
    df["id"] = df["id"].astype(str).str.split(".").str[0].astype(int)
    df["year"] = pd.to_numeric(df["year"].astype(str).str.split(".").str[0], errors="coerce")
    return df


def load_tools() -> pd.DataFrame:
    df = pd.read_csv(
        BASE / "tools.csv",
        sep=";",
        encoding="latin-1",
        keep_default_na=False,
    )
    df["cost_usd"] = (
        df["cost_usd"].astype(str).str.replace("?", "").str.replace(",", "").str.strip()
    )
    df["cost_usd"] = pd.to_numeric(df["cost_usd"], errors="coerce").fillna(0)
    df["nb_studies_in_inventory"] = pd.to_numeric(df["nb_studies_in_inventory"], errors="coerce").fillna(0)
    return df


def load_power_pools() -> pd.DataFrame:
    return pd.read_csv(
        BASE / "power_pools.csv",
        sep=";",
        encoding="latin-1",
        keep_default_na=False,
    )


def get_country_studies(studies: pd.DataFrame, iso: str) -> pd.DataFrame:
    """Return studies that cover a given ISO-2 country code."""
    pattern = r"\b" + re.escape(iso) + r"\b"
    mask = studies["countries"].str.contains(pattern, regex=True, na=False)
    return studies[mask].copy()


def compute_gap_score(row) -> float:
    """
    Gap score 0–100, higher = more under-served.
    Components:
      - African feature coverage (40%)
      - Institutional capacity (30%)
      - Data availability (20%)
      - Model density (10%)
    """
    cap_map = {"yes": 2, "partial": 1, "no": 0}
    dat_map = {"good": 2, "moderate": 1, "poor": 0}
    feat = row.get("feature_ratio", 0)
    cap = cap_map.get(str(row.get("has_institutional_capacity", "no")), 0)
    dat = dat_map.get(str(row.get("data_availability", "poor")), 0)
    n = min(row.get("nb_models_applied", 0), 10)
    return round(
        (1 - feat) * 40
        + (1 - cap / 2) * 30
        + (1 - dat / 2) * 20
        + (1 - n / 10) * 10
    )


def compute_readiness(row) -> float:
    cap_pts = {"yes": 3, "partial": 1.5, "no": 0}.get(str(row.get("has_institutional_capacity", "no")), 0)
    dat_pts = {"good": 3, "moderate": 1.5, "poor": 0}.get(str(row.get("data_availability", "poor")), 0)
    ndc_pt = 1 if str(row.get("has_ndc", "no")) == "yes" else 0
    lts_pt = 1 if str(row.get("has_lts", "no")) == "yes" else 0
    elec_pts = min(float(row.get("electrification_rate", 0)) / 100 * 2, 2)
    return round(cap_pts + dat_pts + ndc_pt + lts_pt + elec_pts, 1)


def enrich_countries(countries: pd.DataFrame, studies: pd.DataFrame) -> pd.DataFrame:
    """Add gap score, readiness, and African feature ratios to countries dataframe."""
    rows = []
    for _, c in countries.iterrows():
        iso = c["iso_code"]
        cs = get_country_studies(studies, iso)
        n = len(cs)
        feats = 0
        if n > 0:
            feats = sum([
                cs["informal_economy"].eq("yes").any(),
                cs["biomass_charcoal"].eq("yes").any(),
                cs["power_reliability"].eq("yes").any(),
                cs["urbanization"].eq("yes").any(),
            ]) / 4
        row = c.to_dict()
        row["n_studies_actual"] = n
        row["feature_ratio"] = feats
        row["gap_score"] = compute_gap_score({**row})
        row["readiness_score"] = compute_readiness(row)
        rows.append(row)
    return pd.DataFrame(rows)
