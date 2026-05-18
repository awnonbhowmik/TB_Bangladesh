"""Choropleth map figures for TB Bangladesh review (requires geopandas)."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# Force the local mpl_toolkits (pip-installed with matplotlib 3.10) to win over
# the system namespace package, which is compiled for an older matplotlib.
import mpl_toolkits as _mt
_mt.__path__ = [str(Path(matplotlib.__file__).parent.parent / "mpl_toolkits")]
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import geopandas as gpd

from src.fetchers.local import DIVISION_CUMULATIVE, DIVISION_INCIDENCE

# ── Paths ─────────────────────────────────────────────────────────────────────
_DATA      = Path(__file__).parent.parent.parent / "data"
_SHP_ADM1  = _DATA / "bgd_adm_bbs_20201113_shp" / "bgd_adm_bbs_20201113_SHP" / "bgd_admbnda_adm1_bbs_20201113.shp"
_SHP_WORLD = _DATA / "ne_110m_admin_0_countries" / "ne_110m_admin_0_countries.shp"

_NAME_MAP = {
    "Barisal":    "Barishal",
    "Chittagong": "Chattogram",
    "Dhaka":      "Dhaka",
    "Khulna":     "Khulna",
    "Mymensingh": "Mymensingh",
    "Rajshahi":   "Rajshahi",
    "Rangpur":    "Rangpur",
    "Sylhet":     "Sylhet",
}

CMAP    = mcolors.LinearSegmentedColormap.from_list("TB", ["cyan", "blue", "green", "red"])
_EDGE   = "#555555"
_EDGE_W = 0.5
_BG     = "#EAF3FF"

_LABEL_OFFSETS: dict[str, tuple[float, float]] = {
    "Dhaka":      ( 0.20, -0.10),
    "Chattogram": ( 0.25, -0.05),
    "Barishal":   (-0.30, -0.18),
    "Khulna":     (-0.35,  0.05),
    "Rajshahi":   (-0.35,  0.05),
    "Rangpur":    ( 0.05,  0.12),
    "Mymensingh": ( 0.22,  0.08),
    "Sylhet":     ( 0.20,  0.05),
}


# ── Shared utilities ──────────────────────────────────────────────────────────
def _load_adm1() -> gpd.GeoDataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gdf = gpd.read_file(_SHP_ADM1)
    gdf["div_name"] = gdf["ADM1_EN"].map(_NAME_MAP).fillna(gdf["ADM1_EN"])
    return gdf


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def _tight_bounds(gdf: gpd.GeoDataFrame, ax: plt.Axes, pad: float = 0.05) -> None:
    b  = gdf.total_bounds
    dx = (b[2] - b[0]) * pad
    dy = (b[3] - b[1]) * pad
    ax.set_xlim(b[0] - dx, b[2] + dx)
    ax.set_ylim(b[1] - dy, b[3] + dy)
    ax.autoscale(False)


def _draw_compass_inset(
    host_ax: plt.Axes,
    size_pct: int = 18,
    loc: str = "upper right",
    bbox_pad: float = -0.01,
) -> None:
    """Compass rose matching the Heatwave-Dhaka notebook (fig 0) style exactly."""
    ax_c = inset_axes(
        host_ax,
        width=f"{size_pct}%", height=f"{size_pct}%",
        loc=loc,
        bbox_to_anchor=(bbox_pad, bbox_pad, 1, 1),
        bbox_transform=host_ax.transAxes,
        borderpad=0,
    )
    ax_c.set_xlim(-1.35, 1.35)
    ax_c.set_ylim(-1.35, 1.35)
    ax_c.set_aspect("equal")
    ax_c.axis("off")

    # White background with light-gray border (same as the notebook)
    ax_c.patch.set_visible(True)
    ax_c.patch.set_facecolor("white")
    ax_c.patch.set_edgecolor("#cccccc")
    ax_c.patch.set_linewidth(0.8)

    # Two concentric outer rings
    for r, lw in [(0.92, 2.5), (0.76, 1.2)]:
        ax_c.add_patch(mpatches.Circle((0, 0), r, color="none", ec="black", lw=lw, zorder=2))

    def _spike(ang: float, length: float, hw: float, col: str) -> None:
        # 4-point polygon: tip → left-base → centre → right-base (compass bearing)
        a  = np.radians(ang)
        al = np.radians(ang - 90)
        ar = np.radians(ang + 90)
        ax_c.add_patch(mpatches.Polygon(
            [[np.sin(a)  * length, np.cos(a)  * length],
             [np.sin(al) * hw,     np.cos(al) * hw    ],
             [0, 0],
             [np.sin(ar) * hw,     np.cos(ar) * hw    ]],
            fc=col, ec="white", lw=0.6, zorder=3,
        ))

    # Cardinal spikes — black fill
    for ang in [0, 90, 180, 270]:
        _spike(ang, 0.72, 0.18, "black")

    # Diagonal spikes — dark gray fill
    for ang in [45, 135, 225, 315]:
        _spike(ang, 0.48, 0.11, "#555555")

    # White highlight on each cardinal spike (inner half, narrow)
    for ang in [0, 90, 180, 270]:
        a  = np.radians(ang)
        al = np.radians(ang - 90)
        ar = np.radians(ang + 90)
        ax_c.add_patch(mpatches.Polygon(
            [[np.sin(a)  * 0.72,  np.cos(a)  * 0.72 ],
             [np.sin(al) * 0.09,  np.cos(al) * 0.09 ],
             [0, 0],
             [np.sin(ar) * 0.09,  np.cos(ar) * 0.09 ]],
            fc="white", ec="white", lw=0, zorder=4,
        ))

    # Centre dot
    ax_c.add_patch(mpatches.Circle((0, 0), 0.08, fc="white", ec="black", lw=1.2, zorder=5))

    # N / S / E / W labels — anchor the near edge (not centre) at _label_r
    # so the visual gap from ring border to letter edge is equal in all directions
    _outer_r = 0.92
    _label_r = _outer_r + 0.28
    for t, x, y, ha, va in [
        ("N",  0,         _label_r,  "center", "bottom"),
        ("S",  0,        -_label_r,  "center", "top"),
        ("E",  _label_r,  0,         "left",   "center"),
        ("W", -_label_r,  0,         "right",  "center"),
    ]:
        ax_c.text(x, y, t, ha=ha, va=va,
                  fontweight="bold", fontsize=9, color="black", zorder=6,
                  clip_on=False)


def _draw_scale_bar_transaxes(
    ax: plt.Axes,
    center_lat: float,
    length_km: int = 200,
    n_segs: int = 4,
    x0: float = 0.05,
    y0: float = 0.04,
) -> None:
    """
    Scale bar in axes-fraction coordinates (transAxes), n_segs alternating segments.
    Default: 200 km in 4 × 50 km segments, alternating black / light-gray.
    """
    xlim = ax.get_xlim()
    lon_span   = xlim[1] - xlim[0]
    km_per_deg = 111.320 * np.cos(np.radians(center_lat))
    scale_frac = length_km / (lon_span * km_per_deg)
    seg        = scale_frac / n_segs
    bar_h      = 0.018   # axes fraction
    step_km    = length_km // n_segs

    # White background pill
    ax.add_patch(mpatches.FancyBboxPatch(
        (x0 - 0.010, y0 - bar_h * 1.5),
        scale_frac + 0.020, bar_h * 5.0,
        boxstyle="round,pad=0", facecolor="white",
        edgecolor="none", alpha=0.82,
        transform=ax.transAxes, zorder=9, clip_on=False,
    ))

    # Alternating black / light-gray segments
    for i in range(n_segs):
        fc = "black" if i % 2 == 0 else "lightgray"
        ax.add_patch(mpatches.Rectangle(
            (x0 + i * seg, y0), seg, bar_h,
            facecolor=fc, edgecolor="black", linewidth=0.7,
            transform=ax.transAxes, zorder=10, clip_on=False,
        ))

    # Labels: only at 0, midpoint, and end to avoid crowding
    label_at = {0, n_segs // 2, n_segs}
    for i in range(n_segs + 1):
        if i not in label_at:
            continue
        km_val = i * step_km
        label  = f"{km_val} km" if i == n_segs else str(km_val)
        ax.text(x0 + i * seg, y0 + bar_h * 1.5, label,
                transform=ax.transAxes, ha="center", va="bottom",
                fontsize=6.5, color="#1a1a1a", zorder=11, clip_on=False)


def _choropleth(
    gdf: gpd.GeoDataFrame, col: str, ax: plt.Axes,
    vmin: float, vmax: float, missing_colour: str = "#cccccc",
) -> None:
    norm       = mcolors.Normalize(vmin=vmin, vmax=vmax)
    scalar_map = cm.ScalarMappable(norm=norm, cmap=CMAP)
    for _, row in gdf.iterrows():
        val    = row.get(col)
        colour = scalar_map.to_rgba(val) if pd.notna(val) else missing_colour
        gpd.GeoDataFrame([row], geometry="geometry").plot(
            ax=ax, color=[colour], edgecolor=_EDGE, linewidth=_EDGE_W,
        )


def _add_colorbar(
    fig: plt.Figure, ax: plt.Axes,
    vmin: float, vmax: float, label: str,
    fmt: str = "{:.0f}",
) -> None:
    sm = cm.ScalarMappable(cmap=CMAP, norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical",
                        fraction=0.035, pad=0.02, shrink=0.75)
    cbar.set_label(label, fontsize=8, labelpad=6)
    cbar.locator   = mticker.MaxNLocator(nbins=6)
    cbar.formatter = mticker.FuncFormatter(lambda x, _: fmt.format(x))
    cbar.update_ticks()


def _label_divisions(
    ax: plt.Axes,
    gdf: gpd.GeoDataFrame,
    extra: dict[str, str] | None = None,
) -> None:
    for _, row in gdf.iterrows():
        name = row["div_name"]
        cx   = row.geometry.centroid.x
        cy   = row.geometry.centroid.y
        dx, dy = _LABEL_OFFSETS.get(name, (0, 0))
        text = f"{name}\n{extra[name]}" if extra and name in extra else name
        ax.text(
            cx + dx, cy + dy, text,
            fontsize=6.5, ha="center", va="center",
            color="#111111", fontweight="semibold",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.72),
        )


def _center_lat(gdf: gpd.GeoDataFrame) -> float:
    b = gdf.total_bounds
    return (b[1] + b[3]) / 2


# ── Map 1: Cumulative cases ───────────────────────────────────────────────────
def map_cumulative_cases(out_dir: Path) -> None:
    gdf = _load_adm1()
    cum = {r[0].rstrip("\xb9"): r[1] for r in DIVISION_CUMULATIVE}
    gdf["cum_cases"] = gdf["div_name"].map(cum)

    vmin, vmax = 0, max(cum.values())

    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_facecolor(_BG); fig.patch.set_facecolor("white")

    _choropleth(gdf, "cum_cases", ax, vmin, vmax)
    _label_divisions(ax, gdf, {k: f"{v:,}" for k, v in cum.items()})
    _tight_bounds(gdf, ax)
    _draw_compass_inset(ax, size_pct=18, loc="upper right")
    _draw_scale_bar_transaxes(ax, _center_lat(gdf), length_km=200)
    _add_colorbar(fig, ax, vmin, vmax, "Cumulative TB cases (2000-2024)", fmt="{:,.0f}")

    ax.set_title("Cumulative TB Case Burden by Division\nBangladesh, 2000-2024",
                 fontsize=10, fontweight="bold", pad=8)
    ax.set_axis_off()
    _save(fig, out_dir / "map1_cumulative_cases.png")


# ── Map 2: Cumulative deaths ──────────────────────────────────────────────────
def map_cumulative_deaths(out_dir: Path) -> None:
    gdf    = _load_adm1()
    deaths = {r[0].rstrip("\xb9"): r[2] for r in DIVISION_CUMULATIVE}
    gdf["cum_deaths"] = gdf["div_name"].map(deaths)

    vmin, vmax = 0, max(deaths.values())

    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_facecolor(_BG); fig.patch.set_facecolor("white")

    _choropleth(gdf, "cum_deaths", ax, vmin, vmax)
    _label_divisions(ax, gdf, {k: f"{v:,}" for k, v in deaths.items()})
    _tight_bounds(gdf, ax)
    _draw_compass_inset(ax, size_pct=18, loc="upper right")
    _draw_scale_bar_transaxes(ax, _center_lat(gdf), length_km=200)
    _add_colorbar(fig, ax, vmin, vmax, "Estimated TB deaths (2000-2024)", fmt="{:,.0f}")

    ax.set_title("Estimated Cumulative TB Deaths by Division\nBangladesh, 2000-2024",
                 fontsize=10, fontweight="bold", pad=8)
    ax.set_axis_off()
    _save(fig, out_dir / "map2_cumulative_deaths.png")


# ── Map 3: Small-multiple incidence panels ────────────────────────────────────
def map_incidence_small_multiples(out_dir: Path) -> None:
    gdf = _load_adm1()
    lat = _center_lat(gdf)

    _DIVS     = ["Barishal", "Chattogram", "Dhaka", "Khulna",
                 "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"]
    key_years = [2000, 2005, 2010, 2015, 2020, 2024]

    rate_by_year:  dict[int, dict[str, float]] = {}
    cases_by_year: dict[int, dict[str, int]]   = {}
    for row in DIVISION_INCIDENCE:
        yr = row[0]
        if yr in key_years:
            rate_by_year[yr]  = {d: row[1 + j * 2] for j, d in enumerate(_DIVS)}
            cases_by_year[yr] = {d: row[2 + j * 2] for j, d in enumerate(_DIVS)}

    all_rates = [v for d in rate_by_year.values() for v in d.values() if v is not None]
    vmin, vmax = 0, max(all_rates)

    # Panel geometry: each panel ~2.8 × 3.62 in (respects Bangladesh's degree aspect ratio)
    fig, axes = plt.subplots(
        2, 3,
        figsize=(8.4, 7.24),
    )
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.01, right=0.88, top=0.91, bottom=0.02,
                        wspace=0.04, hspace=0.10)

    for idx, (ax, yr) in enumerate(zip(axes.flat, key_years)):
        ax.set_facecolor(_BG)
        gdf["rate"]  = gdf["div_name"].map(rate_by_year.get(yr, {}))
        gdf["cases"] = gdf["div_name"].map(cases_by_year.get(yr, {}))
        _choropleth(gdf, "rate", ax, vmin, vmax)
        _tight_bounds(gdf, ax, pad=0.02)

        # Year label with a small gap below the axes top
        ax.set_title(str(yr), fontsize=11, fontweight="bold", pad=5)
        ax.set_axis_off()

        # Division centroid labels: "rate\n(cases)"
        for _, row_g in gdf.iterrows():
            rate  = row_g["rate"]
            cases = row_g["cases"]
            if rate is None or (isinstance(rate, float) and np.isnan(rate)):
                continue
            cx, cy = row_g.geometry.centroid.x, row_g.geometry.centroid.y
            label = f"{int(rate)}\n({int(cases):,})"
            ax.text(cx, cy, label,
                    ha="center", va="center",
                    fontsize=5.2, fontweight="bold",
                    color="white",
                    bbox=dict(boxstyle="round,pad=0.15", fc="none", ec="none"),
                    zorder=5)

    # ONE compass rose in top-right panel (axes[0, 2])
    _draw_compass_inset(axes[0, 2], size_pct=22, loc="upper right", bbox_pad=-0.02)

    # ONE scale bar in bottom-left panel (axes[1, 0])
    _draw_scale_bar_transaxes(axes[1, 0], lat, length_km=200, x0=0.06, y0=0.05)

    # Shared colorbar on the right
    sm = cm.ScalarMappable(cmap=CMAP, norm=mcolors.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar_ax = fig.add_axes([0.895, 0.10, 0.022, 0.80])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="vertical")
    cbar.set_label("Incidence rate\n(per 100,000)", fontsize=9, labelpad=6)
    cbar.locator = mticker.MaxNLocator(nbins=6)
    cbar.update_ticks()

    fig.suptitle("Division-wise TB Incidence Rate — Bangladesh",
                 fontsize=13, fontweight="bold", y=0.975)
    _save(fig, out_dir / "map3_incidence_small_multiples.png")


# ── Map 4: Incidence 2024 with rate labels ────────────────────────────────────
def map_incidence_2024(out_dir: Path) -> None:
    gdf    = _load_adm1()
    _DIVS  = ["Barishal", "Chattogram", "Dhaka", "Khulna",
              "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"]

    latest = next(r for r in reversed(DIVISION_INCIDENCE) if r[0] == 2024)
    rates  = {d: latest[1 + j * 2] for j, d in enumerate(_DIVS)}
    gdf["rate_2024"] = gdf["div_name"].map(rates)

    vmin, vmax = 0, max(v for v in rates.values() if v)

    fig, ax = plt.subplots(figsize=(5.5, 7.5))
    ax.set_facecolor(_BG); fig.patch.set_facecolor("white")

    _choropleth(gdf, "rate_2024", ax, vmin, vmax)
    _label_divisions(ax, gdf, {k: f"{v:.0f}/100k" for k, v in rates.items() if v})
    _tight_bounds(gdf, ax)
    _draw_compass_inset(ax, size_pct=18, loc="upper right")
    _draw_scale_bar_transaxes(ax, _center_lat(gdf), length_km=200)
    _add_colorbar(fig, ax, vmin, vmax, "TB incidence rate (per 100,000)", fmt="{:.0f}")

    ax.set_title("TB Incidence Rate by Division — Bangladesh, 2024",
                 fontsize=10, fontweight="bold", pad=8)
    ax.set_axis_off()
    _save(fig, out_dir / "map4_incidence_2024.png")


# ── Map 5: South Asia regional context ───────────────────────────────────────
def map_south_asia_context(estimates: dict, out_dir: Path) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        world = gpd.read_file(_SHP_WORLD)

    sa_names = ["India", "Myanmar", "Nepal", "Bhutan", "China",
                "Pakistan", "Bangladesh", "Sri Lanka", "Afghanistan"]
    sa = world[world["NAME"].isin(sa_names)].copy()

    _inc_rates = {
        "India": 195, "Pakistan": 268, "Myanmar": 270, "Nepal": 130,
        "Bhutan": 145, "Sri Lanka": 64, "China": 55,
        "Bangladesh": 221, "Afghanistan": 189,
    }
    for yr in ["2024", "2023", "2022"]:
        e = estimates.get(yr, {})
        v = e.get("e_inc_100k", "")
        if v not in ("", None):
            try:
                _inc_rates["Bangladesh"] = float(v); break
            except (ValueError, TypeError):
                pass

    sa["inc_rate"] = sa["NAME"].map(_inc_rates)

    sa_bounds  = sa.total_bounds
    center_lat = (sa_bounds[1] + sa_bounds[3]) / 2

    vmin, vmax = 50, 300
    norm       = mcolors.Normalize(vmin=vmin, vmax=vmax)
    scalar_map = cm.ScalarMappable(norm=norm, cmap=CMAP)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_facecolor(_BG); fig.patch.set_facecolor("white")

    for _, row in sa.iterrows():
        val    = row.get("inc_rate")
        colour = scalar_map.to_rgba(val) if pd.notna(val) else "#cccccc"
        ew     = 1.8 if row["NAME"] == "Bangladesh" else 0.5
        ec     = "#CC0000" if row["NAME"] == "Bangladesh" else _EDGE
        gpd.GeoDataFrame([row], geometry="geometry").plot(
            ax=ax, color=[colour], edgecolor=ec, linewidth=ew,
        )

    for _, row in sa.iterrows():
        cx   = row.geometry.centroid.x
        cy   = row.geometry.centroid.y
        rate = row.get("inc_rate")
        text = f"{row['NAME']}\n{rate:.0f}/100k" if pd.notna(rate) else row["NAME"]
        bold = "bold" if row["NAME"] == "Bangladesh" else "normal"
        ax.text(cx, cy, text, fontsize=7, ha="center", va="center",
                fontweight=bold, color="#111111",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="none", alpha=0.70))

    sm = cm.ScalarMappable(cmap=CMAP, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical",
                        fraction=0.030, pad=0.02, shrink=0.70)
    cbar.set_label("TB incidence rate (per 100,000)", fontsize=8)
    cbar.locator = mticker.MaxNLocator(nbins=6)
    cbar.update_ticks()

    bd_patch = mpatches.Patch(edgecolor="#CC0000", facecolor="none",
                              linewidth=1.8, label="Bangladesh (highlighted)")
    ax.legend(handles=[bd_patch], loc="lower right", fontsize=7, frameon=True)

    ax.autoscale(False)
    _draw_compass_inset(ax, size_pct=12, loc="upper left", bbox_pad=0.01)
    _draw_scale_bar_transaxes(ax, center_lat, length_km=1000, n_segs=4, x0=0.05, y0=0.04)

    ax.set_title("TB Incidence Rate in South Asia — Most Recent Estimates",
                 fontsize=11, fontweight="bold", pad=8)
    ax.set_axis_off()
    _save(fig, out_dir / "map5_south_asia_context.png")


# ── Map 6: % reduction in incidence rate by division ─────────────────────────
def map_incidence_reduction(out_dir: Path) -> None:
    """
    Choropleth of % reduction in TB incidence rate per division.
    Baseline: 2000 for all divisions; 2015 for Mymensingh (year it was established).
    """
    gdf   = _load_adm1()
    _DIVS = ["Barishal", "Chattogram", "Dhaka", "Khulna",
             "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"]

    baseline_year: dict[str, int] = {d: 2000 for d in _DIVS}
    baseline_year["Mymensingh"] = 2015

    rate_baseline: dict[str, float | None] = {}
    rate_2024:     dict[str, float | None] = {}
    for row in DIVISION_INCIDENCE:
        yr = row[0]
        for j, div in enumerate(_DIVS):
            if yr == baseline_year[div] and div not in rate_baseline:
                rate_baseline[div] = row[1 + j * 2]
            if yr == 2024:
                rate_2024[div] = row[1 + j * 2]

    pct_change: dict[str, float] = {}
    for div in _DIVS:
        r0 = rate_baseline.get(div)
        r1 = rate_2024.get(div)
        if r0 and r1 and r0 != 0:
            pct_change[div] = round((r0 - r1) / r0 * 100, 1)

    vmin, vmax = min(pct_change.values()), max(pct_change.values())
    norm        = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sm          = cm.ScalarMappable(norm=norm, cmap=CMAP)

    gdf["pct_red"] = gdf["div_name"].map(pct_change)

    fig, ax = plt.subplots(figsize=(5.5, 7.5))
    ax.set_facecolor(_BG); fig.patch.set_facecolor("white")

    for _, row in gdf.iterrows():
        val    = row.get("pct_red")
        colour = sm.to_rgba(val) if pd.notna(val) else "#cccccc"
        gpd.GeoDataFrame([row], geometry="geometry").plot(
            ax=ax, color=[colour], edgecolor=_EDGE, linewidth=_EDGE_W,
        )

    extra: dict[str, str] = {}
    for div, val in pct_change.items():
        suffix = "†" if div == "Mymensingh" else ""
        extra[div] = f"{val:.0f}%↓{suffix}"
    _label_divisions(ax, gdf, extra)

    _tight_bounds(gdf, ax)
    _draw_compass_inset(ax, size_pct=18, loc="upper right")
    _draw_scale_bar_transaxes(ax, _center_lat(gdf), length_km=200)

    sm2 = cm.ScalarMappable(cmap=CMAP, norm=norm)
    sm2.set_array([])
    cbar = fig.colorbar(sm2, ax=ax, orientation="vertical",
                        fraction=0.035, pad=0.02, shrink=0.75)
    cbar.set_label("Reduction in incidence rate (%)", fontsize=8, labelpad=6)
    cbar.locator   = mticker.MaxNLocator(nbins=6)
    cbar.formatter = mticker.FuncFormatter(lambda x, _: f"{x:.0f}%")
    cbar.update_ticks()

    ax.set_title("% Reduction in TB Incidence Rate by Division\nBangladesh, 2000–2024",
                 fontsize=10, fontweight="bold", pad=8)
    ax.set_axis_off()

    ax.text(0.01, -0.02,
            "† Mymensingh est. 2015; reduction calculated from 2015 baseline.",
            transform=ax.transAxes, fontsize=7.5, color="black",
            va="top", clip_on=False)

    _save(fig, out_dir / "map6_incidence_reduction.png")


# ── Entry point ───────────────────────────────────────────────────────────────
def build_all(estimates: dict, out_dir: Path) -> list[Path]:
    print("    Map 1: Cumulative cases choropleth")
    map_cumulative_cases(out_dir)
    print("    Map 2: Cumulative deaths choropleth")
    map_cumulative_deaths(out_dir)
    print("    Map 3: Incidence small multiples (key years)")
    map_incidence_small_multiples(out_dir)
    print("    Map 4: Incidence 2024 with rate labels")
    map_incidence_2024(out_dir)
    print("    Map 5: South Asia regional context")
    map_south_asia_context(estimates, out_dir)
    print("    Map 6: % reduction in incidence rate 2000→2024")
    map_incidence_reduction(out_dir)
    return sorted(out_dir.glob("map*.png"))
