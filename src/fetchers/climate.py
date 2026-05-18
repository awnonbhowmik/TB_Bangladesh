"""PM2.5 data for Bangladesh: World Bank + WHO GHO + CAMS (three-source merge).

Temperature and humidity use BMD Dhaka station records from local.py — no API fetch needed.
"""

from __future__ import annotations

import statistics
import requests

_TIMEOUT = 90
_BD_LAT  = 23.685
_BD_LON  = 90.356


def _fetch_pm25_worldbank() -> dict[int, float]:
    """World Bank EN.ATM.PM25.MC.M3 — national population-weighted mean, available to ~2020."""
    url = (
        "https://api.worldbank.org/v2/country/BD/indicator/EN.ATM.PM25.MC.M3"
        "?format=json&per_page=50&mrv=30"
    )
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        rows = resp.json()[1] or []
        return {
            int(row["date"]): round(row["value"], 1)
            for row in rows
            if row.get("value") is not None
        }
    except Exception:
        return {}


def _fetch_pm25_who_sdg() -> dict[int, float]:
    """
    WHO SDG indicator SDGPM25 — national mean PM2.5 concentration (µg/m³).
    Covers 2010-2023 for Bangladesh, same methodology as World Bank series.
    Used to fill 2021-2023 where World Bank has no data yet.
    """
    url = "https://ghoapi.azureedge.net/api/SDGPM25"
    params = {"$filter": "SpatialDim eq 'BGD' and Dim1 eq 'RESIDENCEAREATYPE_TOTL'"}
    try:
        resp = requests.get(url, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return {
            item["TimeDim"]: round(item["NumericValue"], 1)
            for item in resp.json().get("value", [])
            if item.get("NumericValue") is not None
        }
    except Exception:
        return {}


def _fetch_pm25_cams(start_year: int = 2024, end_year: int = 2024) -> dict[int, float]:
    """
    Annual mean PM2.5 (µg/m³) from CAMS reanalysis via Open-Meteo air-quality API.
    Used only for years not covered by WHO SDG (currently 2024).
    """
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={_BD_LAT}&longitude={_BD_LON}"
        f"&hourly=pm2_5"
        f"&start_date={start_year}-01-01&end_date={end_year}-12-31"
        f"&timezone=Asia%2FDhaka"
    )
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        data  = resp.json()
        times = data["hourly"]["time"]
        vals  = data["hourly"]["pm2_5"]
        by_year: dict[int, list[float]] = {}
        for t, v in zip(times, vals):
            if v is not None:
                by_year.setdefault(int(t[:4]), []).append(v)
        return {yr: round(statistics.mean(v), 1) for yr, v in by_year.items()}
    except Exception:
        return {}


def fetch_pm25() -> dict[int, float]:
    """
    Merged PM2.5 series for Bangladesh:
      2000-2020: World Bank EN.ATM.PM25.MC.M3 (national population-weighted)
      2021-2023: WHO SDG indicator SDGPM25 (RESIDENCEAREATYPE_TOTL)
      2024:      CAMS reanalysis via Open-Meteo (hourly → annual mean)
    Priority: World Bank base, WHO SDG fills/extends, CAMS adds 2024.
    """
    wb  = _fetch_pm25_worldbank()
    who = _fetch_pm25_who_sdg()
    cam = _fetch_pm25_cams()
    # WB is the primary source; WHO SDG fills gaps (2021-2023); CAMS adds 2024
    return {**wb, **who, **cam}


def fetch_all() -> dict[str, dict[int, float]]:
    return {
        "pm25_national": fetch_pm25(),
    }
