"""Publication-quality seaborn figures for the TB Bangladesh review."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from src.fetchers.local import (
    DIVISION_CUMULATIVE,
    DIVISION_INCIDENCE,
    HDI,
    MEAN_TEMP,
    POPULATION_WORLDOMETER,
    POVERTY_INTERPOLATED,
    POVERTY_SURVEY_YEARS,
)

# ── Global aesthetics ─────────────────────────────────────────────────────────
PALETTE = sns.color_palette("deep")
sns.set_theme(
    style="whitegrid",
    font="DejaVu Sans",
    rc={
        "axes.edgecolor":     ".15",
        "axes.linewidth":     0.8,
        "grid.linewidth":     0.5,
        "grid.alpha":         0.4,
        "xtick.bottom":       True,
        "ytick.left":         True,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "figure.dpi":         150,
        "savefig.dpi":        300,
        "savefig.bbox":       "tight",
        "savefig.pad_inches": 0.05,
        "font.size":          12,
        "axes.titlesize":     16,
        "axes.labelsize":     14,
        "legend.fontsize":    12,
        "xtick.labelsize":    12,
        "ytick.labelsize":    12,
    },
)

YEARS = list(range(2000, 2025))


# ── Helpers ───────────────────────────────────────────────────────────────────
def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.savefig(path)
    plt.close(fig)


def _estimates_df(estimates: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for yr in YEARS:
        e = estimates.get(str(yr), {})
        def _v(k, cast=float):
            val = e.get(k, "")
            try:
                return cast(val) if val not in ("", None) else None
            except (ValueError, TypeError):
                return None
        rows.append({
            "year":       yr,
            "inc":        _v("e_inc_100k"),
            "inc_lo":     _v("e_inc_100k_lo"),
            "inc_hi":     _v("e_inc_100k_hi"),
            "mort":       _v("e_mort_100k"),
            "mort_lo":    _v("e_mort_100k_lo"),
            "mort_hi":    _v("e_mort_100k_hi"),
            "cdr":        _v("c_cdr"),
            "tbhiv_rate": _v("e_inc_tbhiv_100k"),
            "pop":        _v("e_pop_num"),
        })
    return pd.DataFrame(rows)


def _notif_df(notifs: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for yr in YEARS:
        n = notifs.get(str(yr), {})
        def _v(k, cast=float):
            val = n.get(k, "")
            try:
                return cast(val) if val not in ("", None) else None
            except (ValueError, TypeError):
                return None
        rows.append({
            "year":    yr,
            "newinc":  _v("c_newinc", int),
            "m014":    _v("newrel_m014", int),
            "m15p":    _v("newrel_m15plus", int),
            "f014":    _v("newrel_f014", int),
            "f15p":    _v("newrel_f15plus", int),
            "hivtest": _v("newrel_hivtest", int),
            "hivpos":  _v("newrel_hivpos", int),
        })
    return pd.DataFrame(rows)


def _outcomes_df(outc: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for yr in sorted(outc.keys()):
        o = outc[yr]
        def _v(k, cast=float):
            val = o.get(k, "")
            try:
                return cast(val) if val not in ("", None) else None
            except (ValueError, TypeError):
                return None
        rows.append({
            "year":    int(yr),
            "tsr_new": _v("c_new_tsr"),
            "tsr_ret": _v("c_ret_tsr"),
        })
    return pd.DataFrame(rows)


# ── Figure 1: TB detection gap — estimated vs notified absolute case counts ────
def fig_incidence(estimates: dict, notifs: dict, out_dir: Path) -> None:
    """
    Area chart showing the shrinking detection gap over 2000–2024.
    Total estimated incident cases (WHO, absolute) vs notified cases,
    with the undetected gap as a distinct shaded area.
    This is visually and conceptually distinct from fig3 (CDR/TSR percentages).
    """
    est_df   = _estimates_df(estimates)
    notif_df = _notif_df(notifs)

    # Absolute estimated cases (thousands)
    def _abs(key: str) -> pd.Series:
        vals = []
        for yr in YEARS:
            e   = estimates.get(str(yr), {})
            raw = e.get(key, "")
            try:
                vals.append(float(raw) / 1000 if raw not in ("", None) else None)
            except (ValueError, TypeError):
                vals.append(None)
        return pd.Series(vals)

    df = pd.DataFrame({"year": YEARS})
    df["est_k"]     = _abs("e_inc_num")
    df["est_lo_k"]  = _abs("e_inc_num_lo")
    df["est_hi_k"]  = _abs("e_inc_num_hi")
    df["notif_k"]   = notif_df["newinc"].values / 1000
    df = df.dropna(subset=["est_k", "notif_k"])

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    fig.subplots_adjust(bottom=0.28)

    # 95% CI band for estimated incidence
    ax.fill_between(df.year, df.est_lo_k, df.est_hi_k,
                    alpha=0.15, color=PALETTE[0], label="Estimated incidence 95% CI")
    # Estimated incidence line
    ax.plot(df.year, df.est_k, color=PALETTE[0], linewidth=2,
            linestyle="--", label="WHO estimated incidence")
    # Notified cases: filled area from zero to notification count
    ax.fill_between(df.year, 0, df.notif_k,
                    alpha=0.55, color=PALETTE[1])
    ax.plot(df.year, df.notif_k, color=PALETTE[1], linewidth=2,
            marker="o", markersize=3, label="Notified cases (detected)")

    # Shade the detection gap
    ax.fill_between(df.year, df.notif_k, df.est_k,
                    alpha=0.18, color=PALETTE[3],
                    label="Detection gap (undetected cases)")

    ax.set_xlabel("Year")
    ax.set_ylabel("Cases (thousands)")
    ax.set_title(
        "TB Estimated Burden vs Notified Cases — Bangladesh, 2000–2024\n"
        "Shrinking gap reflects rapid gains in case detection",
    )
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}k"))
    ax.set_ylim(0, None)
    ax.legend(frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.24), ncol=2)
    _save(fig, out_dir / "fig1_incidence_trend.png")


# ── Figure 2: Mortality trend with 95% CI ─────────────────────────────────────
def fig_mortality(estimates: dict, out_dir: Path) -> None:
    df = _estimates_df(estimates).dropna(subset=["mort"])

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.fill_between(df.year, df.mort_lo, df.mort_hi, alpha=0.20,
                    color=PALETTE[3], label="95% CI")
    sns.lineplot(data=df, x="year", y="mort", ax=ax,
                 color=PALETTE[3], linewidth=2, label="Mortality rate")
    ax.set_xlabel("Year")
    ax.set_ylabel("TB mortality rate\n(per 100k, HIV-neg)")
    ax.set_title("TB Estimated Mortality Rate — Bangladesh, 2000–2024")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.legend(frameon=False, loc="upper right")
    _save(fig, out_dir / "fig2_mortality_trend.png")


# ── Figure 3: CDR and TSR over time with programme milestones ─────────────────
def fig_cdr_tsr(estimates: dict, outc: dict, out_dir: Path) -> None:
    est_df = _estimates_df(estimates).dropna(subset=["cdr"])
    odf    = _outcomes_df(outc).dropna(subset=["tsr_new"])

    _MILESTONES = [
        (2001, "DOTS\nexpansion"),
        (2007, "NTP strategic\nplan II"),
        (2013, "GeneXpert\nrollout"),
        (2020, "COVID-19\ndisruption"),
    ]

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    fig.subplots_adjust(bottom=0.15)

    for yr, label in _MILESTONES:
        ax.axvline(yr, color="#aaaaaa", linewidth=0.8, linestyle=":")
        ax.text(yr + 0.15, 6, label, fontsize=9, color="#555555",
                va="bottom", ha="left", linespacing=1.3)

    sns.lineplot(data=est_df, x="year", y="cdr", ax=ax,
                 color=PALETTE[0], linewidth=2, marker="o", markersize=4,
                 label="Case Detection Rate (CDR %)")
    sns.lineplot(data=odf, x="year", y="tsr_new", ax=ax,
                 color=PALETTE[2], linewidth=2, marker="s", markersize=4,
                 label="Treatment Success Rate (TSR %)")
    ax.axhline(90, color="grey", linestyle="--", linewidth=0.8,
               label="WHO 90% target")
    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Case Detection Rate & Treatment Success Rate — Bangladesh, 2000–2024\n"
                 "Vertical lines mark key NTP programme milestones")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.set_xlim(1999, 2025)
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, -0.18), ncol=3)
    _save(fig, out_dir / "fig3_cdr_tsr.png")


# ── Figure 4: HIV-TB co-infection ─────────────────────────────────────────────
def fig_hivtb(estimates: dict, out_dir: Path) -> None:
    df = _estimates_df(estimates).dropna(subset=["tbhiv_rate"])

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=df, x="year", y="tbhiv_rate", ax=ax,
                 color=PALETTE[4], linewidth=2, marker="o", markersize=4,
                 label="TB-HIV incidence rate")
    ax.set_xlabel("Year")
    ax.set_ylabel("TB-HIV incidence (per 100k)")
    ax.set_title("Estimated TB-HIV Co-infection Incidence\nBangladesh, 2000–2024")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(4))
    ax.legend(frameon=False, loc="upper left")
    _save(fig, out_dir / "fig4_hivtb.png")


# ── Figure 5: Sex & age distribution (stacked bar, 2012–2024) ─────────────────
def fig_sex_age(notifs: dict, out_dir: Path) -> None:
    ndf = _notif_df(notifs)
    ndf = (
        ndf[ndf.year >= 2012]
        .dropna(subset=["m014", "m15p", "f014", "f15p"])
        .reset_index(drop=True)
        .copy()
    )
    if ndf.empty:
        return

    # Wider figure + extra bottom margin for legend outside the plot
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.subplots_adjust(bottom=0.28)

    bottom = pd.Series([0.0] * len(ndf), index=ndf.index)
    groups = [
        (r"Male $\geq$15",   "m15p", PALETTE[0]),
        (r"Male 0$-$14",     "m014", PALETTE[1]),
        (r"Female $\geq$15", "f15p", PALETTE[2]),
        (r"Female 0$-$14",   "f014", PALETTE[3]),
    ]
    for label, col, colour in groups:
        vals = ndf[col].fillna(0)
        ax.bar(ndf.year.astype(str), vals, bottom=bottom,
               color=colour, label=label, width=0.7)
        bottom = bottom + vals

    ax.set_xlabel("Year")
    ax.set_ylabel("Notified cases")
    ax.set_title("TB Notification by Sex & Age Group — Bangladesh, 2012–2024")
    ax.xaxis.set_tick_params(rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Legend placed below the plot, centred, 4 columns — avoids bar overlap
    ax.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.26),
        ncol=4,
    )
    _save(fig, out_dir / "fig5_sex_age_distribution.png")


# ── Figure 6: Division-wise incidence heatmap ─────────────────────────────────
def fig_division_heatmap(out_dir: Path) -> None:
    divs = ["Barishal", "Chattogram", "Dhaka", "Khulna",
            "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"]
    rows = {}
    for row in DIVISION_INCIDENCE:
        yr = row[0]
        rates = {d: row[1 + j * 2] for j, d in enumerate(divs)}
        rows[yr] = rates

    df = pd.DataFrame(rows, index=divs).T
    df.index = df.index.astype(int)
    df = df[df.index >= 2000]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        df.T.astype(float),
        ax=ax,
        cmap="YlOrRd",
        linewidths=0.3,
        linecolor="white",
        annot=False,
        cbar_kws={"label": "Incidence rate (per 100k)", "shrink": 0.7},
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Division")
    ax.set_title("Division-wise TB Incidence Rate — Bangladesh, 2000–2024")
    ax.set_xticklabels(
        [t.get_text() for t in ax.get_xticklabels()], rotation=45, ha="right"
    )
    _save(fig, out_dir / "fig6_division_heatmap.png")


# ── Figure 7: Division cumulative burden (horizontal bar) ─────────────────────
def fig_division_cumulative(out_dir: Path) -> None:
    divs   = [r[0] for r in DIVISION_CUMULATIVE]
    cases  = [r[1] for r in DIVISION_CUMULATIVE]
    deaths = [r[2] for r in DIVISION_CUMULATIVE]

    df = pd.DataFrame({"Division": divs, "Cases": cases, "Deaths": deaths})
    df = df.sort_values("Cases", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for ax, col, colour, label in zip(
        axes,
        ["Cases", "Deaths"],
        [PALETTE[0], PALETTE[3]],
        ["Cumulative cases (2000–2024)", "Estimated deaths (2000–2024)"],
    ):
        ax.barh(df.Division, df[col], color=colour)
        ax.set_xlabel(label)
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for bar, val in zip(ax.patches, df[col]):
            ax.text(
                bar.get_width() + bar.get_width() * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,}",
                va="center", fontsize=10,
            )

    fig.suptitle("Cumulative TB Burden by Division — Bangladesh, 2000–2024")
    plt.tight_layout()
    _save(fig, out_dir / "fig7_division_cumulative.png")


# ── Figure 8: Socioeconomic correlate — HDI vs CDR ────────────────────────────
def fig_socioeconomic(estimates: dict, out_dir: Path) -> None:
    est_df = _estimates_df(estimates).dropna(subset=["cdr"])
    hdi_df = pd.DataFrame(
        [(yr, val) for yr, val in HDI.items()], columns=["year", "hdi"]
    )
    df = est_df.merge(hdi_df, on="year").dropna()

    fig, ax = plt.subplots(figsize=(6, 4))
    sc = ax.scatter(df.hdi, df.cdr, c=df.year, cmap="plasma", s=50, zorder=3)
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Year")

    try:
        z = np.polyfit(df.hdi.dropna(), df.cdr.dropna(), 1)
        p = np.poly1d(z)
        x_range = pd.Series(sorted(df.hdi))
        ax.plot(x_range, p(x_range), "--", color="grey", linewidth=1.2, zorder=2)
    except Exception:
        pass

    ax.set_xlabel("Human Development Index (HDI)")
    ax.set_ylabel("Case Detection Rate (%)")
    ax.set_title("HDI vs TB Case Detection Rate — Bangladesh, 2000–2024")
    _save(fig, out_dir / "fig8_hdi_vs_cdr.png")


# ── Figure 9: Environmental – PM2.5 and BMD temperature ──────────────────────
def fig_environmental(climate_data: dict, out_dir: Path) -> None:
    real_pm25 = climate_data.get("pm25_national", {})

    yrs = list(range(2000, 2025))
    tmp = [MEAN_TEMP.get(y) for y in yrs]   # BMD Dhaka station
    pm  = [real_pm25.get(y) for y in yrs]

    df = pd.DataFrame({"year": yrs, "pm25": pm, "temp": tmp})
    df_temp = df.dropna(subset=["temp"])
    df_pm   = df.dropna(subset=["pm25"])

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    fig.subplots_adjust(bottom=0.32)   # room for legend below x-axis
    ax2 = ax1.twinx()

    _C_PM   = "#1a5276"   # dark navy — PM2.5 line and left axis
    _C_TEMP = "#1e6b3c"   # dark green — temperature line and right axis
    _C_WHO  = "#555555"   # dark gray — WHO reference lines

    sns.lineplot(data=df_pm, x="year", y="pm25", ax=ax1,
                 color=_C_PM, linewidth=2, marker="o", markersize=3,
                 label=r"PM$_{2.5}$ national mean ($\mu$g/m$^3$)")
    ax1.axhline(10, color=_C_WHO, linestyle=":", linewidth=1.0, alpha=0.85,
                label=r"WHO limit: 10 $\mu$g/m$^3$ (pre-2021)")
    ax1.axhline(5,  color=_C_WHO, linestyle="--", linewidth=1.0, alpha=0.85,
                label=r"WHO limit: 5 $\mu$g/m$^3$ (2021 revised)")

    sns.lineplot(data=df_temp, x="year", y="temp", ax=ax2,
                 color=_C_TEMP, linewidth=2, marker="s", markersize=3,
                 label=r"Mean annual temperature ($^{\circ}$C, BMD)")

    ax1.set_xlabel("Year")
    ax1.set_ylabel(r"PM$_{2.5}$ ($\mu$g/m$^3$)", color=_C_PM)
    ax2.set_ylabel(r"Mean annual temperature ($^{\circ}$C, BMD)", color=_C_TEMP)
    ax1.tick_params(axis="y", labelcolor=_C_PM)
    ax2.tick_params(axis="y", labelcolor=_C_TEMP)
    ax1.xaxis.set_major_locator(mticker.MultipleLocator(4))

    # Combine handles from both axes into a single 2-column legend below the plot
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2, labels1 + labels2,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=2,
        handlelength=2.0,
    )
    if ax2.get_legend():
        ax2.get_legend().remove()

    ax1.set_title(
        r"PM$_{2.5}$ (National) & Mean Temperature (BMD)" + "\nBangladesh, 2000–2024",
    )
    _save(fig, out_dir / "fig9_environmental.png")


# ── Figure 10: Socioeconomic trends panel ────────────────────────────────────
def fig_socioeconomic_trends(wb_data: dict, out_dir: Path) -> None:
    """2×2 panel: GDP, Poverty, HDI, Urban vs Rural population."""
    yrs = YEARS

    gdp     = [wb_data["gdp_per_capita"].get(str(y)) for y in yrs]
    hdi     = [HDI.get(y) for y in yrs]
    poverty = [POVERTY_INTERPOLATED.get(y) for y in yrs]
    survey_yrs = [y for y in yrs if y in POVERTY_SURVEY_YEARS]
    survey_pov = [POVERTY_INTERPOLATED[y] for y in survey_yrs]

    pop_rows  = [POPULATION_WORLDOMETER.get(y) for y in yrs]
    upop = [r[1] / 1e6 if r else None for r in pop_rows]
    rpop = [r[2] / 1e6 if r else None for r in pop_rows]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    # GDP per capita
    ax = axes[0, 0]
    df_gdp = pd.DataFrame({"year": yrs, "gdp": gdp}).dropna()
    ax.plot(df_gdp.year, df_gdp.gdp, color=PALETTE[0], linewidth=2, marker="o", markersize=3)
    ax.fill_between(df_gdp.year, 0, df_gdp.gdp, alpha=0.12, color=PALETTE[0])
    ax.set_title("GDP per Capita (current USD)")
    ax.set_xlabel("Year"); ax.set_ylabel("USD")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(6))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    # Poverty rate
    ax = axes[0, 1]
    ax.plot(yrs, poverty, color=PALETTE[3], linewidth=2, linestyle="--",
            label="Interpolated")
    ax.scatter(survey_yrs, survey_pov, color=PALETTE[3], s=60, zorder=5,
               label="Survey year (WB)")
    ax.set_title("Poverty Rate (<$2.15/day, 2017 PPP)")
    ax.set_xlabel("Year"); ax.set_ylabel("%")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(6))
    ax.legend(frameon=False)

    # HDI
    ax = axes[1, 0]
    df_hdi = pd.DataFrame({"year": yrs, "hdi": hdi}).dropna()
    ax.plot(df_hdi.year, df_hdi.hdi, color=PALETTE[2], linewidth=2, marker="s", markersize=3)
    ax.set_title("Human Development Index (HDI)")
    ax.set_xlabel("Year"); ax.set_ylabel("HDI")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(6))
    ax.set_ylim(0.45, 0.72)

    # Urban vs Rural population
    ax = axes[1, 1]
    df_pop = pd.DataFrame({"year": yrs, "urban": upop, "rural": rpop}).dropna()
    ax.plot(df_pop.year, df_pop.urban, color=PALETTE[1], linewidth=2,
            marker="o", markersize=3, label="Urban (M)")
    ax.plot(df_pop.year, df_pop.rural, color=PALETTE[5], linewidth=2,
            marker="s", markersize=3, label="Rural (M)")
    ax.set_title("Urban vs Rural Population")
    ax.set_xlabel("Year"); ax.set_ylabel("Population (millions)")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(6))
    ax.legend(frameon=False)

    fig.suptitle("Socioeconomic Indicators — Bangladesh, 2000–2024",
                 fontsize=14, fontweight="bold", y=1.02)
    _save(fig, out_dir / "fig10_socioeconomic_trends.png")


# ── Figure 11: Poverty rate vs TB incidence rate (scatter) ───────────────────
def fig_poverty_vs_tb(estimates: dict, out_dir: Path) -> None:
    est_df = _estimates_df(estimates).dropna(subset=["inc"])
    rows = []
    for _, r in est_df.iterrows():
        pov = POVERTY_INTERPOLATED.get(int(r.year))
        if pov is not None:
            rows.append({"year": int(r.year), "inc": r.inc, "poverty": pov,
                         "survey": int(r.year) in POVERTY_SURVEY_YEARS})
    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sc = ax.scatter(df.poverty, df.inc, c=df.year, cmap="plasma",
                    s=55, zorder=3, edgecolors="white", linewidth=0.4)
    # Highlight survey years
    survey = df[df.survey]
    ax.scatter(survey.poverty, survey.inc, s=90, zorder=4,
               facecolors="none", edgecolors="black", linewidth=1.2,
               label="Survey year")

    # Trend line
    z = np.polyfit(df.poverty, df.inc, 1)
    xr = np.linspace(df.poverty.min(), df.poverty.max(), 100)
    ax.plot(xr, np.poly1d(z)(xr), "--", color="grey", linewidth=1.2, zorder=2)

    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Year")

    # Annotate first and last year — 2000 nudged left to avoid colorbar
    offsets = {2000: (-32, 4), 2024: (5, 4)}
    for _, row in df[df.year.isin([2000, 2024])].iterrows():
        ax.annotate(str(int(row.year)), (row.poverty, row.inc),
                    textcoords="offset points",
                    xytext=offsets[int(row.year)], fontsize=10)

    ax.set_xlabel("Poverty rate (% below $2.15/day)")
    ax.set_ylabel("TB incidence rate (per 100k)")
    ax.set_title("Poverty Rate vs TB Incidence Rate — Bangladesh, 2000–2024\n"
                 "Circled points = World Bank HIES survey years")
    ax.legend(frameon=False)
    _save(fig, out_dir / "fig11_poverty_vs_tb.png")


# ── Figure 12: MDR-TB trend ───────────────────────────────────────────────────
def fig_mdr_trend(notifs: dict, out_dir: Path) -> None:
    rows = []
    for yr in YEARS:
        n = notifs.get(str(yr), {})
        def _v(k):
            val = n.get(k, "")
            try:
                return float(val) if val not in ("", None) else None
            except (ValueError, TypeError):
                return None
        mdr    = _v("conf_rrmdr")
        total  = _v("c_newinc")
        if mdr is not None and total:
            rows.append({"year": yr, "mdr": mdr, "pct": mdr / total * 100})
    df = pd.DataFrame(rows)
    if df.empty:
        return

    fig, ax1 = plt.subplots(figsize=(7.5, 4.5))
    ax2 = ax1.twinx()

    ax1.bar(df.year, df.mdr, color=PALETTE[3], alpha=0.75, label="Confirmed RR/MDR cases")
    ax2.plot(df.year, df.pct, color=PALETTE[0], linewidth=2,
             marker="o", markersize=4, label="% of total notified")

    ax1.set_xlabel("Year")
    ax1.set_ylabel("Confirmed RR/MDR-TB cases", color=PALETTE[3])
    ax2.set_ylabel("RR/MDR as % of total notified", color=PALETTE[0])
    ax1.tick_params(axis="y", labelcolor=PALETTE[3])
    ax2.tick_params(axis="y", labelcolor=PALETTE[0])
    ax1.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax1.set_ylim(0)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    fig.subplots_adjust(bottom=0.22)
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False,
               loc="upper center", bbox_to_anchor=(0.5, -0.18),
               ncol=2)
    ax1.set_title("Confirmed RR/MDR-TB Cases — Bangladesh, 2014–2024\n"
                  "Bars = absolute count; line = proportion of total notified")
    _save(fig, out_dir / "fig12_mdr_trend.png")


# ── Figure 13: Risk factors panel ────────────────────────────────────────────
def fig_risk_factors(wb_data: dict, out_dir: Path) -> None:
    """Panel: undernourishment, child stunting, smoking prevalence, health exp % GDP."""
    yrs = YEARS

    def _series(key: str) -> tuple[list, list]:
        vals = [(y, wb_data[key].get(str(y))) for y in yrs]
        xs = [v[0] for v in vals if v[1] is not None]
        ys = [v[1] for v in vals if v[1] is not None]
        return xs, ys

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.subplots_adjust(hspace=0.38, wspace=0.30)

    specs = [
        ("undernourishment",  axes[0, 0], "Undernourishment (% of population)",
         "% of pop.", PALETTE[3], False),
        ("child_stunting",    axes[0, 1], "Child Stunting — height-for-age (% under-5)",
         "% under-5", PALETTE[1], True),
        ("smoking_prevalence",axes[1, 0], "Smoking Prevalence (% adults ≥15)",
         "% adults",  PALETTE[4], True),
        ("health_exp_gdp_pct",axes[1, 1], "Health Expenditure (% of GDP)",
         "% of GDP",  PALETTE[2], False),
    ]

    for key, ax, title, ylabel, colour, is_survey in specs:
        xs, ys = _series(key)
        if is_survey:
            ax.scatter(xs, ys, color=colour, s=55, zorder=4,
                       label="Survey year")
            if len(xs) > 1:
                ax.plot(xs, ys, color=colour, linewidth=1.5,
                        linestyle="--", alpha=0.6)
        else:
            ax.plot(xs, ys, color=colour, linewidth=2,
                    marker="o", markersize=3)
            ax.fill_between(xs, 0, ys, alpha=0.10, color=colour)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(6))
        ax.set_ylim(0)
        if is_survey:
            ax.legend(frameon=False)

    fig.suptitle("TB Risk Factors — Bangladesh, 2000–2024\n"
                 "Source: World Bank Open Data",
                 fontsize=14, fontweight="bold", y=1.02)
    _save(fig, out_dir / "fig13_risk_factors.png")


# ── Shared helper: build aligned DataFrame for analytic figures ───────────────
def _build_analysis_df(estimates: dict, wb_data: dict, climate_data: dict) -> pd.DataFrame:
    """
    One row per year (2000-2024). Columns: TB metrics + all socioeconomic,
    environmental and risk-factor variables with sufficient annual coverage.
    Survey-only variables (stunting, smoking) are excluded to keep N≥20.
    """
    pm25 = climate_data.get("pm25_national", {})
    rows = []
    for yr in YEARS:
        s = str(yr)
        e = estimates.get(s, {})
        def _ev(k):
            v = e.get(k, "")
            try: return float(v) if v not in ("", None) else None
            except: return None

        rows.append({
            "year":          yr,
            "period":        ("2000–08" if yr <= 2008 else
                              "2009–16" if yr <= 2016 else "2017–24"),
            # TB outcomes
            "TB incidence\n(per 100k)":  _ev("e_inc_100k"),
            "TB mortality\n(per 100k)":  _ev("e_mort_100k"),
            "CDR (%)":                   _ev("c_cdr"),
            # Socioeconomic
            "GDP p.c. (USD)":            wb_data["gdp_per_capita"].get(s),
            "HDI":                       HDI.get(yr),
            "Poverty (%)":               POVERTY_INTERPOLATED.get(yr),
            # Health system
            "Health exp.\np.c. (USD)":   wb_data["health_exp_per_capita"].get(s),
            "BCG (%)":                   wb_data["bcg_immunisation"].get(s),
            # Risk factors — annual series only
            "Undernourish.\n(%)":        wb_data["undernourishment"].get(s),
            "Health exp.\n(% GDP)":      wb_data["health_exp_gdp_pct"].get(s),
            # Environmental
            "PM2.5\n(µg/m³)":           pm25.get(yr),
            "Temperature\n(°C, BMD)":    MEAN_TEMP.get(yr),
        })
    return pd.DataFrame(rows)


# ── Figure 14: Correlation matrix ────────────────────────────────────────────
def fig_correlation_matrix(estimates: dict, wb_data: dict,
                            climate_data: dict, out_dir: Path) -> None:
    df = _build_analysis_df(estimates, wb_data, climate_data)
    num = df.drop(columns=["year", "period"])
    corr = num.corr(method="pearson", numeric_only=True)

    n = len(corr)
    fig, ax = plt.subplots(figsize=(13, 11))
    sns.heatmap(
        corr,
        ax=ax,
        cmap="RdBu_r",
        vmin=-1, vmax=1,
        annot=True, fmt=".2f",
        annot_kws={"size": 10, "weight": "bold"},
        linewidths=0.5,
        linecolor="#cccccc",
        square=True,
        cbar_kws={"shrink": 0.6, "label": "Pearson r"},
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label("Pearson r")

    # Bold the two TB-outcome row/column labels
    tb_cols = {"TB incidence\n(per 100k)", "TB mortality\n(per 100k)"}
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        if label.get_text() in tb_cols:
            label.set_fontweight("bold")
            label.set_fontsize(11)
        else:
            label.set_fontsize(10)

    ax.set_title(
        "Pearson Correlation Matrix — TB Outcomes & Determinants\n"
        "Bangladesh, 2000–2024  |  note: correlations partly reflect shared time trend",
        fontsize=11, pad=12,
    )
    ax.tick_params(axis="x", labelrotation=45)
    ax.tick_params(axis="y", labelrotation=0)
    plt.tight_layout()
    _save(fig, out_dir / "fig14_correlation_matrix.png")


# ── Figure 15: Pairplot (TB targets vs key predictors) ───────────────────────
def fig_pairplot(estimates: dict, wb_data: dict,
                 climate_data: dict, out_dir: Path) -> None:
    df = _build_analysis_df(estimates, wb_data, climate_data)

    keep = [
        "TB incidence\n(per 100k)",
        "TB mortality\n(per 100k)",
        "GDP p.c. (USD)",
        "HDI",
        "Poverty (%)",
        "Undernourish.\n(%)",
        "BCG (%)",
        "PM2.5\n(µg/m³)",
        "period",
    ]
    df_pp = df[keep].dropna()

    period_order  = ["2000–08", "2009–16", "2017–24"]
    period_colors = {
        "2000–08": PALETTE[0],
        "2009–16": PALETTE[2],
        "2017–24": PALETTE[3],
    }
    palette = [period_colors[p] for p in period_order]

    with sns.plotting_context("talk", font_scale=1.1):
        g = sns.PairGrid(
            df_pp,
            vars=[c for c in keep if c != "period"],
            hue="period",
            hue_order=period_order,
            palette=palette,
            diag_sharey=False,
            height=3.2,
            aspect=1.0,
        )
        g.map_diag(sns.kdeplot, fill=True, alpha=0.35, linewidth=1.5)
        g.map_lower(sns.scatterplot, s=70, edgecolor="white",
                    linewidth=0.4, alpha=0.85)
        g.map_upper(sns.scatterplot, s=40, edgecolor="none", alpha=0.55)

        tb_vars = {"TB incidence\n(per 100k)", "TB mortality\n(per 100k)"}
        for ax in g.axes.flat:
            if ax is None:
                continue
            for axis, setter in [(ax.get_xlabel(), ax.set_xlabel),
                                  (ax.get_ylabel(), ax.set_ylabel)]:
                if axis in tb_vars:
                    setter(axis, fontweight="bold", fontsize=13)
                elif axis:
                    setter(axis, fontsize=12)
            ax.tick_params(labelsize=11)

        g.add_legend(title="Period", fontsize=12, title_fontsize=13,
                     bbox_to_anchor=(1.01, 0.5), loc="center left",
                     markerscale=1.5)
        g.figure.suptitle(
            "Pairplot — TB Outcomes vs Key Determinants, Bangladesh 2000–2024\n"
            "Colour = time period  |  diagonal: density  |  lower: scatter  |  upper: scatter",
            y=1.01, fontsize=14, fontweight="bold",
        )
        _save(g.figure, out_dir / "fig15_pairplot.png")


# ── Entry point ───────────────────────────────────────────────────────────────
def build_all(
    estimates: dict,
    notifs: dict,
    outc: dict,
    climate_data: dict,
    out_dir: Path,
    wb_data: dict | None = None,
) -> list[Path]:
    """Generate all figures; return list of PNG paths produced."""
    print("    Fig 1: TB detection gap (estimated vs notified cases)")
    fig_incidence(estimates, notifs, out_dir)
    print("    Fig 2: Mortality trend")
    fig_mortality(estimates, out_dir)
    print("    Fig 3: CDR & TSR with programme milestones")
    fig_cdr_tsr(estimates, outc, out_dir)
    print("    Fig 4: HIV-TB co-infection")
    fig_hivtb(estimates, out_dir)
    print("    Fig 5: Sex & age distribution")
    fig_sex_age(notifs, out_dir)
    print("    Fig 6: Division heatmap")
    fig_division_heatmap(out_dir)
    print("    Fig 7: Division cumulative burden")
    fig_division_cumulative(out_dir)
    print("    Fig 8: HDI vs CDR")
    fig_socioeconomic(estimates, out_dir)
    print("    Fig 9: Environmental factors (real data)")
    fig_environmental(climate_data, out_dir)
    if wb_data:
        print("    Fig 10: Socioeconomic trends panel")
        fig_socioeconomic_trends(wb_data, out_dir)
        print("    Fig 11: Poverty vs TB incidence scatter")
        fig_poverty_vs_tb(estimates, out_dir)
        print("    Fig 12: MDR-TB trend")
        fig_mdr_trend(notifs, out_dir)
        print("    Fig 13: Risk factors panel")
        fig_risk_factors(wb_data, out_dir)
        print("    Fig 14: Correlation matrix")
        fig_correlation_matrix(estimates, wb_data, climate_data, out_dir)
        print("    Fig 15: Pairplot")
        fig_pairplot(estimates, wb_data, climate_data, out_dir)
    return sorted(out_dir.glob("*.png"))
