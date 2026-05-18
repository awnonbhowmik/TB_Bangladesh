"""Orchestrates fetching, building, and saving the TB Bangladesh Excel workbook."""

from pathlib import Path

import openpyxl

from src.builders import (
    burden,
    demographics,
    division,
    environmental,
    figures,
    hivtb,
    latex_tables,
    maps,
    notifications,
    outcomes,
    risk_factors,
    socioeconomic,
    sources,
)
from src.fetchers import climate, local, who, worldbank

YEARS = [str(y) for y in range(2000, 2025)]
OUTPUT     = Path(__file__).parent.parent / "data" / "TB_Bangladesh_Review_Data.xlsx"
FIGS_DIR   = Path(__file__).parent.parent / "outputs" / "figures"
MAPS_DIR   = Path(__file__).parent.parent / "outputs" / "maps"
LATEX_DIR  = Path(__file__).parent.parent / "outputs" / "latex"


def fetch_all() -> tuple[dict, dict, dict, dict, dict]:
    print("  Fetching WHO burden estimates...")
    estimates = who.fetch_estimates()
    print("  Fetching WHO case notifications...")
    notifs = who.fetch_notifications()
    print("  Fetching WHO treatment outcomes...")
    outc = who.fetch_outcomes()
    print("  Fetching World Bank indicators...")
    wb_data = worldbank.fetch_all()
    print("  Fetching climate data (ERA5 + World Bank PM2.5)...")
    climate_data = climate.fetch_all()
    return estimates, notifs, outc, wb_data, climate_data


def build(estimates: dict, notifs: dict, outc: dict, wb_data: dict,
          climate_data: dict) -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default blank sheet

    print("  Building Sheet 1: TB Burden Estimates")
    burden.build(wb, estimates, YEARS)

    print("  Building Sheet 2: Notifications & Performance")
    notifications.build(wb, notifs, estimates, outc, YEARS)

    print("  Building Sheet 3: Treatment Outcomes")
    outcomes.build(wb, outc)

    print("  Building Sheet 4: HIV-TB Co-infection")
    hivtb.build(wb, notifs, estimates, YEARS)

    print("  Building Sheet 5: Sex & Age Distribution")
    demographics.build(wb, notifs, YEARS)

    print("  Building Sheet 6: Division-wise Annual Incidence")
    division.build_annual(wb)

    print("  Building Sheet 7: Division Cumulative Summary")
    division.build_cumulative(wb)

    print("  Building Sheet 8: Socioeconomic Indicators")
    socioeconomic.build(wb, wb_data, YEARS)

    print("  Building Sheet 9: Environmental Factors")
    environmental.build(wb, YEARS, climate_data)

    print("  Building Sheet 11: Risk Factors")
    risk_factors.build(wb, wb_data, YEARS)

    print("  Building Sheet 10: Data Sources")
    sources.build(wb)

    return wb


def build_figures(estimates: dict, notifs: dict, outc: dict,
                  climate_data: dict, wb_data: dict) -> None:
    print("Building figures (seaborn)...")
    figures.build_all(estimates, notifs, outc, climate_data, FIGS_DIR, wb_data)
    print(f"  Figures → {FIGS_DIR}/")


def build_maps(estimates: dict) -> None:
    print("Building maps (geopandas)...")
    maps.build_all(estimates, MAPS_DIR)
    print(f"  Maps    → {MAPS_DIR}/")


def build_latex(estimates: dict, notifs: dict, outc: dict, wb_data: dict,
                climate_data: dict | None = None) -> None:
    print("Building LaTeX tables...")
    latex_tables.build_all(estimates, notifs, outc, wb_data, LATEX_DIR, climate_data)
    print(f"  LaTeX   → {LATEX_DIR}/")


def run() -> Path:
    print("Fetching data...")
    estimates, notifs, outc, wb_data, climate_data = fetch_all()

    print("Building workbook...")
    wb = build(estimates, notifs, outc, wb_data, climate_data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    print(f"Saved → {OUTPUT}")

    build_figures(estimates, notifs, outc, climate_data, wb_data)
    build_maps(estimates)
    build_latex(estimates, notifs, outc, wb_data, climate_data)

    return OUTPUT
