# GTM Plan 0→Max — Founder Action Track (driven by YOU, in claude.ai + outreach)

> Reconstructed 8 Jul 2026 — the original doc was lost in the project
> transfer. This version is aligned week-by-week with
> [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md): the build track
> (Claude Code) produces the asset, this track spends it.

**Product**: one-stop maritime GHG compliance scorecard (CII | EU ETS | UK ETS |
FuelEU | IMO NZF) + call-to-action engine + FuelEU pooling marketplace.
**ICP**: mid-size ship managers, 10–50 vessels, trading into Europe — big
enough to have real exposure (€250k–€5m/yr ETS+FuelEU), small enough to lack
an in-house compliance team.
**Wedge**: free, no-data-needed fleet health check built from public
THETIS-MRV data — we show them their own exposure before they give us anything.

Division of labour every week:
- **Claude Code (build)**: everything in IMPLEMENTATION_ROADMAP.md.
- **claude.ai project (planning)**: draft outreach, battle cards, pricing
  models, pitch narratives, objection handling — thinking work.
- **You (doing)**: send the messages, take the calls, make the decisions
  only a founder can make (name, price, partners).

---

## Stage 0 — Foundation (Weeks 1–2, parallel to build Phase 0.5)

Decisions & assets — everything here blocks something later:

| # | Action | Where | Output |
|---|--------|-------|--------|
| A0.1 | Pick the product name + register domain | You (shortlist brainstorm in claude.ai) | Name feeds D0.5.7 branded UI |
| A0.2 | Download real THETIS-MRV export (mrv.emsa.europa.eu → reports → export CSV) and drop into `fixtures/` | You (5 min) | Unblocks D0.5.8 — the single biggest build blocker |
| A0.3 | Pick 2–3 priority vessel types (LNG carrier? ro-ro? cruise?) based on who you can actually reach | You | Ordering for D0.5.2 |
| A0.4 | Build target list: 50 named ship managers matching ICP, with named DPA/fleet-performance/compliance contact each | claude.ai (research + list structure), you (verify on LinkedIn) | The outreach universe |
| A0.5 | Write the one-liner + 3 value props tested against the 30 Sep ETS surrender deadline urgency | claude.ai | Message spine for everything |
| A0.6 | LinkedIn founder presence: bio updated, first post — "we scored X,000 EU-trading ships from public data, here's the fleet-wide picture" (uses D1.1 data) | claude.ai drafts, you post | Inbound surface |
| A0.7 | Competitive brief: DNV Emissions Connect, Siglar, BetterSea, OceanScore, Verifavia — where we win (free lookup, pooling, NZF-ready) | claude.ai | Objection handling + positioning |

**Stage gate**: name chosen, THETIS file delivered, 50-name list exists.

## Stage 1 — First conversations (Weeks 3–6, parallel to build Phase 1)

Goal: **15 demo calls, 3–5 design partners** (free access in exchange for
real noon-report data + weekly feedback + a testimonial).

| # | Action | Where | Cadence |
|---|--------|-------|---------|
| A1.1 | Outreach wave 1: personalised message per target — attach THEIR fleet's estimated health-check PDF (D1.2). "This is what public data says about your fleet; owner data makes it exact." | claude.ai drafts each message from the PDF numbers; you send | 10/week |
| A1.2 | Demo script + live-demo flow (lookup → fleet PDF → what-if simulator) | claude.ai | Before first call |
| A1.3 | Design-partner offer: free until [date], in exchange for data + feedback + logo/testimonial rights | claude.ai drafts agreement outline | Week 3 |
| A1.4 | Call notes → claude.ai after every demo: objections, feature asks, willingness-to-pay signals; weekly synthesis → reprioritise build roadmap | claude.ai | Weekly |
| A1.5 | Content: 1 LinkedIn post/week from real (anonymised) findings — "the average bulk carrier we scored is leaving €X on the table via FuelEU pooling" | claude.ai drafts | Weekly |
| A1.6 | Pricing hypothesis: per-vessel/month subscription tiers + pooling success fee; pressure-test in calls without quoting firm | claude.ai models | Week 4 |

**Stage gate**: ≥3 design partners actively sending data. If <3 after 30
sends, the message or ICP is wrong — run a repositioning session in claude.ai
before sending more.

## Stage 2 — Convert & build the pool (Weeks 7–14, parallel to build Phase 2)

Goal: **first paying pilots + a seeded pooling network before the
30 Apr 2027 registration deadline**.

| # | Action | Where |
|---|--------|-------|
| A2.1 | Convert design partners to paid pilots at pilot pricing (locked 12 months) | You, with claude.ai-drafted proposal per partner |
| A2.2 | Pooling recruitment — SURPLUS ships first (LNG-fuelled, methanol, young eco fleets): "your compliance balance is worth €X to a deficit ship; we find the counterparty" | claude.ai builds the surplus-target list from THETIS data (D1.1) |
| A2.3 | Case study #1 from best design partner: exposure found, actions taken, € saved | claude.ai drafts |
| A2.4 | Monthly regulatory brief (email newsletter) to every contact — the compliance-calendar deadlines (D2.2) as content; nurtures non-converts | claude.ai drafts monthly from the regulatory watch |
| A2.5 | NZF adoption vote (~Oct 2026) media moment: the day it passes, publish "what the vote means for YOUR fleet, calculated" — build flips nzf.py same week (D2.6) | claude.ai pre-drafts both outcomes NOW |
| A2.6 | Decide: raise / bootstrap / grant funding (EU green-shipping grants exist) based on pilot revenue signal | You; claude.ai builds the comparison |

**Stage gate**: ≥2 paying fleets, ≥10 vessels opted into pooling interest list.

## Stage 3 — Scale (Nov 2026 →, parallel to build Phase 3)

- A3.1 First pooling transaction closed → success-fee revenue + case study #2.
- A3.2 Channel partnerships: verifiers, P&I clubs, ship-management software
  (integrations > competition).
- A3.3 NZF-readiness campaign: every EU customer needs the global regime next
  — land-and-expand from FuelEU to NZF module.
- A3.4 Hire #1: maritime domain sales/CS person from a design partner's network.

---

## USP — what you pitch (added 8 Jul 2026)

Every class society and half the maritime-software market gives away a CII/EEXI
calculator. That is a METRIC. CarbonKeel sells the MONEY:

> **One-liner:** "CarbonKeel prices your fleet's entire GHG exposure — EU ETS,
> UK ETS, FuelEU, CII and the 2028 IMO Net-Zero regime — in euros, from public
> data alone, and then finds the cheapest way out: pool it, bank it, or fix it."

**Three pillars (in pitch order):**
1. **We start with YOUR numbers, not a demo.** Before the first call we score
   the prospect's fleet from EMSA's published verified emissions — the same
   figures their own verifier filed. Spot-checks reproduce the verifier's
   ETS-scope CO2 to the tonne. Nobody opens a cold email with the prospect's
   own compliance bill in it.
2. **Four regimes, one card, CFO language.** Not "your CII is C" but "your
   fleet owes 31,000 EUAs by 30 September (€2.2m), your FuelEU balance is
   -1,400 t (€890k penalty or a pooling trade), and the IMO regime adds
   $1.1m from 2028 at your current fuel mix." Deadlines, euros, actions.
3. **Compliance balance is a tradable asset — we treat it like one.** FuelEU
   Art. 20/21: deficits can pool with surpluses instead of paying €2,400/t
   penalties. We compute what a surplus is WORTH and (roadmap) match the
   counterparty. A deficit ship saves ~50% vs penalty; a surplus ship earns
   money it currently leaves on the table. That marketplace is the moat —
   calculators don't have network effects, pools do.

**The demo that closes (added 31 Jul 2026).** In a call, don't tour features —
run this 60-second sequence:
1. Ask for one of their ship names. Type it. The bill appears: "€510,798 this
   year — €363k of EUAs due 30 September, €148k of FuelEU penalty risk."
2. Point at the green chip that appeared by itself: **"Value identified: up to
   €275,548/yr recoverable."** Click it. The levers fill in and the saving is
   recomputed live. *No competitor's tool volunteers the remedy.*
3. Switch the view chip to **Technical / Ops** — same ship, now the CII rating,
   the A–E band, and where it sits among its 50 sister ships.
4. Switch to **Verifier** — the green reconstruction check: our ETS-scope
   figure equals the number their own verifier filed. Then: "your verifier can
   audit every parameter; here's the worksheet."
That sequence answers the three people who will be in the room (money,
operations, assurance) without changing tools.

**Objection killers:**
- **"Can my competitor see my fleet's numbers here?"** (expect this first, in
  every call) → "Your verified emissions are already public — the EU MRV
  Regulation requires the Commission to publish them for every ship over
  5,000 GT, and anyone can download them from EMSA today. What we add is what
  those numbers *cost* you. That part is our calculation, and if you'd rather
  we didn't show it to third parties, say the word and it's off within the
  minute — there's a button on every vessel page. We don't index pages for
  search, we cap anonymous fleet lookups, and we've never sold data.
  Frankly: the number is already being computed about your fleet by
  charterers, banks and analysts. Better it's one you've seen and can correct."
  Then show the suppression working live. It disarms the objection *and*
  demonstrates the claim flow that converts them.
- "Our class society gives us this free" → they give the rating; do they give
  the euro bill across four regimes, the pooling value of the balance, and the
  2028 exposure? Bring the fleet report and let the numbers argue.
- "We have DNV Emissions Connect / OceanScore" → those need onboarding and
  data feeds before the first insight; CarbonKeel's first insight arrives in
  the first email, free. And none of them price the NZF regime today.
- "Numbers are estimates" → yes, labelled so — built only from what your
  verifier already published. Owner noon reports make them audit-grade; the
  ESTIMATE→exact upgrade IS the product funnel.

## Outreach playbook (independent founder, no company yet)

Data assets (regenerate anytime: `python scripts/build_targets.py`):
- `outreach/targets_2025.csv` — 311 mid-size managers (8-60 ships, majority
  container/bulk/tanker), ranked by verifier-reported ETS exposure.
- `outreach/TOP_TARGETS.md` — top-50 briefing table.

**Who to contact, in order of reply likelihood:**
1. Fleet Performance / Energy Efficiency Manager (owns the CII problem)
2. Technical Superintendent / Technical Director (owns the fix)
3. DPA / HSQE Manager (owns the audit trail)
4. Commercial/chartering desk (owns who PAYS under charter clauses — often
   the fastest to care about ETS euros)
Find them: LinkedIn people search on the company name from targets_2025.csv.

**First-touch template (attach their own fleet report, printed to PDF from
`/report?imos=<their IMOs from sample_imos column>`):**

> Subject: [Company]'s 2025 EU compliance bill — from your own verified data
>
> Hi [Name], I pulled [Company]'s [N] ships from the public EU-MRV register
> and priced the fleet's exposure: ~€[X] in EU ETS allowances due by
> 30 September and a FuelEU balance of [Y] tCO2e ([penalty risk €Z / a
> sellable surplus]). One-page breakdown attached — built entirely from the
> figures your verifier filed, so treat it as an estimate with honest labels.
> If it's 80% right, the last 20% takes one noon-report CSV. Worth 20 minutes?

Rules: 10/week max, personalised first line, no follow-up before day 4,
log every reply verbatim into the claude.ai project for weekly synthesis.
As an individual: sign as "[Name], building CarbonKeel" — pre-incorporation
outreach is normal in maritime; incorporate when the first pilot wants paper.

## Zero-budget mode (adopted 8 Jul 2026 — founder operates as an individual)

Nothing in Stage 0-1 requires spending money. The stack:
- **Identity**: personal LinkedIn + Gmail; sign as "[Name], building CarbonKeel".
  Defer domain purchase (~€10) until a prospect asks for a website or the
  first pilot signs — carbonkeel.com was free at last check; re-check then.
- **Lead magnet**: PDF fleet reports generated locally for free —
  `python scripts/make_reports.py --top 10 --pdf` (uses installed Edge as the
  PDF engine). Attach to first-touch emails; no hosting needed.
- **Demo**: run the app locally (`python -m uvicorn api.main:app`) and screen-
  share on the call. The live moment: prospect names any of their ships →
  instant cost card → what-if slider shows "Saves €X/yr". No deployment.
- **When money first makes sense** (in order): domain+email ~€15/yr once
  replies flow; free-tier cloud hosting (Render/Railway) only when a prospect
  wants a self-serve link; incorporation only when a pilot wants a contract.

## Weekly operating rhythm (repeat every week from Week 1)
1. **Mon** — claude.ai: review last week's calls/replies, update target list,
   draft this week's outreach batch.
2. **Tue–Thu** — You: send outreach, take calls, log notes into claude.ai.
3. **Fri** — Claude Code session: build sprint on current phase deliverables;
   feed any feature asks from calls into the roadmap; regulatory watch check.
4. **Metric review (Fri, claude.ai)**: sends, replies, demos, partners,
   vessels on platform, pipeline €.

## North-star metrics by stage
| Stage | Metric | Target |
|-------|--------|--------|
| 0 | Outreach-ready targets | 50 |
| 1 | Design partners with data flowing | 3–5 |
| 2 | Paying fleets / pooled-interest vessels | 2 / 10 |
| 3 | ARR + pooling GMV | first €100k ARR |
