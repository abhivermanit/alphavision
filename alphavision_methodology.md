# AlphaVision Stock Analysis Methodology
## Indian Equity Markets — Deep Value, Long-Term Investment Framework (5–7 Year Horizon)

---

## Philosophy

AlphaVision is built on one conviction: **price is what you pay, value is what you get**. We hunt for businesses worth ₹100 that the market is selling for ₹50–60 — and we hold until the gap closes, however long that takes.

This is not a momentum system. It is not a trading system. It is a **business quality + intrinsic value engine** designed for the patient investor willing to hold through noise, drawdowns, and market irrationality to capture compounding over 5–7 years.

### Core Tenets
1. **Margin of Safety first.** No matter how good the business, we never overpay. A great company at a terrible price is a terrible investment.
2. **Quality gate before valuation.** We do not value junk businesses. Fundamental quality is screened before any valuation work begins.
3. **Permanent capital loss > temporary drawdown.** A 40% drawdown in a great business at fair value is an opportunity. A 40% drawdown in a leveraged, low-quality business may be permanent. We distinguish between the two.
4. **Moat is everything.** Competitive advantage determines whether earnings compound or erode. Every analysis must answer: *why will this business earn above-average returns 7 years from now?*
5. **India-specific context always.** Indian promoter culture, regulatory environment, capital allocation history, and sector dynamics are embedded into every scoring dimension.

---

## Data Inputs Required

The AI agent must have access to all of the following before scoring any stock:

### From yfinance / NSE Data
- [ ] 5-year daily price history (OHLCV)
- [ ] Current market cap, 52-week high/low
- [ ] Average daily traded volume (last 90 days)
- [ ] SMA 50, SMA 200
- [ ] Beta (vs Nifty 500)

### From Screener.in Exported Data
- [ ] 10-year P&L: Revenue, EBITDA, PAT, EPS
- [ ] 10-year Balance Sheet: Total assets, equity, debt, cash
- [ ] 10-year Cash Flow: CFO, capex, FCF
- [ ] Key ratios: ROE, ROCE, D/E, Current ratio, Interest coverage
- [ ] Promoter holding % (quarterly, last 12 quarters)
- [ ] Pledge % of promoter holding
- [ ] Institutional holding (FII + DII %)
- [ ] Peer comparison table (same sector, same size)

### From Annual Reports / Concall Transcripts
- [ ] Management commentary on growth outlook (last 2 years)
- [ ] Capex guidance and purpose (expansion vs maintenance)
- [ ] Competitive positioning statements
- [ ] Related party transaction disclosures
- [ ] Auditor remarks, qualifications, emphasis of matter
- [ ] Contingent liabilities footnotes
- [ ] Segment-wise revenue and margin breakdown

### From News & Social Sentiment
- [ ] Recent regulatory actions (SEBI, RBI, FDA, NPPA, CCI)
- [ ] Promoter buy/sell activity (insider transactions)
- [ ] X/Twitter and Reddit sentiment score (last 30 days)
- [ ] Analyst upgrade/downgrade events (last 90 days)
- [ ] Any ongoing litigation, fraud allegations, or governance controversies

---

## Pre-Screening Gate (Pass/Fail — Run Before Scoring)

Before any stock enters the scoring engine, it must pass ALL of the following hard filters. Failure on any single filter = **immediate disqualification** from further analysis.

### Governance & Promoter Gate
| Filter | Threshold | Fail Condition |
|---|---|---|
| Auditor qualification | Clean audit | Any adverse/qualified opinion |
| Promoter pledge | < 20% of holding | ≥ 20% pledged |
| Promoter holding trend | Stable or increasing | Declining > 5% in last 4 quarters |
| Related party transactions | < 10% of revenue | RPT > 10% without clear rationale |
| Auditor tenure | Same Big 4 / reputed auditor | Frequent auditor changes |
| SEBI/NCLT actions | None active | Any active enforcement action |

### Financial Health Gate
| Filter | Threshold | Fail Condition |
|---|---|---|
| Interest coverage ratio | > 2.0x | ≤ 2.0x for non-financial companies |
| CFO positive | Positive in 3 of last 5 years | Negative CFO > 2 consecutive years |
| Revenue trajectory | Not in structural decline | Revenue declining > 15% YoY for 2+ years |
| Working capital fraud check | Receivable days stable | Receivables growing 2x faster than revenue |

### Liquidity Gate (Runs After Fundamental Gate)
| Filter | Threshold | Note |
|---|---|---|
| Avg daily traded value | > ₹50 Lakhs/day | Micro-caps below this — flag, do not score |
| Market cap | > ₹100 Cr | Below this — operator risk too high |
| Free float | > 20% | Below this — price manipulation risk |

> **Small Cap Note:** If a stock passes the governance and financial health gate but fails the liquidity gate, it is flagged as **WATCHLIST — ILLIQUID**. It receives a full score but carries an automatic 10-point penalty to the final composite score, and position sizing is capped at 3%.

---

## Composite Scoring Model

Every stock that passes the pre-screening gate is scored 0–100 across five pillars.

| Pillar | Weight | What It Captures |
|---|---|---|
| Business Quality & Moat | 30% | Durability of competitive advantage |
| Valuation & Margin of Safety | 30% | How cheap vs intrinsic value |
| Financial Health | 20% | Balance sheet strength, cash generation |
| Management Quality | 10% | Capital allocation, governance track record |
| Macro & Sentiment | 10% | Tailwinds, positioning, narrative |

### Score → Recommendation Map

| Score | Recommendation | Action |
|---|---|---|
| 80–100 | 🟢 STRONG BUY | High conviction entry; up to 8–10% portfolio |
| 65–79 | 🟡 BUY | Gradual accumulation over 3–6 months |
| 50–64 | ⚪ MONITOR | On watchlist; wait for better price or catalyst |
| 35–49 | 🟠 WEAK | Avoid fresh entry; hold only if already owned |
| 0–34 | 🔴 AVOID / EXIT | Do not invest; exit if held |

---

## Pillar 1: Business Quality & Moat (30%)

**The central question: Will this business earn above-average returns on capital 7 years from now?**

### 1.1 Moat Type Identification
The AI agent must classify the moat type. Each type has different durability and India-specific signals:

| Moat Type | India Examples | How to Identify |
|---|---|---|
| **Cost Advantage** | Coal India, IRCTC, Garware Technical | Lowest cost producer in sector; margins above peers consistently |
| **Switching Costs** | TCS, HDFC Bank, Asian Paints | High customer retention; recurring revenue; long client relationships |
| **Network Effects** | BSE, CDSL, Info Edge (Naukri) | Value increases with users; near-monopoly in niche |
| **Intangible Assets** (Brand/IP/License) | Nestle India, Pidilite, Page Industries | Premium pricing power; brand recall; regulatory licenses |
| **Efficient Scale** | CONCOR, Container Corp, Gas Authority | Natural monopoly / duopoly; high entry barriers |
| **No Moat** | Commodity producers, EPC contractors | Cannot price above cost of capital sustainably |

**Scoring:**
- Strong identifiable moat + 10-year evidence: 25–30 points
- Emerging moat / moat under threat: 15–24 points
- Weak or no moat: 0–14 points

### 1.2 Return on Capital Employed (ROCE) — 10-Year Trend
- ROCE > 20% consistently: Exceptional moat (Pidilite, Asian Paints, HDFC Bank)
- ROCE 15–20%: Good business
- ROCE 10–15%: Average; needs moat justification
- ROCE < 10%: Capital destroyer — disqualify unless deep turnaround thesis

> **Why ROCE over ROE:** ROE can be inflated by leverage. ROCE strips out the financing decision and tells you how well the business itself allocates capital — the true test of a moat.

### 1.3 Incremental ROCE (IROE)
- **What it is:** Return earned on NEW capital deployed in last 3 years
- **Formula:** Change in EBIT ÷ Change in Capital Employed
- **Why it matters:** Historical ROCE tells you the past. IROE tells you if the moat is *holding* as the business scales
- **Threshold:** IROE > 15% signals the business can reinvest at high rates — the engine of compounding

### 1.4 Revenue Concentration Risk
- Top 1 customer > 30% of revenue: High concentration risk
- Exports > 60% to single geography: FX + geopolitical risk
- Single product > 70% of revenue: Product obsolescence risk

### 1.5 Sectoral Competitive Intensity Check
Score the sector on Porter's Five Forces (simplified):
- Threat of new entrants (capital requirements, regulatory barriers)
- Supplier bargaining power (raw material dependency)
- Customer bargaining power (B2B vs B2C, contract lengths)
- Substitute threat
- Rivalry intensity

---

## Pillar 2: Valuation & Margin of Safety (30%)

**We use three valuation methods. Each produces an intrinsic value estimate. The composite Margin of Safety (MoS) is the average discount across all three.**

### 2.1 Graham Number (P/E + P/B Composite)
Classic Benjamin Graham approach — appropriate for asset-heavy and stable-earning businesses.

**Formula:**
```
Graham Number = √(22.5 × EPS × Book Value Per Share)
```

**Interpretation:**
- Current price < Graham Number by > 30%: Strong value signal
- Current price < Graham Number by 15–30%: Moderate value
- Current price > Graham Number: No margin of safety on this metric

**India-specific adjustments:**
- Use 3-year average EPS (not trailing) to smooth cyclicality
- Exclude goodwill and intangibles from book value for conservative estimate
- For NBFCs/banks: use P/B vs historical band instead (Graham Number not applicable)
- **Do not apply to:** Loss-making companies, negative book value companies, pure holding companies

### 2.2 Discounted Cash Flow (Conservative DCF)
Appropriate for capital-light, high-FCF businesses (IT, FMCG, Pharma).

**Framework:**
```
Intrinsic Value = Sum of PV of FCF (Years 1–7) + Terminal Value

FCF Projection:
- Use last 5-year median FCF growth rate
- Cap at min(historical rate, 15%) — never assume > 15% growth
- Apply 20% haircut to projected FCF (conservatism buffer)

Discount Rate:
- Large cap: 12%
- Mid cap: 14%
- Small cap: 16–18%
(Reflects India equity risk premium + size premium)

Terminal Growth Rate:
- 4–5% (India nominal GDP growth floor)
- Never use > 6%

Margin of Safety:
- Buy only if current price < 60% of DCF value (i.e., > 40% MoS)
```

**Red flags in DCF:**
- If the valuation only works with > 20% growth: The business is priced for perfection — avoid
- If FCF is consistently lower than reported PAT: Earnings quality issue — use lower FCF

### 2.3 EV/EBITDA + FCF Yield (Relative + Absolute Combo)
Best for cyclical sectors, capital-intensive businesses, and peer comparison.

**EV/EBITDA:**
```
EV = Market Cap + Total Debt - Cash & Equivalents
EV/EBITDA scoring:
- < 8x: Potentially deep value (check why — sector headwind? temporary earnings dip?)
- 8–15x: Reasonable for quality business
- > 20x: Expensive; requires exceptional growth to justify
- Compare vs: 5-year historical average for the stock AND sector median
```

**FCF Yield:**
```
FCF Yield = Free Cash Flow ÷ Market Cap × 100
- > 8%: Excellent — stock is generating strong cash vs its price
- 5–8%: Good
- 3–5%: Fair
- < 3%: Expensive or capital-hungry business
```

**FCF Quality Check:**
```
FCF Conversion = FCF ÷ PAT
- > 80%: High quality earnings (cash backs profit)
- 50–80%: Acceptable
- < 50%: Earnings may be accounting-driven, not real cash — discount valuation
```

### 2.4 Composite Margin of Safety Score

| Method | MoS Calculated | Weight |
|---|---|---|
| Graham Number discount | % below Graham Number | 30% |
| DCF discount | % below DCF intrinsic value | 40% |
| FCF Yield attractiveness | FCF yield rank vs peers | 30% |

**Final MoS Score → Points:**
- Composite MoS > 40%: 25–30 points
- Composite MoS 25–40%: 18–24 points
- Composite MoS 10–25%: 10–17 points
- Composite MoS < 10% or stock is expensive: 0–9 points

---

## Pillar 3: Financial Health (20%)

**A great business at a great price is worthless if the balance sheet breaks before the thesis plays out.**

### 3.1 Debt Analysis
| Metric | Green | Yellow | Red |
|---|---|---|---|
| D/E Ratio (non-financial) | < 0.5 | 0.5–1.5 | > 1.5 |
| Net Debt/EBITDA | < 1.5x | 1.5–3x | > 3x |
| Interest Coverage | > 5x | 2–5x | < 2x |
| Debt maturity profile | Long-term (> 3 yr) | Mixed | Short-term heavy |

> **India note:** Post IL&FS (2018) and DHFL collapse, high-debt Indian companies face severe re-rating risk during credit tightening. Prefer net-debt-free or low-debt businesses — the peace of mind is worth the valuation premium.

### 3.2 Cash Flow Quality
- **CFO/PAT ratio > 1.0** over 5 years: Cash earnings exceed accounting earnings — the gold standard
- **Consistent positive CFO:** 4 out of 5 years minimum
- **Capex characterization:** Is capex maintenance (sustaining existing business) or growth (expanding capacity)?
  - Maintenance capex > 60% of CFO: Business is a treadmill, not a compounder
  - Growth capex with ROCE > cost of capital: Value-creating

### 3.3 Working Capital Analysis
**Receivable Days, Inventory Days, Payable Days — track 5-year trend:**
- Receivables rising faster than revenue: Potential channel stuffing or collection risk
- Inventory build-up without revenue growth: Demand slowdown signal
- **Negative working capital** (payables > receivables + inventory): Suppliers fund the business — highest quality signal (D-Mart, Infosys model)

### 3.4 Altman Z-Score (Bankruptcy Risk)
```
Z = 1.2×(Working Capital/Total Assets) + 1.4×(Retained Earnings/Total Assets)
    + 3.3×(EBIT/Total Assets) + 0.6×(Market Cap/Total Liabilities)
    + 1.0×(Revenue/Total Assets)

Z > 2.99: Safe zone
1.81–2.99: Grey zone — caution
< 1.81: Distress zone — avoid
```

### 3.5 Dividend & Capital Allocation Track Record
- **Consistent dividend payer:** Signals real earnings, promoter confidence
- **Buybacks at low valuations:** Best use of capital — management acts like owners
- **Acquisitions:** Scrutinize. Most Indian acquisitions destroy value. Check post-acquisition ROCE
- **Unnecessary cash hoarding:** Large cash with no deployment plan — question promoter intent

---

## Pillar 4: Management Quality (10%)

**In India, you are co-investing with the promoter. Their character, competence, and capital allocation history matter as much as the business fundamentals.**

### 4.1 Promoter Character Assessment
| Signal | Positive | Negative |
|---|---|---|
| Shareholding trend | Increasing / stable | Declining consistently |
| Pledging history | Zero or declining | Rising pledge % |
| Salary vs profits | Reasonable (< 5% PAT) | Excessive extraction |
| Related party deals | Minimal, arm's length | Large, opaque RPTs |
| Past regulatory actions | Clean record | SEBI/SFIO/ED history |
| Public communication | Transparent, consistent | Opaque, over-promising |

### 4.2 Capital Allocation Scorecard
Assess the last 5–7 years of capital allocation decisions:
- **ROCE on new investments:** Did new capex earn above cost of capital?
- **Acquisition track record:** Were acquired businesses integrated successfully?
- **Debt management:** Was debt taken on for growth or survival?
- **Shareholder returns:** Dividends, buybacks, or value-destructive diversification?

Score 1–10 on capital allocation quality. Convert to 0–10 points in this pillar.

### 4.3 Concall & Annual Report Quality Checks
AI agent must parse last 4 concall transcripts and last 2 annual reports for:
- **Consistency:** Do management projections from 2 years ago match today's reality?
- **Candor:** Do they acknowledge failures, or only celebrate wins?
- **Specificity:** Vague language ("we are optimistic about the future") = low quality. Specific guidance with reasoning = high quality
- **Red flag phrases:** "One-time item" appearing every year, "working capital normalization," "demand environment remains challenging"

### 4.4 Skin in the Game
- Promoter holding > 50%: High alignment
- Promoter has personal wealth tied to business (no excessive diversification into unrelated businesses)
- Management compensation linked to ROCE / shareholder returns (check ESOP terms)

---

## Pillar 5: Macro & Sentiment (10%)

### 5.1 Sector Cycle Positioning
Map the sector to its position in the business cycle:

| Cycle Phase | Characteristics | Action |
|---|---|---|
| **Early Recovery** | Valuations low, news bad, smart money accumulating | Best buying opportunity |
| **Growth Phase** | Earnings upgrades, institutional buying | Add to winners |
| **Euphoria** | High valuations, retail frenzy, every stock "going up" | Stop buying, review exits |
| **Contraction** | Earnings misses, de-rating, sector headwinds | Avoid, wait |

### 5.2 India Macro Signals (Agent must check)
- **RBI Rate Cycle:** Easing = bullish for banking, NBFC, real estate, auto. Tightening = rotate to defensive
- **INR vs USD:** Weak INR = headwind for import-heavy (oil, electronics); tailwind for IT exporters
- **FII Flow Trend:** 3-month rolling FII net buy/sell in sector — persistent selling = valuation opportunity if fundamentals intact
- **Government Capex Cycle:** Budget allocation to infra, defense, railways — identifies structural tailwind sectors
- **GST Collection Trend:** Proxy for economic activity; 3 consecutive months of > ₹1.5 lakh Cr = healthy demand
- **PLI Scheme Status:** Which companies have received PLI disbursements (vs just approvals) — disbursement = real cash flow impact

### 5.3 Sentiment Scoring (Contrarian Framework)
```
Sentiment Score (0–100):
- 0–20: Extreme Fear — potential contrarian BUY (if fundamentals intact)
- 20–40: Pessimism — monitor closely
- 40–60: Neutral — sentiment not a factor
- 60–80: Optimism — cautious; verify fundamentals support price
- 80–100: Extreme Greed — avoid new entry; consider trimming

Sources: X/Twitter keyword analysis, Reddit (r/IndiaInvestments, r/Dalal_Street),
         Google Trends for stock name, analyst consensus direction
```

**Contrarian rule:** Sentiment score < 25 on a stock with composite fundamental score > 65 = highest-priority buy signal.

### 5.4 Institutional Activity Signals
- **Mutual fund SIP inflows into sector:** Structural demand for sector stocks
- **FII buying after sustained selling:** Smart money re-entry signal
- **Bulk/block deal analysis:** Who is buying and selling in large quantities (NSE bulk deal data)
- **Insider buying (promoter market purchases):** Strongest signal of undervaluation

---

## Fraud & Red Flag Detection Framework

**India-specific forensic checks the AI agent must run on every stock:**

### Accounting Red Flags
| Red Flag | What to Check | Source |
|---|---|---|
| Cash vs profit divergence | 3-year CFO/PAT < 0.5 | Screener cash flow |
| Receivables inflation | Receivable days growing > 30% YoY | Screener ratios |
| Inventory manipulation | Inventory days growing without revenue growth | Screener ratios |
| Capitalization of expenses | R&D / marketing being capitalized | Annual report notes |
| Frequent restatements | Any prior year restatement | Annual report |
| Auditor change | Change without clear reason | BSE filings |
| Subsidiaries explosion | Large number of subsidiaries, esp. overseas | Annual report |
| Other income > 20% PAT | Non-operating income masking weak core business | Screener P&L |

### Promoter Red Flags
- Promoter pledge crossing 20% — especially if rising trend
- Promoter selling in open market while pledging (double exit signal)
- Promoter salary > ₹10 Cr in a company with < ₹100 Cr PAT
- Multiple group companies with inter-company loans at below-market rates
- Promoter converting warrants only when stock is at high prices

### Operator Risk (Small Cap Specific)
- Price up > 100% in 12 months with no fundamental change
- Volume spikes (5–10x normal) with no news
- Bulk of trading in BSE SME / low-liquidity exchange
- Company appearing in "penny stock" screeners repeatedly

---

## Sector-Specific Scoring Adjustments

### IT Services (TCS, Infosys, Wipro, HCL, LTIMindtree)
**Additional metrics:** Deal TCV (Total Contract Value) wins, revenue-per-employee trend, EBIT margin guidance, attrition rate
**Valuation anchor:** FCF yield + P/E vs historical band (DCF less reliable due to lumpy capex)
**Key risk:** US tech spending slowdown, visa cost inflation, AI commoditizing low-value IT work
**Moat check:** Is revenue sticky (multi-year contracts) or project-based?

### Banking & NBFC (HDFC Bank, ICICI, Kotak, Bajaj Finance)
**Do NOT use D/E, Graham Number.** Use instead:
- NIM (Net Interest Margin): > 4% for retail banks is good
- GNPA / NNPA: Gross/Net NPA < 2% / 1% for quality banks
- PCR (Provision Coverage Ratio): > 70% shows conservative provisioning
- RoA: > 1.5% for banks; > 3% for NBFCs
- CASA ratio: > 40% = low-cost funding advantage
**Valuation:** P/B vs historical band; P/ABV (Adjusted Book Value)

### Pharma (Sun, Dr. Reddy, Cipla, Divi's)
**Additional metrics:** US ANDA pipeline, US FDA audit status (VAI/OAI), domestic formulations growth, API vs formulations mix
**Key risk:** US FDA import alert = immediate 20–30 point score penalty
**Moat check:** Complex generics pipeline, branded generics in India, CDMO relationships

### Consumer Staples (Nestle, HUL, Pidilite, Asian Paints)
**Primary moat check:** Brand pricing power — can they raise prices without volume loss?
**Valuation:** Premium P/E is justified; use FCF yield and PEG ratio
**Key metric:** Volume growth (not just value growth) — if only value growing via price hikes, demand is weak

### Capital Goods / Infrastructure (L&T, Siemens, ABB)
**Additional metrics:** Order book size and executable timeline, working capital cycle, L1 win rate
**Valuation:** EV/EBITDA + order book/market cap ratio
**Key risk:** Government payment delays, commodity cost escalation in fixed-price contracts

### Real Estate (DLF, Godrej Properties, Prestige)
**Primary metric:** Pre-sales bookings, collections efficiency, net debt trajectory
**Avoid:** High-debt, low-cash-collection developers
**Opportunity:** Asset-light models (platform deals, rental yield assets)

---

## Invalidation Framework — Exit Signals

Every BUY thesis must have explicit exit conditions. We do not hold through fundamental deterioration.

| Signal | Severity | Action |
|---|---|---|
| ROCE drops below 12% for 2 consecutive years | High | Re-evaluate; likely exit |
| D/E crosses 2.0 unexpectedly (non-financial) | High | Exit within 1 quarter |
| Promoter pledge > 30% | High | Reduce position immediately |
| CFO negative for 2 consecutive years | High | Exit thesis |
| Earnings miss > 20% for 2 consecutive quarters | Medium | Re-evaluate thesis |
| Auditor resignation or adverse opinion | Critical | Exit immediately |
| Active SEBI / ED / SFIO investigation | Critical | Exit immediately |
| Key management exit (CEO/CFO) without succession | Medium | Monitor closely; re-score |
| Moat visibly eroding (new competitor, tech disruption) | High | Re-evaluate; set 6-month timeline |
| Price crosses intrinsic value by > 30% (fully valued) | Positive | Consider trimming |

---

## Position Sizing Framework

```
Position Size = f(Conviction Score, Margin of Safety, Liquidity, Portfolio Concentration)

STRONG BUY (80–100): 6–10% of portfolio
  - Build in 2–3 tranches over 3 months
  - Do not deploy full position on day one

BUY (65–79): 3–6% of portfolio
  - SIP-style accumulation over 6 months

MONITOR (50–64): 0–2% (tracking position only)

Small/Mid Cap Adjustment:
  - Mid cap (₹5,000–₹20,000 Cr market cap): Max 6% per stock
  - Small cap (₹500–₹5,000 Cr): Max 4% per stock
  - Micro cap (₹100–₹500 Cr): Max 2% per stock

Sector Concentration Cap: Never > 25% in single sector
Single Stock Cap: Never > 10% of portfolio
Cash Buffer: Maintain 10–15% cash for opportunistic buying during market dislocations
```

---

## Rebalancing & Review Cadence

| Frequency | Action |
|---|---|
| **Daily** | Price alerts for > 5% single-day moves; sentiment spike detection |
| **Weekly** | Technical check — SMA crossovers, support/resistance breaks, volume anomalies |
| **Quarterly** | Re-score after earnings results; check all Pillar 3 metrics; concall review |
| **Semi-annual** | Pillar 1 & 4 review — is the moat intact? Management quality unchanged? |
| **Annual** | Full thesis review — would you buy this stock today at today's price? If not, why hold? |

---

## Screener.in Query Template (For Agent to Generate Watchlist)

```
Value Investing Pre-Screener Query:
Market Cap > 100
Average daily volume > 50 Lakh (on NSE)
ROCE > 15%
Debt to equity < 1
Interest Coverage > 3
CFO positive (last 3 years)
Promoter holding > 40%
EPS growth 5Year > 10%
P/E < Industry P/E
P/B < 3
FCF > 0 (last 3 years)
Dividend Yield > 0.5 OR Buyback in last 3 years
```

---

## AI Agent Processing Instructions

When analyzing any stock, the agent must follow this exact sequence:

```
STEP 1: DATA COLLECTION
  → Pull all required data from yfinance, Screener export, annual report, news

STEP 2: PRE-SCREENING GATE
  → Run all governance, financial health, and liquidity filters
  → If ANY hard filter fails → OUTPUT: "DISQUALIFIED — [reason]" → STOP

STEP 3: PILLAR SCORING
  → Score each pillar independently
  → Document evidence for every score given (not just the number)
  → Flag any data gaps (missing concalls, incomplete financials)

STEP 4: COMPOSITE SCORE & RECOMMENDATION
  → Calculate weighted composite
  → Apply small/mid cap liquidity penalty if applicable
  → Map to recommendation

STEP 5: THESIS CONSTRUCTION
  → Write 3-paragraph investment thesis:
    Para 1: Why this business has durable competitive advantage
    Para 2: Why it is undervalued — which valuation metric gives margin of safety
    Para 3: What are the key risks and what would invalidate this thesis

STEP 6: MONITORING TRIGGERS
  → Set 3–5 specific, measurable signals to watch that would change the thesis
  → These should be company-specific, not generic

OUTPUT FORMAT:
  Stock Name | Score | Recommendation | MoS % | Key Risk | Thesis Summary | Next Review Date
```

---

## Glossary of India-Specific Terms

| Term | Meaning |
|---|---|
| **GNPA / NNPA** | Gross / Net Non-Performing Assets — bank loan quality metric |
| **CAR** | Capital Adequacy Ratio — RBI-mandated buffer for banks |
| **CASA** | Current Account Savings Account ratio — low-cost deposits |
| **PLI** | Production Linked Incentive — govt scheme for manufacturing |
| **NPPA** | National Pharmaceutical Pricing Authority — price control body |
| **SFIO** | Serious Fraud Investigation Office — corporate fraud investigator |
| **SEBI PCA** | Prompt Corrective Action — regulatory restriction framework |
| **NIM** | Net Interest Margin — bank profitability metric |
| **TCV** | Total Contract Value — IT deal size metric |
| **ANDA** | Abbreviated New Drug Application — US generic drug approval |
| **VAI / OAI** | Voluntary / Official Action Indicated — FDA audit outcomes |
| **PCR** | Provision Coverage Ratio — how much of bad loans are provided for |
| **F&O Expiry** | Futures & Options expiry — creates artificial price volatility weekly |
| **Operator** | Market manipulator in small/mid cap stocks — avoid operator-driven moves |
| **Promoter** | Founding family / controlling shareholder — Indian equivalent of founder |

---

*Last updated: June 2026 | Version 2.0 | AlphaVision Deep Value Framework*
*Next review: September 2026 (post Q1 FY27 earnings season)*
