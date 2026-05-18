"""Sheet 5: Sex & Age Distribution (available from 2012 onward)."""

from openpyxl.workbook import Workbook

from src.styles import autofit, safe, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "Male 0–14\n(cases)", "Male 15+\n(cases)", "Male Total", "Male %",
    "Female 0–14\n(cases)", "Female 15+\n(cases)", "Female Total", "Female %",
    "Children 0–14\n(total)", "Children %", "Total\nNotified",
]

NOTE = (
    "Source: WHO notifications CSV (newrel_m014, newrel_m15plus, newrel_f014, newrel_f15plus). "
    "Sex/age disaggregated data available from 2012 onward, when Bangladesh shifted to combined "
    "new+relapse reporting. Bangladesh consistently shows ~57–60% male predominance."
)


def build(wb: Workbook, notifications: dict[str, dict], years: list[str]) -> None:
    ws = wb.create_sheet("5. Sex & Age Distribution")
    ws.sheet_properties.tabColor = "C55A11"
    write_headers(ws, HEADERS, "orange")

    data_row = 2
    for i, yr in enumerate(years):
        n = notifications.get(yr, {})
        m014 = safe(n, "newrel_m014",    int)
        m15p = safe(n, "newrel_m15plus", int)
        f014 = safe(n, "newrel_f014",    int)
        f15p = safe(n, "newrel_f15plus", int)

        if m014 is None and m15p is None:
            continue  # no sex/age data for this year

        m_tot = (m014 or 0) + (m15p or 0)
        f_tot = (f014 or 0) + (f15p or 0)
        total = m_tot + f_tot
        ch014 = (m014 or 0) + (f014 or 0)

        write_data(ws, data_row, 1,  yr,                                          i, bold=True, align="center")
        write_data(ws, data_row, 2,  m014,                                        i, num_format="#,##0")
        write_data(ws, data_row, 3,  m15p,                                        i, num_format="#,##0")
        write_data(ws, data_row, 4,  m_tot,                                       i, num_format="#,##0")
        write_data(ws, data_row, 5,  round(m_tot / total * 100, 1) if total else None, i, num_format="0.0")
        write_data(ws, data_row, 6,  f014,                                        i, num_format="#,##0")
        write_data(ws, data_row, 7,  f15p,                                        i, num_format="#,##0")
        write_data(ws, data_row, 8,  f_tot,                                       i, num_format="#,##0")
        write_data(ws, data_row, 9,  round(f_tot / total * 100, 1) if total else None, i, num_format="0.0")
        write_data(ws, data_row, 10, ch014,                                       i, num_format="#,##0")
        write_data(ws, data_row, 11, round(ch014 / total * 100, 1) if total else None, i, num_format="0.0")
        write_data(ws, data_row, 12, total,                                       i, num_format="#,##0")
        data_row += 1

    ws.freeze_panes = "B2"
    write_note(ws, data_row + 1, 1, len(HEADERS), NOTE)
    autofit(ws)
