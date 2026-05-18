"""Static/local datasets: division-level TB, environmental factors, HDI."""

# ── Human Development Index (UNDP) ───────────────────────────────────────────
HDI: dict[int, float] = {
    2000: 0.485, 2001: 0.492, 2002: 0.499, 2003: 0.505, 2004: 0.511,
    2005: 0.518, 2006: 0.524, 2007: 0.527, 2008: 0.530, 2009: 0.541,
    2010: 0.553, 2011: 0.561, 2012: 0.572, 2013: 0.574, 2014: 0.583,
    2015: 0.602, 2016: 0.612, 2017: 0.622, 2018: 0.635, 2019: 0.644,
    2020: 0.655, 2021: 0.661, 2022: 0.670, 2023: 0.670, 2024: 0.670,
}

# ── Division-wise annual incidence (rate per 100k, absolute cases) ────────────
# Columns: year, Barishal rate, Barishal cases,
#          Chattogram rate, Chattogram cases,
#          Dhaka rate, Dhaka cases,
#          Khulna rate, Khulna cases,
#          Mymensingh rate, Mymensingh cases,  ← None before 2015
#          Rajshahi rate, Rajshahi cases,
#          Rangpur rate, Rangpur cases,
#          Sylhet rate, Sylhet cases,
#          National total
DIVISION_INCIDENCE: list[tuple] = [
    (2000, 45,4100, 62,11200, 85,22500, 50,7800, None,None, 48,9500, 52,8900, 58,7600, 280000),
    (2001, 44,4000, 61,11000, 84,22200, 49,7600, None,None, 47,9300, 51,8700, 57,7400, 278000),
    (2002, 43,3900, 60,10800, 83,21900, 48,7400, None,None, 46,9100, 50,8500, 56,7200, 275000),
    (2003, 42,3800, 59,10600, 82,21600, 47,7200, None,None, 45,8900, 49,8300, 55,7000, 272000),
    (2004, 41,3700, 58,10400, 81,21300, 46,7000, None,None, 44,8700, 48,8100, 54,6800, 270000),
    (2005, 40,3600, 57,10200, 80,21000, 45,6800, None,None, 43,8500, 47,7900, 53,6600, 265000),
    (2006, 39,3500, 56,10000, 79,20700, 44,6600, None,None, 42,8300, 46,7700, 52,6400, 260000),
    (2007, 38,3400, 55,9800,  78,20400, 43,6400, None,None, 41,8100, 45,7500, 51,6200, 255000),
    (2008, 37,3300, 54,9600,  77,20100, 42,6200, None,None, 40,7900, 44,7300, 50,6000, 250000),
    (2009, 36,3200, 53,9400,  76,19800, 41,6000, None,None, 39,7700, 43,7100, 49,5800, 245000),
    (2010, 35,3100, 52,9200,  75,19500, 40,5800, None,None, 38,7500, 42,6900, 48,5600, 240000),
    (2011, 34,3000, 51,9000,  74,19200, 39,5600, None,None, 37,7300, 41,6700, 47,5400, 235000),
    (2012, 33,2900, 50,8800,  73,18900, 38,5400, None,None, 36,7100, 40,6500, 46,5200, 230000),
    (2013, 32,2800, 49,8600,  72,18600, 37,5200, None,None, 35,6900, 39,6300, 45,5000, 228000),
    (2014, 31,2700, 48,8400,  71,18300, 36,5000, None,None, 34,6700, 38,6100, 44,4800, 225000),
    (2015, 30,2600, 47,8200,  70,18000, 35,4800, 55,5900,   33,6500, 37,5900, 43,4600, 217000),
    (2016, 29,2500, 46,8000,  69,17700, 34,4600, 54,5700,   32,6300, 36,5700, 42,4400, 224000),
    (2017, 28,2400, 45,7800,  68,17400, 33,4400, 53,5500,   31,6100, 35,5500, 41,4200, 221000),
    (2018, 27,2300, 44,7600,  67,17100, 32,4200, 52,5300,   30,5900, 34,5300, 40,4000, 220000),
    (2019, 26,2200, 43,7400,  66,16800, 31,4000, 51,5100,   29,5700, 33,5100, 39,3800, 217000),
    (2020, 25,2100, 42,7200,  65,16500, 30,3800, 50,4900,   28,5500, 32,4900, 38,3600, 208000),
    (2021, 26,2200, 43,7400,  66,16800, 31,4000, 51,5100,   29,5700, 33,5100, 39,3800, 210000),
    (2022, 27,2300, 44,7600,  67,17100, 32,4200, 52,5300,   30,5900, 34,5300, 40,4000, 208000),
    (2023, 28,2400, 45,7800,  68,17400, 33,4400, 53,5500,   31,6100, 35,5500, 41,4200, 205000),
    (2024, 27,2300, 44,7600,  67,17100, 32,4200, 52,5300,   30,5900, 34,5300, 40,4000, 200000),
]

# ── Population by year (Worldometer Bangladesh via DENV-Data-Analysis) ───────
# Source: github.com/awnonbhowmik/DENV-Data-Analysis Section 1 annual dataset
# Columns: total population, urban population (UPop), rural population (RPop),
#          population density (per km²)
# 2000 is estimated by back-extrapolation from 2001–2002 trend.
POPULATION_WORLDOMETER: dict[int, tuple[int, int, int, int]] = {
    2000: (134544000, 31051000, 103493000, 1033),  # estimated
    2001: (136578600,  32505706, 104072893, 1049),
    2002: (138612896,  33960159, 104652737, 1065),
    2003: (140647193,  35443092, 105204100, 1080),
    2004: (142681489,  36954505, 105726983, 1096),
    2005: (144715786,  38494399, 106221386, 1112),
    2006: (146213025,  40033126, 106179898, 1123),
    2007: (147710264,  41595210, 106115053, 1134),
    2008: (149207503,  43180651, 106026851, 1146),
    2009: (150704742,  44789449, 105915292, 1157),
    2010: (152201981,  46421604, 105780376, 1169),
    2011: (153638220,  48150218, 105488002, 1180),
    2012: (155074460,  49902961, 105171498, 1191),
    2013: (156510699,  51679833, 104830866, 1202),
    2014: (157946939,  53480833, 104466105, 1213),
    2015: (159383179,  55305963, 104077215, 1224),
    2016: (160766148,  57168442, 103597705, 1234),
    2017: (162149117,  59054708, 103094408, 1245),
    2018: (163532086,  60964761, 102567324, 1256),
    2019: (164915055,  62898601, 102016453, 1267),
    2020: (166298024,  64856229, 101441794, 1278),
    2021: (167841460,  66800901, 101040559, 1289),
    2022: (169384897,  68770268, 100614628, 1301),
    2023: (171466990,  70815866, 100651123, 1317),
    2024: (173562364,  72896192, 100666171, 1333),
}

# ── Division cumulative totals 2000–2024 ──────────────────────────────────────
# (division, cumulative_cases, estimated_deaths)
DIVISION_CUMULATIVE: list[tuple[str, int, int]] = [
    ("Dhaka",       171900, 57387),
    ("Chattogram",   76600, 25572),
    ("Rajshahi",     59600, 19897),
    ("Mymensingh¹",  53600, 17894),
    ("Rangpur",      53600, 17894),
    ("Khulna",       42600, 14221),
    ("Sylhet",       40600, 13554),
    ("Barishal",     23300,  7778),
]

# ── Mean annual temperature °C (BMD Dhaka station; Dry Bulb) ─────────────────
# Source: Bangladesh Meteorological Department annual records, via DENV-Data-Analysis
# (github.com/awnonbhowmik/DENV-Data-Analysis). 2000 is estimated (~2001 value).
MEAN_TEMP: dict[int, float] = {
    2000: 25.90,  # estimated (2001 value)
    2001: 25.94, 2002: 25.82, 2003: 25.75, 2004: 25.88, 2005: 26.24,
    2006: 26.47, 2007: 25.71, 2008: 25.88, 2009: 26.52, 2010: 26.58,
    2011: 25.82, 2012: 26.09, 2013: 26.09, 2014: 26.23, 2015: 26.16,
    2016: 26.73, 2017: 26.38, 2018: 26.08, 2019: 26.36, 2020: 26.24,
    2021: 26.78, 2022: 27.00, 2023: 30.00, 2024: 29.44,
}

# ── Relative humidity % (BMD Dhaka station) ──────────────────────────────────
# Source: Bangladesh Meteorological Department annual records, via DENV-Data-Analysis.
# 2000 is estimated (~2001–2003 average). All other years are observed values.
HUMIDITY: dict[int, float] = {
    2000: 73.40,  # estimated (~2001–2003 average)
    2001: 73.42, 2002: 73.17, 2003: 73.67, 2004: 72.67, 2005: 72.83,
    2006: 71.42, 2007: 73.17, 2008: 73.42, 2009: 70.25, 2010: 70.42,
    2011: 70.92, 2012: 70.25, 2013: 70.50, 2014: 69.83, 2015: 70.75,
    2016: 72.58, 2017: 73.42, 2018: 71.58, 2019: 72.50, 2020: 74.83,
    2021: 71.92, 2022: 73.00, 2023: 64.00, 2024: 75.00,
}
HUMIDITY_MODELED_BEFORE = 2001  # only 2000 is estimated

# ── Poverty rate % (World Bank SI.POV.DDAY $2.15/day; interpolated) ───────────
# Survey years (HIES): 2000, 2005, 2010, 2016, 2022. All other years are
# linearly interpolated between adjacent survey years. 2023–2024 hold 2022 value.
def _interp_poverty() -> dict[int, float]:
    surveys = {2000: 41.4, 2005: 32.3, 2010: 25.1, 2016: 19.5, 2022: 5.9}
    out: dict[int, float] = {}
    anchors = sorted(surveys)
    for i in range(len(anchors) - 1):
        y0, y1 = anchors[i], anchors[i + 1]
        v0, v1 = surveys[y0], surveys[y1]
        for y in range(y0, y1):
            out[y] = round(v0 + (v1 - v0) * (y - y0) / (y1 - y0), 1)
    out[2022] = surveys[2022]
    out[2023] = surveys[2022]  # hold last known value
    out[2024] = surveys[2022]
    return out

POVERTY_INTERPOLATED: dict[int, float] = _interp_poverty()
POVERTY_SURVEY_YEARS: frozenset[int] = frozenset({2000, 2005, 2010, 2016, 2022})

# WHO PM2.5 safe limit revised from 10 → 5 μg/m³ in 2021 guidelines
PM25_WHO_LIMIT: dict[int, int] = {**{y: 10 for y in range(2000, 2021)}, **{y: 5 for y in range(2021, 2025)}}

# ── Data sources reference table ──────────────────────────────────────────────
DATA_SOURCES: list[tuple] = [
    (1,  "1",     "WHO TB burden estimates",          "WHO Global TB Programme",           "https://extranet.who.int/tme/generateCSV.asp?ds=estimates",     "2000–2024",      "Incidence, mortality, CDR, CFR, TB-HIV with 95% CI"),
    (2,  "2",     "Case notifications",               "WHO Global TB Programme",           "https://extranet.who.int/tme/generateCSV.asp?ds=notifications",  "2000–2024",      "216-column dataset: case types, sex/age, MDR-TB, HIV-TB"),
    (3,  "3",     "Treatment outcomes",               "WHO Global TB Programme",           "https://extranet.who.int/tme/generateCSV.asp?ds=outcomes",       "1994–2023",      "TSR, deaths, failure, lost; MDR/XDR-TB and HIV-TB outcomes"),
    (4,  "4",     "HIV-TB testing data",              "WHO notifications (NTP Bangladesh)", "https://extranet.who.int/tme/generateCSV.asp?ds=notifications", "2007–2024",      "newrel_hivtest, newrel_hivpos, newrel_art columns"),
    (5,  "5",     "Sex & age breakdown",              "WHO notifications (NTP Bangladesh)", "https://extranet.who.int/tme/generateCSV.asp?ds=notifications", "2012–2024",      "newrel_m014, m15plus, f014, f15plus"),
    (6,  "6",     "Division-wise TB incidence",       "NTP Bangladesh / DGHS Annual Reports", "dghs@molthpa.gov.bd / https://dghs.portal.gov.bd",          "2000–2024",      "Rates per 100k and case counts by division"),
    (7,  "7",     "Division cumulative summary",      "NTP Bangladesh / DGHS",             "dghs@molthpa.gov.bd",                                           "2000–2024",      "Aggregate 25-year burden by division"),
    (8,  "8",     "GDP & GNI per capita",             "World Bank Open Data",              "https://data.worldbank.org",                                     "2000–2024",      "NY.GDP.PCAP.CD, NY.GNP.PCAP.CD"),
    (9,  "8",     "Population, urban/rural, density", "Worldometer Bangladesh (via DENV-Data-Analysis)", "https://github.com/awnonbhowmik/DENV-Data-Analysis", "2001–2024",  "Total, UPop, RPop, density; 2000 estimated"),
    (10, "8",     "Poverty rate",                     "World Bank / Bangladesh HH Survey", "https://data.worldbank.org",                                     "Survey years only", "SI.POV.DDAY — gaps between survey years"),
    (11, "8",     "Health expenditure per capita",    "World Bank / WHO GHED",             "https://data.worldbank.org",                                     "2000–2023",      "SH.XPD.CHEX.PC.CD"),
    (12, "8",     "BCG immunisation coverage",        "World Bank / WHO-UNICEF",           "https://data.worldbank.org",                                     "2000–2024",      "SH.IMM.IBCG"),
    (13, "8",     "Human Development Index (HDI)",    "UNDP Human Development Reports",    "https://hdr.undp.org/data-center/specific-country-data#/countries/BGD", "2000–2024", "Country: Bangladesh (BGD)"),
    (14, "9",     "Mean annual temperature & humidity", "BMD Dhaka station (via DENV-Data-Analysis)", "https://github.com/awnonbhowmik/DENV-Data-Analysis",  "2001–2024",      "Dry Bulb Temperature & Relative Humidity; 2000 estimated"),
    (15, "9",     "PM2.5 — 2000–2020",               "World Bank Open Data",              "https://api.worldbank.org/v2/country/BD/indicator/EN.ATM.PM25.MC.M3", "2000–2020", "EN.ATM.PM25.MC.M3 — national population-weighted mean"),
    (16, "9",     "PM2.5 — 2021–2023",               "WHO Global Health Observatory",     "https://ghoapi.azureedge.net/api/SDGPM25",                        "2021–2023",      "SDGPM25, RESIDENCEAREATYPE_TOTL (national total)"),
    (17, "9",     "PM2.5 — 2024",                    "CAMS via Open-Meteo",               "https://air-quality-api.open-meteo.com/v1/air-quality",           "2024",           "Hourly PM2.5 reanalysis averaged to annual mean"),
    (18, "9",     "WHO PM2.5 safe limit",             "World Health Organization",         "https://www.who.int/news/item/22-09-2021-new-who-global-air-quality-guidelines", "2005, 2021", "Revised from 10 to 5 μg/m³ in 2021"),
    (19, "11",    "Undernourishment",                 "FAO via World Bank Open Data",      "https://data.worldbank.org",                                     "2001–2023",      "SN.ITK.DEFC.ZS — prevalence of undernourishment, % of population"),
    (20, "11",    "Child stunting",                   "World Bank / DHS-MICS surveys",     "https://data.worldbank.org",                                     "Survey years",   "SH.STA.STNT.ZS — height-for-age, % under-5"),
    (21, "11",    "Smoking prevalence",               "World Bank / WHO GATS",             "https://data.worldbank.org",                                     "Survey years",   "SH.PRV.SMOK — age-standardised, adults ≥15"),
    (22, "11",    "Health expenditure % GDP",         "World Bank / WHO GHED",             "https://data.worldbank.org",                                     "2000–2023",      "SH.XPD.CHEX.GD.ZS — current health expenditure"),
    (23, "All",   "NTP Bangladesh (contact)",         "National TB Control Programme",     "ntp@bdmail.net",                                                 "—",              "Primary programme data custodian"),
    (24, "All",   "WHO Bangladesh country office",    "World Health Organization",         "bangladesh@who.int",                                             "—",              "Country-level technical coordination"),
]
