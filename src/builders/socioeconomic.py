"""Sheet 8: Socioeconomic Indicators (World Bank + UNDP HDI)."""

from openpyxl.workbook import Workbook

from src.fetchers.local import (
    HDI,
    POPULATION_WORLDOMETER,
    POVERTY_INTERPOLATED,
    POVERTY_SURVEY_YEARS,
)
from src.styles import autofit, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "GDP per Capita\n(USD)", "GNI per Capita\n(USD)", "Human Dev.\nIndex (HDI)",
    "Poverty Rate\n(% <$2.15/day)\n★=survey year",
    "Total\nPopulation", "Urban Pop\n(n)", "Rural Pop\n(n)", "Pop. Density\n(per km²)",
    "Health Exp.\nper Capita (USD)", "BCG Immun.\n(% of infants)",
]

NOTE = (
    "Sources: World Bank Open Data — GDP (NY.GDP.PCAP.CD), GNI (NY.GNP.PCAP.CD), "
    "Health Exp (SH.XPD.CHEX.PC.CD), BCG (SH.IMM.IBCG). "
    "HDI from UNDP Human Development Reports (Bangladesh). "
    "Poverty rate (SI.POV.DDAY, $2.15/day international line): survey years 2000, 2005, 2010, 2016, 2022 "
    "from World Bank; non-survey years linearly interpolated (yellow); 2023–2024 held at 2022 value. "
    "Population, Urban Pop, Rural Pop, Population Density: Worldometer Bangladesh "
    "(via DENV-Data-Analysis, github.com/awnonbhowmik/DENV-Data-Analysis); "
    "2000 estimated by back-extrapolation. "
    "Health expenditure 2024: not yet reported by World Bank."
)


def build(wb: Workbook, wb_data: dict[str, dict[str, float]], years: list[str]) -> None:
    ws = wb.create_sheet("8. Socioeconomic Indicators")
    ws.sheet_properties.tabColor = "833C00"
    write_headers(ws, HEADERS, "red")

    for i, yr in enumerate(years):
        y = int(yr)
        pop_row   = POPULATION_WORLDOMETER.get(y)
        total_pop = pop_row[0] if pop_row else None
        upop      = pop_row[1] if pop_row else None
        rpop      = pop_row[2] if pop_row else None
        density   = pop_row[3] if pop_row else None

        pov_survey = y in POVERTY_SURVEY_YEARS
        pov_val    = wb_data["poverty_rate"].get(yr) if pov_survey else POVERTY_INTERPOLATED.get(y)

        hexp      = wb_data["health_exp_per_capita"].get(yr)
        row = i + 2

        write_data(ws, row, 1,  yr,        i, bold=True, align="center")
        write_data(ws, row, 2,  wb_data["gdp_per_capita"].get(yr), i, num_format="#,##0.0")
        write_data(ws, row, 3,  wb_data["gni_per_capita"].get(yr), i, num_format="#,##0")
        write_data(ws, row, 4,  HDI.get(y),                        i, num_format="0.000")
        write_data(ws, row, 5,  pov_val,   i, num_format="0.0",    warn=not pov_survey)
        write_data(ws, row, 6,  total_pop, i, num_format="#,##0")
        write_data(ws, row, 7,  upop,      i, num_format="#,##0")
        write_data(ws, row, 8,  rpop,      i, num_format="#,##0")
        write_data(ws, row, 9,  density,   i, num_format="#,##0")
        write_data(ws, row, 10, hexp,      i, num_format="#,##0.0", warn=hexp is None)
        write_data(ws, row, 11, wb_data["bcg_immunisation"].get(yr), i, num_format="0")

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS) + 1, NOTE)
    autofit(ws)
