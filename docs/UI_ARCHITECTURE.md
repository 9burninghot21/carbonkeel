# CarbonKeel — Website Structure & Design Specification

Grounding material: *Refactoring UI* (Wathan/Schoger), *Designing Interfaces*
(Tidwell), *The Design of Everyday Things* (Norman), *Information
Architecture* (Rosenfeld/Morville), *Information Dashboard Design* (Few).
Each decision below names the principle it applies. This spec IS the build
plan for Phase 2.5 — deliverables reference these section numbers.

---

## 1. Conceptual model (Norman)

The user's mental model we design for — everything maps to one sentence:

> **"Find my ship → see my bill → find the cheapest way out → act before the
> deadline."**

Four stages = four permanent regions of the product. Users never need to
understand "engines", "regimes" or "THETIS"; those are system-model details
kept behind the curtain. Every screen answers one of the four stages, and
navigation order mirrors the stages (natural mapping).

Anti-goal (Norman's gulf of evaluation): never show a number without its
consequence. "CII ratio 1.102" is system model; "Rated D — 3rd year at D
forces a corrective plan; here are the levers" is user model.

## 1b. Value-first principle & persona views (added 31 Jul 2026)

**The differentiator.** Competitors return a *rating*. CarbonKeel returns a
*number with a remedy attached*. So the product never shows exposure without
also probing whether that exposure is recoverable.

**Value probe (implemented).** The moment a vessel is scored, the page
silently re-runs the same deterministic engines with a standard lever package
(20% B100 on EU legs, −10% speed). If it finds >€1,000/yr of avoidable cost,
a green chip appears above the result:
> 💡 Value identified: up to €275,548/yr recoverable with standard levers — show me ▸

Clicking it switches to the Owner view, opens the what-if panel pre-filled
with those levers, and renders the delta. This turns Norman's *gulf of
execution* into a single click: the user never has to know which knobs exist.
Rules: probe is silent (no spinner, failure is invisible), never shown when
value ≤ €1k (no fake urgency), and always reproducible in the what-if panel —
the claim can be checked immediately.

**Persona views (implemented).** Same data, three framings, switchable by
chips on every vessel result. The choice persists across lookups — a person's
role does not change per ship.

| View | Who | Leads with | Answers |
|---|---|---|---|
| **Owner / CFO** (default) | owner, commercial, finance | the € bill (hierarchy winner) + bullet graphs per regime with deadlines and EUA price sensitivity | "what do I owe, when, and what if prices move?" |
| **Technical / Ops** | superintendent, fleet performance, DPA | the CII rating + A–E band chart + fleet-context strip, then ranked operational levers, what-if open by default | "how bad is the rating and which lever moves it?" |
| **Verifier** | verifier, auditor, charterer's vetting | provenance table: filed totals, derived distance (labelled ESTIMATE), verifier-reported ETS scope vs our reconstruction, intensity vs target, and a link to the machine-readable worksheet | "can I reproduce these numbers?" |

The Verifier view opens with a reconstruction check — a green ✓ when our
ETS-scope figure matches the value the ship's own verifier filed. That single
line is the credibility asset no competitor can copy without doing the same
deterministic work.

## 1c. Trust & data control — the "can my competitor see this?" objection

**The legal position.** Every emissions figure we serve is published by EMSA
because Article 21 of Reg. (EU) 2015/757 *obliges* the Commission to publish
it: per ship, per year, verified, free, no login. Republishing is lawful, needs
no consent, and involves no personal data (ships and companies are not natural
persons, so GDPR does not bite). A competitor can already pull any operator's
verified emissions from `mrv.emsa.europa.eu` today.

**The commercial position — which matters more.** "Legal" does not stop a
prospect thinking *"so my competitor can see mine?"* and closing the tab. That
objection must be answered inside the product, not in a FAQ nobody reads.

**The asymmetry we designed around** — the honest distinction that makes a
real control possible:

| | Whose it is | Can it be hidden? |
|---|---|---|
| Verified CO₂, fuel, intensity, EEXI/EEDI/EIV, company | **EMSA's**, public by law | No — and pretending otherwise would be theatre; it is one click away at source |
| Cost exposure, CII rating, FuelEU balance, penalty risk, lever savings, fleet rankings | **Ours** (our arithmetic about their ship) | **Yes — on the operator's request, immediately** |

Nobody can compel us to publish our own calculations about someone else's
vessel. That is a control we can actually honour, so we offer it unconditionally.

**Implemented (31 Jul 2026):**
- **Suppression** — `POST /api/claim` with `kind=suppress` takes effect *at
  once*, no human in the loop. We do not make an operator wait for a
  "commercial discussion" to stop showing our estimates. Enforced across
  lookup, EEXI, fleet, siblings, report and audit — verified by 8 leak tests,
  including that a suppressed ship vanishes from *other operators'* fleet
  charts (50 → 49 siblings).
- **Claim / correct** — logged for verification, and deliberately do **not**
  auto-suppress. Correction is the data-acquisition funnel: "that estimate is
  wrong" → "send the real figure and we'll label it owner-verified."
- **Anti-harvesting** — anonymous fleet analysis and reports capped at 8
  vessels; sliding-window rate limit per IP. Harvesting the register is the
  behaviour that would genuinely harm operators; one honest lookup is not.
- **No search indexing** — `noindex` meta + robots.txt. Googling a ship's name
  must never surface our estimate of its bill.
- **"Is this your ship?"** on every vessel result → the control panel, and a
  **Your data** nav item rendering docs/DATA_AND_PRIVACY.md.

**Why this converts rather than costs.** The suppressed-vessel screen still
shows the public EMSA facts, explains why, and offers the operator a claim
path. So the feature that protects a stranger is also the one that identifies
a lead: the person most likely to click "this is my ship" is exactly the buyer.
Positioning line for calls: *"the number is already being computed about your
fleet — by charterers, banks and analysts. We'd rather it be one you've seen,
can audit, and can replace with your own data."*

## 2. Information architecture (Rosenfeld & Morville)

### 2.1 Organization scheme
Task-based top level (not audience- or regulation-based — owners don't wake
up thinking "EU 2023/1805", they think "what do I owe / am I OK / what do I
sign"). Regulations appear as *labels on results*, not as navigation.

### 2.2 Sitemap
```
carbonkeel.com
├── Check a vessel          (search-first funnel; the front door)
│     └── vessel result page  [bill card · CII charts · fleet context · what-if]
├── Free tools              (lead magnets, zero-input-friction)
│     ├── EEXI check          [registry ships + custom vessel]
│     └── Compliance calendar [view + .ics download]
├── My fleet                (the paid product surface)
│     ├── Fleet dashboard     [table + totals + pooling banner]
│     ├── Pooling             [optimizer result · agreement draft · partner matching (P2)]
│     └── Reports             [health-check PDF · audit worksheets]
├── Method                  (trust page: formulas, sources, ESTIMATE policy,
│                            CALCULATION_NOTES rendered; verifier-facing)
└── About / Contact         (founder story, one CTA: "send your IMO list")
```
Current 4-tab app maps onto this cleanly; "Method" and "About" are new
static pages. Rule (IA labeling): one term per concept everywhere —
"bill" (not cost/exposure/liability interchangeably), "balance" (FuelEU),
"rating" (CII), "verdict" (EEXI), "deadline" (calendar).

### 2.3 Navigation systems
- **Global**: top bar, 5 items max, current page marked (you-are-here).
- **Local**: within My fleet only (Dashboard / Pooling / Reports).
- **Contextual**: every result card cross-links the next stage of the story
  (vessel → fleet: "check the whole fleet"; fleet → pooling: "€X avoidable";
  EEXI fail → vessel check). Tidwell's *escape hatch*: logo always returns
  to Check a vessel.
- **Search is the primary IA** for this product (16,673 known objects): the
  vessel search box is the hero of the front page and persists in the top
  bar on every other page (Tidwell: *global search*; IA: search as
  navigation for large homogeneous collections).

## 3. Page layouts

### 3.1 Front door — "Check a vessel"
Single-purpose landing (Tidwell: *center stage*). One search input,
autosuggest after 3 chars, nothing else competing. Sub-line states the
value + the price ("free, from public verified data"). No feature tour, no
marketing hero — the product demo IS the landing.
- Empty state (before first search): 3 example ships as clickable chips
  ("try MSC SERENA") — Tidwell's *starting point* + Norman's signifier that
  this box is the whole interface.

### 3.2 Vessel result page (the money screen) — dashboard rules apply (Few)
One screen, no scrolling for the primary answer (Few: a dashboard fits on
one view; detail below the fold is fine, the VERDICT is not).

Layout, top to bottom:
1. **Identity strip**: name, IMO, type, year, ESTIMATE badge. Small, muted.
2. **The bill** (single most important number — Refactoring UI: one clear
   hierarchy winner): total € exposure, huge; beneath it the three
   components (ETS / FuelEU / NZF) as **bullet graphs**, not tiles:
   each = label · bar to scale vs fleet-type median · figure · deadline.
   (Few: bullet graphs replace gauges/tiles; comparative context turns a
   number into information.)
3. **CII panel**: band bar (exists) + fleet-context strip chart (exists).
   Both follow Few: no 3-D, no legends where direct labeling works, muted
   grid, data-ink maximised. Colors: rating semantics only (see §5).
4. **Actions list**: verb-first, ranked by € impact, each with its deadline
   (Norman: bridge the gulf of execution — every insight ends in a do).
5. **What-if strip**: progressive disclosure (Tidwell) — collapsed one-line
   affordance "What would biofuel or slowing down save? ▸", expands to the
   two inputs + recompute. Result renders as delta vs baseline, never a
   fresh unexplained card.
6. Footer of card: provenance line + link to audit worksheet ("Method").

### 3.3 EEXI (free tools)
Two clearly separated cards (registry ship / custom vessel) — already built
as the guided 1-2-3 stepper; keep. Add per §2.3 a contextual CTA on every
verdict: compliant → "now check the operational bill (CII/ETS)"; not →
"levers + full check". (Tidwell: *sequence map* pattern for the steps.)

### 3.4 Fleet dashboard
- Totals row first (Few: summary before detail), then pooling banner
  (colored ONLY when there is money — alert color discipline, §5), then the
  table.
- Table (Tidwell: *sortable table* + *row striping off*, alignment per
  Refactoring UI: numbers right-aligned, tabular figures): columns Vessel |
  CII proxy | EUAs | ETS € | FuelEU t | Penalty €. Row click = drill into
  vessel (Tidwell: *one-window drilldown*).
- Add per-row **sparkline** (Few) once multi-year data lands (P2): 3-year
  CO₂/nm trend, no axes.

### 3.5 Calendar
List view (exists) + **timeline strip**: 12-month horizontal band with
deadline ticks colored by regime, "today" marker (Norman: mapping — time
flows left→right). ICS button stays primary.

### 3.6 Method (new, static)
Renders CALCULATION_NOTES content: formulas, parameter tables + sources,
worked examples, ESTIMATE policy, data provenance & Art. 21 legality note.
This page converts verifiers and skeptical superintendents — trust is a
feature (Norman: make the system image match the honest model).

## 4. Component inventory (Designing Interfaces patterns)

| Component | Pattern (Tidwell) | States to build |
|---|---|---|
| Vessel search | Autocompletion, Input prompt | idle / typing / results / no-match / unsupported-type |
| Score bullet graph | — (Few) | ok / attention / alert / no-data ("needs DWT") |
| CII band bar | — (Few, custom) | rated / needs-capacity |
| Fleet strip chart | — (Few, custom) | ≥2 ships / single-ship (hide) / no-company |
| Guided form (EEXI custom) | Wizard-lite, Good defaults | per-step enable, self-labelling CTA (exists) |
| What-if | Progressive disclosure | collapsed / expanded / result-delta |
| Data table | Sortable table, One-window drilldown | loading / sorted / empty / partial (unsupported rows) |
| Deadline item | Titled sections | upcoming / <14 days (alert) / past (muted) |
| Banners | Notification | money-good / money-bad / caveat — never stacked >1 |
| ESTIMATE badge | — | fixed; never restyled, never omitted |

Every interactive element needs visible affordance (Norman): buttons look
raised/filled, chips look toggleable, table headers show sort carets,
disabled CTAs explain themselves in their own label (already the pattern in
the custom form — extend everywhere: "Enter DWT to check", not a dead grey
button).

## 5. Design tokens (Refactoring UI)

- **Spacing**: 4-px base scale (4/8/12/16/24/32/48); default to MORE space
  between groups than within (proximity = grouping); kill borders where
  spacing or background-shift can separate (current cards keep 1 hairline
  max).
- **Type**: 2 families max (system stack fine). Scale: 12 / 13.5 / 15 / 18 /
  24 / 32. Hierarchy by weight + color before size (Refactoring UI:
  "don't rely on size alone"): primary = ink 800-weight, secondary = muted
  400. Numbers: tabular-nums everywhere data aligns.
- **Color roles** (not palette-as-decoration):
  - `--ink` text, `--muted` secondary, `--navy` surfaces (current values OK)
  - **Semantic, used ONLY for meaning** (Few's alert discipline):
    green = money saved / compliant / surplus; red = payable / breach;
    amber = caveat / estimate / deadline<14d; teal = brand + interactive
    ONLY (links, buttons, selected). If everything is colored, nothing is.
  - CII A–E ramp: green → light-green → amber → light-red → red (exists).
- **Elevation**: 2 levels only (page, card). No shadows-for-decoration.
- **Charts** (Few): no gridlines heavier than data, no legends when direct
  labels fit, no pies, no gauges, no 3-D ever. Muted axis text 11px.

## 6. Forgiveness & feedback (Norman)

- Every action <100 ms visual feedback; >1 s = labelled progress ("Scoring
  vessel…" exists; add to every fetch).
- Errors: never dead-end. "Ship type not supported" → offer custom EEXI
  path; "no ports matched" → show which and how to fix. Constraint over
  correction: disable + explain beats error toast (already the custom-form
  pattern — make it global policy).
- Destructive/irreversible: nothing in-app currently deletes; keep it so.
- The ESTIMATE badge is a *signifier of honesty* — clicking it explains the
  method (links §3.6). Never let marketing pressure remove it.

## 7. Responsive & accessibility floor

Single-column stack under 720 px; charts scale via viewBox (exists); touch
targets ≥40 px; contrast ≥4.5:1 for text (check amber-on-navy!); every
chart's data also reachable as text (table or title attrs — exists);
keyboard: search → arrows through suggestions → Enter (TO BUILD).

---

## Phase 2.5 — build plan from this spec (est. 2 weekends)

| # | Deliverable | Spec ref |
|---|---|---|
| U1 | Global top bar + 5-area IA, search persistent on all pages | §2.2–2.3 |
| U2 | Vessel page rebuild: bill-first hierarchy + bullet graphs replacing score tiles | §3.2, Few |
| U3 | Landing empty-state with example chips; keyboard nav on search | §3.1, §7 |
| U4 | What-if → progressive disclosure with delta rendering | §3.2.5 |
| U5 | Calendar timeline strip + <14-day alert state | §3.5 |
| U6 | Method page rendering CALCULATION_NOTES + provenance | §3.6 |
| U7 | Token pass: spacing scale, semantic-color audit, tabular numbers, contrast check | §5, §7 |
| U8 | Fleet drilldown row-click + per-row CII-proxy column | §3.4 |
| U9 | State inventory sweep: every component's empty/loading/error per §4 table | §4, §6 |

Follows Phase 2.5: the P1 regulation tabs (Poseidon "Finance readiness",
"Who pays?" ETSA split, SEEMP III generator — REGULATION_LANDSCAPE.md) each
built AS a "My fleet" local-nav item using these components.

---

## QA log — UI-tester sweep, 31 Jul 2026 (18 scripted checks)

Bugs found and fixed:
1. **`Failed to parse URL from /api/lookup/…`** (reported by founder) — every
   fetch used a root-relative path, which cannot resolve when the page is
   opened as a `file://` document. Fixed with an `API` base constant that is
   empty when served over http(s) and `http://127.0.0.1:8000` otherwise.
   All fetches, `window.open` and audit links now route through it.
2. **What-if request bypassed the fix** — its URL was built in a variable, so
   the first pass missed it. Now uses the same base.
3. **Stale-cache trap** — the browser served an old page shell after edits,
   silently hiding new features (this is how bug 1 appeared "unfixed" during
   testing, and would break a live demo). Fixed server-side:
   `Cache-Control: no-store` on the app shell.
4. **Example chip mislabelled** — a chip labelled "search MAERSK" was wired to
   a hard-coded IMO of a different ship. Split into `tryExample()` (direct
   lookup) and `trySearch()` (fills the box and triggers suggestions).
5. **Zero-value bullet graphs rendered a red bar** — €0 UK ETS drew a 2%-wide
   red stub, implying a debt that does not exist. Zero now renders an empty
   track and a green `€0 ✓` (Few: colour carries meaning only).
6. **Bullet bar collapsed to 41 px on mobile** — the 110 px label + 110 px
   value left no room for the bar, destroying the chart's only job. Mobile
   now stacks label/value on one row with a full-width 285 px track.

Verified passing: cruise + bulk lookups, all three persona views, value probe
and one-click lever application (€275,548/yr on the demo vessel), DWT upgrade
→ CII band chart → verifier audit-link unlock, EEXI registry + custom guided
form (incl. GT/DWT label switching and disabled-CTA guidance), fleet
dashboard with sorting and row drilldown, calendar timeline, Method page,
keyboard navigation (↑/↓/Esc), unsupported-type escape hatch to custom EEXI,
404 messaging, top-bar search visibility rule, and no horizontal overflow at
375 px. Backend: 103 engine checks green.
