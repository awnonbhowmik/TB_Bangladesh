"""Sheet 1: WHO TB Burden Estimates (incidence, mortality, CDR, CFR, TB-HIV)."""

from openpyxl.workbook import Workbook

from src.styles import autofit, safe, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "Est. Incidence\n(number)", "Inc. Low\n(95% CI)", "Inc. High\n(95% CI)",
    "Incidence Rate\n(per 100k)", "Rate Low", "Rate High",
    "Est. Deaths\n(HIV-neg)", "Deaths Low", "Deaths High",
    "Mortality Rate\n(per 100k)", "Mort. Low", "Mort. High",
    "TB-HIV Inc.\n(number)", "TB-HIV Rate\n(per 100k)",
    "Case Detection\nRate (%)", "Case Fatality\nRate (%)",
]

NOTE = (
    "Source: WHO Global TB Programme burden estimates — "
    "https://extranet.who.int/tme/generateCSV.asp?ds=estimates | "
    "CDR = Case Detection Rate (notified/estimated×100). "
    "CFR = Case Fatality Rate. CI = 95% confidence interval."
)


def build(wb: Workbook, estimates: dict[str, dict], years: list[str]) -> None:
    ws = wb.create_sheet("1. TB Burden Estimates")
    ws.sheet_properties.tabColor = "1F4E79"
    write_headers(ws, HEADERS, "blue")

    for i, yr in enumerate(years):
        e = estimates.get(yr, {})
        row = i + 2
        write_data(ws, row, 1,  yr,                              i, bold=True, align="center")
        write_data(ws, row, 2,  safe(e, "e_inc_num", int),       i, num_format="#,##0")
        write_data(ws, row, 3,  safe(e, "e_inc_num_lo", int),    i, num_format="#,##0")
        write_data(ws, row, 4,  safe(e, "e_inc_num_hi", int),    i, num_format="#,##0")
        write_data(ws, row, 5,  safe(e, "e_inc_100k"),           i, num_format="0")
        write_data(ws, row, 6,  safe(e, "e_inc_100k_lo"),        i, num_format="0")
        write_data(ws, row, 7,  safe(e, "e_inc_100k_hi"),        i, num_format="0")
        write_data(ws, row, 8,  safe(e, "e_mort_num", int),      i, num_format="#,##0")
        write_data(ws, row, 9,  safe(e, "e_mort_num_lo", int),   i, num_format="#,##0")
        write_data(ws, row, 10, safe(e, "e_mort_num_hi", int),   i, num_format="#,##0")
        write_data(ws, row, 11, safe(e, "e_mort_100k"),          i, num_format="0.0")
        write_data(ws, row, 12, safe(e, "e_mort_100k_lo"),       i, num_format="0.0")
        write_data(ws, row, 13, safe(e, "e_mort_100k_hi"),       i, num_format="0.0")
        write_data(ws, row, 14, safe(e, "e_inc_tbhiv_num", int), i, num_format="#,##0")
        write_data(ws, row, 15, safe(e, "e_inc_tbhiv_100k"),     i, num_format="0.00")
        write_data(ws, row, 16, safe(e, "c_cdr"),                i, num_format="0")
        write_data(ws, row, 17, safe(e, "cfr_pct"),              i, num_format="0")

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS), NOTE)
    autofit(ws)
