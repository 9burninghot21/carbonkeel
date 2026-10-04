# Calculation notes — audit this by hand

Every number CarbonKeel shows comes from one of six deterministic engines.
This document states each engine's formula, parameters (with source), and a
worked example you can recompute on a calculator. The same examples run as
assertions in `tests/test_engines.py` (96 checks) — if you change a table,
the tests force the hand-computation to be redone.

## 1. CII (MARPOL Annex VI Reg. 28 — `cii.py`)

```
attained CII = Σ(fuel_t × CF) × 10⁶ / (Capacity × Distance_nm)     [G1]
reference    = a × Capacity_ref^(-c)                               [G2]
required     = reference × (1 − Z/100)                             [G3]
rating       = A/B/C/D/E via attained/required vs dd vector        [G4]
```
- CF (tCO₂/t fuel): HFO 3.114, LFO 3.151, MDO/MGO 3.206, LNG 2.750,
  methanol 1.375 (2018 DCS Guidelines / G1).
- (a, c) and dd vectors verified line-by-line against the official
  MEPC.353(78) / MEPC.354(78) PDFs, including: gas-carrier 65k dwt split,
  general-cargo 20k split, LNG-carrier 65k/100k splits, bulk 279k cap,
  vehicle-carrier 57,700 GT reference cap, GT capacity basis for
  ro-ro/ro-pax/cruise/vehicle.
- Z factors: 2023–26 = 5/7/9/11%; 2027–30 = 13.625/16.25/18.875/21.5%
  (MEPC.400(83)).
- G5 corrections (MEPC.355(78)) are applied only when the operator supplies
  documented values (`CIICorrections`) — never inferred.

**Worked example** (test `test_cii`): bulk carrier, 50,000 dwt, 3,000 t HFO,
50,000 nm, 2026. CO₂ = 3,000×3.114 = 9,342 t. Attained =
9,342×10⁶/(50,000×50,000) = **3.737**. Reference = 4745×50,000^-0.622 =
**5.668**. Required = 5.668×0.89 = **5.044**. Ratio 0.741 ≤ d1 0.86 → **A**.

**Known estimate-path caveats** (free lookup only): distance is backed out of
"CO₂ per distance" in the MRV filing; DWT/GT is user-supplied; fuel mix is
assumed HFO-equivalent. Owner data removes all three.

## 2. EEXI (Reg. 23/25 — `eexi.py`) — FREE CHECK

```
required EEXI = (1 − X/100) × a × Capacity^(-c)      [EEDI reference line]
verdict: reported attained (from the ship's own MRV filing) vs required
```
- Reduction factors (Y) per MARPOL Annex VI **Reg. 25 Table 3** — verified
  line-by-line against the consolidated Annex VI text on 2 Oct 2026; all twelve
  ship types match. The cruise band applies to cruise passenger ships having
  non-conventional propulsion and is measured in GT.
- **Capacity basis per MEPC.364(79) §2.2.3** (verified 2 Oct 2026):
  - §2.2.3.1 bulk, tanker, gas, LNG, ro-ro cargo (incl. vehicle carrier),
    ro-ro passenger, general cargo, reefer, combination -> **deadweight**
  - §2.2.3.2 passenger and cruise passenger ships -> **gross tonnage**
  - §2.2.3.3 containerships -> **70% deadweight for the attained index**, but
    §2.2.3.3.3-.4 state a = 174.22 and c = 0.201 were fitted against *100%*
    deadweight, so the **required** value uses full DWT. Using 70% in both
    places understates the required value and lets a non-compliant ship look
    compliant — this was a real bug, fixed 2 Oct 2026.
- Reg. 25.2: for ro-ro cargo and ro-ro passenger ships the phase-2 reference
  line under Reg. 24.3 applies.
- If the filing reports EEDI/EIV instead of EEXI, the verdict is labelled
  INDICATIVE (design index ≠ certified EEXI).

**Worked example** (test `test_eexi`): bulk 93,000 dwt, reported
"EEXI (2.97)". Reference = 961.79×93,000^-0.477 = **4.103**; X = 20% →
required = **3.283**. 2.97 ≤ 3.283 → **COMPLIANT**, margin +9.5%.

## 3. EU ETS (Directive 2003/87/EC — `euets.py`)

```
CO₂e = Σ_legs Σ_fuels tonnes × scope_share × (CF + CH₄_EF×28 + N₂O_EF×265)
EUAs = CO₂e × phase-in (2024: 40%, 2025: 70%, 2026+: 100%)
```
- Scope shares: intra-EEA & berth 100%, one-EEA-end 50%.
- CH₄/N₂O included from reporting year 2026, GWP100 AR5 (28/265).
- Liquid-fuel EFs 0.00005/0.00018 t/t (verified vs Annex II/Reg. 2015/757);
  LNG methane = engine-type slip: Otto-MS 3.1%, Otto-SS 1.7%, Diesel-DF
  0.2%, LBSI 2.6% of fuel mass.
- Validation: our scope reconstruction reproduces the verifier-reported
  "CO2 to be reported under Directive 2003/87/EC" figure exactly on spot
  checks (e.g. IMO 9464663: 7,409.0 t both).

## 4. FuelEU Maritime (Reg. (EU) 2023/1805 — `fueleu.py`)

```
intensity = Σ(tonnes × LCV × WtW) / Σ(tonnes × LCV)     [in-scope energy]
CB [gCO₂e] = (target − intensity) × energy               [Annex IV]
penalty    = |CB| / (intensity × 41,000) × €2,400        [Art. 23]
```
- Target: 91.16 × (1−2%) for 2025–29, −6% from 2030, etc.
- LCV/WtW verified against Annex II (EUR-Lex CELEX 32023R1805): HFO 91.74,
  LFO 91.39, MGO 90.77, LNG 89.20/82.87/76.08/86.94 by engine, fossil
  methanol 103.15. FuelEU GWPs are AR4 (25/298) — deliberately different
  from ETS.
- Certified values (Art. 10) override defaults via `certified_props`.

**Worked example** (test `test_fueleu`): 3,000 t HFO intra-EEA, 2026.
Energy = 121.5×10⁶ MJ; intensity 91.74 vs target 89.3368 → CB = **−292 t**;
penalty = 292×10⁶/(91.74×41,000)×2,400 = **€186,310**.

## 5. UK ETS (`ukets.py`)
Same gas basis as EU ETS; scope = UK domestic voyages/berth at 100%,
GB↔NI 50% (leg `uk_share` from port pairs); no phase-in; first period
H2 2026. UKA price is an input (default £40, indicative).

## 6. IMO Net-Zero Framework (`nzf.py`) — SCENARIO until adopted
```
GFI = Σ(tonnes × LCV × WtW) / Σ(tonnes × LCV)    [all voyages, WtW]
above Base target   → Tier 2 units @ $380/t (plus Tier 1 band)
Base…Direct band    → Tier 1 units @ $100/t
below Direct target → Surplus Units
```
Targets per MEPC 83 approval (2028 Base −4%/Direct −17% vs 93.3). Every
output carries the "not yet adopted" note; vote ~Oct 2026.

## 7. Pooling optimizer (`pooling.py`)
0/1 knapsack: admit deficit ships (weight = |CB|, value = standalone
penalty) into the surplus pool such that Σ CB ≥ 0, maximising avoided
penalty. Exact DP at 1-tonne granularity below 500k t capacity; greedy
density fallback above. Test pins the optimum against a hand-built case.

## Cross-cutting rules
- No LLM ever produces a number (architecture rule 1; the LLM only maps
  column names, and its output is validated then applied by code).
- ESTIMATE labelling on all public-data outputs; audit worksheet with every
  parameter + source, available as a full calculation worksheet from the Verifier view of any vessel.
- Currency/price assumptions (EUA €70, UKA £40, €/£ 1.15) are inputs, not
  facts — the UI shows EUA sensitivity at €60/80/100.
