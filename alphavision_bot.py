"""
AlphaVision — Deep Value Investment Intelligence Engine
Nifty 50 Stock Analysis | 5–7 Year Horizon | Indian Equity Markets
Methodology: alphavision_methodology.md
"""

import os
import math
import asyncio
import time
import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
import pandas as pd
import numpy as np
from supabase import create_client, Client

load_dotenv()

# ==================== CONFIG ====================
X_BEARER_TOKEN   = os.getenv("X_BEARER_TOKEN")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
SUPABASE_URL     = os.getenv("SUPABASE_URL")
SUPABASE_KEY     = os.getenv("SUPABASE_KEY")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

NIFTY_500_STOCKS = [
    # Nifty 50
    "TCS", "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE",
    "LT", "MARUTI", "ASIANPAINT", "SUNPHARMA", "WIPRO", "DRREDDY", "HCLTECH",
    "TECHM", "TATASTEEL", "ADANIPORTS", "POWERGRID", "NTPC", "IOC",
    "HINDUNILVR", "KOTAKBANK", "AXISBANK", "BAJAJFINSV", "BHARTIARTL",
    "TITAN", "NESTLEIND", "ULTRACEMCO", "INDUSINDBK", "TATACONSUM",
    "DIVISLAB", "CIPLA", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO",
    "BRITANNIA", "COALINDIA", "ONGC", "BPCL", "HINDALCO",
    "JSWSTEEL", "TATAMOTORS", "M&M", "GRASIM", "APOLLOHOSP",
    "SBILIFE", "HDFCLIFE", "ADANIENT", "SHREECEM", "PIDILITIND",

    # Nifty Next 50
    "HAVELLS", "VOLTAS", "GODREJCP", "MARICO", "DABUR", "BERGEPAINT",
    "COLPAL", "EMAMILTD", "MUTHOOTFIN", "CHOLAFIN", "BAJAJHLDNG",
    "TORNTPHARM", "ALKEM", "AUROPHARMA", "BIOCON", "LUPIN",
    "LICHSGFIN", "PFC", "RECLTD", "NHPC", "TATAPOWER", "TORNTPOWER",
    "CESC", "JSPL", "SAIL", "ASHOKLEY", "TVSMOTOR", "MRF",
    "MPHASIS", "LTIM", "PERSISTENT", "COFORGE", "OFSS",
    "FEDERALBNK", "IDFCFIRSTB", "BANDHANBNK", "AUBANK",
    "DMART", "TRENT", "PAGEIND", "SIEMENS", "ABB", "CUMMINSIND",
    "THERMAX", "BEL", "HAL", "CONCOR", "SRF", "TATACHEM",
    "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE",

    # Nifty Midcap 150
    "ASTRAL", "SUPREMEIND", "POLYCAB", "KANSAINER", "NILKAMAL",
    "WHIRLPOOL", "SYMPHONY", "BLUESTARCO", "BATAINDIA", "RELAXO",
    "VMART", "SHOPERSTOP", "ABFRL", "RAYMOND", "KPRMILL",
    "GLENMARK", "IPCALAB", "NATCOPHARM", "GRANULES", "LALPATHLAB",
    "METROPOLIS", "MAXHEALTH", "FORTIS", "APOLLOTYRE", "CEATLTD",
    "EXIDEIND", "AMARARAJA", "BALKRISIND", "ESCORTS", "SUNDRMFAST",
    "TATAELXSI", "KPITTECH", "ZENSAR", "RATEGAIN", "TANLA",
    "RBLBANK", "MANAPPURAM", "AAVAS", "HOMEFIRST", "CREDITACC",
    "CANFINHOME", "HUDCO", "IRFC", "IREDA", "SJVN",
    "NATIONALUM", "HINDCOPPER", "MOIL", "GMRINFRA", "IRB",
    "BHEL", "BEML", "COCHINSHIP", "RITES", "IRCON", "KNR", "NCC",
    "NAVINFLUOR", "DEEPAKNTR", "GNFC", "ATUL", "FLUOROCHEM",
    "PHOENIXLTD", "SOBHA", "BRIGADE", "KOLTEPATIL",
    "ABBOTINDIA", "PFIZER", "GLAXO", "SANOFI",
    "MOTHERSON", "BOSCHLTD", "SCHAEFFLER", "TIMKEN", "SKF",
    "TATACOMM", "HFCL", "STLTECH",
    "KALYANKJIL", "PNCINFRA", "AHLUCONT", "MAHLOG",
    "SBICARD", "CHOLAFIN", "SPANDANA", "FUSION", "UGROCAP",
    "UJJIVANSFB", "EQUITASBNK", "SURYODAY",
    "HEXAWARE", "INTELLECT", "MASTEK", "ROUTE",
    "VINATIORGA", "GALAXYSURF", "FINEORG", "ALKYLAMINE", "SUDARSCHEM",

    # Nifty Smallcap 250 (top liquid names)
    "ZOMATO", "NYKAA", "PAYTM", "POLICYBZR", "CARTRADE",
    "EASEMYTRIP", "IRCTC", "RAILVIKAS", "RVNL", "NBCC",
    "HUDCO", "SJVN", "NTPCGREEN", "ADANIGREEN", "ADANIPOWER",
    "ADANITRANS", "ADANIWILMAR", "ADANIPORTS",
    "PATANJALI", "EMUDHRA", "ZAGGLE", "HAPPYMIND",
    "LATENTVIEW", "DATAMATICS", "CYIENT", "LTTS", "BIRLASOFT",
    "NIITTECH", "MPHASIS", "SASKEN", "SONATSOFTW", "NEWGEN",
    "NUCLEUS", "RAMCOCEM", "DALMIANAT", "HEIDELBERG", "BIRLACORPN",
    "JKCEMENT", "ORIENTCEM", "SAGAR", "MANGALAM",
    "PIIND", "BALAMINES", "TATACHEM", "GUJALKALI", "CAMLIN",
    "CLEAN", "ROSSARI", "EPSILON", "ANURAS", "LXCHEM",
    "IGPL", "TDPOWERSYS", "GPPL", "MAHSEAMLES", "RKFORGE",
    "RATNAMANI", "WELCORP", "MSTCLTD", "MOIL", "HINDCOPPER",
    "MIDHANI", "MTNL", "HCLTECH",
    "JBCHEPHARM", "AJANTPHARM", "ERIS", "LINDHURST", "SOLARA",
    "SEQUENT", "SUVEN", "DIVI", "NEULANDLAB", "DISHMAN",
    "WOCKPHARMA", "STRIDES", "CAPLIPOINT", "SMSPHARMA",
    "FINPIPE", "APTUS", "ARMANFIN", "MAS", "SPANDANA",
    "UJJIVAN", "JANA", "ESAFSFB", "REPCO", "SATIN",
    "PAISALO", "SBFC", "VLS", "MUTHOOTMF", "IIISL",
    "NUVOCO", "PRISMJOHNS", "STARCEMENT", "KAKATCEM", "DECCAN",
    "DELTACORP", "WONDERLA", "MAHINDCIE", "ENDURANCE", "SUPRAJIT",
    "SUBROS", "GABRIEL", "JAYINDLTD", "UCALFUEL", "HIKAL",
    "SWARAJENG", "VSTIND", "MAHSCOOTER", "KINETIC",
    "TTKPRESTIG", "HAWKINS", "PRESTIGE", "SKFINDIA", "GRINDWELL",
    "CARBORUNIV", "GRAPHITE", "HLEGLAS", "ASAHIINDIA",
    "CENTURYPLY", "GREENPANEL", "KITEX", "GARFIBRES",
    "SPORTKING", "INDORAMA", "FILATEX", "SPENTEX",
    "BAJAJCON", "JYOTHYLAB", "ZYDUSWELL", "GODFRYPHLP", "VST",
    "RADICO", "GLOBUSSPR", "ABDL", "GMMPFAUDLR",
    "INDIAMART", "JUSTDIAL", "MATRIMONY", "NAUKRI", "INFOEDGE",
    "MAKEMYTRIP", "YATRA", "CLEARTRIP",
    "DELHIVERY", "BLUEDART", "GATI", "MAHINDLOG", "TCI",
    "PGHH", "GILLETTE", "CASTROLIND", "SUPPETRO", "MOLD-TEK",
    "AARTIIND", "VINDHYATEL", "HSCL", "SAREGAMA", "TIPSINDLTD",
    "PVRINOX", "INOXWIND", "SUZLON", "RPOWER", "JSWENERGY",
    "GREENKO", "ACME", "WAAREEENER", "PREMIER",
    "GENESYS", "TANGERINE", "ARVINDFASN", "GOKALDAS",
    "TIRUMALCHM", "AMARAJABAT", "COSMOFILMS", "POLYPLEX",
    "UFLEX", "HUHTAMAKI", "MANJUSHREE", "MOLD-TEK",
    "RESPONIND", "JAMNAAUTO", "SHRIRAMFIN", "CHOICEIN",
    "MOTILALOFS", "IIFL", "ANGELONE", "5PAISA", "GEOJITFSL",
    "ICICIPRULI", "STARHEALTH", "NIACL", "UIIC", "ORIENTINS",
    "GICRE", "ICICIGI", "HDFCAMC", "NIPPONLIFE", "MIRAE",
    "UTIAMC", "ABSLAMC",
]

# Deduplicate while preserving order
seen = set()
NIFTY_500_STOCKS = [s for s in NIFTY_500_STOCKS if not (s in seen or seen.add(s))]
NIFTY_50_STOCKS  = NIFTY_500_STOCKS  # alias used throughout the code

# Sector mapping — replaces yfinance sector lookup
STOCK_SECTOR_MAP = {
    "TCS": "Technology", "INFY": "Technology", "WIPRO": "Technology",
    "HCLTECH": "Technology", "TECHM": "Technology",
    "HDFCBANK": "Financial Services", "ICICIBANK": "Financial Services",
    "SBIN": "Financial Services", "BAJFINANCE": "Financial Services",
    "RELIANCE": "Energy", "NTPC": "Utilities", "POWERGRID": "Utilities",
    "IOC": "Energy", "ADANIPORTS": "Industrials",
    "LT": "Industrials",
    "MARUTI": "Consumer Cyclical",
    "ASIANPAINT": "Consumer Defensive",
    "SUNPHARMA": "Healthcare", "DRREDDY": "Healthcare",
    "TATASTEEL": "Basic Materials",
}

BANKING_SECTORS = {"Financial Services", "Banks", "NBFC"}
LARGE_CAP_THRESHOLD = 20_000_00_00_000   # ₹20,000 Cr in paise → use marketCap in USD, so approx $2.5B
MID_CAP_THRESHOLD   = 5_000_00_00_000    # ₹5,000 Cr

SECTOR_MOAT_MAP = {
    "Technology":           "Switching Costs",
    "Financial Services":   "Switching Costs",
    "Consumer Defensive":   "Intangible Assets",
    "Consumer Cyclical":    "Intangible Assets",
    "Industrials":          "Efficient Scale",
    "Energy":               "Efficient Scale",
    "Healthcare":           "Intangible Assets",
    "Basic Materials":      "No Moat",
    "Utilities":            "Efficient Scale",
    "Communication Services": "Network Effect",
    "Real Estate":          "Efficient Scale",
}

SECTOR_MACRO_BIAS = {
    "Technology":           +5,   # USD strength tailwind for IT exporters
    "Financial Services":   +5,   # RBI easing cycle tailwind
    "Healthcare":           +3,   # PLI scheme support
    "Consumer Defensive":   +2,   # Stable demand
    "Utilities":            +3,   # Govt capex tailwind
    "Industrials":          +4,   # Infra / PLI tailwind
    "Energy":               -2,   # Govt-controlled pricing for OMCs
    "Consumer Cyclical":    +1,
    "Basic Materials":      -1,   # Global commodity cycle risk
    "Communication Services": +2,
    "Real Estate":          +2,   # Rate cut tailwind
}


def validate_env():
    missing = [k for k, v in {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID":   TELEGRAM_CHAT_ID,
        "OPENAI_API_KEY":     OPENAI_API_KEY,
        "SUPABASE_URL":       SUPABASE_URL,
        "SUPABASE_KEY":       SUPABASE_KEY,
    }.items() if not v]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")


# ==================== SCREENER.IN SCRAPER ====================

SCREENER_BASE = "https://www.screener.in/company/{symbol}/consolidated/"
SCREENER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
_screener_cache: Dict[str, Dict] = {}


def _parse_number(val: str) -> Optional[float]:
    try:
        return float(str(val).replace(",", "").replace("%", "").strip())
    except (ValueError, AttributeError):
        return None


def _parse_table(section) -> Dict[str, List[Optional[float]]]:
    """Parse a Screener section div into {row_label: [float, ...]}."""
    result = {}
    if section is None:
        return result
    table = section.find("table")
    if table is None:
        return result
    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        label = cells[0].get_text(strip=True).rstrip("+").strip()
        values = [_parse_number(c.get_text(strip=True)) for c in cells[1:]]
        if label:
            result[label] = values
    return result


def fetch_screener_data(ticker: str) -> Dict:
    """
    Fetch and parse Screener.in data for a ticker.
    Tries consolidated view first, falls back to standalone.
    Results are cached per run to avoid repeat fetches.
    """
    symbol = ticker.replace(".NS", "").replace(".BO", "")
    if symbol in _screener_cache:
        return _screener_cache[symbol]

    data = {}
    for view in ("consolidated", "standalone"):
        url = f"https://www.screener.in/company/{symbol}/{view}/"
        try:
            resp = requests.get(url, headers=SCREENER_HEADERS, timeout=10)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Find sections by their id
            sections = {
                "profit-loss":   soup.find(id="profit-loss"),
                "balance-sheet": soup.find(id="balance-sheet"),
                "cash-flow":     soup.find(id="cash-flow"),
                "ratios":        soup.find(id="ratios"),
                "shareholding":  soup.find(id="shareholding"),
            }

            pl   = _parse_table(sections["profit-loss"])
            bs   = _parse_table(sections["balance-sheet"])
            cf   = _parse_table(sections["cash-flow"])
            rat  = _parse_table(sections["ratios"])
            shdg = _parse_table(sections["shareholding"])

            def get(d, *keys):
                for k in keys:
                    for dk in d:
                        if k.lower() in dk.lower():
                            return d[dk]
                return []

            def latest(lst):
                for v in reversed(lst):
                    if v is not None:
                        return v
                return None

            def last_n(lst, n):
                clean = [v for v in lst if v is not None]
                return clean[-n:] if len(clean) >= n else clean

            data["revenue_10y"]            = get(pl, "Sales", "Revenue")
            data["pat_10y"]                = get(pl, "Net Profit")
            data["ebitda_10y"]             = get(pl, "Operating Profit")
            data["eps_10y"]                = get(pl, "EPS")
            data["cfo_10y"]                = get(cf, "Cash from Operating")
            data["capex_10y"]              = get(cf, "Capital Expenditure")
            data["debt_10y"]               = get(bs, "Borrowings")
            data["equity_10y"]             = get(bs, "Equity Capital")
            data["roce_10y"]               = get(rat, "ROCE")
            data["roe_10y"]                = get(rat, "ROE")
            data["de_ratio_10y"]           = get(rat, "Debt to equity", "D/E")
            data["interest_coverage_10y"]  = get(rat, "Interest Coverage")
            data["receivable_days_10y"]    = get(rat, "Debtor Days")
            data["inventory_days_10y"]     = get(rat, "Days Inventory", "Inventory Days")
            data["promoter_holding_qtly"]  = get(shdg, "Promoter")
            data["pledge_pct_qtly"]        = get(shdg, "Pledge")
            data["fii_holding"]            = latest(get(shdg, "FII"))
            data["dii_holding"]            = latest(get(shdg, "DII"))

            # Computed FCF
            cfos   = data["cfo_10y"]
            capexs = data["capex_10y"]
            if cfos and capexs:
                data["fcf_10y"] = [
                    (c - abs(k)) if (c is not None and k is not None) else None
                    for c, k in zip(cfos, capexs)
                ]
            else:
                data["fcf_10y"] = []

            # Convenience lookups
            data["roce_latest"]              = latest(data["roce_10y"])
            data["de_ratio_latest"]          = latest(data["de_ratio_10y"])
            data["interest_coverage_latest"] = latest(data["interest_coverage_10y"])
            data["promoter_holding_latest"]  = latest(data["promoter_holding_qtly"])
            data["pledge_pct_latest"]        = latest(data["pledge_pct_qtly"])
            data["cfo_last5"]                = last_n(data["cfo_10y"], 5)
            data["fcf_last5"]                = last_n(data["fcf_10y"], 5)
            data["eps_last3"]                = last_n(data["eps_10y"], 3)
            data["revenue_last3"]            = last_n(data["revenue_10y"], 3)
            data["_view"]                    = view
            data["_source"]                  = "screener.in"

            # Extract current price and market cap from the top of the page
            try:
                price_span = soup.find("span", class_="number")
                if not price_span:
                    price_span = soup.select_one("#top-ratios li:first-child .number")
                # Try the top-ratios section for Current Price and Market Cap
                top_ratios = soup.find(id="top-ratios")
                if top_ratios:
                    for li in top_ratios.find_all("li"):
                        label = li.get_text(" ", strip=True).lower()
                        val_span = li.find("span", class_="number")
                        if not val_span:
                            continue
                        val = _parse_number(val_span.get_text(strip=True))
                        if "current price" in label or "price" in label:
                            data["current_price"] = val
                        elif "market cap" in label:
                            data["market_cap_cr"] = val
                        elif "52 week high" in label or "high" in label:
                            data["week52_high"] = val
                        elif "52 week low" in label or "low" in label:
                            data["week52_low"] = val
            except Exception:
                pass

            # Detect recent quarterly results (last 7 days)
            try:
                quarters = soup.select("#quarters table tr")
                if quarters and len(quarters) > 1:
                    # First header row contains quarter dates
                    header_cells = quarters[0].find_all("th")
                    if len(header_cells) > 1:
                        latest_quarter = header_cells[1].get_text(strip=True)
                        data["latest_quarter"] = latest_quarter
                        # Check if it contains current month/year (recent result)
                        now = datetime.now()
                        current_markers = [
                            str(now.year),
                            f"{now.month:02d}",
                            now.strftime("%b"),
                        ]
                        data["recent_earnings"] = any(
                            m in latest_quarter for m in current_markers
                        )
            except Exception:
                pass

            print(f"[Screener:{view}] ✓", end=" ")
            break

        except Exception as e:
            print(f"[Screener:{view}] error: {e}", end=" ")
            continue

        time.sleep(0.5)  # polite delay between requests

    _screener_cache[symbol] = data
    return data


# ==================== PRE-SCREENING GATE ====================

def run_prescreening_gate(ticker: str, yf_info: Dict, screener: Dict) -> Tuple[bool, bool, List[str]]:
    """
    Returns (passed, illiquid_flag, fail_reasons)
    passed=False → stock is disqualified
    illiquid_flag=True → 10-point penalty applied later
    """
    fail_reasons = []
    illiquid = False

    # --- Governance Gate (screener data) ---
    pledge = screener.get("pledge_pct_latest")
    if pledge is not None:
        if pledge >= 20:
            fail_reasons.append(f"Promoter pledge {pledge:.1f}% ≥ 20% threshold")

    promo_qtly = screener.get("promoter_holding_qtly", [])
    if len(promo_qtly) >= 4:
        recent = [v for v in promo_qtly[-4:] if v is not None]
        if len(recent) >= 2 and (recent[0] - recent[-1]) > 5:
            fail_reasons.append(f"Promoter holding declined {recent[0] - recent[-1]:.1f}% in last 4 quarters")

    # --- Financial Health Gate (screener data) ---
    ic = screener.get("interest_coverage_latest")
    if ic is not None and ic <= 2.0:
        fail_reasons.append(f"Interest coverage {ic:.1f}x ≤ 2.0x threshold")

    cfo_last5 = [v for v in screener.get("cfo_last5", []) if v is not None]
    if len(cfo_last5) >= 3:
        negative_years = sum(1 for v in cfo_last5 if v < 0)
        if negative_years >= 2:
            fail_reasons.append(f"CFO negative in {negative_years} of last 5 years")

    rev = [v for v in screener.get("revenue_last3", []) if v is not None]
    if len(rev) >= 2:
        for i in range(1, len(rev)):
            if rev[i - 1] > 0 and ((rev[i - 1] - rev[i]) / rev[i - 1]) > 0.15:
                fail_reasons.append("Revenue declined > 15% YoY for consecutive years")
                break

    rec_days = [v for v in screener.get("receivable_days_10y", [])[-3:] if v is not None]
    rev_trend = [v for v in screener.get("revenue_10y", [])[-3:] if v is not None]
    if len(rec_days) >= 2 and len(rev_trend) >= 2:
        rec_growth = (rec_days[-1] - rec_days[0]) / max(abs(rec_days[0]), 1)
        rev_growth = (rev_trend[-1] - rev_trend[0]) / max(abs(rev_trend[0]), 1)
        if rec_growth > 2 * rev_growth and rec_growth > 0.3:
            fail_reasons.append("Receivable days growing 2× faster than revenue — potential collection risk")

    # --- Liquidity Gate (yfinance) ---
    avg_vol    = yf_info.get("averageVolume", 0) or 0
    curr_price = yf_info.get("currentPrice") or yf_info.get("regularMarketPrice") or 0
    daily_val_inr = avg_vol * curr_price * 84  # rough USD→INR (1 USD ≈ ₹84)
    market_cap_inr = (yf_info.get("marketCap") or 0) * 84

    if market_cap_inr < 100_00_00_000:  # < ₹100 Cr
        fail_reasons.append(f"Market cap < ₹100 Cr — operator risk too high")
    elif daily_val_inr < 50_00_000:  # < ₹50 Lakhs
        illiquid = True  # penalty only, not disqualification

    passed = len(fail_reasons) == 0
    return passed, illiquid, fail_reasons


# ==================== PILLAR 1: BUSINESS QUALITY & MOAT (30%) ====================

def score_business_quality(yf_info: Dict, screener: Dict) -> Dict:
    score = 0
    details = {}

    # ROCE 10-year trend
    roce_series = [v for v in screener.get("roce_10y", []) if v is not None]
    if roce_series:
        avg_roce = sum(roce_series) / len(roce_series)
        details["avg_roce"] = round(avg_roce, 1)
        details["roce_years"] = len(roce_series)

        if avg_roce >= 20:
            score += 28
        elif avg_roce >= 15:
            score += 21
        elif avg_roce >= 10:
            score += 12
        else:
            score += 4

        # Trend bonus: improving ROCE
        if len(roce_series) >= 3:
            trend = roce_series[-1] - roce_series[0]
            if trend > 3:
                score += 2
            elif trend < -5:
                score -= 3
    else:
        # Fallback: use yfinance ROE as ROCE proxy
        roe = (yf_info.get("returnOnEquity") or 0) * 100
        details["avg_roce"] = round(roe, 1)
        details["roce_years"] = 0
        details["note"] = "ROCE proxy from yfinance ROE (screener data unavailable)"
        if roe >= 20:
            score += 22
        elif roe >= 15:
            score += 16
        elif roe >= 10:
            score += 10
        else:
            score += 3

    # IROE (Incremental ROCE) — Change in EBIT / Change in Capital Employed
    ebitda_series = [v for v in screener.get("ebitda_10y", [])[-4:] if v is not None]
    equity_series = [v for v in screener.get("equity_10y", [])[-4:] if v is not None]
    debt_series   = [v for v in screener.get("debt_10y", [])[-4:] if v is not None]
    if len(ebitda_series) >= 2 and len(equity_series) >= 2 and len(debt_series) >= 2:
        delta_ebit = ebitda_series[-1] - ebitda_series[0]
        delta_ce   = (equity_series[-1] + debt_series[-1]) - (equity_series[0] + debt_series[0])
        if delta_ce > 0:
            iroe = (delta_ebit / delta_ce) * 100
            details["iroe"] = round(iroe, 1)
            if iroe >= 15:
                score += 2  # compounding moat intact

    # Moat type classification
    sector = yf_info.get("sector", "")
    moat_type = SECTOR_MOAT_MAP.get(sector, "Unclassified")
    # Refine: high stable ROCE = stronger moat signal
    roce_val = details.get("avg_roce", 0)
    if roce_val >= 20 and moat_type == "Unclassified":
        moat_type = "Switching Costs"
    elif roce_val < 10:
        moat_type = "No Moat"
    details["moat_type"] = moat_type

    score = min(30, max(0, score))
    details["score"] = score
    return details


# ==================== PILLAR 2: VALUATION & MARGIN OF SAFETY (30%) ====================

def _discount_rate(market_cap_usd: float) -> float:
    mc_inr = market_cap_usd * 84
    if mc_inr >= LARGE_CAP_THRESHOLD:
        return 0.12
    elif mc_inr >= MID_CAP_THRESHOLD:
        return 0.14
    return 0.16


def score_valuation(yf_info: Dict, screener: Dict) -> Dict:
    score = 0
    details = {}
    mos_scores = []
    sector = yf_info.get("sector", "")
    is_bank = any(s in sector for s in BANKING_SECTORS)

    curr_price = yf_info.get("currentPrice") or yf_info.get("regularMarketPrice") or 0
    market_cap = yf_info.get("marketCap") or 0
    book_value = yf_info.get("bookValue") or 0

    # 2a. Graham Number (skip for banks)
    if not is_bank and curr_price > 0 and book_value > 0:
        eps_series = [v for v in screener.get("eps_last3", []) if v is not None]
        trailing_eps = yf_info.get("trailingEps") or 0
        avg_eps = sum(eps_series) / len(eps_series) if eps_series else trailing_eps

        if avg_eps > 0:
            graham = math.sqrt(22.5 * avg_eps * book_value)
            mos_g = (graham - curr_price) / graham * 100
            details["graham_number"] = round(graham, 2)
            details["mos_graham_pct"] = round(mos_g, 1)
            # Map to 0–30
            if mos_g >= 40:
                mos_scores.append((30, 0.3))
            elif mos_g >= 25:
                mos_scores.append((22, 0.3))
            elif mos_g >= 10:
                mos_scores.append((14, 0.3))
            else:
                mos_scores.append((5, 0.3))
        else:
            details["graham_note"] = "Negative EPS — Graham Number skipped"

    # 2b. Conservative DCF (7-year)
    fcf_series = [v for v in screener.get("fcf_last5", []) if v is not None]
    fcf_yf     = yf_info.get("freeCashFlow") or 0
    fcf_base   = sorted(fcf_series)[len(fcf_series) // 2] if fcf_series else fcf_yf  # median

    if fcf_base and fcf_base > 0 and curr_price > 0 and market_cap > 0:
        # Growth rate: 5-year FCF CAGR capped at 15%, haircut 20%
        if len(fcf_series) >= 2 and fcf_series[0] and fcf_series[0] > 0:
            raw_cagr = (fcf_series[-1] / fcf_series[0]) ** (1 / len(fcf_series)) - 1
        else:
            raw_cagr = 0.08  # conservative default
        growth = min(raw_cagr, 0.15) * 0.80  # 20% haircut

        dr  = _discount_rate(market_cap)
        tgr = 0.05
        pv_sum = 0.0
        fcf_t = fcf_base
        for t in range(1, 8):
            fcf_t *= (1 + growth)
            pv_sum += fcf_t / ((1 + dr) ** t)
        terminal_val = fcf_t * (1 + tgr) / (dr - tgr)
        pv_terminal  = terminal_val / ((1 + dr) ** 7)
        intrinsic    = pv_sum + pv_terminal
        mos_dcf      = (intrinsic - market_cap) / intrinsic * 100

        details["dcf_intrinsic_cr"] = round(intrinsic / 1e7, 0)  # in ₹ Cr approx
        details["mos_dcf_pct"]      = round(mos_dcf, 1)
        details["dcf_growth_used"]  = round(growth * 100, 1)
        details["dcf_dr_used"]      = round(dr * 100, 1)

        if mos_dcf >= 40:
            mos_scores.append((30, 0.4))
        elif mos_dcf >= 25:
            mos_scores.append((22, 0.4))
        elif mos_dcf >= 10:
            mos_scores.append((14, 0.4))
        else:
            mos_scores.append((5, 0.4))
    else:
        details["dcf_note"] = "Negative or unavailable FCF — DCF skipped"

    # 2c. EV/EBITDA + FCF Yield
    total_debt = yf_info.get("totalDebt") or 0
    total_cash = yf_info.get("totalCash") or 0
    ebitda_yf  = yf_info.get("ebitda") or 0
    net_income = yf_info.get("netIncomeToCommon") or 1

    ev_ebitda_score = 0
    fcf_yield_score = 0

    if market_cap > 0 and ebitda_yf > 0:
        ev = market_cap + total_debt - total_cash
        ev_ebitda = ev / ebitda_yf
        details["ev_ebitda"] = round(ev_ebitda, 1)
        if ev_ebitda < 8:
            ev_ebitda_score = 15
        elif ev_ebitda <= 15:
            ev_ebitda_score = 10
        elif ev_ebitda <= 20:
            ev_ebitda_score = 5
        else:
            ev_ebitda_score = 2

    if market_cap > 0 and fcf_yf and fcf_yf > 0:
        fcf_yield = (fcf_yf / market_cap) * 100
        details["fcf_yield_pct"] = round(fcf_yield, 1)
        if fcf_yield >= 8:
            fcf_yield_score = 15
        elif fcf_yield >= 5:
            fcf_yield_score = 10
        elif fcf_yield >= 3:
            fcf_yield_score = 6
        else:
            fcf_yield_score = 2

        fcf_conversion = fcf_yf / max(abs(net_income), 1) * 100
        details["fcf_conversion_pct"] = round(fcf_conversion, 1)

    combined_rel = (ev_ebitda_score + fcf_yield_score) / 2
    mos_scores.append((min(30, combined_rel), 0.3))

    # Composite MoS score
    if mos_scores:
        total_w = sum(w for _, w in mos_scores)
        score = sum(s * w for s, w in mos_scores) / total_w
    else:
        score = 5  # no valuation data

    score = min(30, max(0, round(score)))
    details["score"] = score

    # Best MoS % for display
    mos_vals = [details.get("mos_graham_pct"), details.get("mos_dcf_pct")]
    valid_mos = [v for v in mos_vals if v is not None]
    details["best_mos_pct"] = round(max(valid_mos), 1) if valid_mos else None

    # Safe entry price: lower of Graham Number and DCF-implied price, with 10% additional buffer
    # This is the price at which a deep-value investor would confidently initiate a position
    safe_prices = []
    if details.get("graham_number") and details["graham_number"] > 0:
        safe_prices.append(details["graham_number"] * 0.90)
    if details.get("mos_dcf_pct") and market_cap > 0 and curr_price > 0:
        # DCF intrinsic is in Cr (total market cap). Per-share price = intrinsic_cr * 1e7 / shares
        # Approximate shares = market_cap / curr_price
        shares_approx = market_cap / max(curr_price, 1)
        if shares_approx > 0 and details.get("dcf_intrinsic_cr"):
            dcf_per_share = (details["dcf_intrinsic_cr"] * 1e7) / shares_approx
            safe_prices.append(dcf_per_share * 0.90)
    details["safe_entry_price"] = round(min(safe_prices), 2) if safe_prices else None
    details["current_price"]    = round(curr_price, 2)

    return details


# ==================== PILLAR 3: FINANCIAL HEALTH (20%) ====================

def score_financial_health(yf_info: Dict, screener: Dict) -> Dict:
    score = 0
    details = {}

    # Debt analysis
    de_latest = screener.get("de_ratio_latest") or (yf_info.get("debtToEquity") or 0) / 100
    ic_latest = screener.get("interest_coverage_latest")
    if ic_latest is None:
        # approximate from yfinance: EBIT / interest expense
        ebit = (yf_info.get("ebitda") or 0) - (yf_info.get("depreciationAndAmortization") or 0)
        interest = yf_info.get("interestExpense") or 1
        ic_latest = ebit / max(abs(interest), 1) if ebit else None

    details["de_ratio"]         = round(de_latest, 2)
    details["interest_coverage"] = round(ic_latest, 1) if ic_latest else None

    # D/E scoring
    if de_latest < 0.5:
        score += 6
    elif de_latest <= 1.5:
        score += 4
    elif de_latest <= 3.0:
        score += 1

    # Interest coverage scoring
    if ic_latest:
        if ic_latest >= 5:
            score += 4
        elif ic_latest >= 2:
            score += 2

    # CFO/PAT ratio (cash quality)
    cfo_last5 = [v for v in screener.get("cfo_last5", []) if v is not None]
    pat_last5 = [v for v in screener.get("pat_10y", [])[-5:] if v is not None]
    if cfo_last5 and pat_last5 and len(cfo_last5) == len(pat_last5):
        ratios = [c / max(abs(p), 1) for c, p in zip(cfo_last5, pat_last5) if p != 0]
        avg_cfo_pat = sum(ratios) / len(ratios) if ratios else None
        if avg_cfo_pat:
            details["avg_cfo_pat_ratio"] = round(avg_cfo_pat, 2)
            if avg_cfo_pat >= 1.0:
                score += 4
            elif avg_cfo_pat >= 0.7:
                score += 2

    # Working capital trend
    rec_days = [v for v in screener.get("receivable_days_10y", [])[-3:] if v is not None]
    if len(rec_days) >= 2:
        rec_trend = rec_days[-1] - rec_days[0]
        details["receivable_days_trend"] = round(rec_trend, 1)
        if rec_trend < 0:
            score += 2  # improving collections
        elif rec_trend > 20:
            score -= 2

    # Altman Z-Score (approximate with available yfinance fields)
    mc  = yf_info.get("marketCap") or 0
    tl  = yf_info.get("totalDebt") or 1
    rev = yf_info.get("totalRevenue") or 0
    ta  = yf_info.get("totalAssets") or 1
    re  = yf_info.get("retainedEarnings") or 0
    wc  = (yf_info.get("currentAssets") or 0) - (yf_info.get("currentLiabilities") or 0)
    ebit_z = (yf_info.get("ebitda") or 0) - (yf_info.get("depreciationAndAmortization") or 0)

    if ta > 0:
        z = (1.2 * wc / ta) + (1.4 * re / ta) + (3.3 * ebit_z / ta) + (0.6 * mc / tl) + (1.0 * rev / ta)
        details["altman_z"] = round(z, 2)
        if z >= 2.99:
            score += 4
        elif z >= 1.81:
            score += 2

    # Dividend track record
    div_rate = yf_info.get("dividendRate") or 0
    if div_rate > 0:
        score += 2
        details["dividend_paying"] = True
    else:
        details["dividend_paying"] = False

    score = min(20, max(0, score))
    details["score"] = score
    return details


# ==================== PILLAR 4: MANAGEMENT QUALITY (10%) ====================

def score_management_quality(yf_info: Dict, screener: Dict) -> Dict:
    score = 5  # start at neutral mid-point
    details = {}

    # Promoter holding trend (screener quarterly)
    promo_qtly = [v for v in screener.get("promoter_holding_qtly", []) if v is not None]
    if promo_qtly:
        latest_h = promo_qtly[-1]
        details["promoter_holding_pct"] = round(latest_h, 1)
        if latest_h >= 50:
            score += 2
        elif latest_h >= 35:
            score += 1

        if len(promo_qtly) >= 4:
            trend = promo_qtly[-1] - promo_qtly[-4]
            details["promoter_holding_trend_4q"] = round(trend, 1)
            if trend >= 1:
                score += 1
            elif trend <= -2:
                score -= 2

    # Pledge %
    pledge = screener.get("pledge_pct_latest")
    if pledge is not None:
        details["pledge_pct"] = round(pledge, 1)
        if pledge == 0:
            score += 1
        elif pledge < 10:
            score += 0
        elif pledge < 20:
            score -= 1

    # Institutional holding trend
    fii = screener.get("fii_holding")
    dii = screener.get("dii_holding")
    if fii is not None and dii is not None:
        inst_total = fii + dii
        details["institutional_holding_pct"] = round(inst_total, 1)
        if inst_total >= 40:
            score += 1

    # Capital allocation proxy: IROE reuse from Pillar 1 not available here,
    # so use consistency of positive FCF as proxy
    fcf_last5 = [v for v in screener.get("fcf_last5", []) if v is not None]
    if fcf_last5:
        positive_fcf_years = sum(1 for v in fcf_last5 if v > 0)
        details["positive_fcf_years_of_5"] = positive_fcf_years
        if positive_fcf_years >= 4:
            score += 1
        elif positive_fcf_years <= 2:
            score -= 1

    # Dividend consistency proxy
    div_rate = yf_info.get("dividendRate") or 0
    if div_rate > 0:
        score += 1
        details["consistent_dividend"] = True

    if not screener:
        details["note"] = "Limited data — screener CSV not available"

    score = min(10, max(0, score))
    details["score"] = score
    return details


# ==================== PILLAR 5: MACRO & SENTIMENT (10%) ====================

def get_news_sentiment(stock_name: str, symbol: str) -> Dict:
    """
    Fetch Google News RSS headlines for the stock and use Claude to score sentiment.
    Returns sentiment score 0-100 and top headlines.
    """
    try:
        query = f"{stock_name} NSE stock India"
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return {"score": 50, "signal": "NEUTRAL", "headlines": []}

        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item")[:8]
        headlines = [item.find("title").get_text(strip=True) for item in items if item.find("title")]

        if not headlines:
            return {"score": 50, "signal": "NEUTRAL", "headlines": []}

        # Use OpenAI to score sentiment from headlines
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"score": 50, "signal": "NEUTRAL", "headlines": headlines[:3]}
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = f"""You are a financial sentiment analyst for Indian equities.

Stock: {stock_name} ({symbol}.NS)
Recent news headlines:
{chr(10).join(f"- {h}" for h in headlines)}

Score the overall investment sentiment from these headlines on a scale of 0-100:
- 0-20: Extreme negative (fraud, bankruptcy, regulatory action, major loss)
- 20-40: Negative (earnings miss, headwinds, management concerns)
- 40-60: Neutral (mixed news, routine updates)
- 60-80: Positive (earnings beat, new contracts, expansion)
- 80-100: Strongly positive (major win, sector tailwind, analyst upgrade)

Reply with ONLY a JSON object: {{"score": <number>, "reason": "<10 words max>"}}"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=60,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content.strip())
        score = max(0, min(100, int(result.get("score", 50))))
        return {"score": score, "signal": result.get("reason", ""), "headlines": headlines[:3]}

    except Exception as e:
        print(f"  [OpenAI sentiment error] {type(e).__name__}: {e}")
        return {"score": 50, "signal": "NEUTRAL", "headlines": []}


def score_macro_sentiment(ticker: str, stock_name: str, yf_info: Dict) -> Dict:
    score = 5  # neutral base
    details = {}

    sector = yf_info.get("sector", "")
    macro_adj = SECTOR_MACRO_BIAS.get(sector, 0)
    score += macro_adj
    details["sector"]    = sector
    details["macro_adj"] = macro_adj

    # Beta risk adjustment
    beta = yf_info.get("beta") or 1.0
    details["beta"] = round(beta, 2)
    if beta > 1.5:
        score -= 1
    elif beta < 0.7:
        score += 1

    # Google News RSS + Claude sentiment
    news = get_news_sentiment(stock_name, ticker)
    sentiment_raw = news["score"]
    details["sentiment_raw"]     = sentiment_raw
    details["sentiment_reason"]  = news["signal"]
    details["top_headlines"]     = news["headlines"]

    if sentiment_raw <= 20:
        sentiment_contribution = 7
        details["sentiment_signal"] = "EXTREME_FEAR_CONTRARIAN"
    elif sentiment_raw <= 40:
        sentiment_contribution = 5
        details["sentiment_signal"] = "PESSIMISM"
    elif sentiment_raw <= 60:
        sentiment_contribution = 5
        details["sentiment_signal"] = "NEUTRAL"
    elif sentiment_raw <= 80:
        sentiment_contribution = 4
        details["sentiment_signal"] = "OPTIMISM_CAUTION"
    else:
        sentiment_contribution = 2
        details["sentiment_signal"] = "EXTREME_GREED_AVOID"

    score = score - 5 + sentiment_contribution

    score = min(10, max(0, score))
    details["score"] = score
    return details


# ==================== COMPOSITE SCORING ====================

def compute_composite_score(p1: Dict, p2: Dict, p3: Dict, p4: Dict, p5: Dict,
                             gate_passed: bool, illiquid: bool) -> Dict:
    composite = (
        p1["score"] / 30 * 30 * 0.30 +
        p2["score"] / 30 * 30 * 0.30 +
        p3["score"] / 20 * 20 * 0.20 +
        p4["score"] / 10 * 10 * 0.10 +
        p5["score"] / 10 * 10 * 0.10
    )
    # Simplified: pillars are already on their natural scale (p1 0-30, p2 0-30, etc.)
    # Composite = sum of raw pillar scores, normalised to 0-100
    composite = p1["score"] + p2["score"] + p3["score"] + p4["score"] + p5["score"]

    if illiquid:
        composite -= 10
        composite = max(0, composite)

    composite = min(100, max(0, round(composite, 1)))

    if composite >= 80:
        recommendation = "🟢 STRONG BUY"
        horizon        = "3–5 Years"
        risk_profile   = "Low–Medium"
        position_pct   = "6–10%"
    elif composite >= 65:
        recommendation = "🟡 BUY"
        horizon        = "2–3 Years"
        risk_profile   = "Medium"
        position_pct   = "3–6%"
    elif composite >= 50:
        recommendation = "⚪ MONITOR"
        horizon        = "Watch; wait for better price"
        risk_profile   = "Medium"
        position_pct   = "0–2% (tracking)"
    elif composite >= 35:
        recommendation = "🟠 WEAK"
        horizon        = "N/A"
        risk_profile   = "High"
        position_pct   = "0%"
    else:
        recommendation = "🔴 AVOID / EXIT"
        horizon        = "N/A"
        risk_profile   = "Very High"
        position_pct   = "0%"

    return {
        "composite_score": composite,
        "recommendation":  recommendation,
        "horizon":         horizon,
        "risk_profile":    risk_profile,
        "position_pct":    position_pct,
    }


# ==================== INVALIDATION TRIGGERS ====================

def build_invalidation_triggers(p1: Dict, p2: Dict, p3: Dict, screener: Dict) -> List[str]:
    triggers = []
    roce = p1.get("avg_roce")
    if roce and roce < 15:
        triggers.append("ROCE drops below 12% for 2 consecutive years")
    de = p3.get("de_ratio", 0)
    if de > 1.5:
        triggers.append(f"D/E already elevated at {de:.1f}x — exit if crosses 2.0x unexpectedly")
    else:
        triggers.append("D/E ratio crosses 2.0x unexpectedly")
    pledge = screener.get("pledge_pct_latest")
    if pledge is not None and pledge > 10:
        triggers.append(f"Promoter pledge rising above 20% (currently {pledge:.1f}%)")
    else:
        triggers.append("Promoter pledge crosses 20%")
    triggers.append("CFO negative for 2 consecutive years")
    mos = p2.get("best_mos_pct")
    if mos and mos > 0:
        triggers.append("Price rises to fully valued — trim if composite MoS < 10%")
    triggers.append("Auditor resignation or adverse audit opinion")
    return triggers[:5]


# ==================== THESIS GENERATOR (OpenAI) ====================

def generate_thesis_with_claude(analysis: Dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    p1 = analysis.get("pillar1", {})
    p2 = analysis.get("pillar2", {})
    p3 = analysis.get("pillar3", {})
    p4 = analysis.get("pillar4", {})
    p5 = analysis.get("pillar5", {})

    prompt = (
        f"You are AlphaVision, a deep-value analyst for Indian equities.\n\n"
        f"Stock: {analysis['stock_name']} ({analysis['ticker']})\n"
        f"Sector: {analysis.get('sector', 'N/A')}\n"
        f"Score: {analysis['composite_score']}/100  Rec: {analysis['recommendation']}\n\n"
        f"P1 Business ({p1.get('score','N/A')}/30): Moat={p1.get('moat_type','N/A')}, ROCE={p1.get('avg_roce','N/A')}%\n"
        f"P2 Valuation ({p2.get('score','N/A')}/30): MoS={p2.get('best_mos_pct','N/A')}%, EV/EBITDA={p2.get('ev_ebitda','N/A')}x\n"
        f"P3 Health ({p3.get('score','N/A')}/20): D/E={p3.get('de_ratio','N/A')}, IntCov={p3.get('interest_coverage','N/A')}x\n"
        f"P4 Mgmt ({p4.get('score','N/A')}/10): Promoter={p4.get('promoter_holding_pct','N/A')}%, Pledge={p4.get('pledge_pct','N/A')}%\n"
        f"P5 Macro ({p5.get('score','N/A')}/10): {p5.get('sentiment_signal','Neutral')}\n\n"
        f"Write 3 short paragraphs (2-3 sentences each):\n"
        f"1. Why this business has a durable competitive advantage.\n"
        f"2. Why it is undervalued now (cite a specific metric with number).\n"
        f"3. The single biggest risk that would invalidate this thesis.\n"
        f"Institutional tone. No bullets. No headers."
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        print(f"  [OpenAI thesis error] {type(e).__name__}: {e}")
        return ""


def get_52w_context(price: float, high: float, low: float) -> Dict:
    """Returns how far price is from 52w high/low and position in range."""
    if not price or not high or not low or high == low:
        return {}
    pct_from_high = round((price - high) / high * 100, 1)
    pct_from_low  = round((price - low) / low * 100, 1)
    position_pct  = round((price - low) / (high - low) * 100, 1)
    return {
        "week52_high":      round(high, 2),
        "week52_low":       round(low, 2),
        "pct_from_high":    pct_from_high,   # negative = below high
        "pct_from_low":     pct_from_low,    # positive = above low
        "range_position":   position_pct,    # 0% = at low, 100% = at high
    }



def _fetch_nse_quote(symbol: str) -> Dict:
    """
    Get current price and market cap from Screener.in data (already fetched).
    Falls back to deriving market cap from EPS × P/E if not directly available.
    """
    screener = _screener_cache.get(symbol, {})
    price    = screener.get("current_price") or 0
    mc_cr    = screener.get("market_cap_cr") or 0

    if mc_cr == 0 and price == 0:
        return {}

    return {
        "currentPrice": price,
        "marketCap_cr": mc_cr,
        "52WeekHigh":   screener.get("week52_high") or 0,
        "52WeekLow":    screener.get("week52_low") or 0,
        "symbol":       symbol,
    }


def build_info_from_screener(symbol: str, screener: Dict, nse_quote: Dict) -> Dict:
    """
    Build a unified info dict from Screener.in data + NSE quote.
    This replaces the yfinance info dict throughout the scoring pipeline.
    """
    def latest(lst):
        for v in reversed(lst or []):
            if v is not None:
                return v
        return None

    price         = nse_quote.get("currentPrice") or screener.get("current_price") or 0
    market_cap_cr = nse_quote.get("marketCap_cr") or screener.get("market_cap_cr") or 0
    market_cap_inr = market_cap_cr * 1e7

    pat_series   = [v for v in screener.get("pat_10y", []) if v is not None]
    rev_series   = [v for v in screener.get("revenue_10y", []) if v is not None]
    debt_series  = [v for v in screener.get("debt_10y", []) if v is not None]
    equity_series= [v for v in screener.get("equity_10y", []) if v is not None]
    ebitda_series= [v for v in screener.get("ebitda_10y", []) if v is not None]
    cfo_series   = [v for v in screener.get("cfo_10y", []) if v is not None]
    capex_series = [v for v in screener.get("capex_10y", []) if v is not None]
    eps_series   = [v for v in screener.get("eps_10y", []) if v is not None]

    pat_latest   = latest(pat_series) or 0
    rev_latest   = latest(rev_series) or 0
    debt_latest  = latest(debt_series) or 0
    equity_latest= latest(equity_series) or 0
    ebitda_latest= latest(ebitda_series) or 0
    cfo_latest   = latest(cfo_series) or 0
    capex_latest = latest(capex_series) or 0
    eps_latest   = latest(eps_series) or 0

    # FCF
    fcf_latest = (cfo_latest - abs(capex_latest)) if (cfo_latest and capex_latest) else 0
    fcf_yield  = (fcf_latest / max(market_cap_cr, 1)) * 100 if market_cap_cr else 0

    # D/E
    de_ratio = screener.get("de_ratio_latest") or (
        debt_latest / max(equity_latest, 1) if equity_latest else 0
    )

    # Book value per share — equity in Cr / shares (shares = market_cap_cr / price)
    shares_outstanding = (market_cap_cr / price) if price > 0 else 0
    book_value = (equity_latest / shares_outstanding) if shares_outstanding > 0 else 0

    # Profit margin
    profit_margin = (pat_latest / max(rev_latest, 1)) * 100 if rev_latest else 0

    # ROE
    roe = (latest(screener.get("roe_10y", [])) or 0)

    # Interest coverage
    ic = screener.get("interest_coverage_latest") or 0

    # Sector
    sector = STOCK_SECTOR_MAP.get(symbol, "")

    return {
        "currentPrice":         price,
        "marketCap":            market_cap_inr,
        "marketCap_cr":         market_cap_cr,
        "sector":               sector,
        "bookValue":            book_value,
        "trailingEps":          eps_latest,
        "returnOnEquity":       roe / 100 if roe else 0,
        "debtToEquity":         de_ratio * 100,  # pillar functions divide by 100
        "freeCashFlow":         fcf_latest * 1e7,  # convert Cr to rupees
        "totalDebt":            debt_latest * 1e7,
        "totalCash":            0,
        "ebitda":               ebitda_latest * 1e7,
        "totalRevenue":         rev_latest * 1e7,
        "netIncomeToCommon":    pat_latest * 1e7,
        "profitMargins":        profit_margin / 100,
        "interestExpense":      0,
        "totalAssets":          (equity_latest + debt_latest) * 1e7,
        "currentAssets":        0,
        "currentLiabilities":   0,
        "retainedEarnings":     0,
        "depreciationAndAmortization": 0,
        "dividendRate":         1 if latest(screener.get("pat_10y", [])) else 0,
        "beta":                 1.0,
        "averageVolume":        1_000_000,  # assume liquid for Nifty 50
        "52WeekHigh":           nse_quote.get("52WeekHigh", 0),
        "52WeekLow":            nse_quote.get("52WeekLow", 0),
    }


def _fetch_yf_info(ticker: str, retries: int = 4) -> Dict:
    """Kept for compatibility — now delegates to NSE + Screener pipeline."""
    symbol = ticker.replace(".NS", "").replace(".BO", "")
    screener = fetch_screener_data(symbol)
    nse_quote = _fetch_nse_quote(symbol)
    if not nse_quote.get("currentPrice"):
        return {}
    return build_info_from_screener(symbol, screener, nse_quote)


# ==================== FULL STOCK ANALYSIS ====================

def analyse_stock(symbol: str) -> Optional[Dict]:
    stock_name = symbol

    # Fetch from Screener.in only — price + all fundamentals
    screener  = fetch_screener_data(symbol)
    nse_quote = _fetch_nse_quote(symbol)  # reads from screener cache

    if not nse_quote.get("currentPrice") and not screener.get("market_cap_cr"):
        print(f"No price/market cap data — skipping")
        return None

    yf_info = build_info_from_screener(symbol, screener, nse_quote)

    if not yf_info.get("marketCap"):
        print(f"No market cap — skipping")
        return None

    # Pre-screening gate
    passed, illiquid, fail_reasons = run_prescreening_gate(symbol, yf_info, screener)
    if not passed:
        print(f"DISQUALIFIED: {'; '.join(fail_reasons)}")
        return {
            "ticker":          symbol,
            "stock_name":      stock_name,
            "gate_passed":     False,
            "fail_reasons":    fail_reasons,
            "recommendation":  "🔴 DISQUALIFIED",
            "composite_score": 0,
            "timestamp":       datetime.now().isoformat(),
        }

    # Score all 5 pillars
    p1 = score_business_quality(yf_info, screener)
    p2 = score_valuation(yf_info, screener)
    p3 = score_financial_health(yf_info, screener)
    p4 = score_management_quality(yf_info, screener)
    p5 = score_macro_sentiment(symbol, stock_name, yf_info)

    p1["sector"] = yf_info.get("sector", "")

    composite = compute_composite_score(p1, p2, p3, p4, p5, passed, illiquid)
    invalidation = build_invalidation_triggers(p1, p2, p3, screener)

    result = {
        "ticker":          symbol,
        "stock_name":      stock_name,
        "sector":          yf_info.get("sector", ""),
        "gate_passed":     True,
        "illiquid_flag":   illiquid,
        "fail_reasons":    [],
        "pillar1":         p1,
        "pillar2":         p2,
        "pillar3":         p3,
        "pillar4":         p4,
        "pillar5":         p5,
        "composite_score": composite["composite_score"],
        "recommendation":  composite["recommendation"],
        "horizon":         composite["horizon"],
        "risk_profile":    composite["risk_profile"],
        "position_pct":    composite["position_pct"],
        "invalidation_triggers": invalidation,
        "screener_loaded": bool(screener),
        "recent_earnings": screener.get("recent_earnings", False),
        "latest_quarter":  screener.get("latest_quarter", ""),
        "week52":          get_52w_context(
            yf_info.get("currentPrice", 0),
            screener.get("week52_high", 0),
            screener.get("week52_low", 0),
        ),
        "timestamp":       datetime.now().isoformat(),
    }

    # Generate Claude thesis
    result["thesis"] = generate_thesis_with_claude(result)
    return result


# ==================== TAX CALCULATOR (FY 2025-26, Indian Resident) ====================

# Indian equity transaction charges
STT_BUY          = 0.001    # 0.1% on buy
STT_SELL         = 0.001    # 0.1% on sell
EXCHANGE_LEVY    = 0.0000325 # NSE exchange transaction charge
GST_RATE         = 0.18     # 18% GST on brokerage + exchange levy
STAMP_DUTY       = 0.00015  # 0.015% on buy only (max ₹1500, ignored for simplicity)
SEBI_TURNOVER    = 0.000001 # ₹1 per ₹10L

# Tax rates FY 2025-26
STCG_RATE        = 0.20     # 20% on gains if held < 12 months
LTCG_RATE        = 0.125    # 12.5% on gains if held > 12 months
LTCG_EXEMPTION   = 125000   # ₹1.25 lakh per year exempt from LTCG


def calculate_charges(value: float, is_buy: bool) -> float:
    """Total transaction charges on a buy or sell of given value (in ₹)."""
    stt         = value * (STT_BUY if is_buy else STT_SELL)
    exchange    = value * EXCHANGE_LEVY
    stamp       = value * STAMP_DUTY if is_buy else 0
    sebi        = value * SEBI_TURNOVER
    gst         = (exchange) * GST_RATE
    return stt + exchange + stamp + sebi + gst


def tax_and_breakeven(
    buy_price: float,
    investment_amount: float,
    target_return_pct: float = 15.0,
) -> Dict:
    """
    Calculate break-even, stop-loss, and exit targets with full tax impact.

    Args:
        buy_price:           Price per share at entry (₹)
        investment_amount:   Total amount to invest (₹)
        target_return_pct:   Desired net return % after all charges + tax

    Returns dict with STCG and LTCG scenarios.
    """
    shares = int(investment_amount / buy_price)
    if shares == 0:
        return {}

    actual_investment = shares * buy_price
    buy_charges       = calculate_charges(actual_investment, is_buy=True)
    total_cost        = actual_investment + buy_charges
    cost_per_share    = total_cost / shares

    def exit_analysis(sell_price: float, holding_months: int) -> Dict:
        sell_value   = shares * sell_price
        sell_charges = calculate_charges(sell_value, is_buy=False)
        gross_profit = sell_value - actual_investment
        net_proceeds = sell_value - sell_charges

        if holding_months < 12:
            tax = max(0, gross_profit) * STCG_RATE
            tax_type = "STCG 20%"
        else:
            taxable_gain = max(0, gross_profit - LTCG_EXEMPTION)
            tax = taxable_gain * LTCG_RATE
            tax_type = "LTCG 12.5%"

        net_profit    = net_proceeds - total_cost - tax
        net_return_pct = (net_profit / total_cost) * 100

        return {
            "sell_price":      round(sell_price, 2),
            "gross_profit":    round(gross_profit, 2),
            "sell_charges":    round(sell_charges, 2),
            "tax":             round(tax, 2),
            "tax_type":        tax_type,
            "net_profit":      round(net_profit, 2),
            "net_return_pct":  round(net_return_pct, 1),
        }

    # Break-even price (covers all buy+sell charges, zero profit)
    # Solve: shares*p - sell_charges(shares*p) - total_cost = 0
    # Approximate: p = total_cost / (shares * (1 - STT_SELL - EXCHANGE_LEVY - SEBI_TURNOVER))
    net_factor    = 1 - STT_SELL - EXCHANGE_LEVY - SEBI_TURNOVER
    breakeven     = total_cost / (shares * net_factor)

    # Stop-loss: -7% from buy price (standard swing stop), adjusted
    stoploss_price = buy_price * 0.93
    stoploss       = exit_analysis(stoploss_price, holding_months=1)

    # STCG target: achieve desired return % net of STCG tax (held ~6 months)
    # Solve iteratively
    def find_target_price(months: int, target_pct: float) -> float:
        lo, hi = buy_price, buy_price * 5
        for _ in range(50):
            mid = (lo + hi) / 2
            ea  = exit_analysis(mid, months)
            if ea["net_return_pct"] < target_pct:
                lo = mid
            else:
                hi = mid
        return round(mid, 2)

    stcg_target_price = find_target_price(6, target_return_pct)
    ltcg_target_price = find_target_price(13, target_return_pct)

    return {
        "shares":              shares,
        "investment":          round(actual_investment, 2),
        "buy_charges":         round(buy_charges, 2),
        "total_cost":          round(total_cost, 2),
        "cost_per_share":      round(cost_per_share, 2),
        "breakeven_price":     round(breakeven, 2),
        "stoploss_price":      round(stoploss_price, 2),
        "stoploss_loss":       round(stoploss["net_profit"], 2),
        "stcg_target_price":   stcg_target_price,
        "stcg_at_target":      exit_analysis(stcg_target_price, 6),
        "ltcg_target_price":   ltcg_target_price,
        "ltcg_at_target":      exit_analysis(ltcg_target_price, 13),
        "target_return_pct":   target_return_pct,
    }


def format_tax_summary(symbol: str, buy_price: float, investment: float,
                       safe_entry: float = None) -> str:
    """Format entry levels, tax, and break-even summary for Telegram."""
    if not buy_price or not investment:
        return ""
    t = tax_and_breakeven(buy_price, investment)
    if not t:
        return ""
    stcg = t["stcg_at_target"]
    ltcg = t["ltcg_at_target"]

    entry_line = ""
    if safe_entry and safe_entry > 0:
        if buy_price <= safe_entry:
            entry_line = f"✅ *Safe entry: ₹{safe_entry:.0f}* — current price is at/below safe level\n"
        else:
            gap_pct = ((buy_price - safe_entry) / safe_entry) * 100
            entry_line = (
                f"⏳ *Safe entry: ₹{safe_entry:.0f}* "
                f"({gap_pct:.0f}% above — wait for pullback)\n"
            )

    return (
        f"{entry_line}"
        f"💰 *₹{investment:,.0f} at ₹{buy_price:.0f}* → {t['shares']} shares\n"
        f"Break-even: ₹{t['breakeven_price']:.1f} | Stop-loss: ₹{t['stoploss_price']:.1f} "
        f"(−₹{abs(t['stoploss_loss']):,.0f})\n"
        f"STCG exit (< 1yr): ₹{t['stcg_target_price']:.1f} → *net {stcg['net_return_pct']}%* "
        f"after ₹{stcg['tax']:,.0f} tax (20%)\n"
        f"LTCG exit (> 1yr): ₹{t['ltcg_target_price']:.1f} → *net {ltcg['net_return_pct']}%* "
        f"after ₹{ltcg['tax']:,.0f} tax (12.5%)\n"
    )


# ==================== TELEGRAM MESSAGING ====================

async def _send(message: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    async with bot:
        # Split into chunks of 4000 chars to stay under Telegram's 4096 limit
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=chunk, parse_mode="Markdown")
            if len(chunks) > 1:
                await asyncio.sleep(0.5)


def send_telegram_message(message: str):
    try:
        asyncio.run(_send(message))
        print("✓ Telegram message sent")
    except TelegramError as e:
        print(f"✗ Telegram error: {e}")


def format_telegram_message(results: List[Dict], disqualified: List[Dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Only show top 7 by composite score, minimum score 65
    top = sorted(
        [r for r in results if r["gate_passed"] and r["composite_score"] >= 65],
        key=lambda x: x["composite_score"],
        reverse=True,
    )[:7]

    total_analysed  = len(results) + len(disqualified)
    total_passed    = len(results)
    total_buys      = len([r for r in results if r["composite_score"] >= 65])

    msg = (
        f"*🎯 ALPHAVISION DEEP VALUE REPORT*\n"
        f"_{now} IST_\n"
        f"_{total_analysed} stocks scanned → {total_passed} passed gate → {total_buys} BUY/STRONG BUY_\n\n"
    )

    if not top:
        msg += "_No strong buys today. Market may be fully valued — hold cash._\n"
        return msg

    msg += "*── TODAY'S STRONG PICKS ──*\n\n"

    for r in top:
        p1  = r.get("pillar1", {})
        p2  = r.get("pillar2", {})
        p5  = r.get("pillar5", {})
        w52 = r.get("week52", {})

        mos      = p2.get("best_mos_pct")
        mos_str  = f" | MoS {mos:.0f}%" if mos else ""

        # 52-week range bar
        pos       = w52.get("range_position")
        from_high = w52.get("pct_from_high")
        if pos is not None and from_high is not None:
            bar       = "█" * int(pos / 10) + "░" * (10 - int(pos / 10))
            w52_str   = f"52w [{bar}] {from_high:+.1f}% from high\n"
        else:
            w52_str   = ""

        # Earnings flag
        earnings_str = f"⚡ *Results: {r.get('latest_quarter', '')}*\n" if r.get("recent_earnings") else ""

        # Top headline
        headlines = p5.get("top_headlines", [])
        news_str  = f"📰 _{headlines[0][:90]}_\n" if headlines else ""

        # Sector rank tag
        sector_str = r.get("sector", "N/A")
        if r.get("best_in_sector"):
            sector_str += " 🏆"
        rank = r.get("sector_rank")
        total = r.get("sector_total")
        rank_str = f" (#{rank}/{total} in sector)" if rank and total else ""

        # Tax summary (default ₹50,000 investment per stock)
        price       = p2.get("current_price") or r.get("week52", {}).get("week52_high", 0) * 0.9
        safe_entry  = p2.get("safe_entry_price")
        tax_str     = format_tax_summary(r["stock_name"], price, 50000, safe_entry) if price else ""

        msg += (
            f"*{r['stock_name']}* | {r['recommendation']} | {r['composite_score']}/100{mos_str}\n"
            f"{earnings_str}"
            f"Moat: {p1.get('moat_type', 'N/A')} | ROCE: {p1.get('avg_roce', 'N/A')}% | "
            f"{sector_str}{rank_str}\n"
            f"{w52_str}"
            f"{news_str}"
            + (f"_{r['thesis'][:180].strip()}_\n" if r.get('thesis') else "")
            + f"{tax_str}\n"
        )

    # Contrarian alert (extreme fear + score ≥ 55 but didn't make top 7)
    contrarian = [
        r for r in results
        if r["gate_passed"]
        and r.get("pillar5", {}).get("sentiment_signal") == "EXTREME_FEAR_CONTRARIAN"
        and r["composite_score"] >= 55
        and r not in top
    ][:2]
    if contrarian:
        msg += "*── ⚡ CONTRARIAN WATCH ──*\n"
        for r in contrarian:
            msg += f"*{r['stock_name']}* — Extreme fear | Score {r['composite_score']}/100\n"
        msg += "\n"

    msg += f"_AlphaVision | Deep Value | 5–7yr Horizon | {total_analysed} stocks universe_"
    return msg


# ==================== DATABASE ====================

# ==================== DATABASE (SUPABASE) ====================

def save_recommendation(result: Dict):
    """Upsert a recommendation record to Supabase."""
    try:
        db = get_supabase()
        db.table("recommendations").upsert({
            "ticker":             result["ticker"],
            "date":               result["timestamp"],
            "recommendation":     result["recommendation"],
            "composite_score":    result.get("composite_score", 0),
            "p1_moat_score":      result.get("pillar1", {}).get("score"),
            "p2_valuation_score": result.get("pillar2", {}).get("score"),
            "p3_health_score":    result.get("pillar3", {}).get("score"),
            "p4_management_score":result.get("pillar4", {}).get("score"),
            "p5_macro_score":     result.get("pillar5", {}).get("score"),
            "margin_of_safety_pct": result.get("pillar2", {}).get("best_mos_pct"),
            "moat_type":          result.get("pillar1", {}).get("moat_type"),
            "gate_passed":        result.get("gate_passed", False),
            "fail_reasons":       "; ".join(result.get("fail_reasons", [])),
            "risk_profile":       result.get("risk_profile"),
            "horizon":            result.get("horizon"),
            "position_pct":       result.get("position_pct"),
            "thesis":             result.get("thesis"),
            "invalidation_triggers": "; ".join(result.get("invalidation_triggers", [])),
            "screener_loaded":    result.get("screener_loaded", False),
            "sector":             result.get("sector", ""),
            "best_in_sector":     result.get("best_in_sector", False),
            "sector_rank":        result.get("sector_rank"),
            "sector_total":       result.get("sector_total"),
        }, on_conflict="ticker,date").execute()
    except Exception as e:
        print(f"[DB] save error for {result.get('ticker')}: {e}")


# ==================== WATCHLIST (SUPABASE) ====================

def update_watchlist(results: List[Dict]) -> List[Dict]:
    """
    Add MONITOR stocks (50-64) to watchlist.
    Alert if any watchlist stock crossed into BUY (≥65) today.
    Returns list of crossover alert dicts.
    """
    try:
        db        = get_supabase()
        alerts    = []
        score_map = {r["ticker"]: r for r in results if r.get("gate_passed")}

        # Fetch existing watchlist
        rows = db.table("watchlist").select("ticker,score_when_added,alerted").execute().data or []
        existing_tickers = {row["ticker"] for row in rows}

        for row in rows:
            ticker  = row["ticker"]
            alerted = row["alerted"]
            result  = score_map.get(ticker)
            if not result:
                continue
            score = result["composite_score"]
            if score >= 65 and not alerted:
                alerts.append(result)
                db.table("watchlist").update({"score_today": score, "alerted": True}).eq("ticker", ticker).execute()
            else:
                db.table("watchlist").update({"score_today": score}).eq("ticker", ticker).execute()

        # Add new MONITOR stocks
        for r in results:
            if r.get("gate_passed") and 50 <= r["composite_score"] < 65 and r["ticker"] not in existing_tickers:
                db.table("watchlist").upsert({
                    "ticker":           r["ticker"],
                    "sector":           r.get("sector", ""),
                    "date_added":       datetime.now().date().isoformat(),
                    "score_when_added": r["composite_score"],
                    "score_today":      r["composite_score"],
                    "alerted":          False,
                }, on_conflict="ticker").execute()

        # Remove stocks that dropped below 45 and were never alerted
        db.table("watchlist").delete().lt("score_today", 45).eq("alerted", False).execute()

        return alerts
    except Exception as e:
        print(f"[Watchlist] error: {e}")
        return []


def format_watchlist_alert(alerts: List[Dict]) -> Optional[str]:
    if not alerts:
        return None
    msg = "*🚨 WATCHLIST CROSSOVER ALERT*\n\n"
    msg += "_These stocks moved from MONITOR → BUY territory today:_\n\n"
    for r in alerts:
        p1  = r.get("pillar1", {})
        p2  = r.get("pillar2", {})
        mos = p2.get("best_mos_pct")
        msg += (
            f"*{r['stock_name']}* — {r['recommendation']} | {r['composite_score']}/100\n"
            f"Moat: {p1.get('moat_type', 'N/A')} | ROCE: {p1.get('avg_roce', 'N/A')}%"
            + (f" | MoS {mos:.0f}%" if mos else "") + "\n"
            + (f"_{r['thesis'][:150].strip()}_\n\n" if r.get('thesis') else "\n")
        )
    msg += "_Consider buying on Groww. Review thesis before acting._"
    return msg


# ==================== PEER COMPARISON ====================

def tag_best_in_sector(results: List[Dict]) -> List[Dict]:
    """
    For each sector, find the highest scoring stock and tag it as best in sector.
    Also computes each stock's percentile rank within its sector.
    """
    from collections import defaultdict
    sector_groups: Dict[str, List[Dict]] = defaultdict(list)

    for r in results:
        if r.get("gate_passed") and r.get("sector"):
            sector_groups[r["sector"]].append(r)

    for sector, stocks in sector_groups.items():
        if len(stocks) < 2:
            continue
        stocks_sorted = sorted(stocks, key=lambda x: x["composite_score"], reverse=True)
        # Tag the top stock in each sector
        stocks_sorted[0]["best_in_sector"] = True
        # Add sector rank to all
        for i, s in enumerate(stocks_sorted):
            s["sector_rank"]  = i + 1
            s["sector_total"] = len(stocks_sorted)

    return results


def save_to_db(conn, result: Dict):
    save_recommendation(result)


# ==================== HOLDINGS MONITOR ====================

def get_holdings() -> List[Dict]:
    """Fetch all active holdings from Supabase."""
    try:
        db   = get_supabase()
        rows = db.table("holdings").select("*").eq("active", True).execute().data or []
        return rows
    except Exception as e:
        print(f"[Holdings] fetch error: {e}")
        return []


def add_holding(ticker: str, buy_price: float, quantity: int, notes: str = "") -> bool:
    """Insert a new holding into Supabase."""
    try:
        db = get_supabase()
        db.table("holdings").insert({
            "ticker":           ticker.upper(),
            "buy_price":        buy_price,
            "quantity":         quantity,
            "buy_date":         datetime.now().date().isoformat(),
            "invested_amount":  round(buy_price * quantity, 2),
            "notes":            notes,
            "active":           True,
        }).execute()
        return True
    except Exception as e:
        print(f"[Holdings] insert error: {e}")
        return False


def monitor_holdings() -> Optional[str]:
    """
    Run full analysis on all active holdings.
    Generate an alert if any holding shows a red flag:
      - Composite score dropped ≥15 pts vs score_at_buy
      - Pillar 3 health score < 8/20
      - Sentiment flipped to EXTREME_GREED (overvalued, consider selling)
      - MoS turned deeply negative (price > 120% of intrinsic)
      - P&L summary with current STCG/LTCG tax impact
    Returns a formatted Telegram message, or None if all clear.
    """
    holdings = get_holdings()
    if not holdings:
        return None

    print(f"\n📊 Monitoring {len(holdings)} holdings...")

    alerts   = []
    all_ok   = []

    for h in holdings:
        ticker     = h["ticker"]
        buy_price  = h["buy_price"]
        quantity   = h["quantity"]
        buy_date   = h.get("buy_date", "")
        score_ref  = h.get("score_at_buy") or 65  # default if not stored

        print(f"  [{ticker}]", end=" ", flush=True)
        try:
            result = analyse_stock(ticker)
        except Exception as e:
            print(f"error: {e}")
            continue

        if result is None:
            print("no data")
            continue

        score       = result.get("composite_score", 0)
        p2          = result.get("pillar2", {})
        p3          = result.get("pillar3", {})
        p5          = result.get("pillar5", {})
        curr_price  = p2.get("current_price") or buy_price
        sentiment   = p5.get("sentiment_signal", "NEUTRAL")
        mos         = p2.get("best_mos_pct")

        # P&L
        pnl_per_share = curr_price - buy_price
        pnl_total     = round(pnl_per_share * quantity, 2)
        pnl_pct       = round((pnl_per_share / buy_price) * 100, 1) if buy_price else 0

        # Holding period (days)
        try:
            from datetime import date
            held_days = (date.today() - date.fromisoformat(buy_date)).days if buy_date else 0
        except Exception:
            held_days = 0
        held_months = held_days / 30

        # Tax on current P&L
        invested = buy_price * quantity
        tax_info = tax_and_breakeven(buy_price, invested)
        if tax_info:
            ea = tax_info  # reuse exit_analysis logic below
        gross_gain  = pnl_total
        if gross_gain > 0:
            if held_months < 12:
                tax_on_pnl  = gross_gain * STCG_RATE
                tax_type    = "STCG 20%"
            else:
                taxable     = max(0, gross_gain - LTCG_EXEMPTION)
                tax_on_pnl  = taxable * LTCG_RATE
                tax_type    = "LTCG 12.5%"
            net_pnl     = round(gross_gain - tax_on_pnl, 2)
        else:
            tax_on_pnl  = 0
            tax_type    = "—"
            net_pnl     = round(gross_gain, 2)

        # Detect red flags
        red_flags = []
        score_drop = score_ref - score
        if score_drop >= 15:
            red_flags.append(f"Score fell {score_drop} pts ({score_ref} → {score})")
        if (p3.get("score") or 20) < 8:
            red_flags.append(f"Financial health weak ({p3.get('score', '?')}/20)")
        if sentiment == "EXTREME_GREED_AVOID":
            red_flags.append("Sentiment: extreme greed — market may be overvaluing")
        if mos is not None and mos < -20:
            red_flags.append(f"Stock now {abs(mos):.0f}% ABOVE intrinsic value — overvalued")
        if pnl_pct <= -10:
            red_flags.append(f"Down {abs(pnl_pct):.1f}% — approaching stop-loss territory")

        entry = {
            "ticker":       ticker,
            "stock_name":   result.get("stock_name", ticker),
            "buy_price":    buy_price,
            "curr_price":   curr_price,
            "quantity":     quantity,
            "pnl_total":    pnl_total,
            "pnl_pct":      pnl_pct,
            "net_pnl":      net_pnl,
            "tax_on_pnl":   round(tax_on_pnl, 2),
            "tax_type":     tax_type,
            "held_days":    held_days,
            "score":        score,
            "score_ref":    score_ref,
            "mos":          mos,
            "sentiment":    sentiment,
            "red_flags":    red_flags,
            "recommendation": result.get("recommendation", ""),
            "p1":           result.get("pillar1", {}),
        }

        if red_flags:
            alerts.append(entry)
            print(f"⚠ {len(red_flags)} flag(s): {', '.join(red_flags[:1])}")
        else:
            all_ok.append(entry)
            print(f"✓ {score}/100 | P&L {pnl_pct:+.1f}%")

    if not alerts and not all_ok:
        return None

    # Format the full holdings report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"*📊 ALPHAVISION PORTFOLIO MONITOR*\n_{now} IST_\n\n"

    if alerts:
        msg += "*⚠ ACTION REQUIRED ──*\n\n"
        for e in alerts:
            pnl_sign = "+" if e["pnl_pct"] >= 0 else ""
            msg += (
                f"*{e['stock_name']}* | {e['score']}/100 | "
                f"P&L: *{pnl_sign}{e['pnl_pct']:.1f}%* "
                f"(₹{e['pnl_total']:+,.0f})\n"
                f"Bought @ ₹{e['buy_price']:.0f} → Now ₹{e['curr_price']:.0f} "
                f"| Held {e['held_days']}d\n"
                f"Net after {e['tax_type']}: ₹{e['net_pnl']:+,.0f}\n"
            )
            for flag in e["red_flags"]:
                msg += f"🚨 {flag}\n"
            msg += "\n"

    if all_ok:
        msg += "*✅ HOLDINGS OK ──*\n\n"
        for e in all_ok:
            pnl_sign = "+" if e["pnl_pct"] >= 0 else ""
            mos_str  = f" | MoS {e['mos']:.0f}%" if e["mos"] is not None else ""
            msg += (
                f"*{e['stock_name']}* | {e['score']}/100{mos_str} | "
                f"*{pnl_sign}{e['pnl_pct']:.1f}%* "
                f"(₹{e['net_pnl']:+,.0f} net of {e['tax_type']})\n"
                f"@ ₹{e['buy_price']:.0f} → ₹{e['curr_price']:.0f} | {e['held_days']}d held\n\n"
            )

    msg += "_AlphaVision | Monitor your investments daily_"
    return msg


def format_buy_confirmation(ticker: str, price: float, qty: int) -> str:
    """Telegram reply after /buy command."""
    invested = price * qty
    t = tax_and_breakeven(price, invested)
    if not t:
        return f"✅ *{ticker}* logged: {qty} shares @ ₹{price:.0f} (₹{invested:,.0f})"
    stcg = t["stcg_at_target"]
    ltcg = t["ltcg_at_target"]
    return (
        f"✅ *{ticker} added to portfolio*\n"
        f"{qty} shares @ ₹{price:.0f} = ₹{invested:,.0f} invested\n\n"
        f"Break-even: ₹{t['breakeven_price']:.1f}\n"
        f"Stop-loss: ₹{t['stoploss_price']:.1f} (−₹{abs(t['stoploss_loss']):,.0f})\n\n"
        f"To earn 15% net:\n"
        f"• Sell before 1yr @ ₹{t['stcg_target_price']:.1f} "
        f"(after ₹{stcg['tax']:,.0f} STCG tax)\n"
        f"• Hold > 1yr, sell @ ₹{t['ltcg_target_price']:.1f} "
        f"(after ₹{ltcg['tax']:,.0f} LTCG tax)\n"
    )


def run_daily_analysis():
    validate_env()
    print("🚀 AlphaVision Deep Value Engine Starting...")
    print(f"   Analysing {len(NIFTY_50_STOCKS)} stocks\n")

    results      = []
    disqualified = []

    for symbol in NIFTY_50_STOCKS:
        print(f"  [{symbol}]", end=" ", flush=True)
        try:
            result = analyse_stock(symbol)
            if result is None:
                print("skip (no data)")
                continue
            if result["gate_passed"]:
                results.append(result)
                print(f"✓ {result['composite_score']}/100 {result['recommendation']}")
            else:
                disqualified.append(result)
                print(f"✗ DISQUALIFIED")
        except Exception as e:
            print(f"✗ Error: {str(e)[:60]}")

    # Sort by composite score
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    print(f"\n✓ Analysis complete: {len(results)} scored, {len(disqualified)} disqualified")

    # Peer comparison — tag best in sector
    results = tag_best_in_sector(results)

    # Watchlist: check crossovers, add new MONITOR stocks
    watchlist_alerts = update_watchlist(results)

    # Save all results to Supabase
    for r in results + disqualified:
        save_recommendation(r)

    # Send main daily report
    message = format_telegram_message(results, disqualified)
    send_telegram_message(message)

    # Send watchlist crossover alerts separately
    alert_msg = format_watchlist_alert(watchlist_alerts)
    if alert_msg:
        send_telegram_message(alert_msg)

    # Monitor active holdings and send alert if any red flags
    portfolio_msg = monitor_holdings()
    if portfolio_msg:
        send_telegram_message(portfolio_msg)


if __name__ == "__main__":
    # GitHub Actions cron runs this once daily at 9:15 AM IST and exits.
    # Scheduling is handled entirely by .github/workflows/daily_analysis.yml
    run_daily_analysis()
