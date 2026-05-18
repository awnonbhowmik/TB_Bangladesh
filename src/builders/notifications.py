"""Sheet 2: Case Notifications & Program Performance."""

from openpyxl.workbook import Workbook

from src.styles import autofit, safe, write_data, write_headers, write_note

HEADERS = [
    "Year",
    "Total Notified\n(new+relapse)", "New\nSmear-Pos", "New\nSmear-Neg",
    "Extra-\npulmonary", "Confirmed\nRR/MDR-TB", "RR/MDR-TB\nStarted Tx",
    "Case Detection\nRate (%)", "TSR – New\n(%)", "TSR –\nRetreatment (%)",
]

NOTE = (
    "Source: WHO notifications & outcomes CSVs. "
    "Smear-pos/neg reporting discontinued after 2011 (shifted to GeneXpert-based definitions). "
    "TSR = Treatment Success Rate (%). CDR = notified/estimated×100."
)


def build(
    wb: Workbook,
    notifications: dict[str, dict],
    estimates: dict[str, dict],
    outcomes: dict[str, dict],
    years: list[str],
) -> None:
    ws = wb.create_sheet("2. Notifications & Performance")
    ws.sheet_properties.tabColor = "2E75B6"
    write_headers(ws, HEADERS, "teal")

    for i, yr in enumerate(years):
        n = notifications.get(yr, {})
        e = estimates.get(yr, {})
        o = outcomes.get(yr, {})
        row = i + 2
        write_data(ws, row, 1,  yr,                          i, bold=True, align="center")
        write_data(ws, row, 2,  safe(n, "c_newinc", int),    i, num_format="#,##0")
        write_data(ws, row, 3,  safe(n, "new_sp", int),      i, num_format="#,##0")
        write_data(ws, row, 4,  safe(n, "new_sn", int),      i, num_format="#,##0")
        write_data(ws, row, 5,  safe(n, "new_ep", int),      i, num_format="#,##0")
        write_data(ws, row, 6,  safe(n, "conf_rrmdr", int),  i, num_format="#,##0")
        write_data(ws, row, 7,  safe(n, "conf_rrmdr_tx", int), i, num_format="#,##0")
        write_data(ws, row, 8,  safe(e, "c_cdr"),            i, num_format="0")
        write_data(ws, row, 9,  safe(o, "c_new_tsr"),        i, num_format="0")
        write_data(ws, row, 10, safe(o, "c_ret_tsr"),        i, num_format="0")

    ws.freeze_panes = "B2"
    write_note(ws, len(years) + 3, 1, len(HEADERS), NOTE)
    autofit(ws)
