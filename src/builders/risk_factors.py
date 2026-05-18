"""Sheet 11: TB Risk Factors (World Bank indicators)."""

from openpyxl.workbook import Workbook

from src.styles import autofit, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "Undernourishment\n(% of pop.)",
    "Child Stunting\n(% under-5)\n★=survey year",
    "Smoking Prevalence\n(% adults)\n★=survey year",
    "Health Exp.\n(% of GDP)",
]

NOTE = (
    "Sources: World Bank Open Data. "
    "Undernourishment: FAO prevalence of undernourishment (SN.ITK.DEFC.ZS), annual 2001–2023. "
    "Child stunting: prevalence of stunting, height-for-age (SH.STA.STNT.ZS), survey years. "
    "Smoking prevalence: age-standardised prevalence of current tobacco smoking, adults ≥15 "
    "(SH.PRV.SMOK), survey years. "
    "Health expenditure as % of GDP: current health expenditure (SH.XPD.CHEX.GD.ZS). "
    "Yellow cells = no data reported for that year."
)

# Survey-based indicators — only specific years have real data
_STUNTING_YEARS  = frozenset({"2000","2001","2002","2003","2004","2005","2006","2007",
                               "2011","2012","2013","2014","2015","2018","2019","2022"})
_SMOKING_YEARS   = frozenset({"2000","2005","2007","2010","2015","2020","2021","2022"})


def build(wb: Workbook, wb_data: dict[str, dict[str, float]], years: list[str]) -> None:
    ws = wb.create_sheet("11. Risk Factors")
    ws.sheet_properties.tabColor = "375623"
    write_headers(ws, HEADERS, "green")

    for i, yr in enumerate(years):
        row = i + 2

        undernut = wb_data["undernourishment"].get(yr)
        stunting = wb_data["child_stunting"].get(yr)
        smoking  = wb_data["smoking_prevalence"].get(yr)
        hexp_gdp = wb_data["health_exp_gdp_pct"].get(yr)

        write_data(ws, row, 1, yr,       i, bold=True, align="center")
        write_data(ws, row, 2, undernut, i, num_format="0.0", warn=undernut is None)
        write_data(ws, row, 3, stunting, i, num_format="0.0", warn=yr not in _STUNTING_YEARS)
        write_data(ws, row, 4, smoking,  i, num_format="0.0", warn=yr not in _SMOKING_YEARS)
        write_data(ws, row, 5, hexp_gdp, i, num_format="0.00", warn=hexp_gdp is None)

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS) + 1, NOTE)
    autofit(ws)
