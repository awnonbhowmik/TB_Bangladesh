"""Fetch socioeconomic indicators from the World Bank Open Data API."""

import requests

_BASE = "https://api.worldbank.org/v2/country/BD/indicator"
_HEADERS = {"User-Agent": "TB-Bangladesh-Review/0.1"}
_TIMEOUT = 30

INDICATORS: dict[str, str] = {
    # Socioeconomic
    "gdp_per_capita":       "NY.GDP.PCAP.CD",
    "gni_per_capita":       "NY.GNP.PCAP.CD",
    "poverty_rate":         "SI.POV.DDAY",
    # Health system
    "health_exp_per_capita":"SH.XPD.CHEX.PC.CD",
    "health_exp_gdp_pct":   "SH.XPD.CHEX.GD.ZS",
    "bcg_immunisation":     "SH.IMM.IBCG",
    # Risk factors
    "undernourishment":     "SN.ITK.DEFC.ZS",
    "smoking_prevalence":   "SH.PRV.SMOK",
    "child_stunting":       "SH.STA.STNT.ZS",
}


def _fetch_indicator(code: str) -> dict[str, float]:
    """Return {year_str: value} for a single World Bank indicator (Bangladesh, 2000–2024)."""
    url = f"{_BASE}/{code}?format=json&per_page=100&date=2000:2024"
    resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    return {
        str(item["date"]): item["value"]
        for item in payload[1]
        if item["value"] is not None
    }


def fetch_all() -> dict[str, dict[str, float]]:
    """Return all World Bank indicators as {name: {year: value}}."""
    return {name: _fetch_indicator(code) for name, code in INDICATORS.items()}
