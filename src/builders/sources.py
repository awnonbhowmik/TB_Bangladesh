"""Sheet 10: Data Sources & References."""

from openpyxl.workbook import Workbook

from src.fetchers.local import DATA_SOURCES
from src.styles import autofit, write_data, write_headers

HEADERS = ["#", "Sheet(s)", "Dataset / Variable", "Source Organization", "URL / Contact", "Coverage", "Notes"]


def build(wb: Workbook) -> None:
    ws = wb.create_sheet("10. Data Sources")
    ws.sheet_properties.tabColor = "595959"
    write_headers(ws, HEADERS, "grey")

    for i, row_data in enumerate(DATA_SOURCES):
        for col, val in enumerate(row_data, 1):
            align = "center" if col == 1 else "left"
            write_data(ws, i + 2, col, val, i, align=align)

    autofit(ws)
    # Override widths for URL-heavy columns
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 30
    ws.column_dimensions["E"].width = 55
    ws.column_dimensions["G"].width = 36
