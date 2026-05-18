"""Sheet 3: Treatment Outcomes (TSR, deaths, MDR-TB, XDR-TB, HIV-TB)."""

from openpyxl.workbook import Workbook

from src.styles import autofit, safe, write_data, write_headers, write_note

HEADERS = [
    "Year", "Cohort (n)", "Success (n)", "TSR (%)", "Died (n)", "Failed (n)", "Lost (n)",
    "Retreatment\nTSR (%)", "HIV-TB\nCohort", "HIV-TB\nSuccess", "HIV-TB\nTSR (%)",
    "MDR-TB\nCohort", "MDR-TB\nSuccess", "MDR-TB\nTSR (%)", "MDR-TB\nDied", "MDR-TB\nLost",
    "XDR-TB\nCohort", "XDR-TB\nSuccess",
]

NOTE = (
    "Source: WHO outcomes CSV. Outcomes reported with ~2-year lag (cohort year). "
    "Pre-2012: smear-positive cohort used as proxy for total cohort. "
    "TSR = treated successfully / cohort × 100. "
    "2024: data pending WHO Global TB Report 2026."
)


def build(wb: Workbook, outcomes: dict[str, dict]) -> None:
    ws = wb.create_sheet("3. Treatment Outcomes")
    ws.sheet_properties.tabColor = "375623"
    write_headers(ws, HEADERS, "green")

    sorted_years = sorted(outcomes.keys())
    if "2024" not in outcomes:
        sorted_years = sorted_years + ["2024"]

    for i, yr in enumerate(sorted_years):
        o = outcomes.get(yr, {})
        row = i + 2
        # Use newrel (post-2012 combined definition) falling back to smear-positive cohort
        coh  = safe(o, "newrel_coh",  int) or safe(o, "new_sp_coh",  int)
        succ = safe(o, "newrel_succ", int) or safe(o, "new_sp_cur",  int)
        died = safe(o, "newrel_died", int) or safe(o, "new_sp_died", int)
        fail = safe(o, "newrel_fail", int) or safe(o, "new_sp_fail", int)
        lost = safe(o, "newrel_lost", int) or safe(o, "new_sp_def",  int)
        mdr_c = safe(o, "mdr_coh",  int)
        mdr_s = safe(o, "mdr_succ", int)
        mdr_tsr = round(mdr_s / mdr_c * 100, 1) if mdr_c and mdr_s else None

        write_data(ws, row, 1,  yr,                        i, bold=True, align="center")
        write_data(ws, row, 2,  coh,                       i, num_format="#,##0")
        write_data(ws, row, 3,  succ,                      i, num_format="#,##0")
        write_data(ws, row, 4,  safe(o, "c_new_tsr"),      i, num_format="0")
        write_data(ws, row, 5,  died,                      i, num_format="#,##0")
        write_data(ws, row, 6,  fail,                      i, num_format="#,##0")
        write_data(ws, row, 7,  lost,                      i, num_format="#,##0")
        write_data(ws, row, 8,  safe(o, "c_ret_tsr"),      i, num_format="0")
        write_data(ws, row, 9,  safe(o, "tbhiv_coh", int), i, num_format="#,##0")
        write_data(ws, row, 10, safe(o, "tbhiv_succ", int),i, num_format="#,##0")
        write_data(ws, row, 11, safe(o, "c_tbhiv_tsr"),    i, num_format="0")
        write_data(ws, row, 12, mdr_c,                     i, num_format="#,##0")
        write_data(ws, row, 13, mdr_s,                     i, num_format="#,##0")
        write_data(ws, row, 14, mdr_tsr,                   i, num_format="0.0")
        write_data(ws, row, 15, safe(o, "mdr_died", int),  i, num_format="#,##0")
        write_data(ws, row, 16, safe(o, "mdr_lost", int),  i, num_format="#,##0")
        write_data(ws, row, 17, safe(o, "xdr_coh",  int),  i, num_format="#,##0")
        write_data(ws, row, 18, safe(o, "xdr_succ", int),  i, num_format="#,##0")

    ws.freeze_panes = "B2"
    write_note(ws, len(sorted_years) + 3, 1, len(HEADERS), NOTE)
    autofit(ws)
