# TB Bangladesh Review — Data Pipeline

[![GitHub](https://img.shields.io/badge/GitHub-TB__Bangladesh-blue?logo=github)](https://github.com/awnonbhowmik/TB_Bangladesh)

Automated data pipeline for a systematic review of tuberculosis in Bangladesh (2000–2024).
Produces an annotated Excel workbook, publication-quality seaborn figures, choropleth maps, and LaTeX tables from live APIs and curated local datasets.

---

## Output

| Artifact | Location | Description |
|----------|----------|-------------|
| Excel workbook | `data/TB_Bangladesh_Review_Data.xlsx` | 11 sheets, colour-coded, freeze-panes, source notes |
| Figures (PNG) | `outputs/figures/` | 15 seaborn figures at 300 DPI |
| Maps (PNG) | `outputs/maps/` | 6 choropleth maps at 300 DPI |
| LaTeX tables | `outputs/latex/` | 11 booktabs tables + master appendix document |

---

## Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/awnonbhowmik/TB_Bangladesh.git
cd TB_Bangladesh

# 2. Install dependencies (Python 3.13)
python3.13 -m pip install -e .

# 3. Download the Bangladesh division shapefile (not included — 259 MB)
#    https://data.humdata.org/dataset/cod-ab-bgd
#    Extract into: data/bgd_adm_bbs_20201113_shp/

# 4. Run the full pipeline (~2–3 min, requires internet)
python3.13 main.py
```

Outputs are written to `outputs/` and `data/`. All API calls include timeouts; failed fetches fall back to local estimates (flagged yellow in the workbook).

---

## Data Setup

Two files are **not** included in the repository and must be obtained separately:

| File | Reason excluded | How to obtain |
|------|----------------|---------------|
| `data/bgd_adm_bbs_20201113_shp/` | 259 MB — exceeds GitHub limit | [OCHA HDX](https://data.humdata.org/dataset/cod-ab-bgd) — download and extract into `data/` |
| `data/TB_Bangladesh_Review_Data.xlsx` | Generated artefact | Run `python3.13 main.py` to regenerate |

The Natural Earth world shapefile (`data/ne_110m_admin_0_countries/`) **is** included in the repo (764 KB).

---

## Data Sources

### TB Epidemiology — WHO Global TB Programme

**URL:** `https://extranet.who.int/tme/generateCSV.asp`

Three datasets fetched at runtime via CSV download:

| Dataset | Parameter | Sheet(s) | Figures |
|---------|-----------|----------|---------|
| Burden estimates | `ds=estimates` | Sheet 1 | Fig 1, 2, 3 |
| Case notifications | `ds=notifications` | Sheet 2, 4, 5 | Fig 3, 4, 5 |
| Treatment outcomes | `ds=outcomes` | Sheet 3 | Fig 3 |

**Key fields used:**
- `e_inc_num`, `e_inc_num_lo`, `e_inc_num_hi` — estimated incident cases (absolute, with 95% CI)
- `e_inc_100k` — incidence rate per 100,000
- `e_mort_exc_tbhiv_num` — estimated TB mortality (HIV-negative)
- `e_tbhiv_prct` — HIV-TB co-infection percentage
- `c_newinc` — notified new and relapse cases
- `c_cdr` — case detection rate
- `cfr` — case fatality ratio

**Coverage:** 2000–2024 (most recent year subject to WHO publication schedule).
**Citation:** WHO Global Tuberculosis Report, annual.

---

### Socioeconomic Indicators — World Bank Open Data API

**Base URL:** `https://api.worldbank.org/v2/country/BD/indicator/{CODE}?format=json`

| Indicator | World Bank Code | Sheet |
|-----------|----------------|-------|
| GDP per capita (current USD) | `NY.GDP.PCAP.CD` | Sheet 8 |
| GNI per capita (current USD) | `NY.GNP.PCAP.CD` | Sheet 8 |
| Total population | `SP.POP.TOTL` | Sheet 8 |
| Urban population (% of total) | `SP.URB.TOTL.IN.ZS` | Sheet 8 |
| Poverty headcount ratio (<$2.15/day) | `SI.POV.DDAY` | Sheet 8 |
| Current health expenditure per capita | `SH.XPD.CHEX.PC.CD` | Sheet 8 |
| BCG immunisation coverage (% of 1-year-olds) | `SH.IMM.IBCG` | Sheet 8 |

**Coverage:** 2000–2024 (some indicators lag 1–2 years).
**Citation:** World Bank Open Data. https://data.worldbank.org

---

### PM2.5 Air Pollution — Three merged sources

PM2.5 data is assembled from three sources in priority order:

#### 1. World Bank `EN.ATM.PM25.MC.M3` (2000–2020)
**URL:** `https://api.worldbank.org/v2/country/BD/indicator/EN.ATM.PM25.MC.M3`
National population-weighted mean annual PM2.5 exposure (µg/m³). Satellite-derived (van Donkelaar et al., processed by WHO/World Bank). Most methodologically consistent series for the 2000–2020 period.

#### 2. WHO GHO `SDGPM25` (2021–2023)
**URL:** `https://ghoapi.azureedge.net/api/SDGPM25`
WHO Global Health Observatory SDG indicator for ambient PM2.5 concentration. Filtered to `RESIDENCEAREATYPE_TOTL` (national total). Fills the gap left by the World Bank series which ends at 2020.

#### 3. CAMS Reanalysis via Open-Meteo (2024)
**URL:** `https://air-quality-api.open-meteo.com/v1/air-quality`
Copernicus Atmosphere Monitoring Service (CAMS) hourly PM2.5 reanalysis at lat=23.685, lon=90.356 (Bangladesh centroid). Hourly values aggregated to annual mean. Used only for 2024, which is not yet covered by the WHO SDG series.

**Sheet:** 9 (Environmental Factors) | **Figure:** Fig 9

---

### Temperature & Humidity — Bangladesh Meteorological Department (BMD)

**Source:** `src/fetchers/local.py` (static data compiled from BMD station records)

Annual Dry Bulb Temperature (mean annual temperature, °C) and Relative Humidity (%) from the **Bangladesh Meteorological Department (BMD) Dhaka station**, sourced from the [DENV-Data-Analysis](https://github.com/awnonbhowmik/DENV-Data-Analysis) consolidated dataset (annual records, 2001–2024).

- **Temperature:** Mean annual Dry Bulb Temperature (°C) at Dhaka BMD station.
- **Humidity:** Annual mean Relative Humidity (%) at Dhaka BMD station.
- **Coverage:** 2001–2024 observed; 2000 estimated from adjacent years.

**Sheet:** 9 | **Figure:** Fig 9

---

### Division-level TB Data — Curated Local Dataset

**Source file:** `src/fetchers/local.py`

Division-level TB data is not available from any public API. It was manually compiled from:
- National TB Control Programme (NTP) annual reports, Bangladesh
- DGDA and IEDCR published surveillance data
- Peer-reviewed literature on regional TB burden

**Data included:**

| Variable | Years | Divisions |
|----------|-------|-----------|
| Annual incidence rate (per 100,000) | 2000–2024 | 8 divisions |
| Annual notified cases (absolute) | 2000–2024 | 8 divisions |
| Cumulative cases 2000–2024 | — | 8 divisions |
| Estimated cumulative deaths 2000–2024 | — | 8 divisions |

**Divisions:** Barishal, Chattogram, Dhaka, Khulna, Mymensingh (from 2015), Rajshahi, Rangpur, Sylhet.

**Note:** Mymensingh was carved out of Dhaka division in 2015; data before 2015 is `None`.

**Sheets:** 6 (Division Annual), 7 (Division Cumulative) | **Maps:** Map 1–5

---


### WHO PM2.5 Safe Limits

**Source:** WHO Global Ambient Air Quality Guidelines

| Guideline | PM2.5 Annual Mean | Year |
|-----------|------------------|------|
| Previous guideline | 10 µg/m³ | Pre-2021 |
| Updated guideline | 5 µg/m³ | 2021 |

**Citation:** World Health Organization (2021). *WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide.*

---

### Human Development Index — UNDP

**Source:** `src/fetchers/local.py` (manually compiled from UNDP HDR)

**URL:** https://hdr.undp.org/data-center/human-development-index

Annual HDI values for Bangladesh (2000–2024) from the UNDP Human Development Report.

**Sheet:** 8

---

### Shapefiles

| File | Source | Used for |
|------|--------|----------|
| `data/bgd_adm_bbs_20201113_shp/` | OCHA HDX — Bangladesh Admin Boundaries | Maps 1–5 (division-level choropleths) |
| `data/ne_110m_admin_0_countries/` | Natural Earth 1:110m Cultural Vectors | Map 6 (South Asia context) |

**Bangladesh shapefile:** https://data.humdata.org/dataset/cod-ab-bgd
**Natural Earth:** https://www.naturalearthdata.com/downloads/110m-cultural-vectors/

Division name mapping applied: `Barisal → Barishal`, `Chittagong → Chattogram` (shapefile uses older spellings).

---

## Project Structure

```
TB_BD/
├── main.py                        # Entry point
├── pyproject.toml                 # Dependencies (Python 3.13)
├── src/
│   ├── workbook.py                # Pipeline orchestrator
│   ├── styles.py                  # Excel styling utilities
│   ├── fetchers/
│   │   ├── who.py                 # WHO TB Programme API
│   │   ├── worldbank.py           # World Bank Open Data API
│   │   ├── climate.py             # PM2.5 merged (World Bank + WHO GHO + CAMS)
│   │   └── local.py               # Curated division-level data, HDI, humidity
│   └── builders/
│       ├── burden.py              # Sheet 1: TB Burden Estimates
│       ├── notifications.py       # Sheet 2: Notifications & Performance
│       ├── outcomes.py            # Sheet 3: Treatment Outcomes
│       ├── hivtb.py               # Sheet 4: HIV-TB Co-infection
│       ├── demographics.py        # Sheet 5: Sex & Age Distribution
│       ├── division.py            # Sheets 6–7: Division-wise Data
│       ├── socioeconomic.py       # Sheet 8: Socioeconomic Indicators
│       ├── environmental.py       # Sheet 9: Environmental Factors
│       ├── sources.py             # Sheet 10: Data Sources
│       ├── figures.py             # 9 seaborn figures
│       ├── maps.py                # 6 choropleth maps (geopandas)
│       └── latex_tables.py        # LaTeX booktabs tables
├── data/                          # Input data only
│   ├── bgd_adm_bbs_20201113_shp/  # Bangladesh division shapefile
│   └── ne_110m_admin_0_countries/ # Natural Earth world shapefile
└── outputs/                       # Generated figures/maps/tables (git-ignored)
    ├── figures/                   # fig1–fig9 (.png)
    ├── maps/                      # map1–map6 (.png)
    └── latex/                     # table1–table7.tex + appendix
```

---

## Workbook Sheets

| # | Sheet | Primary Source |
|---|-------|---------------|
| 1 | TB Burden Estimates | WHO Global TB Programme |
| 2 | Notifications & Performance | WHO Global TB Programme |
| 3 | Treatment Outcomes | WHO Global TB Programme |
| 4 | HIV-TB Co-infection | WHO Global TB Programme |
| 5 | Sex & Age Distribution | WHO Global TB Programme |
| 6 | Division-wise Annual Incidence | NTP / local curated |
| 7 | Division Cumulative Summary | NTP / local curated |
| 8 | Socioeconomic Indicators | World Bank Open Data |
| 9 | Environmental Factors | BMD (temperature, humidity), World Bank, WHO GHO, CAMS (PM2.5) |
| 10 | Data Sources | — |
| 11 | Risk Factors | World Bank (undernourishment, child stunting, smoking, health exp % GDP) |

**Colour coding:** Yellow cells = estimated/modelled value used (real data unavailable). Tab colours group related sheets.

---

## Figures

| Figure | Title | Source |
|--------|-------|--------|
| Fig 1 | TB Incidence vs Notified Cases (detection gap) | WHO |
| Fig 2 | TB Mortality Trend | WHO |
| Fig 3 | Case Detection Rate & Treatment Success Rate | WHO |
| Fig 4 | HIV-TB Co-infection Trend | WHO |
| Fig 5 | Notified Cases by Sex & Age Group | WHO |
| Fig 6 | Division-wise Incidence Heatmap | Local / NTP |
| Fig 7 | Cumulative Cases vs Deaths by Division | Local / NTP |
| Fig 8 | Incidence vs Population Density Scatter | WHO + World Bank |
| Fig 9 | PM2.5 & Temperature Trends | World Bank, WHO GHO, CAMS (PM2.5); BMD (temperature) |
| Fig 10 | Socioeconomic Trends Panel (GDP, poverty, HDI, population) | World Bank; UNDP; Worldometer |
| Fig 11 | Poverty Rate vs TB Incidence Scatter | World Bank; WHO |
| Fig 12 | MDR/RR-TB Trend (cases + % of total notified) | WHO Global TB Programme |
| Fig 13 | Risk Factors Panel (undernourishment, stunting, smoking, health exp) | World Bank |

---

## Maps

| Map | Title | Source |
|-----|-------|--------|
| Map 1 | Cumulative TB Cases by Division (2000–2024) | Local / NTP |
| Map 2 | Estimated Cumulative Deaths by Division | Local / NTP |
| Map 3 | Division Incidence Rate — Key Years (2000–2024) | Local / NTP |
| Map 4 | TB Incidence Rate by Division — 2024 | Local / NTP |
| Map 5 | TB Incidence Rate in South Asia (context) | WHO + Natural Earth |
| Map 6 | % Reduction in TB Incidence Rate by Division (2000→2024) | Local / NTP |

All Bangladesh maps use a custom colormap anchored at 0. Compass rose and 200 km scale bar on every map. Map 3 uses a single shared compass and scale bar. Map 6 uses RdYlGn colormap (green = greater improvement). Division-level CFR data is presented in Table 4 and Table 7. *Mymensingh division (est. 2015) shown as N/A on Map 6.

---

## Dependencies

```toml
python = ">=3.13"
openpyxl = ">=3.1"      # Excel workbook generation
requests = ">=2.32"      # API fetching
matplotlib = ">=3.9"     # Plotting backend
seaborn = ">=0.13"       # Statistical figures
pandas = ">=2.2"         # Data manipulation
numpy = ">=1.26"         # Numerical operations
geopandas = ">=1.0"      # Choropleth maps
shapely = ">=2.0"        # Geometry operations
pyogrio = ">=0.10"       # Shapefile I/O backend
```

Install with: `python3.13 -m pip install -e .`
