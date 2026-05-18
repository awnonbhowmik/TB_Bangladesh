"""Generate publication-quality LaTeX tables (booktabs) for the TB Bangladesh review."""

from __future__ import annotations

import statistics as _st
from pathlib import Path

from src.fetchers.local import (
    DIVISION_CUMULATIVE,
    DIVISION_INCIDENCE,
    HDI,
    MEAN_TEMP,
    HUMIDITY,
    POPULATION_WORLDOMETER,
    POVERTY_INTERPOLATED,
    POVERTY_SURVEY_YEARS,
)

YEARS = [str(y) for y in range(2000, 2025)]

# ── Helpers ───────────────────────────────────────────────────────────────────
def _v(row: dict, key: str, cast=float, fmt: str = "{:.0f}") -> str:
    val = row.get(key, "")
    if val in ("", None):
        return "---"
    try:
        return fmt.format(cast(val))
    except (ValueError, TypeError):
        return "---"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _escape(s: str) -> str:
    return (
        s.replace("&", r"\&")
         .replace("%", r"\%")
         .replace("_", r"\_")
         .replace("^", r"\^{}")
         .replace("#", r"\#")
         .replace("$", r"\$")
         .replace("{", r"\{")
         .replace("}", r"\}")
         .replace("~", r"\textasciitilde{}")
         .replace("¹", r"$^{1}$")
    )


# ── Table 1A: Current TB Overview in Bangladesh ───────────────────────────────
def table_overview(out_dir: Path) -> None:
    rows = [
        ("Annual Incidence",
         r"$\approx$379,000 new cases per year",
         r"One of the WHO's 30 highest TB-burden countries."),
        ("Annual Mortality",
         r"$\approx$44,000 deaths per year",
         r"Averages over 120 fatalities every single day."),
        ("Funding Status",
         r"Critical Crisis",
         r"Sudden cuts from USAID and the Global Fund have left programmes near collapse."),
        ("Workforce Impact",
         r"1{,}600$+$ health workers laid off",
         r"Loss of specialised staff has fractured national preventive operations."),
        ("MDR-TB Burden",
         r"$\approx$5{,}000 cases annually",
         r"Multidrug-resistant TB is rising; fewer than half of these cases are detected."),
        ("Childhood TB",
         r"Critically underdiagnosed",
         r"Detection rates for children under five remain dangerously below the "
         r"10--15\,\% global benchmark."),
        ("Diagnostic Upgrades",
         r"600$+$ molecular tools deployed",
         r"Transitioning away from traditional microscopy to rapid, highly sensitive testing."),
        ("Primary Drivers",
         r"Urban density \& climatic factors",
         r"Malnutrition, overcrowded cities (Dhaka), and flooding accelerate transmission."),
    ]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Current tuberculosis situation in Bangladesh}",
        r"\label{tab:overview}",
        r"\small",
        r"\begin{tabular}{p{3.2cm}p{4.5cm}p{7.0cm}}",
        r"\toprule",
        r"\textbf{Category} & \textbf{Key metric / status}"
        r" & \textbf{Critical impacts \& details} \\",
        r"\midrule",
    ]
    for cat, metric, detail in rows:
        lines.append(f"{cat} & {metric} & {detail}" + r" \\[3pt]")
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Sources: WHO Global TB Report 2024; NTP Bangladesh Annual Report 2023;"
        r" Global Fund Programme Update 2024; USAID Bangladesh Health Office.",
        r"\end{table}",
    ]
    _write(out_dir / "table1a_overview.tex", "\n".join(lines))


# ── Table 1B: Precise TB Infection State & Risk Profiles ─────────────────────
def table_risk_profiles(out_dir: Path) -> None:
    rows = [
        ("Global Burden Rank",
         "National Standing",
         r"6th globally in overall tuberculosis disease burden."),
        ("Incidence Rate",
         "Plateaued Transmission",
         r"221 cases per 100{,}000 population; stagnant for 6 consecutive years."),
        ("Annual Mortality",
         "Flatlined Progress",
         r"44{,}000 deaths per year (averaging exactly 121 lives lost daily)."),
        ("Notification Gap",
         "Missing / Undetected Cases",
         r"$\approx$66{,}000 cases go undetected annually out of 379{,}000 estimated."),
        ("Gender Risk",
         "Male Vulnerability Profile",
         r"Men carry an adjusted relative risk (aRR\,$=$\,1.58) for treatment failure."),
        ("Elderly Risk",
         "Age 60$+$ Mortality",
         r"Mortality rises to 6.4\,\% (aRR\,$=$\,3.53) vs.\ 1.0\,\% in young adults."),
        ("Pediatric Risk",
         "Under-5 Mortality Rate",
         r"Children under five face a 5.4\,\% mortality rate once infected."),
        ("Retreatment Risk",
         "Prior Exposure Failure",
         r"Retreatment patients carry a 1.71--1.78$\times$ higher risk of clinical failure."),
    ]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Precise tuberculosis infection state and risk profiles --- Bangladesh}",
        r"\label{tab:risk_profiles}",
        r"\small",
        r"\begin{tabular}{p{3.2cm}p{4.5cm}p{7.0cm}}",
        r"\toprule",
        r"\textbf{Category} & \textbf{Specific indicator / metric}"
        r" & \textbf{Precise statistical value \& context} \\",
        r"\midrule",
    ]
    for cat, metric, detail in rows:
        lines.append(f"{cat} & {metric} & {detail}" + r" \\[3pt]")
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" aRR = adjusted relative risk."
        r" Sources: WHO Global TB Report 2024; Islam et al.\ (2023);"
        r" NTP Bangladesh outcome cohort analyses; WHO Global TB Database.",
        r"\end{table}",
    ]
    _write(out_dir / "table1b_risk_profiles.tex", "\n".join(lines))


# ── Shared: collect dataset rows ─────────────────────────────────────────────
def _dataset_rows(
    estimates: dict, notifs: dict, outc: dict, wb_data: dict,
    climate_data: dict | None
) -> list[tuple[str, dict]]:
    """Return [(year_str, {key: float|None})] for 2000-2024 — all dataset variables."""
    pm25 = (climate_data or {}).get("pm25_national", {})
    rows = []
    for yr in YEARS:
        y = int(yr)
        e = estimates.get(yr, {})
        n = notifs.get(yr, {})
        o = outc.get(yr, {})
        pop_row = POPULATION_WORLDOMETER.get(y)
        pov_survey = y in POVERTY_SURVEY_YEARS
        pov_raw = wb_data["poverty_rate"].get(yr) if pov_survey else POVERTY_INTERPOLATED.get(y)
        gdp_raw = wb_data["gdp_per_capita"].get(yr)
        cdr_raw = e.get("c_cdr")
        tsr_raw = o.get("c_new_tsr")

        def _f(v):
            try:
                return float(v) if v not in (None, "") else None
            except (ValueError, TypeError):
                return None

        rows.append((yr, {
            "pop_m":    pop_row[0] / 1e6    if pop_row else None,
            "density":  float(pop_row[3])   if pop_row else None,
            "upop_m":   pop_row[1] / 1e6   if pop_row else None,
            "rpop_m":   pop_row[2] / 1e6   if pop_row else None,
            "gdp":      _f(gdp_raw),
            "hdi":      _f(HDI.get(y)),
            "poverty":  _f(pov_raw),
            "pm25":     _f(pm25.get(y)),
            "temp":     _f(MEAN_TEMP.get(y)),
            "humidity": _f(HUMIDITY.get(y)),
            "e_inc_k":  _f(e.get("e_inc_num", "")) and _f(e.get("e_inc_num")) / 1000
                        if _f(e.get("e_inc_num")) else None,
            "e_mort_k": _f(e.get("e_mort_exc_tbhiv_num")) / 1000
                        if _f(e.get("e_mort_exc_tbhiv_num")) else None,
            "notif_k":  _f(n.get("c_newinc")) / 1000
                        if _f(n.get("c_newinc")) else None,
            "cdr":      _f(cdr_raw),
            "tsr":      _f(tsr_raw),
        }))
    return rows


def _fmt_cell(v: float | None, fmt: str) -> str:
    return fmt.format(v) if v is not None else "---"


# ── Table 9: Full Dataset (NiV Table 2 equivalent) ───────────────────────────
def table_dataset(
    estimates: dict, notifs: dict, outc: dict, wb_data: dict,
    out_dir: Path, climate_data: dict | None = None
) -> None:
    rows = _dataset_rows(estimates, notifs, outc, wb_data, climate_data)

    lines = [
        r"\begin{sidewaystable}",
        r"\centering",
        r"\caption{Dataset used for the study --- Bangladesh, 2000--2024}",
        r"\label{tab:dataset}",
        r"\footnotesize",
        r"\begin{tabular}{lrrrrrrrrrrrrrrr}",
        r"\toprule",
        # Header row 1
        (r"\textbf{Year}"
         r" & \textbf{Pop}"
         r" & \textbf{$\rho$}"
         r" & \textbf{UPop}"
         r" & \textbf{RPop}"
         r" & \textbf{GDP}"
         r" & \textbf{HDI}"
         r" & \textbf{Pov}"
         r" & \textbf{PM$_{2.5}$}"
         r" & \textbf{Temp}"
         r" & \textbf{Hum}"
         r" & \textbf{$E_{\mathrm{inc}}$}"
         r" & \textbf{$E_{\mathrm{mort}}$}"
         r" & \textbf{Notif}"
         r" & \textbf{CDR}"
         r" & \textbf{TSR} \\"),
        # Unit row
        (r" & (M)"
         r" & (km$^{-2}$)"
         r" & (M)"
         r" & (M)"
         r" & (USD)"
         r" & "
         r" & (\%)"
         r" & ($\mu$g\,m$^{-3}$)"
         r" & (\textdegree C)"
         r" & (\%)"
         r" & ($\times 10^3$)"
         r" & ($\times 10^3$)"
         r" & ($\times 10^3$)"
         r" & (\%)"
         r" & (\%) \\"),
        r"\midrule",
    ]

    for yr, d in rows:
        cells = [
            yr,
            _fmt_cell(d["pop_m"],    "{:.1f}"),
            _fmt_cell(d["density"],  "{:,.0f}"),
            _fmt_cell(d["upop_m"],   "{:.1f}"),
            _fmt_cell(d["rpop_m"],   "{:.1f}"),
            _fmt_cell(d["gdp"],      "{:,.0f}"),
            _fmt_cell(d["hdi"],      "{:.3f}"),
            _fmt_cell(d["poverty"],  "{:.1f}"),
            _fmt_cell(d["pm25"],     "{:.1f}"),
            _fmt_cell(d["temp"],     "{:.1f}"),
            _fmt_cell(d["humidity"], "{:.1f}"),
            _fmt_cell(d["e_inc_k"],  "{:.0f}"),
            _fmt_cell(d["e_mort_k"], "{:.0f}"),
            _fmt_cell(d["notif_k"],  "{:.0f}"),
            _fmt_cell(d["cdr"],      "{:.0f}"),
            _fmt_cell(d["tsr"],      "{:.0f}"),
        ]
        lines.append(" & ".join(cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Abbreviations:"
        r" Pop, total population (millions); $\rho$, population density (per km$^{2}$);"
        r" UPop, urban population (millions); RPop, rural population (millions);"
        r" GDP, gross domestic product per capita (current USD);"
        r" HDI, Human Development Index; Pov, poverty headcount ratio"
        r" (\% below \$2.15/day --- interpolated in non-survey years);"
        r" PM$_{2.5}$, national mean ambient PM$_{2.5}$ ($\mu$g\,m$^{-3}$);"
        r" Temp, mean annual dry-bulb temperature (\textdegree C, BMD Dhaka station);"
        r" Hum, mean annual relative humidity (\%, BMD Dhaka station);"
        r" $E_{\mathrm{inc}}$, estimated TB incidence cases ($\times 10^3$);"
        r" $E_{\mathrm{mort}}$, estimated TB deaths ($\times 10^3$, HIV-negative);"
        r" Notif, notified new and relapse TB cases ($\times 10^3$);"
        r" CDR, case detection rate (\%); TSR, treatment success rate (\%)."
        r" Sources: Worldometer (population); World Bank Open Data (GDP, poverty);"
        r" UNDP (HDI); World Bank\,/\,WHO\,/\,CAMS (PM$_{2.5}$);"
        r" BMD via DENV-Data-Analysis (temperature, humidity);"
        r" WHO Global TB Programme (TB estimates, notifications, outcomes).",
        r"\end{sidewaystable}",
    ]
    _write(out_dir / "table2_dataset.tex", "\n".join(lines))


# ── Table 10: Descriptive Statistics (NiV Table 3 equivalent) ────────────────
def table_descriptive_stats(
    estimates: dict, notifs: dict, outc: dict, wb_data: dict,
    out_dir: Path, climate_data: dict | None = None
) -> None:
    rows = _dataset_rows(estimates, notifs, outc, wb_data, climate_data)

    # Map of label → key in the row dict
    VAR_ORDER = [
        ("Population (M)",                         "pop_m",    "{:.2f}"),
        ("Density (per km$^{2}$)",                 "density",  "{:.0f}"),
        ("Urban population (M)",                   "upop_m",   "{:.2f}"),
        ("Rural population (M)",                   "rpop_m",   "{:.2f}"),
        ("GDP per capita (USD)",                   "gdp",      "{:,.0f}"),
        ("Human Development Index",                "hdi",      "{:.3f}"),
        ("Poverty rate (\\%)",                     "poverty",  "{:.2f}"),
        ("PM$_{2.5}$ ($\\mu$g\\,m$^{-3}$)",       "pm25",     "{:.2f}"),
        ("Mean temperature (\\textdegree C)",       "temp",     "{:.2f}"),
        ("Humidity (\\%)",                         "humidity", "{:.2f}"),
        ("Estimated incidence ($\\times 10^3$)",   "e_inc_k",  "{:.2f}"),
        ("Estimated deaths ($\\times 10^3$)",      "e_mort_k", "{:.2f}"),
        ("Notified cases ($\\times 10^3$)",        "notif_k",  "{:.2f}"),
        ("CDR (\\%)",                              "cdr",      "{:.2f}"),
        ("TSR (\\%)",                              "tsr",      "{:.2f}"),
    ]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Summary of descriptive statistics for study variables ---"
        r" Bangladesh, 2000--2024}",
        r"\label{tab:descriptive_stats}",
        r"\small",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Variable} & \textbf{Mean} & \textbf{Standard deviation}"
        r" & \textbf{Min} & \textbf{Max} \\",
        r"\midrule",
    ]

    for label, key, fmt in VAR_ORDER:
        vals = [d[key] for _, d in rows if d[key] is not None]
        if not vals:
            lines.append(f"{label} & --- & --- & --- & --- \\\\")
            continue
        mean = _st.mean(vals)
        sd   = _st.stdev(vals) if len(vals) > 1 else 0.0
        mn   = min(vals)
        mx   = max(vals)
        cells = [label,
                 fmt.format(mean),
                 fmt.format(sd),
                 fmt.format(mn),
                 fmt.format(mx)]
        lines.append(" & ".join(cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Statistics computed over all available annual observations, 2000--2024"
        r" ($n = 25$ for most variables; TSR reported with $\approx$2-year lag and"
        r" missing for the most recent cohort years)."
        r" CDR = case detection rate; TSR = treatment success rate."
        r" Poverty rate interpolated linearly between World Bank HIES survey anchors"
        r" (2000, 2005, 2010, 2016, 2022); 2023--2024 held at 2022 value."
        r" See Table~2 for the full annual series.",
        r"\end{table}",
    ]
    _write(out_dir / "table3_descriptive_stats.tex", "\n".join(lines))


# ── Table 1: TB Burden Estimates ──────────────────────────────────────────────
def table_burden(estimates: dict, out_dir: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{WHO TB Burden Estimates — Bangladesh, 2000--2024}",
        r"\label{tab:burden}",
        r"\small",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"\multicolumn{1}{c}{\textbf{Year}} &"
        r"\multicolumn{3}{c}{\textbf{Incidence rate (per 100\,k)}} &"
        r"\multicolumn{3}{c}{\textbf{Mortality rate (per 100\,k)}} &"
        r"\multicolumn{1}{c}{\textbf{CDR (\%)}} \\",
        r"\cmidrule(lr){2-4} \cmidrule(lr){5-7}",
        r"& Estimate & Low & High & Estimate & Low & High & \\",
        r"\midrule",
    ]

    for yr in YEARS:
        e = estimates.get(yr, {})
        row = " & ".join([
            yr,
            _v(e, "e_inc_100k",    fmt="{:.0f}"),
            _v(e, "e_inc_100k_lo", fmt="{:.0f}"),
            _v(e, "e_inc_100k_hi", fmt="{:.0f}"),
            _v(e, "e_mort_100k",   fmt="{:.1f}"),
            _v(e, "e_mort_100k_lo",fmt="{:.1f}"),
            _v(e, "e_mort_100k_hi",fmt="{:.1f}"),
            _v(e, "c_cdr",         fmt="{:.0f}"),
        ])
        lines.append(row + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize CDR = case detection rate (notified/estimated $\times$ 100)."
        r" 95\% confidence intervals from WHO Global TB Programme burden estimates.",
        r"\end{table}",
    ]
    _write(out_dir / "table1_burden.tex", "\n".join(lines))


# ── Table 2: Case Notifications & Performance ─────────────────────────────────
def table_notifications(notifs: dict, estimates: dict, outc: dict, out_dir: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{TB Case Notifications and Programme Performance — Bangladesh, 2000--2024}",
        r"\label{tab:notifications}",
        r"\small",
        r"\resizebox{\textwidth}{!}{",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"\textbf{Year} & \textbf{Total notified} & \textbf{Smear-pos} & "
        r"\textbf{Extra-pulm} & \textbf{Conf.\ RR/MDR} & \textbf{CDR (\%)} & \textbf{TSR (\%)} \\",
        r"\midrule",
    ]

    for yr in YEARS:
        n = notifs.get(yr, {})
        e = estimates.get(yr, {})
        o = outc.get(yr, {})
        row = " & ".join([
            yr,
            _v(n, "c_newinc",   int, "{:,}"),
            _v(n, "new_sp",     int, "{:,}"),
            _v(n, "new_ep",     int, "{:,}"),
            _v(n, "conf_rrmdr", int, "{:,}"),
            _v(e, "c_cdr",      fmt="{:.0f}"),
            _v(o, "c_new_tsr",  fmt="{:.0f}"),
        ])
        lines.append(row + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Smear-pos = new smear-positive pulmonary TB; reporting shifted to GeneXpert-based definitions after 2011."
        r" Extra-pulm = extra-pulmonary TB."
        r" CDR = case detection rate; TSR = treatment success rate (\%)."
        r" Source: WHO Global TB Programme notifications and outcomes datasets.",
        r"\end{table}",
    ]
    _write(out_dir / "table2_notifications.tex", "\n".join(lines))


# ── Table 3: Treatment Outcomes ───────────────────────────────────────────────
def table_outcomes(outc: dict, out_dir: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{TB Treatment Outcomes — Bangladesh (cohort years)}",
        r"\label{tab:outcomes}",
        r"\small",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"\textbf{Year} & \textbf{Cohort} & \textbf{Success} & \textbf{TSR (\%)} &"
        r" \textbf{Died} & \textbf{Failed} & \textbf{Lost} \\",
        r"\midrule",
    ]

    def _fmt_n(x: str) -> str:
        try:
            return f"{int(float(x)):,}" if x not in ("", None) else "---"
        except (ValueError, TypeError):
            return "---"

    for yr in sorted(outc.keys()):
        o = outc[yr]
        coh  = o.get("newrel_coh",  "") or o.get("new_sp_coh",  "")
        succ = o.get("newrel_succ", "") or o.get("new_sp_cur",  "")
        died = o.get("newrel_died", "") or o.get("new_sp_died", "")
        fail = o.get("newrel_fail", "") or o.get("new_sp_fail", "")
        lost = o.get("newrel_lost", "") or o.get("new_sp_def",  "")

        row = " & ".join([
            yr,
            _fmt_n(coh),
            _fmt_n(succ),
            _v(o, "c_new_tsr", fmt="{:.0f}"),
            _fmt_n(died),
            _fmt_n(fail),
            _fmt_n(lost),
        ])
        lines.append(row + r" \\")

    # 2024 outcomes not yet reported by WHO (cohort data published with ~2-year lag)
    if "2024" not in outc:
        lines.append(r"2024 & \multicolumn{6}{c}{\textit{Not yet reported by WHO}} \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Outcomes reported with $\approx$2-year lag (cohort year shown)."
        r" Pre-2012: smear-positive cohort used as proxy for total cohort."
        r" TSR = treated successfully / cohort $\times$ 100."
        r" 2024 data pending WHO Global TB Report 2026."
        r" Source: WHO Global TB Programme outcomes dataset.",
        r"\end{table}",
    ]
    _write(out_dir / "table3_outcomes.tex", "\n".join(lines))


# ── Table 4: Division Cumulative Summary ──────────────────────────────────────
def table_division_cumulative(out_dir: Path) -> None:
    # Division order and index mapping in DIVISION_INCIDENCE rows:
    # [0]=year; pairs (rate, cases) at indices (1,2),(3,4),(5,6),(7,8),(9,10),(11,12),(13,14),(15,16)
    # for Barishal, Chattogram, Dhaka, Khulna, Mymensingh, Rajshahi, Rangpur, Sylhet
    div_idx = {
        "Barishal": 2, "Chattogram": 4, "Dhaka": 6, "Khulna": 8,
        "Mymensingh": 10, "Rajshahi": 12, "Rangpur": 14, "Sylhet": 16,
    }

    # Sum annual cases by period from DIVISION_INCIDENCE
    pre: dict[str, int] = {d: 0 for d in div_idx}
    post: dict[str, int] = {d: 0 for d in div_idx}
    for row in DIVISION_INCIDENCE:
        yr = row[0]
        for d, idx in div_idx.items():
            v = row[idx]
            if v is not None:
                if yr <= 2014:
                    pre[d] += v
                else:
                    post[d] += v

    # National CFR from DIVISION_CUMULATIVE (original 2015-2024 data, ratio is stable)
    raw_cases = sum(c for _, c, _ in DIVISION_CUMULATIVE)
    raw_deaths = sum(d for _, _, d in DIVISION_CUMULATIVE)
    CFR = raw_deaths / raw_cases  # ~0.334

    # Display order: descending by 2000-2024 total
    display_order = ["Dhaka", "Chattogram", "Rajshahi", "Rangpur",
                     "Khulna", "Sylhet", "Mymensingh", "Barishal"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Cumulative TB Burden by Division --- Bangladesh, 2000--2024."
        r" Split at 2015 to reflect the creation of Mymensingh division.}",
        r"\label{tab:division_cumulative}",
        r"\small",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Division}"
        r" & \textbf{Cases 2000--14}"
        r" & \textbf{Cases 2015--24}"
        r" & \textbf{Total 2000--24}"
        r" & \textbf{Est.\ deaths} \\",
        r"\midrule",
    ]

    tc_pre = tc_post = tc_tot = td_tot = 0
    for div in display_order:
        p = pre[div]
        q = post[div]
        total = p + q
        deaths = round(total * CFR)

        if div == "Dhaka":
            label = r"Dhaka$^{\dagger}$"
            pre_str = f"{p:,}"
        elif div == "Mymensingh":
            label = r"Mymensingh$^{\ddagger}$"
            pre_str = r"---"
            p = 0  # don't double-count in national total
        else:
            label = _escape(div)
            pre_str = f"{p:,}"

        lines.append(
            f"{label} & {pre_str} & {q:,} & {total:,} & {deaths:,}" + r" \\"
        )
        tc_pre  += p
        tc_post += q
        tc_tot  += total
        td_tot  += deaths

    lines += [
        r"\midrule",
        rf"\textbf{{Bangladesh total}}"
        rf" & \textbf{{{tc_pre:,}}}"
        rf" & \textbf{{{tc_post:,}}}"
        rf" & \textbf{{{tc_tot:,}}}"
        rf" & \textbf{{{td_tot:,}}} \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Estimated deaths = total cases $\times$ national CFR"
        r" (case-fatality ratio $\approx$\,"
        + f"{CFR*100:.1f}"
        + r"\,\%, derived from WHO burden estimates)."
        r" $^{\dagger}$Dhaka 2000--2014 includes the territory that became Mymensingh division in 2015;"
        r" the two cannot be separated from published records."
        r" $^{\ddagger}$Mymensingh established as a separate division in 2015;"
        r" pre-2015 burden is subsumed within the Dhaka 2000--2014 figure."
        r" Case counts derived from NTP Bangladesh / DGHS Annual Reports.",
        r"\end{table}",
    ]
    _write(out_dir / "table4_division_cumulative.tex", "\n".join(lines))


# ── Table 5: Socioeconomic Indicators ─────────────────────────────────────────
def table_socioeconomic(wb_data: dict, out_dir: Path) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Socioeconomic Indicators --- Bangladesh, 2000--2024}",
        r"\label{tab:socioeconomic}",
        r"\small",
        r"\resizebox{\textwidth}{!}{",
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"\textbf{Year} & \textbf{GDP p.c.\ (USD)} & \textbf{HDI} &"
        r" \textbf{Poverty (\%)} &"
        r" \textbf{Urban pop.\ (M)} & \textbf{Rural pop.\ (M)} &"
        r" \textbf{Density (km$^{-2}$)} &"
        r" \textbf{Health exp.\ (USD)} & \textbf{BCG (\%)} \\",
        r"\midrule",
    ]

    def _fmt(v, fmt_str: str) -> str:
        return fmt_str.format(v) if v is not None else "---"

    for yr in YEARS:
        y    = int(yr)
        gdp  = wb_data["gdp_per_capita"].get(yr)
        hexp = wb_data["health_exp_per_capita"].get(yr)
        bcg  = wb_data["bcg_immunisation"].get(yr)
        hdi  = HDI.get(y)
        pop_row = POPULATION_WORLDOMETER.get(y)
        upop    = pop_row[1] / 1e6 if pop_row else None
        rpop    = pop_row[2] / 1e6 if pop_row else None
        density = pop_row[3] if pop_row else None

        # Poverty: use WB survey value for known years; interpolated otherwise
        pov_survey = y in POVERTY_SURVEY_YEARS
        pov_val = wb_data["poverty_rate"].get(yr) if pov_survey else POVERTY_INTERPOLATED.get(y)
        if pov_val is not None:
            pov_str = "{:.1f}".format(float(pov_val))
            if not pov_survey:
                pov_str += r"$^\dagger$"
        else:
            pov_str = "---"

        row = " & ".join([
            yr,
            _fmt(gdp,     "{:,.0f}"),
            _fmt(hdi,     "{:.3f}"),
            pov_str,
            _fmt(upop,    "{:.1f}"),
            _fmt(rpop,    "{:.1f}"),
            _fmt(density, "{:,}"),
            _fmt(hexp,    "{:,.0f}"),
            _fmt(float(bcg) if bcg else None, "{:.0f}"),
        ])
        lines.append(row + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" GDP p.c.\ = gross domestic product per capita (current USD; World Bank)."
        r" HDI = Human Development Index (UNDP)."
        r" Poverty = population below \$2.15/day international poverty line (\%; World Bank"
        r" SI.POV.DDAY); survey years 2000, 2005, 2010, 2016, 2022;"
        r" $\dagger$~linearly interpolated between survey anchors; 2023--2024 held at 2022 value."
        r" Urban and Rural pop.\ in millions; Density per km$^2$:"
        r" Worldometer Bangladesh (via DENV-Data-Analysis,"
        r" github.com/awnonbhowmik/DENV-Data-Analysis); 2000 estimated."
        r" Health exp.\ = current health expenditure per capita (USD; World Bank)."
        r" BCG = BCG immunisation coverage (\% of infants; World Bank).",
        r"\end{table}",
    ]
    _write(out_dir / "table5_socioeconomic.tex", "\n".join(lines))


# ── Table 6: Environmental Factors ───────────────────────────────────────────
def table_environmental(out_dir: Path, climate_data: dict | None = None) -> None:
    pm25_real = (climate_data or {}).get("pm25_national", {})

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Environmental Factors --- Bangladesh, 2000--2024}",
        r"\label{tab:environmental}",
        r"\small",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"\textbf{Year} & \textbf{Mean temp.\ (\textdegree C)} &"
        r" \textbf{Humidity (\%)} &"
        r" \textbf{PM\textsubscript{2.5} --- national mean ($\mu$g\,m$^{-3}$)} \\",
        r"\midrule",
    ]

    def _f(v, s: str) -> str:
        return s.format(v) if v is not None else "---"

    for yr_str in YEARS:
        y    = int(yr_str)
        temp = MEAN_TEMP.get(y)
        hum  = HUMIDITY.get(y)
        pm   = pm25_real.get(y)
        row  = " & ".join([
            yr_str,
            _f(temp, "{:.1f}"),
            _f(hum,  "{:.1f}"),
            _f(pm,   "{:.1f}"),
        ])
        lines.append(row + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Temperature and Humidity: Bangladesh Meteorological Department (BMD) Dhaka station"
        r" annual records (Dry Bulb Temperature, Relative Humidity);"
        r" sourced from DENV-Data-Analysis (github.com/awnonbhowmik/DENV-Data-Analysis)."
        r" 2000 values are estimated from adjacent years."
        r" PM\textsubscript{2.5} 2000--2020: World Bank indicator EN.ATM.PM25.MC.M3"
        r" (national population-weighted)."
        r" PM\textsubscript{2.5} 2021--2023: WHO GHO indicator SDGPM25 (national total)."
        r" PM\textsubscript{2.5} 2024: CAMS reanalysis via Open-Meteo."
        r" WHO PM\textsubscript{2.5} guideline revised from 10 to"
        r" 5\,\textmu{}g\,m\textsuperscript{$-3$} in 2021.",
        r"\end{table}",
    ]
    _write(out_dir / "table6_environmental.tex", "\n".join(lines))


# ── Table 7: Division-wise Incidence Rates — Key Years ───────────────────────
def table_division_incidence(out_dir: Path) -> None:
    _DIVS     = ["Barishal", "Chattogram", "Dhaka", "Khulna",
                 "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"]
    key_years = [2000, 2005, 2010, 2015, 2020, 2024]

    rate_by_year:  dict[int, dict[str, object]] = {}
    cases_by_year: dict[int, dict[str, object]] = {}
    for row in DIVISION_INCIDENCE:
        yr = row[0]
        if yr in key_years:
            rate_by_year[yr]  = {d: row[1 + j * 2] for j, d in enumerate(_DIVS)}
            cases_by_year[yr] = {d: row[2 + j * 2] for j, d in enumerate(_DIVS)}

    yr_cols = " & ".join([r"\textbf{" + str(y) + r"}" for y in key_years])
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{TB Incidence Rate (per 100,000) and Absolute Cases by Division"
        r" --- Bangladesh, Selected Years}",
        r"\label{tab:division_incidence}",
        r"\small",
        r"\resizebox{\textwidth}{!}{",
        r"\begin{tabular}{l" + "rr" * len(key_years) + "}",
        r"\toprule",
        r"\multirow{2}{*}{\textbf{Division}} & "
        + " & ".join(
            r"\multicolumn{2}{c}{\textbf{" + str(y) + r"}}"
            for y in key_years
        ) + r" \\",
        r"\cmidrule(lr){2-3}" + "".join(
            rf"\cmidrule(lr){{{2+i*2}-{3+i*2}}}"
            for i in range(1, len(key_years))
        ),
        r" & " + " & ".join(
            r"\footnotesize Rate & \footnotesize Cases"
            for _ in key_years
        ) + r" \\",
        r"\midrule",
    ]

    for div in _DIVS:
        cells = []
        for yr in key_years:
            rate  = rate_by_year[yr].get(div)
            cases = cases_by_year[yr].get(div)
            if rate is None:
                cells += ["---", "---"]
            else:
                cells += [str(int(rate)), f"{int(cases):,}"]
        lines.append(_escape(div) + " & " + " & ".join(cells) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Rate = TB incidence rate per 100,000 population."
        r" Cases = estimated absolute notified cases."
        r" Mymensingh became a separate division in 2015 (shown as --- before that year)."
        r" Source: NTP Bangladesh / DGHS Annual Reports.",
        r"\end{table}",
    ]
    _write(out_dir / "table7_division_incidence.tex", "\n".join(lines))


# ── Table 8: Risk Factors ─────────────────────────────────────────────────────
def table_risk_factors(wb_data: dict, out_dir: Path) -> None:
    _STUNTING_YEARS = frozenset({"2000","2001","2002","2003","2004","2005","2006","2007",
                                  "2011","2012","2013","2014","2015","2018","2019","2022"})
    _SMOKING_YEARS  = frozenset({"2000","2005","2007","2010","2015","2020","2021","2022"})

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{TB-Associated Risk Factors --- Bangladesh, 2000--2024}",
        r"\label{tab:riskfactors}",
        r"\small",
        r"\resizebox{\textwidth}{!}{",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"\textbf{Year} & \textbf{Undernourishment (\%)} &"
        r" \textbf{Child Stunting (\%$^\dagger$)} &"
        r" \textbf{Smoking (\%$^\ddagger$)} &"
        r" \textbf{Health Exp.\ (\% GDP)} \\",
        r"\midrule",
    ]

    def _f(v, s): return s.format(v) if v is not None else "---"

    for yr in YEARS:
        undernut = wb_data["undernourishment"].get(yr)
        stunting = wb_data["child_stunting"].get(yr)
        smoking  = wb_data["smoking_prevalence"].get(yr)
        hexp_gdp = wb_data["health_exp_gdp_pct"].get(yr)
        lines.append(" & ".join([
            yr,
            _f(undernut, "{:.1f}"),
            _f(stunting, "{:.1f}"),
            _f(smoking,  "{:.1f}"),
            _f(hexp_gdp, "{:.2f}"),
        ]) + r" \\")

    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\par\smallskip",
        r"\raggedright\footnotesize"
        r" Undernourishment: FAO prevalence of undernourishment, \% of population"
        r" (World Bank SN.ITK.DEFC.ZS); annual 2001--2023."
        r" $\dagger$~Child stunting: prevalence of stunting, height-for-age, \% of children under-5"
        r" (World Bank SH.STA.STNT.ZS); survey years only, shown as --- otherwise."
        r" $\ddagger$~Smoking: age-standardised prevalence of current tobacco smoking, \% adults $\geq$15"
        r" (World Bank SH.PRV.SMOK); survey years only."
        r" Health exp.\ = current health expenditure as \% of GDP (World Bank SH.XPD.CHEX.GD.ZS).",
        r"\end{table}",
    ]
    _write(out_dir / "table8_risk_factors.tex", "\n".join(lines))


# ── Master .tex wrapper ───────────────────────────────────────────────────────
def write_master(out_dir: Path) -> None:
    """Write a standalone LaTeX document that inputs all tables and figures."""
    content = r"""\documentclass[12pt,a4paper]{article}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{graphicx}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{longtable}
\usepackage{geometry}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage{float}
\usepackage{rotating}
\usepackage{hyperref}

%% subcaption styling
\captionsetup[subfigure]{labelfont=bf, textfont=normalfont,
                          singlelinecheck=false, justification=raggedright}

\geometry{margin=2.5cm}

\graphicspath{{../figures/}{../maps/}}
\DeclareGraphicsExtensions{.png}

\title{TB in Bangladesh: Data Appendix\\
       \large Supplementary Tables and Figures}
\author{TB Bangladesh Review}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\clearpage

%% ─── Tables ────────────────────────────────────────────────────────────────
\section{Supplementary Tables}

%% Tables 1A and 1B share the counter value "1"; label suffix set manually.
\renewcommand{\thetable}{1A}
\input{table1a_overview}
\clearpage

\addtocounter{table}{-1}%   keep counter at 1 for the B sub-table
\renewcommand{\thetable}{1B}
\input{table1b_risk_profiles}
\renewcommand{\thetable}{\arabic{table}}%  restore normal numbering
\clearpage

\input{table2_dataset}
\clearpage

\input{table3_descriptive_stats}
\clearpage

\input{table1_burden}
\clearpage

\input{table2_notifications}
\clearpage

\input{table3_outcomes}
\clearpage

\input{table4_division_cumulative}
\clearpage

\input{table5_socioeconomic}
\clearpage

\input{table6_environmental}
\clearpage

\input{table7_division_incidence}
\clearpage

\input{table8_risk_factors}
\clearpage

%% ─── Figures ───────────────────────────────────────────────────────────────
\section{Supplementary Figures}
\noindent\textit{Figures are ordered to match the narrative flow of the review:
national burden $\to$ programme performance $\to$ demographics $\to$
geographic distribution $\to$ determinants $\to$ statistical analysis.
Multi-panel figures use lettered sub-panels (A, B, C\ldots).}
\bigskip

%% Figure 1 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  %% Panel A — full width on top
  \begin{subfigure}[t]{\textwidth}
    \includegraphics[width=\textwidth]{fig1_incidence_trend}
    \subcaption{Estimated TB burden versus notified cases, 2000--2024.
      The shaded blue band is the WHO 95\,\% confidence interval for estimated incidence;
      the orange filled area represents the detection gap (undetected cases).
      The rapid convergence after 2010 reflects scaled-up DOTS and GeneXpert deployment.}
    \label{fig:1a}
  \end{subfigure}
  \vspace{0.8em}
  %% Panels B and C — side by side
  \begin{subfigure}[t]{0.48\textwidth}
    \includegraphics[width=\textwidth]{fig2_mortality_trend}
    \subcaption{Estimated TB mortality rate (per 100\,000, HIV-negative) with 95\,\%
      confidence interval.  Mortality fell from $\sim$75 to $\sim$27 per 100\,000,
      a $>$60\,\% decline over 25 years.}
    \label{fig:1b}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.48\textwidth}
    \includegraphics[width=\textwidth]{fig4_hivtb}
    \subcaption{Estimated TB-HIV co-infection incidence rate (per 100\,000).
      Bangladesh maintains HIV prevalence $<0.1$\,\%; the plateau since $\sim$2012
      reflects the low but stable co-infection background.}
    \label{fig:1c}
  \end{subfigure}
  \caption{\textbf{National TB epidemiological trends --- Bangladesh, 2000--2024.}
    Panel~(A) contextualises absolute burden against detection capacity;
    panels~(B) and~(C) track mortality and HIV co-infection trajectories.
    Together they establish the epidemiological arc of Bangladesh's TB response over 25 years.
    \textit{Source: WHO Global TB Programme burden estimates and notifications datasets.}}
  \label{fig:epi_trends}
\end{figure}
\clearpage

%% Figure 2 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{0.56\textwidth}
    \includegraphics[width=\textwidth]{fig3_cdr_tsr}
    \subcaption{Case Detection Rate (CDR, \%) and Treatment Success Rate (TSR, \%)
      with key NTP programme milestones.  Bangladesh surpassed the WHO 90\,\%
      TSR target by 2009 and has sustained it since; CDR crossed 80\,\% in 2019
      before a COVID-19-related dip in 2020--21.}
    \label{fig:2a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.42\textwidth}
    \includegraphics[width=\textwidth]{fig12_mdr_trend}
    \subcaption{Confirmed RR/MDR-TB cases (bars, left axis) and proportion of
      total notified cases (line, right axis), 2014--2024.
      Absolute case counts have risen despite a declining proportion,
      signalling an absolute drug-resistance burden that requires sustained vigilance.}
    \label{fig:2b}
  \end{subfigure}
  \caption{\textbf{National TB programme performance --- Bangladesh, 2000--2024.}
    Panel~(A) shows the trajectory of case-finding and treatment success alongside
    the four pivotal NTP milestones (DOTS expansion 2001, strategic plan II 2007,
    GeneXpert rollout 2013, COVID-19 disruption 2020).
    Panel~(B) tracks the emerging drug-resistance challenge.
    Both indicators are prerequisites for achieving WHO End-TB targets by 2030.
    \textit{Source: WHO Global TB Programme.}}
  \label{fig:prog_perf}
\end{figure}
\clearpage

%% Figure 3 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{fig5_sex_age_distribution}
  \caption{\textbf{TB notifications by sex and age group --- Bangladesh, 2012--2024.}
    Stacked bars show four demographic strata: males $\geq$15 (dominant stratum, blue),
    females $\geq$15 (green), males 0--14 (orange), and females 0--14 (red).
    Adult males consistently account for $\sim$55\,\% of all notifications,
    consistent with the global pattern of higher TB exposure and prevalence in working-age men.
    The decline in 2020 reflects COVID-19-related health-service disruption;
    the subsequent rebound demonstrates programme resilience.
    Sex- and age-disaggregated data available from 2012 onward.
    \textit{Source: WHO Global TB Programme notifications dataset.}}
  \label{fig:demographics}
\end{figure}
\clearpage

%% Figure 4 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{\textwidth}
    \includegraphics[width=\textwidth, height=0.28\textheight, keepaspectratio]{map5_south_asia_context}
    \subcaption{TB incidence rate (per 100\,000) across South and Southeast Asia ---
      most recent WHO estimates.  Bangladesh (red border) carries one of the region's
      highest absolute burdens, second only to India in total case count,
      yet its incidence rate is lower than several neighbouring countries.}
    \label{fig:4a}
  \end{subfigure}
  \vspace{0.8em}
  \begin{subfigure}[t]{0.50\textwidth}
    \includegraphics[width=\textwidth, height=0.30\textheight, keepaspectratio]{map4_incidence_2024}
    \subcaption{Division-level TB incidence rate (per 100\,000) --- Bangladesh, 2024.
      Dhaka and Chattogram divisions record the highest rates,
      driven by population density and urban migration.}
    \label{fig:4b}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.46\textwidth}
    \includegraphics[width=\textwidth, height=0.30\textheight, keepaspectratio]{map6_incidence_reduction}
    \subcaption{Proportional reduction in TB incidence rate by division, 2000$\to$2024.
      Greener shading indicates greater improvement.
      $\dagger$Mymensingh division established 2015; reduction calculated from 2015 baseline.}
    \label{fig:4c}
  \end{subfigure}
  \caption{\textbf{Geographic distribution of TB burden --- regional context and within-country variation.}
    Panel~(A) situates Bangladesh within the South Asian high-burden region.
    Panel~(B) shows the within-country distribution in 2024, highlighting
    the urban concentration of disease.
    Panel~(C) quantifies progress: all divisions achieved at least a 4\,\% reduction,
    but the magnitude varies substantially, pointing to persistent geographic inequities.
    \textit{Sources: WHO Global TB Programme; NTP Bangladesh / DGHS Annual Reports;
    Natural Earth 1:110m boundaries; OCHA HDX Bangladesh Admin Boundaries.}}
  \label{fig:geo_dist}
\end{figure}
\clearpage

%% Figure 5 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{map3_incidence_small_multiples}
  \caption{\textbf{Division-wise TB incidence rate (per 100\,000) at key years ---
    Bangladesh, 2000--2024.}
    Each panel label shows both the incidence rate and absolute notified case count.
    The progression from 2000 to 2024 illustrates the uneven pace of decline:
    Dhaka consistently leads in absolute burden; Mymensingh appears from 2015
    (carved from Dhaka division); all divisions show declining rates by 2020--24,
    accelerated by intensified case-finding efforts.
    \textit{Source: NTP Bangladesh / DGHS Annual Reports.}}
  \label{fig:geo_temporal}
\end{figure}
\clearpage

%% Figure 6 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{\textwidth}
    \includegraphics[width=\textwidth]{fig6_division_heatmap}
    \subcaption{Division-wise TB incidence rate heatmap, 2000--2024.
      Colour intensity encodes incidence per 100\,000.
      Dhaka (darkest) has remained the highest-burden division throughout;
      Mymensingh data begin in 2015.}
    \label{fig:6a}
  \end{subfigure}
  \vspace{0.8em}
  \begin{subfigure}[t]{\textwidth}
    \includegraphics[width=\textwidth]{fig7_division_cumulative}
    \subcaption{Cumulative TB cases (left) and estimated deaths (right) by division,
      2000--2024, sorted by descending case count.
      Dhaka accounts for $\sim$28\,\% of all cumulative cases;
      together Dhaka and Chattogram represent nearly half the national burden.}
    \label{fig:6b}
  \end{subfigure}
  \caption{\textbf{Division-level TB burden --- temporal heatmap and cumulative summary,
    Bangladesh 2000--2024.}
    Panel~(A) reveals year-on-year trends within each division;
    panel~(B) converts those trends into cumulative burden for direct comparison
    across the eight administrative units.
    The contrast between Dhaka and Barishal ($\sim$7$\times$ difference in cumulative cases)
    underscores the need for geographically targeted resource allocation.
    \textit{Source: NTP Bangladesh / DGHS Annual Reports.}}
  \label{fig:div_burden}
\end{figure}
\clearpage

%% Figure 7 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{0.48\textwidth}
    \includegraphics[width=\textwidth]{map1_cumulative_cases}
    \subcaption{Cumulative TB cases by division, 2000--2024.
      Darker shading indicates higher absolute case burden.}
    \label{fig:7a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.48\textwidth}
    \includegraphics[width=\textwidth]{map2_cumulative_deaths}
    \subcaption{Estimated cumulative TB deaths by division, 2000--2024.
      Deaths estimated by applying the national case-fatality ratio to division case counts.}
    \label{fig:7b}
  \end{subfigure}
  \caption{\textbf{Cumulative geographic TB burden --- Bangladesh, 2000--2024.}
    The spatial concentration of cumulative cases and deaths mirrors population density:
    Dhaka and Chattogram divisions together bear $\sim$43\,\% of the 25-year case total
    and an equivalent share of estimated mortality.
    Barishal records the lowest burden in both panels, consistent with its
    lower population density and historically better TB indicators.
    \textit{Source: NTP Bangladesh / DGHS Annual Reports.}}
  \label{fig:geo_cumul}
\end{figure}
\clearpage

%% Figure 8 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{\textwidth}
    \includegraphics[width=\textwidth, height=0.38\textheight, keepaspectratio]{fig10_socioeconomic_trends}
    \subcaption{Socioeconomic indicator trends, 2000--2024.
      GDP per capita rose $\sim$5$\times$ in constant USD;
      poverty (below \$2.15/day) fell from 41\,\% to $<$6\,\%;
      the Human Development Index climbed from 0.47 to 0.68;
      and urban population grew from $\sim$25\,\% to $\sim$40\,\% of total.}
    \label{fig:8a}
  \end{subfigure}
  \vspace{0.8em}
  \begin{subfigure}[t]{0.60\textwidth}
    \centering
    \includegraphics[width=\textwidth, height=0.32\textheight, keepaspectratio]{fig8_hdi_vs_cdr}
    \subcaption{HDI vs.\ Case Detection Rate --- each point is one year,
      colour-coded by calendar year.  The strong positive correlation
      ($r \approx +0.97$) confirms that human development gains
      are a structural enabler of improved TB case-finding.}
    \label{fig:8b}
  \end{subfigure}
  \caption{\textbf{Socioeconomic determinants of TB --- Bangladesh, 2000--2024.}
    Panel~(A) documents Bangladesh's remarkable development trajectory over the study period.
    Panel~(B) demonstrates that this trajectory closely tracks the country's
    capacity to detect TB cases: as the HDI rose, CDR rose in near-lockstep,
    suggesting that investments in education, health infrastructure and income
    simultaneously strengthened the TB response.
    \textit{Sources: World Bank Open Data (GDP, poverty, urbanisation);
    UNDP Human Development Reports; WHO Global TB Programme.}}
  \label{fig:socioeco}
\end{figure}
\clearpage

%% Figure 9 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{0.54\textwidth}
    \includegraphics[width=\textwidth]{fig9_environmental}
    \subcaption{National mean PM\textsubscript{2.5} ($\mu$g\,m$^{-3}$, left axis)
      and mean annual temperature at the BMD Dhaka station (\textdegree C, right axis),
      2000--2024.
      Bangladesh consistently exceeds both the pre-2021 WHO guideline (10\,$\mu$g\,m$^{-3}$)
      and the 2021 revised guideline (5\,$\mu$g\,m$^{-3}$) by a factor of $5$--$10\times$,
      constituting a persistent environmental TB risk modifier.}
    \label{fig:9a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.44\textwidth}
    \includegraphics[width=\textwidth]{fig13_risk_factors}
    \subcaption{TB-associated behavioural and nutritional risk factor trends, 2000--2024.
      Undernourishment declined steadily; child stunting fell from $\sim$51\,\%
      to $\sim$24\,\% of under-fives; adult smoking prevalence decreased markedly;
      health expenditure as a share of GDP remained low but stable.}
    \label{fig:9b}
  \end{subfigure}
  \caption{\textbf{Environmental and behavioural risk factors for TB ---
    Bangladesh, 2000--2024.}
    Panel~(A) highlights air-pollution exposure as a structural environmental driver:
    PM\textsubscript{2.5} concentrations far exceed safe limits throughout the study period,
    impairing respiratory defences and amplifying susceptibility to airborne \textit{M.\ tuberculosis}.
    Panel~(B) shows that while nutritional and smoking risks have improved substantially,
    persistent undernutrition and a low health-expenditure share remain priority targets.
    \textit{Sources: World Bank (PM\textsubscript{2.5}, undernourishment, stunting, smoking,
    health expenditure); WHO GHO; CAMS/Open-Meteo; BMD.}}
  \label{fig:risk_factors}
\end{figure}
\clearpage

%% Figure 10 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[t]{0.44\textwidth}
    \includegraphics[width=\textwidth]{fig11_poverty_vs_tb}
    \subcaption{Poverty rate vs.\ TB incidence rate, 2000--2024.
      Each point is one year, colour-coded by calendar year;
      circled points are World Bank HIES survey years.
      The near-horizontal scatter reveals that TB incidence
      has remained remarkably flat ($\sim$220 per 100\,000) even as poverty
      fell from 41\,\% to $<$6\,\%, suggesting that detection improvements
      have kept notified incidence stable as the true burden declined.}
    \label{fig:10a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[t]{0.54\textwidth}
    \includegraphics[width=\textwidth]{fig14_correlation_matrix}
    \subcaption{Pearson correlation matrix of TB outcomes and determinants.
      TB incidence and mortality (bold labels) show strong negative correlations
      with CDR, HDI, GDP and health expenditure ($r < -0.95$),
      and strong positive correlations with poverty ($r > +0.95$).
      Correlations partly reflect shared secular time trends;
      causal inference requires covariate adjustment.}
    \label{fig:10b}
  \end{subfigure}
  \caption{\textbf{Statistical associations between TB outcomes and key determinants ---
    Bangladesh, 2000--2024.}
    Panel~(A) illustrates the decoupling of poverty reduction from notified TB incidence,
    consistent with rising case detection masking a declining true burden.
    Panel~(B) provides a system-level view: virtually all socioeconomic and
    programme indicators correlate at $|r| > 0.9$ with TB outcomes,
    underscoring the multi-factorial nature of the epidemic and the importance
    of addressing poverty, nutrition, environment and health-system capacity simultaneously.
    \textit{Sources: WHO Global TB Programme; World Bank Open Data; UNDP; BMD.}}
  \label{fig:stats}
\end{figure}
\clearpage

%% Figure 11 ─────────────────────────────────────────────────────────────────
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{fig15_pairplot}
  \caption{\textbf{Pairplot of TB outcomes against key determinants ---
    Bangladesh, 2000--2024.}
    Each of the 64 cells shows the bivariate relationship between one pair of
    the eight variables: TB incidence rate, TB mortality rate, GDP per capita,
    Human Development Index, poverty rate, undernourishment, BCG coverage,
    and PM\textsubscript{2.5} concentration.
    Points are colour-coded by time period:
    2000--08 (blue), 2009--16 (green), 2017--24 (red).
    Diagonal cells show kernel density estimates for each variable;
    lower-triangle cells show scatter plots; upper-triangle cells show scatter overlays.
    TB incidence and mortality labels are \textbf{bold}.
    The clear period-based clustering confirms the structural shift in Bangladesh's
    TB epidemiology across three phases of the national response.
    \textit{Sources: WHO Global TB Programme; World Bank Open Data; UNDP; BMD.}}
  \label{fig:pairplot}
\end{figure}

\end{document}
"""
    _write(out_dir / "TB_Bangladesh_Appendix.tex", content)


# ── Entry point ───────────────────────────────────────────────────────────────
def build_all(
    estimates: dict,
    notifs: dict,
    outc: dict,
    wb_data: dict,
    out_dir: Path,
    climate_data: dict | None = None,
) -> list[Path]:
    """Generate all LaTeX table files; return list of .tex paths produced."""
    print("    Table 1A: TB overview")
    table_overview(out_dir)
    print("    Table 1B: Risk profiles")
    table_risk_profiles(out_dir)
    print("    Table 2: Full dataset")
    table_dataset(estimates, notifs, outc, wb_data, out_dir, climate_data)
    print("    Table 3: Descriptive statistics")
    table_descriptive_stats(estimates, notifs, outc, wb_data, out_dir, climate_data)
    print("    Table 4: Burden estimates")
    table_burden(estimates, out_dir)
    print("    Table 5: Notifications")
    table_notifications(notifs, estimates, outc, out_dir)
    print("    Table 6: Treatment outcomes")
    table_outcomes(outc, out_dir)
    print("    Table 7: Division cumulative")
    table_division_cumulative(out_dir)
    print("    Table 8: Socioeconomic indicators")
    table_socioeconomic(wb_data, out_dir)
    print("    Table 9: Environmental factors")
    table_environmental(out_dir, climate_data)
    print("    Table 10: Division incidence key years")
    table_division_incidence(out_dir)
    print("    Table 11: Risk factors")
    table_risk_factors(wb_data, out_dir)
    print("    Master LaTeX document")
    write_master(out_dir)
    return sorted(out_dir.glob("*.tex"))
