# CLAUDE.md — Maritime GHG Compliance Platform

## What this is
One-stop platform for maritime GHG compliance: IMO CII/DCS, EU ETS, FuelEU
Maritime, UK ETS, and IMO Net-Zero Framework (scenario mode until adopted).
Product = four-score vessel card (Regulatory Health, Cost Exposure, Compliance
Asset €, Future Readiness) + call-to-action engine + (Phase 2) FuelEU pooling
marketplace. Target customer: mid-size ship managers (10–50 vessels) trading
into Europe. Full GTM plan: docs/GTM_Plan_0_to_Max.md. Regulatory reference:
docs/IMO_GHG_Regulatory_Knowledge_Base.md.

## Non-negotiable architecture rules
1. **LLMs never calculate compliance numbers.** LLMs only map input data to
   the canonical schema (src/ghgcore/schema.py) and draft explanations.
   All figures come from deterministic engines with an audit trail.
2. Every regulatory parameter (Z factors, targets, penalty rates, fuel
   properties) lives in named module-level tables — never inline — so a
   regulation change is a one-table diff.
3. Anything uncertain is marked `VERIFY` in code/tests and listed below.
   Never silently "fix" a VERIFY value: verify against the primary source,
   cite it in the commit message, then remove the tag.
4. Estimates from public data are always labelled ESTIMATE in output.

## Layout
- src/ghgcore/schema.py    canonical Vessel/Voyage/Fuel spine
- src/ghgcore/cii.py       IMO Reg.28 engine (G1–G4)
- src/ghgcore/fueleu.py    Reg. (EU) 2023/1805 engine (balance, penalty, pooling value)
- src/ghgcore/euets.py     EU ETS engine (2026 rules: 100%, CH4/N2O CO2e)
- src/ghgcore/nzf.py       IMO Net-Zero Framework scenario engine (parameterized)
- src/ghgcore/scorecard.py composite four-score card + CTA rules
- src/ghgcore/thetis.py    EMSA THETIS-MRV public-data ingestion (free lookup funnel)
- src/ghgcore/ingest.py    agentic ingestion: synonym mapper + LLM prompt contract
- tests/test_engines.py    hand-computed worked examples (run: python3 tests/test_engines.py)
- demo.py                  end-to-end demo of both data paths

## VERIFY backlog (before any customer-facing number)
- [x] G2/G4 tables for implemented types — verified 8 Jul 2026 against official
      MEPC.353(78)/354(78) PDFs (wwwcdn.imo.org). Fixed: gas-carrier dd vector
      was the ≥65k variant paired with the <65k reference line; both split
      halves now implemented. Added general-cargo <20k dwt line.
- [x] Ship types LNG carrier / ro-ro / ro-pax / cruise / vehicle carrier —
      DONE 8 Jul 2026 with official MEPC.353/354(78) params incl. LNG
      65k/100k dwt splits, vehicle-carrier 57,700 GT reference cap, GT
      capacity basis, missing-GT guard. 12 CII types live (~1,781 more ships
      in the lookup). Still unmapped: container/ro-ro, generic passenger,
      offshore/other (no G2 line exists for them).
- [~] G5 correction factors & voyage adjustments (MEPC.355(78)) — application
      mechanism DONE 8 Jul (CIICorrections in cii.py: exclusions + capacity
      factor, audit-noted); deriving the factors themselves stays operator
      input by design. Built-in ice-class/shuttle-tanker factor tables = later.
- [x] FuelEU fuel LCV/WtW — verified 8 Jul 2026 against Reg. 2023/1805
      Annex II (EUR-Lex CELEX 32023R1805); WtW recomputed from official
      LCV/WtT/Cf/slip inputs with AR4 GWPs. Fixed: LNG 76.1→89.20 (Otto MS
      slip priced), methanol 97.1→103.15, B100 →16.4 (UCOME default).
      Remaining: biofuel E per actual BDN/certificate (pathway-specific).
- [x] EU ETS CH4/N2O factors — liquid-fuel defaults confirmed vs Annex II /
      Reg. 2015/757; fixed LNG CH4 10x error (0.0031→0.031 t/t, Otto MS
      slip). Remaining: per-engine slip split (Otto SS/Diesel DF/LBSI) needs
      engine type in schema.
- [ ] Biofuel treatment: MEPC.1/Circ.905 (CII) and RED II certification (ETS/FuelEU).
- [ ] NZF target tables & RU prices vs final adopted text (vote ~Oct 2026).
- [x] THETIS export columns — verified 8 Jul 2026 against real 2025-v6 and
      2024-v228 XLSX files (fixtures/); loader reproduces verifier-reported
      ETS-scope CO2 exactly on spot checks. Download API in thetis.py docstring.

## Phase roadmap
Full deliverable-level plan: **docs/IMPLEMENTATION_ROADMAP.md** (build track,
executed in Claude Code) paired week-by-week with **docs/GTM_Plan_0_to_Max.md**
(founder action track: outreach, partners, pricing). Check the roadmap at
session start; build the current phase's next unfinished deliverable unless
told otherwise.
- **Phase 0 (done):** engines + scorecard + both ingestion paths + tests.
- **Phase 0.5 (DONE 8 Jul 2026, except noted):** product name = **CarbonKeel**
  (carbonkeel.com free at check time; founder to register + trademark-check).
  Focus types per founder: container, bulk carrier, tanker. Done: CII G2/G4
  verified vs official MEPC.353/354(78) PDFs (fixed gas-carrier 65k split,
  added GC<20k); projection.py annualisation; ports.py per-leg EU scoping +
  UK shares; ukets.py (UK ETS live 1 Jul 2026, domestic, CO2+CH4+N2O, GB-NI
  50%); api/main.py FastAPI + api/static/index.html branded lookup page
  (run: python -m uvicorn api.main:app); real THETIS 2024+2025 exports wired.
  Carried to Phase 1: FuelEU Annex II + ETS CH4/N2O factor verification;
  LNG/ro-ro/ro-pax/cruise ship types (official params already in cii.py
  comments).
- **Phase 1 (target 21 Aug 2026):** THETIS bulk import; fleet health-check
  PDF (the free sales asset); fleet dashboard; what-if simulator; LLM
  ingestion fallback live; verifier-ready audit trail.
- **Phase 2 (target mid-Oct 2026):** auth/multi-tenant; compliance calendar +
  alerts; FuelEU pooling optimizer (maximise avoided penalty s.t. pool
  CB >= 0) + agreement doc-gen; billing; NZF adoption-vote same-week switch.
- **Phase 3 (post-NZF adoption):** SU/RU ledger, GFI Registry integration,
  SU transfer marketplace, cross-regime fleet optimisation.

## Regulatory watch (check on every session; update tables + this file)
- MEPC extraordinary session ~Oct 2026: NZF adoption vote -> update nzf.py
  status/params. MEPC 84 outcomes: DCS data access amendments.
- CII Phase 2 review (2026–2028): possible new metrics -> keep engine pluggable.
- EU ETS 2026 review: possible 400–5,000 GT extension; offshore ≥5k GT joins 2027.
- UK ETS maritime live since 1 Jul 2026 -> build ukets.py analogous to euets.py.
- FuelEU: Norway/Iceland EEA application status; RFNBO 2034 trigger monitoring.
Sources: IMO press room, EUR-Lex, DNV/ABS/LR statutory news, EMSA.
