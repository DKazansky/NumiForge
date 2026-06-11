# CoinFalcon — Project Brief

## What This Is
CoinFalcon is a B2B AI-powered coin grading and valuation platform for professional coin dealers.
It identifies, grades, and values coins from images using computer vision (Claude Sonnet vision API),
returning structured grading data, melt value calculations, multi-source market pricing, and buying
recommendations. The core use case is bulk coin evaluation at the point of purchase.

## Current Status
**MVP v0.7.9** — active development. Two-track build:
- `coinfalcon_dev.html` — development build, all new work lands here
- `coinfalcon_demo.html` — stable build frozen for dealer demos and pilots
- `coinfalcon_proxy.py` / `coinfalcon_proxy.js` — local proxy server (required for Greysheet + PCGS APIs)

## Primary User
Coin dealers making bulk buying decisions. A dealer evaluating a collection of 20–200 coins needs
fast, reliable grades and buy prices. CoinFalcon replaces manual per-coin research.

---

## Tech Stack

### Current MVP (single-file prototype)
- **Frontend**: Vanilla HTML/CSS/JS, IBM Plex Mono + Sans, dark theme
- **Vision AI**: Claude Sonnet (`claude-sonnet-4-6`), vision API
- **Local proxy**: Flask (Python) or Node.js built-ins — required for CORS on Greysheet + PCGS
- **No backend, no database, no auth**

### API Integrations
| API | Purpose | Auth | Status |
|---|---|---|---|
| Anthropic | Vision grading | Bearer `sk-ant-...` | ✓ Working |
| CDN Greysheet | Wholesale bid + CPG + PCGS + NGC + Blue Book | `x-api-key` + `x-api-token` headers | Auth confirmed, coin lookup in progress |
| PCGS | Official retail price by PCGS# + grade | Bearer token | CORS resolved via proxy |
| Numista | Foreign coin catalog + composition + ref images | `Numista-API-Key` header | ✓ Working |
| gold-api.com | Live spot prices (XAU/XAG/XPT/XPD) | None (free) | ✓ Working |

### Planned Production Stack (Phase 2)
- **Backend**: Python + FastAPI (absorbs proxy, adds eBay API, PCGS pop report)
- **Database**: Supabase (PostgreSQL + auth + file storage)
- **Frontend**: React/Next.js
- **eBay API**: Purchased access, awaiting backend (CORS + ToS prevent client-side use)

---

## Pricing Tier Architecture
Pricing fires after grading via ⟳ Fetch Live Prices button:

| Tier | Source | Coverage |
|---|---|---|
| 0A | **CDN Greysheet API** | US coins — wholesale bid + CPG retail + PCGS + NGC + Blue Book in one call |
| 0B | **PCGS API** | US coins with PCGS# — official retail price at exact grade |
| 1 | **Web search** (PCGS CoinFacts + NGC + eBay) | All coins — AI-sourced, date-validated |
| 2 | **coinfoxa.com** | Foreign coins + Tier 1 misses |

eBay data includes 90-day staleness detection — data older than 90 days shows ⚠ STALE badge.

---

## Key Features (v0.7.9)

### Grading
- Multi-coin detection — all coins in a single image graded independently
- Grid position assignment (A1, B2...) for bulk lot reference
- Sheldon scale grading (all 30 valid grades, conservative bias)
- Denomination verification — character-by-character read with self-confirmation
- Date verification — digit-by-digit, no inference from series knowledge
- Slab detection — PCGS/NGC/ANACS/ICG holder identification
- Cert number extraction — character-by-character from slab label
- Problem flagging — cleaned, artificial toning, environmental damage, tooling, holes, edge damage
- Special designation detection — CAC, PL, DMPL, Cameo, Deep Cameo

### Pricing & Valuation
- Melt value — ASW/AGW/APW × live spot price with explicit formula display
- Greysheet dedicated panel — wholesale bid, CPG retail, PCGS guide, NGC guide, Blue Book, dealer spread, CAC flag
- Live price fetch — separate trigger, updates all coin panels in parallel
- Stale data detection — `found_date` field + client-side 90-day check

### Catalog Enrichment
- Numista integration — KM catalog refs, verified metal composition, reference images, mintage
- Metal composition cross-check — >2% discrepancy between AI and Numista flagged

### Image Quality
- Pre-flight checks — resolution (≥800px), aspect ratio, overexposure, edge contrast (Sobel)
- Canvas-based analysis, no API calls, no cost

### Export
- PDF report — cover page + per-coin pages, all grading data, Greysheet pricing, melt calc
- CSV export — all fields including holder, cert number, Greysheet prices, Numista data, stale flags

### Infrastructure
- Two-track development — `coinfalcon_dev.html` + `coinfalcon_demo.html`
- Local proxy (`coinfalcon_proxy.py`) — serves HTML files + proxies Greysheet/PCGS API calls
- API status panel — live connection dots for all 4 APIs, per-API test buttons
- Session stats — images analyzed, coins found, buy signals, avg confidence

---

## JSON Output Schema (per coin)
```
grid_position, coin_id (country, denomination, series, year, mint_mark, variety, pcgs_number),
holder (type, service, cert_number, label_grade, label_designation),
denomination_check (characters_read, verbatim_text, confirmed_denomination, confidence, note),
date (digit_1–4, full_year, date_confidence, date_note),
grade (sheldon_low/high, designation, full_grade, grade_confidence, grade_note),
surface (luster, strike, contact_marks, wear_description),
problems (cleaned, artificial_toning, environmental_damage, tooling, hole_or_mount, edge_damage, summary),
value (low_usd, mid_usd, high_usd, basis, note),
confidence_pct, overall_confidence, key_observations,
flags (is_key_date, is_semi_key, needs_expert_review, review_reason),
buying_recommendation, recommendation_reason,
precious_metal (metal, composition, fineness, gross_weight_g, asw_oz, agw_oz, apw_oz, apdw_oz, metal_note)
```

---

## Business Context
- **Stage**: Working MVP in active dealer testing
- **Owner**: Numismatic domain expert with existing dealer relationships
- **Target market**: US coin dealers, bulk buying decisions (B2B)
- **Pricing model**: $149/month flat (≤500 coins), $0.20/coin overage
- **API cost per coin**: ~$0.05 (Claude Sonnet vision)
- **Gross margin at scale**: ~85%
- **Competitive moat**: Proprietary dealer correction dataset (Phase 2) + accuracy benchmarks + dealer relationships

---

## Roadmap

### Phase 1 — Current (MVP validation)
- Dealer pilot agreements / letters of intent
- Greysheet API coin lookup completion (GsId mapping)
- PCGS API pricing confirmation
- eBay API integration (requires Phase 2 backend for CORS/ToS compliance)

### Phase 2 — Backend (60–180 days)
- FastAPI backend replacing local proxy
- Supabase (PostgreSQL + auth + file storage)
- eBay completed listings API (real sold prices, date-filtered)
- PCGS Population Report integration (scarcity context)
- Slabbed vs raw price distinction
- Dealer feedback loop → proprietary correction dataset

### Phase 3 — Scale (180–365 days)
- React/Next.js frontend
- Dealer association outreach
- Case studies + accuracy benchmarks published
- Multi-dealer pricing consensus model

---

## Coin Photo Guidance (for dealers)
- Minimum 800×800px per face; 1200×1200px preferred
- 45° raking light — reveals luster, surface texture, contact marks
- Dark matte background (black velvet or card)
- Separate obverse/reverse images; edge shot for high-grade coins
- Macro focus — coin face must fill the frame

---

## Coding Conventions
- All JS inline in single HTML file (no modules, no bundler, no build step)
- CSS variables for theming: dark bg `#0e0e0e`, gold accent `#c9a84c`
- IBM Plex Mono for all data display; IBM Plex Sans for UI text
- Python scripts for batch file edits with integrity checks after every change
- Two-track build: dev branch (`coinfalcon_dev.html`) promoted to demo (`coinfalcon_demo.html`)
- Version archives tagged in Git (`git tag v0.7.4` etc.) — no versioned filename copies needed

---

## Files in This Repository
| File | Purpose |
|---|---|
| `coinfalcon_dev.html` | Active development build |
| `coinfalcon_demo.html` | Stable demo build for dealer presentations |
| `coinfalcon_proxy.py` | Local proxy server — Python/Flask |
| `coinfalcon_proxy.js` | Local proxy server — Node.js (no npm required) |
| `coinfalcon_brief.md` | This document |
