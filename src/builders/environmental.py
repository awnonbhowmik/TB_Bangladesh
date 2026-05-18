"""Sheet 9: Environmental Factors (temperature, humidity, PM2.5)."""

from openpyxl.workbook import Workbook

from src.fetchers.local import (
    HUMIDITY,
    HUMIDITY_MODELED_BEFORE,
    MEAN_TEMP,
    PM25_WHO_LIMIT,
)
from src.styles import autofit, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "Mean Annual\nTemp (°C)\nBMD", "Relative\nHumidity (%)\nBMD",
    "PM2.5 – National\n(µg/m³)\nWorld Bank",
    "WHO PM2.5\nLimit (µg/m³)",
]

NOTE = (
    "Temperature and Humidity: Bangladesh Meteorological Department (BMD) Dhaka station "
    "annual records (Dry Bulb Temperature, Relative Humidity), sourced from "
    "DENV-Data-Analysis (github.com/awnonbhowmik/DENV-Data-Analysis). "
    "2000 values are estimated from adjacent years. "
    "PM2.5 2000–2020: World Bank indicator EN.ATM.PM25.MC.M3 (national population-weighted). "
    "PM2.5 2021–2023: WHO SDG indicator SDGPM25 (national total, WHO GHO API). "
    "PM2.5 2024: CAMS reanalysis via Open-Meteo air-quality API (hourly → annual mean). "
    "Yellow = no data. "
    "WHO PM2.5 safe limit revised from 10 to 5 µg/m³ in the 2021 guidelines."
)


def build(wb: Workbook, years: list[str], climate_data: dict) -> None:
    ws = wb.create_sheet("9. Environmental Factors")
    ws.sheet_properties.tabColor = "7030A0"
    write_headers(ws, HEADERS, "purple")

    real_pm25  = climate_data.get("pm25_national", {})

    for i, yr in enumerate(years):
        y = int(yr)
        modeled_hum  = y < HUMIDITY_MODELED_BEFORE
        # BMD station data is the primary source; ERA5 grid mean is not used
        temp_val     = MEAN_TEMP.get(y)
        temp_modeled = temp_val is None

        pm25_val     = real_pm25.get(y)
        pm25_missing = pm25_val is None
        row = i + 2

        write_data(ws, row, 1, yr,                        i, bold=True, align="center")
        write_data(ws, row, 2, temp_val,                  i, num_format="0.00", warn=temp_modeled)
        write_data(ws, row, 3, HUMIDITY.get(y),           i, num_format="0.0",  warn=modeled_hum)
        write_data(ws, row, 4, pm25_val,                  i, num_format="0.0",  warn=pm25_missing)
        write_data(ws, row, 5, PM25_WHO_LIMIT.get(y),     i, num_format="0")

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS), NOTE)
    autofit(ws)
