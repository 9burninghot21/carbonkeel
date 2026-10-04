# Regulatory coverage map — what we compute, and what we could

Reviewed 2 Aug 2026. For each item: what the rule obliges, who it binds, what
CarbonKeel would compute, the report it produces, and what data that needs.
Ordered by **value per unit of build effort**, not by regulation importance.

Legend for data: **[have]** = computable from what we already hold (public
THETIS export or the noon-report/BDN data an owner already sends us);
**[small]** = needs one or two extra fields; **[new]** = needs a new source.

---

## ✅ Already live

| Regulation | Instrument | Status |
|---|---|---|
| Operational carbon intensity | MARPOL Annex VI **Reg. 28 (CII)**, G1–G5 | Full calculator, ratings, trajectory to 2030 |
| Technical efficiency | MARPOL Annex VI **Reg. 23/25 (EEXI)** | Required vs attained, custom-vessel mode ⚠ tables still VERIFY-tagged |
| EU emissions trading | **Directive 2003/87/EC** (2026 rules: 100%, CH₄/N₂O) | Allowances, cost, scope splits |
| UK emissions trading | **UK ETS (Maritime) Order 2026** | UK domestic + GB↔NI |
| Fuel GHG intensity | **Reg. (EU) 2023/1805 (FuelEU)** | Balance, penalty, pooling optimiser, agreement draft |
| Global GHG pricing (future) | **IMO Net-Zero Framework** | Scenario mode until the adoption vote |
| Deadlines across all of the above | — | Calendar + .ics |

---

## Tier 1 — build next (mandatory duties, data we already have)

### 1. SEEMP Part III corrective action plan — MARPOL Annex VI Reg. 26
**The obligation.** Every ship ≥5,000 GT carries a SEEMP Part III (CII
implementation plan). A ship rated **D for three consecutive years, or E for
one year**, must add a documented **corrective action plan** — and the flag or
RO will not issue the Statement of Compliance without it.
**What we compute.** Who is triggered (we already produce the rating and the
three-year trajectory), the size of the gap to C, and the lever set that
closes it — ranked by €/tonne.
**Report.** A pre-filled SEEMP Part III draft: current rating history, root
cause, selected measures with expected CII effect, implementation timeline,
review points. **[have]**
**Why first.** It is the only item on this page where a bad free result
*creates a legal duty* the owner must discharge. That is the cleanest possible
free → paid conversion: "you are E; here is the plan you now have to file."

### 2. IMO DCS annual submission pack — MARPOL Annex VI Reg. 27
**The obligation.** Ships ≥5,000 GT report annual fuel oil consumption per
fuel type, distance, hours under way to the Administration/RO; data due within
three months of year end, Statement of Compliance within five.
**What we compute.** The full DCS dataset from the same noon-report ingestion
that feeds CII — plus consistency checks against the MRV figures (the two
regimes must tell the same story, and mismatches are a common finding).
**Report.** DCS submission sheet + a reconciliation showing DCS vs EU MRV vs
our CII inputs agreeing. **[have]**
**Why.** Recurring, annual, unavoidable, and today it is done in spreadsheets.

### 3. AER + Poseidon Principles / Sea Cargo Charter alignment
**The obligation.** Not a law — a financing and chartering condition. 35+ banks
(≈80% of ship finance) score each financed vessel's **AER** against a
decarbonisation trajectory and disclose portfolio alignment annually; cargo
owners do the same under the Sea Cargo Charter.
**What we compute.** AER (gCO₂/dwt·nm — we already have the components), the
alignment delta vs the applicable trajectory, and the fleet-weighted portfolio
score a lender would see.
**Report.** "What your bank sees" — per-vessel and portfolio alignment, with
the same lever analysis showing what moves it. **[have]**
**Why.** It attaches your numbers to someone else's money. An owner ignores a
€150k penalty; they do not ignore a covenant conversation.

### 4. Charter-party cost allocation — BIMCO ETS / FuelEU / CII clauses
**The obligation.** Not regulation but its commercial shadow: the BIMCO
Emissions Trading Scheme Allowances Clause, FuelEU Maritime Clause and CII
Operations Clause split liability between owner and charterer. Disputes are
live and expensive.
**What we compute.** Per-voyage allowance and penalty liability split by
charter type and period, showing each side's exposure on the same voyage set.
**Report.** "Who pays?" statement — clause-ready numbers for the fixture.
**[small]** (needs charter period and party per voyage)
**Why.** It reaches the commercial desk, which is a faster buyer than the
technical department and controls a different budget.

---

## Tier 2 — high value, modest extra data

### 5. Sulphur / ECA compliance and fuel-switch cost — MARPOL Annex VI Reg. 14
0.50% m/m global; **0.10% inside ECAs**, and the **Mediterranean SOx ECA has
applied since 1 May 2025** — a live change many operators are still absorbing.
We already resolve port pairs, so we can flag ECA legs, check the fuel actually
burned against the applicable limit, and price the compliant-fuel delta.
**Report.** ECA exposure per voyage, non-compliance flags, annual fuel-switch
cost. **[small]** (needs sulphur content per bunker — it is on the BDN)

### 6. NOx Tier applicability — MARPOL Annex VI Reg. 13
Tier III applies to engines on ships built on/after 1 Jan 2016 in the North
American and US Caribbean NECAs, and on/after 1 Jan 2021 in the Baltic and
North Sea NECAs. Purely deterministic from keel-laying date + trading pattern.
**Report.** Tier obligation per vessel per trading area, and where a ship is
about to enter an area its engines are not certified for. **[small]**
(needs build date and engine certification — from the EIAPP certificate)

### 7. EEOI — MEPC.1/Circ.684
The cargo-carried intensity indicator (gCO₂ per tonne-mile). Voluntary for the
ship, but it is the number **cargo owners** need for their own reporting, and
it underpins Sea Cargo Charter scoring.
**Report.** Per-voyage and per-cargo emissions statements. **[small]**
(needs cargo quantity per voyage) — and it opens a second customer segment.

### 8. FuelEU shore-power (OPS) obligation — Reg. (EU) 2023/1805 Art. 6
From 1 Jan 2030, container and passenger ships at TEN-T ports must connect to
onshore power supply at berth (with defined exemptions). Planning starts now
because retrofits are long-lead.
**Report.** Port-call exposure screen: which of your calls fall in scope, the
energy involved, and the penalty if not connected. **[small]** (needs port
calls with berth time — already in noon reports)

### 9. Compliance-calendar extensions: BWM, IHM/HKC, surveys
Not GHG, but the same audience and near-zero build cost — they make the
calendar the one an operator actually keeps open:
- **Ballast Water Management Convention** — D-2 standard now applies to all
  ships; sampling and survey schedule.
- **Hong Kong Convention** (in force 26 June 2025) + **EU Ship Recycling
  Regulation** — Inventory of Hazardous Materials must be maintained and
  surveyed.
- **IAPP/EIAPP, SEEMP and DCS survey dates** tied to the ship's survey cycle.
**Report.** Extended calendar entries per vessel. **[small]** (needs each
vessel's survey anniversary)

---

## Tier 3 — adjacent, watch, or deliberately excluded

- **EEDI (Reg. 21)** — newbuild design index, Phase 3 in force. Only relevant
  to owners with ships on order; our EEXI engine already holds the reference
  lines, so it is a small extension if a customer asks.
- **CSRD / ESRS E1 + GLEC/ISO 14083 shipper statements** — sells the *same*
  computation to cargo owners for their Scope 3. A second segment, not a
  second engine.
- **EU Taxonomy alignment screening** — for owners raising green finance.
- **EU ETS 2026 review** — likely extension to 400–5,000 GT ships; offshore
  vessels join in 2027. Our engines are already GT-threshold parameterised.
- **CII Phase 2 review (2026–28)** — the metric itself may change (cbDIST /
  cgDIST candidates). This is exactly why every parameter lives in a named
  table rather than inline.
- **Onboard carbon capture (OCC)** — MEPC is still writing the crediting
  rules; would change every engine's CO₂ accounting when it lands.
- **Voluntary carbon offsets — deliberately excluded.** No regime among CII,
  ETS, FuelEU or NZF recognises them. Selling them alongside compliance
  numbers would cost more credibility than it earns.

---

## Recommended build order

1. **SEEMP Part III generator** — converts a bad free rating into a legal duty
   only we are positioned to discharge.
2. **AER / Poseidon alignment** — puts your number in front of the lender.
3. **DCS submission pack** — recurring annual work, currently manual.
4. **Who-pays (charter-party split)** — reaches the commercial buyer.
5. **ECA/sulphur + NOx Tier** — completes "vessel compliance" beyond GHG.

Items 1–3 need **no data we do not already have**. That is the argument for
doing them before anything requiring new inputs.
