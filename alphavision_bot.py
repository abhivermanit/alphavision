"""
AlphaVision — Deep Value Investment Intelligence Engine
Nifty 50 Stock Analysis | 5–7 Year Horizon | Indian Equity Markets
Methodology: alphavision_methodology.md
"""

import os
import math
import asyncio
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
import pandas as pd
import numpy as np
from anthropic import Anthropic

load_dotenv()

# ==================== CONFIG ====================
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

NIFTY_50_STOCKS = [
    "TCS", "RELIANCE", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "BAJFINANCE", "LT", "MARUTI", "ASIANPAINT",
    "SUNPHARMA", "WIPRO", "DRREDDY", "HCLTECH", "TECHM",
    "TATASTEEL", "ADANIPORTS", "POWERGRID", "NTPC", "IOC",
]

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
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
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

def get_x_sentiment(stock_name: str) -> float:
    """Keyword-based X/Twitter sentiment. Returns 0–100."""
    if not X_BEARER_TOKEN:
        return 50
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    params = {
        "query": f"{stock_name} stock India",
        "max_results": 100,
        "tweet.fields": "public_metrics",
    }
    try:
        resp = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers=headers, params=params, timeout=5,
        )
        if resp.status_code != 200:
            return 50
        tweets = resp.json().get("data", [])
        if not tweets:
            return 50
        positive = ["buy", "bullish", "strong", "growth", "profit", "outperform", "breakout", "rally"]
        negative = ["sell", "bearish", "weak", "decline", "loss", "underperform", "crash", "fraud"]
        s = 50
        for t in tweets:
            text = t.get("text", "").lower()
            s += sum(2 for w in positive if w in text)
            s -= sum(2 for w in negative if w in text)
        return min(100, max(0, s))
    except Exception:
        return 50


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
        score -= 1  # high systematic risk
    elif beta < 0.7:
        score += 1  # defensive character

    # X/Twitter sentiment with contrarian framework
    sentiment_raw = get_x_sentiment(stock_name)
    details["sentiment_raw"] = round(sentiment_raw, 1)

    if sentiment_raw <= 20:
        # Extreme fear → contrarian buy signal (if fundamentals are strong, handled in composite)
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

    score = score - 5 + sentiment_contribution  # replace neutral base with sentiment

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


# ==================== CLAUDE THESIS GENERATOR ====================

def generate_thesis_with_claude(analysis: Dict) -> str:
    client = Anthropic()

    p1 = analysis["pillar1"]
    p2 = analysis["pillar2"]
    p3 = analysis["pillar3"]

    prompt = f"""You are AlphaVision, a deep-value institutional analyst specialising in Indian equities (BSE/NSE).

Stock: {analysis['stock_name']} ({analysis['ticker']})
Sector: {p1.get('sector', analysis.get('sector', 'N/A'))}
Composite Score: {analysis['composite_score']}/100
Recommendation: {analysis['recommendation']}

Pillar Scores:
- Business Quality & Moat ({p1.get('score', 'N/A')}/30): Moat = {p1.get('moat_type', 'N/A')}, Avg ROCE = {p1.get('avg_roce', 'N/A')}%
- Valuation & MoS ({p2.get('score', 'N/A')}/30): Best MoS = {p2.get('best_mos_pct', 'N/A')}%, EV/EBITDA = {p2.get('ev_ebitda', 'N/A')}x, FCF Yield = {p2.get('fcf_yield_pct', 'N/A')}%
- Financial Health ({p3.get('score', 'N/A')}/20): D/E = {p3.get('de_ratio', 'N/A')}, Interest Coverage = {p3.get('interest_coverage', 'N/A')}x, Altman Z = {p3.get('altman_z', 'N/A')}
- Management Quality ({analysis['pillar4'].get('score', 'N/A')}/10): Promoter Holding = {analysis['pillar4'].get('promoter_holding_pct', 'N/A')}%, Pledge = {analysis['pillar4'].get('pledge_pct', 'N/A')}%
- Macro & Sentiment ({analysis['pillar5'].get('score', 'N/A')}/10): {analysis['pillar5'].get('sentiment_signal', 'N/A')}

Write exactly 3 short paragraphs (2–3 sentences each):
Para 1 — Why this business has a durable competitive advantage (reference moat type and ROCE).
Para 2 — Why it is undervalued or fairly valued right now (reference a specific valuation metric with the number).
Para 3 — The single biggest risk and what would invalidate this thesis.

Institutional tone. No bullet points. No headers. No fluff."""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"Thesis unavailable: {str(e)[:80]}"


def _fetch_nse_quote(symbol: str) -> Dict:
    """
    Fetch current price and market cap from NSE India public API.
    No rate limiting issues — NSE is the primary exchange for these stocks.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
    }
    session = requests.Session()
    session.headers.update(headers)
    try:
        # Warm up session with a cookie
        session.get("https://www.nseindia.com", timeout=10)
        time.sleep(1)
        resp = session.get(
            f"https://www.nseindia.com/api/quote-equity?symbol={symbol}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            pd_data = data.get("priceInfo", {})
            md_data = data.get("metadata", {})
            price = pd_data.get("lastPrice") or pd_data.get("close") or 0
            shares = md_data.get("issuedSize") or 0
            market_cap_cr = (price * shares) / 1e7 if shares else 0
            return {
                "currentPrice":  price,
                "marketCap_cr":  round(market_cap_cr, 0),
                "52WeekHigh":    pd_data.get("weekHighLow", {}).get("max", 0),
                "52WeekLow":     pd_data.get("weekHighLow", {}).get("min", 0),
                "symbol":        symbol,
            }
    except Exception as e:
        print(f"[NSE] {symbol} error: {e}", end=" ")
    return {}


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

    price        = nse_quote.get("currentPrice") or 0
    market_cap_cr = nse_quote.get("marketCap_cr") or 0
    market_cap_inr = market_cap_cr * 1e7  # in rupees

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

    # Book value per share (approx)
    book_value = equity_latest  # in Cr; per share needs share count

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

    # Fetch from Screener.in and NSE (no yfinance)
    screener  = fetch_screener_data(symbol)
    nse_quote = _fetch_nse_quote(symbol)

    if not nse_quote.get("currentPrice"):
        print(f"No price data from NSE — skipping")
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
        "timestamp":       datetime.now().isoformat(),
    }

    # Generate Claude thesis
    result["thesis"] = generate_thesis_with_claude(result)
    return result


# ==================== TELEGRAM MESSAGING ====================

async def _send(message: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")


def send_telegram_message(message: str):
    try:
        asyncio.run(_send(message))
        print("✓ Telegram message sent")
    except TelegramError as e:
        print(f"✗ Telegram error: {e}")


def format_telegram_message(results: List[Dict], disqualified: List[Dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"*🎯 ALPHAVISION DEEP VALUE REPORT*\n_{now} IST_\n\n"

    # Top BUY / STRONG BUY stocks
    buys = [r for r in results if r["gate_passed"] and r["composite_score"] >= 65][:5]
    if buys:
        msg += "*── TOP PICKS ──*\n\n"
        for r in buys:
            p2 = r.get("pillar2", {})
            mos = p2.get("best_mos_pct")
            mos_str = f" | MoS {mos:.0f}%" if mos else ""
            msg += (
                f"*{r['stock_name']}* ({r['ticker']})\n"
                f"{r['recommendation']} | Score: {r['composite_score']}/100{mos_str}\n"
                f"Moat: {r['pillar1'].get('moat_type', 'N/A')} | "
                f"ROCE: {r['pillar1'].get('avg_roce', 'N/A')}%\n"
                f"Horizon: {r['horizon']} | Position: {r['position_pct']}\n"
                f"_{r['thesis'][:180].strip()}..._\n\n"
            )

    # Contrarian alerts (extreme fear + strong fundamentals)
    contrarian = [
        r for r in results
        if r["gate_passed"]
        and r["pillar5"].get("sentiment_signal") == "EXTREME_FEAR_CONTRARIAN"
        and r["composite_score"] >= 55
    ]
    if contrarian:
        msg += "*── ⚡ CONTRARIAN ALERT ──*\n"
        for r in contrarian:
            msg += f"*{r['stock_name']}* — Extreme fear + score {r['composite_score']}/100\n"
        msg += "\n"

    # MONITOR stocks
    monitors = [r for r in results if r["gate_passed"] and 50 <= r["composite_score"] < 65][:3]
    if monitors:
        msg += "*── MONITOR LIST ──*\n"
        for r in monitors:
            msg += f"*{r['stock_name']}* — {r['composite_score']}/100 | {r['recommendation']}\n"
        msg += "\n"

    # Disqualified
    if disqualified:
        msg += "*── ❌ DISQUALIFIED ──*\n"
        for r in disqualified[:3]:
            msg += f"{r['stock_name']}: _{r['fail_reasons'][0]}_\n"
        msg += "\n"

    msg += "_AlphaVision | Deep Value | 5–7yr Horizon_"
    return msg


# ==================== DATABASE ====================

def init_db():
    conn = sqlite3.connect("alphavision.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS recommendations (
        ticker TEXT, date TEXT, recommendation TEXT, composite_score REAL,
        p1_moat_score REAL, p2_valuation_score REAL, p3_health_score REAL,
        p4_management_score REAL, p5_macro_score REAL,
        margin_of_safety_pct REAL, moat_type TEXT,
        gate_passed INTEGER, fail_reasons TEXT,
        risk_profile TEXT, horizon TEXT, position_pct TEXT,
        thesis TEXT, invalidation_triggers TEXT,
        screener_loaded INTEGER
    )""")
    conn.commit()
    return conn


def save_to_db(conn: sqlite3.Connection, result: Dict):
    c = conn.cursor()
    c.execute("""INSERT INTO recommendations VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        result["ticker"],
        result["timestamp"],
        result["recommendation"],
        result.get("composite_score", 0),
        result.get("pillar1", {}).get("score"),
        result.get("pillar2", {}).get("score"),
        result.get("pillar3", {}).get("score"),
        result.get("pillar4", {}).get("score"),
        result.get("pillar5", {}).get("score"),
        result.get("pillar2", {}).get("best_mos_pct"),
        result.get("pillar1", {}).get("moat_type"),
        int(result.get("gate_passed", False)),
        "; ".join(result.get("fail_reasons", [])),
        result.get("risk_profile"),
        result.get("horizon"),
        result.get("position_pct"),
        result.get("thesis"),
        "; ".join(result.get("invalidation_triggers", [])),
        int(result.get("screener_loaded", False)),
    ))
    conn.commit()


# ==================== MAIN EXECUTION ====================

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

    # Send Telegram
    message = format_telegram_message(results, disqualified)
    send_telegram_message(message)

    # Save to DB
    conn = init_db()
    for r in results + disqualified:
        save_to_db(conn, r)
    conn.close()


if __name__ == "__main__":
    run_daily_analysis()
