# Implementation Roadmap — Build Track (executed in Claude Code)

Companion doc: [GTM_Plan_0_to_Max.md](GTM_Plan_0_to_Max.md) — the go-to-market
action plan the founder drives in parallel (claude.ai project + outreach).
Every build phase below names the GTM asset it unblocks; ship the build
deliverable BEFORE the GTM motion that depends on it.

Dates are anchored to today = 8 Jul 2026. Regulatory hard deadlines that
shape sequencing:
- 30 Sep 2026 — EU ETS surrender deadline for 2025 emissions (sales hook NOW)
- ~Oct 2026  — IMO NZF adoption vote (positioning moment; nzf.py goes live-mode)
- 31 Jan 2027 — FuelEU: 2026 monitoring data to verifiers
- 30 Apr 2027 — FuelEU: pooling registration for compliance year 2026
- 1 Jul 2026 — UK ETS maritime already live (ukets.py is overdue, not optional)

---

## Phase 0 — Calculation core  ✅ DONE
Engines (CII G1–G4, EU ETS 2026 rules, FuelEU balance/penalty/pooling, NZF
scenario), canonical schema, two ingestion paths, scorecard, 28-check test
suite, demo. Status: transferred from claude.ai project 7 Jul 2026, verified.

---

## Phase 0.5 — Trustworthy numbers + free lookup live (Weeks 1–2, target 24 Jul 2026)

Goal: a stranger can enter an IMO number and get an honest estimated
scorecard; every number behind it is verified or clearly labelled ESTIMATE.

| # | Deliverable | Acceptance criteria |
|---|------------|---------------------|
| D0.5.1 | VERIFY backlog top 4 cleared | G2 (a,c) + G4 dd tables checked line-by-line vs MEPC.353(78)/354(78) incl. gas-carrier ≥65k split & GC <20k dwt; FuelEU LCV/WtW vs Reg. 2023/1805 Annex II; ETS CH4/N2O factors vs MRV implementing acts; each fix cites primary source in commit msg, VERIFY tag removed |
| D0.5.2 | New ship types | LNG carrier, ro-ro, ro-pax, cruise (GT-based capacity) in schema + G2/G4 tables + tests |
| D0.5.3 | Annualisation module (`projection.py`) | Partial-year activity → projected year-end CII rating + FuelEU balance + ETS cost, with confidence band; demo Path B shows projected (not raw partial) rating |
| D0.5.4 | Per-leg EU scoping (`ports.py`) | Port → country → EEA lookup table; ingest derives INTRA/EXTRA/OUT scope from port pairs; noon-report flag about single-scope removed |
| D0.5.5 | UK ETS engine (`ukets.py`) | Mirrors euets.py with UK scope rules (live since 1 Jul 2026); scorecard shows combined EU+UK exposure |
| D0.5.6 | FastAPI service (`api/`) | `GET /lookup/{imo}` (THETIS path), `POST /score` (owner data), JSON scorecard; runs locally with `uvicorn` |
| D0.5.7 | Single-page lookup UI | IMO number in → four-score card out, ESTIMATE watermark, email-gate before full detail (lead capture), branded once name is chosen |
| D0.5.8 | Real THETIS export wired | ✅ DONE 8 Jul 2026 — no login needed: EMSA public API (`/api/public-emission-report/downloadable-files` lists versions; `/reporting-period-document/binary/{rp}/{version}` downloads). 2025-v6 (16,673 ships) + 2024-v228 in fixtures/; `load_thetis_xlsx` + per-scope leg reconstruction; `scripts/lookup.py` CLI; spot check reproduces verifier ETS-scope CO2 exactly |

Unblocks GTM: free-lookup link for outreach messages; credible "verified
against MEPC/EUR-Lex" claim.

## Phase 1 — Sales assets + paid-product core (Weeks 3–6, target 21 Aug 2026)

Goal: the free funnel produces a fleet-level PDF that opens doors, and the
paid product is demonstrable end-to-end on a design partner's real data.

| # | Deliverable | Acceptance criteria |
|---|------------|---------------------|
| D1.1 | THETIS bulk import + cache | ⚙ PARTIAL 8 Jul — full 16.7k-ship export loads in-process (~30 s once, then <1 ms lookups); persistent cache + refresh job still to do |
| D1.2 | Fleet health-check report | ✅ DONE 8 Jul — `/report?imos=…` branded print-to-PDF page (api/report.py): per-vessel table, fleet totals, FuelEU balance framing, ESTIMATE labels. Outreach targets: `scripts/build_targets.py` → outreach/targets_2025.csv (311 ICP companies ranked by verified ETS exposure) + TOP_TARGETS.md |
| D1.3 | Multi-vessel fleet dashboard | ⚙ PARTIAL 8 Jul — `/api/fleet` + report page cover read-only; interactive sortable dashboard still to do |
| D1.4 | What-if simulator | ✅ DONE 8 Jul — biofuel % + speed % on the lookup card (`_whatif` transform in api/main.py, same engines, no parallel math); savings/cost delta banner vs baseline. Fuel-switch scenarios + LCV-corrected biofuel substitution still to refine |
| D1.5 | LLM ingestion fallback | ✅ DONE 8 Jul (plumbing) — `match_columns_llm` in ingest.py: strict JSON contract, validation rejects invented columns/fields, injectable client (contract-tested without API); goes live the moment ANTHROPIC_API_KEY is set. Still to do: run against 3 real messy files once a key exists |
| D1.6 | Verifier-ready audit trail | ✅ DONE 8 Jul — `ghgcore/audit.py` + `GET /api/audit/{imo}?dwt=`: inputs, every parameter used with source citation, intermediates, results |
| D1.7 | Remaining VERIFY items | ⚙ PARTIAL 8 Jul — FuelEU Annex II LCV/WtW and ETS CH4/N2O verified vs EUR-Lex (LNG 10x slip error fixed). Remaining: G5 correction factors (MEPC.355(78)), biofuel per-BDN certification, per-engine LNG slip split (needs engine type in schema) |
| D1.8 | FuelEU pooling optimizer (pulled fwd from D2.3) | ✅ DONE 8 Jul — `ghgcore/pooling.py`: exact 0/1-knapsack pool selection (max avoided penalty s.t. CB ≥ 0), in /api/fleet + fleet report + dashboard banner |

Unblocks GTM: design-partner demos, free health-check campaign, pricing
conversations backed by the audit trail ("your verifier can check us").

## Phase 2 — Monetisation + pooling marketplace (Weeks 7–14, target mid-Oct 2026)

Goal: paying pilots on the platform; pooling matchmaking ready well before
the 30 Apr 2027 registration deadline.

| # | Deliverable | Acceptance criteria |
|---|------------|---------------------|
| D2.1 | Auth + multi-tenant fleets | Org accounts, vessel ownership, role-based access; a manager sees only their fleet. DEFERRED: zero-budget mode, no users yet |
| D2.2 | Compliance calendar + alerts | ✅ ENGINE DONE 8 Jul — `ghgcore/deadlines.py` (8 dated obligations/yr across 5 regimes with legal basis) + `/api/calendar` JSON + `/api/calendar.ics` (14-day alarms, imports into Outlook/Google). Email alerts deferred with D2.1 |
| D2.3 | Pooling optimizer | ✅ DONE 8 Jul (see D1.8) |
| D2.4 | Pool agreement doc-gen | ✅ DONE 8 Jul — `ghgcore/pool_agreement.py` + `GET /api/pool-agreement?imos=…`: negotiation-ready markdown draft, numbers from engines only, 30-70% compensation range, DRAFT/not-legal-advice labelled |
| D2.5 | Billing | Subscription per vessel + success-fee hook on pooling savings; Stripe |
| D2.6 | NZF adoption-vote switch | Day the Oct 2026 vote lands: nzf.py params updated to adopted text, "scenario" labels flip to "regulation", changelog published — this is a marketing event, build must be same-week |

Unblocks GTM: paid pilot conversion, pooling network recruitment (surplus
ships are the scarce side — recruit them first), NZF-day announcement.

## Phase 2.5 — Product UI build-out (added 13 Jul 2026)

Full spec: **docs/UI_ARCHITECTURE.md** (IA + layouts + tokens + component
states, grounded in Refactoring UI / Designing Interfaces / Norman /
Rosenfeld-Morville / Few).

✅ U1–U9 DONE 13 Jul 2026 (UI v0.5, live-verified): global top bar with
5-area IA + persistent search (hidden on vessel page where search is the
hero); bill-first vessel page — €-total hierarchy winner + bullet graphs
(ETS/FuelEU/UK ETS bars + NZF scenario line) replacing the four equal
tiles; landing example chips; keyboard nav on all autosuggests
(↑/↓/Enter/Esc); what-if behind progressive disclosure (<details>);
calendar timeline SVG (regime-colored ticks, today marker, ⚠ <14-day
alert); Method trust page rendering CALCULATION_NOTES.md client-side;
4-px token scale + tabular-nums + semantic-color discipline; fleet table
row-click drilldown + CO₂/nm column; unsupported-type errors now route to
the custom EEXI path (no dead ends).

Then the P1 regulation tabs from docs/REGULATION_LANDSCAPE.md, built as
"My fleet" local-nav items on the U-series components:
| # | Deliverable |
|---|------------|
| R1 | Finance readiness (Poseidon Principles / Sea Cargo Charter alignment) — VERIFY trajectory tables from PP Technical Guidance first |
| R2 | "Who pays?" — ETSA/FuelEU charter-party cost allocation per voyage |
| R3 | SEEMP Part III generator (paid follow-on to bad free CII check) |

## Phase 3 — NZF regime + scale (post-adoption, Nov 2026 →)

| # | Deliverable |
|---|------------|
| D3.1 | SU/RU ledger + GFI Registry integration (once IMO publishes interface) |
| D3.2 | SU transfer marketplace (reuse pooling matchmaker architecture) |
| D3.3 | DCS/MRV verifier data-exchange integrations (THETIS submission prep) |
| D3.4 | Fleet optimisation across ALL regimes simultaneously (one fuel decision → CII+ETS+FuelEU+NZF joint impact) |

---

## Standing rules for every build session
1. CLAUDE.md architecture rules are non-negotiable (LLMs never calculate;
   parameters in named tables; VERIFY discipline; ESTIMATE labelling).
2. Every phase ends with: tests green, demo runs, README updated.
3. Regulatory watch (CLAUDE.md) checked at session start; table changes are
   their own commits citing the source.
