"""Sheet 4: HIV-TB Co-infection."""

from openpyxl.workbook import Workbook

from src.styles import autofit, safe, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "TB Patients\nTested for HIV", "HIV-pos\nTB Patients", "HIV+ TB\non ART",
    "HIV+ TB\nPrevalence (%)",
    "Est. TB-HIV\nIncidence (n)", "Est. TB-HIV\nRate (per 100k)",
    "TB-HIV Inc.\nLow (95% CI)", "TB-HIV Inc.\nHigh (95% CI)",
]

NOTE = (
    "Source: WHO notifications (HIV testing reported by NTP) + WHO burden estimates. "
    "Bangladesh HIV prevalence <0.1% — TB-HIV co-infection is among the world's lowest. "
    "HIV testing of TB patients expanded systematically after 2013."
)


def build(
    wb: Workbook,
    notifications: dict[str, dict],
    estimates: dict[str, dict],
    years: list[str],
) -> None:
    ws = wb.create_sheet("4. HIV-TB Co-infection")
    ws.sheet_properties.tabColor = "7030A0"
    write_headers(ws, HEADERS, "purple")

    for i, yr in enumerate(years):
        n = notifications.get(yr, {})
        e = estimates.get(yr, {})
        tested = safe(n, "newrel_hivtest", int)
        hivpos = safe(n, "newrel_hivpos",  int)
        art    = safe(n, "newrel_art",     int)
        pct    = round(hivpos / tested * 100, 2) if tested and hivpos else None
        row = i + 2

        write_data(ws, row, 1, yr,                                  i, bold=True, align="center")
        write_data(ws, row, 2, tested,                              i, num_format="#,##0")
        write_data(ws, row, 3, hivpos,                              i, num_format="#,##0")
        write_data(ws, row, 4, art,                                 i, num_format="#,##0")
        write_data(ws, row, 5, pct,                                 i, num_format="0.00")
        write_data(ws, row, 6, safe(e, "e_inc_tbhiv_num",    int),  i, num_format="#,##0")
        write_data(ws, row, 7, safe(e, "e_inc_tbhiv_100k"),         i, num_format="0.00")
        write_data(ws, row, 8, safe(e, "e_inc_tbhiv_num_lo", int),  i, num_format="#,##0")
        write_data(ws, row, 9, safe(e, "e_inc_tbhiv_num_hi", int),  i, num_format="#,##0")

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS), NOTE)
    autofit(ws)
