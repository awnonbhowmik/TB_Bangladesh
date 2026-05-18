"""Fetch TB data from WHO Global TB Programme extranet CSV endpoints."""

import csv
import io
import requests

_BASE = "https://extranet.who.int/tme/generateCSV.asp"
_HEADERS = {"User-Agent": "TB-Bangladesh-Review/0.1"}
_TIMEOUT = 90


def _fetch(dataset: str) -> dict[str, dict]:
    """Download a WHO TB CSV and return {year: row_dict} for Bangladesh (iso2=BD)."""
    url = f"{_BASE}?ds={dataset}"
    resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return {row["year"]: row for row in reader if row.get("iso2") == "BD"}


def fetch_estimates() -> dict[str, dict]:
    """WHO burden estimates: incidence, mortality, CDR, CFR, TB-HIV (2000–2024)."""
    return _fetch("estimates")


def fetch_notifications() -> dict[str, dict]:
    """WHO case notifications: case types, sex/age, MDR-TB, HIV-TB (2000–2024)."""
    return _fetch("notifications")


def fetch_outcomes() -> dict[str, dict]:
    """WHO treatment outcomes: TSR, deaths, failures, MDR/XDR-TB (1994–2023)."""
    return _fetch("outcomes")
