# Getting fluent again — maritime GHG, in the order it matters

You do not need to be a naval architect. You need to hold a twenty-minute
conversation with a fleet performance manager without saying anything that
makes them stop taking you seriously. That is a much smaller target, and it is
reachable in about two weeks at fifteen minutes a day.

Read this in order. Each day ends with one thing to *do* in the app, because
the numbers stick when you have watched them move.

---

## The map: four regimes, two regulators, one question

An owner trading into Europe is hit by four separate pricing regimes. They
overlap, use different boundaries, and nobody has unified them:

| | Who made it | What it measures | What it costs |
|---|---|---|---|
| **CII** | IMO (global) | *Operational* carbon intensity — CO₂ per capacity per mile | No direct fine. A bad rating forces a corrective action plan and starts costing you charters. |
| **EEXI** | IMO (global) | *Technical* efficiency — the ship's design, not how you sail it | One-off. Fail and the ship cannot trade until it is fixed. |
| **EU ETS** | EU | Tonnes of CO₂e in EU scope | You buy allowances. Real cash, every September. |
| **FuelEU** | EU | GHG *intensity* of the energy you burn (well-to-wake) | €2,400/t penalty — or you pool your way out. |

And one more, pending: the **IMO Net-Zero Framework** — a global version of
FuelEU with a price attached. Approved in principle April 2025, the adoption
vote was adjourned in October 2025 and reconvenes this month.

The single distinction that unlocks everything else:

> **CII and EEXI measure the ship. ETS measures what you emitted. FuelEU
> measures what your fuel was made of.**

You can be excellent on one and terrible on another. An LNG carrier burning
boil-off gas sails past FuelEU and can still rate D on CII. A modern eco-bulker
can hold an A rating and still owe a seven-figure ETS bill because it simply
sails a lot. Owners find this maddening, and saying so out loud is an instant
credibility signal.

---

## Day 1–3 · CII, because it is what they will raise first

**What it is.** Each year, every ship over 5,000 GT computes
`CO₂ emitted ÷ (capacity × distance sailed)`. That is the *attained* CII. It is
compared to a *required* CII — the 2019 fleet median for that ship type, reduced
by a percentage (the **Z factor**) that tightens annually:

| 2023 | 2024 | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|---|---|
| 5% | 7% | 9% | **11%** | 13.625% | 16.25% | 18.875% | 21.5% |

The ratio of attained to required gives a letter, **A to E**. Rate **D for three
consecutive years, or E for one**, and you must file a corrective action plan in
your SEEMP Part III before your Statement of Compliance is issued.

**Why owners are angry about it.** The metric is distance-based, so it rewards
sailing far and penalises useful work. A ship that waits at anchor burning
auxiliary fuel scores badly; a ship that steams empty across an ocean scores
well. Short-sea operators are hit hardest. "Sailing in circles improves your
CII" is a real industry joke — and repeating it tells a superintendent you have
actually talked to operators.

**What they actually do about it.** Slow down (fuel burn scales roughly with the
cube of speed, so −10% speed is a large cut), clean the hull and propeller,
optimise routing, blend biofuel, or fit energy-saving devices. Slowing down is
far and away the most common because it costs nothing to try.

> **Do today:** open the CII calculator (key `<your-access-key>`), run
> 50,000 dwt bulk carrier / 4,300 t HFO / 50,000 nm / 2026. You get **D**. Now
> look at the trajectory strip: same ship, same operation, **E by 2030**. That
> is the conversation that sells.

---

## Day 4 · EEXI, the one-off exam

A *design* index: what the ship would emit per tonne-mile at 75% engine power,
by construction, regardless of how you sail it. Required value = an EEDI
reference line reduced by a factor (20% for most bulkers and tankers, up to 50%
for large container ships).

Fail and the standard fix is an **EPL** or **ShaPoLi** — Engine Power
Limitation / Shaft Power Limitation. You physically cap the engine, which lowers
the calculated index. The ship keeps trading; it just cannot go as fast. Most of
the world fleet passed this way in 2023.

EEXI is largely a settled problem — which is exactly why it makes such a good
free giveaway. It is cheap for us, familiar to them, and it opens the door to
CII and the money regimes.

---

## Day 5–7 · EU ETS, where the cash leaves

**Scope** — learn this cold, it comes up constantly:

- Voyage **between two EEA ports**: 100% of emissions count
- Voyage **into or out of** the EEA: **50%**
- **At berth** in an EEA port: 100%

Phase-in of how many allowances you actually surrender: 40% for 2024, 70% for
2025, **100% from 2026**. And from the 2026 reporting year, **methane and
nitrous oxide** join CO₂, counted as CO₂-equivalent.

One **EUA** (EU Allowance) covers one tonne of CO₂e. You buy them on the market
and surrender them by **30 September** of the following year. Price moves — at
€70/t a mid-size fleet is a seven-figure annual line item, which is why our tool
shows the bill at €60, €80 and €100 rather than pretending one price is a fact.

**Who pays** is the live commercial fight. The regulation puts the duty on the
"shipping company" — usually the ISM manager — but under a time charter the
*charterer* makes the speed and routing decisions that create the emissions.
BIMCO wrote an ETS Allowances Clause to allocate it. Disputes are common, and
the phrase "who pays under your charter party?" is a genuinely good question to
ask on a first call.

---

## Day 8–11 · FuelEU — this is your business, learn it properly

Regulation (EU) 2023/1805, in force since 1 January 2025. Same 100%/50%/berth
scope as ETS. But it does **not** count tonnes — it limits the **GHG intensity**
of the energy you use, measured **well-to-wake** (production *and* combustion).

- Baseline: **91.16 gCO₂e/MJ** (the 2020 fleet average)
- Reduction: **−2% from 2025**, −6% from 2030, −14.5% 2035, −31% 2040,
  −62% 2045, −80% 2050
- So the 2026 limit is about **89.34 gCO₂e/MJ**

Now the fact that creates your entire business:

| Fuel | Well-to-wake intensity | vs the 89.34 limit |
|---|---|---|
| HFO | 91.74 | **over** |
| VLSFO | 91.39 | **over** |
| MGO | 90.77 | **over** |
| LNG (Otto, medium speed) | 89.20 | just under |
| LNG (Diesel dual-fuel) | 76.08 | well under |
| B100 biofuel (UCOME) | ~16.4 | far under |

**Every conventional fuel is already non-compliant.** Burn ordinary fuel oil and
you accrue a deficit by default, from day one. There is no "run a tight ship"
escape — only fuel changes.

**Compliance balance** = (target − your actual intensity) × energy used. Positive
is surplus, negative is deficit. A deficit costs **€2,400 per tonne of
VLSFO-equivalent** energy (Article 23).

**The three ways out** (Articles 20–21) — know these by heart:

1. **Bank** a surplus forward into next year.
2. **Borrow** up to 2% from next year, with a 10% penalty on the borrowed amount.
3. **Pool** with other ships. The pool's *combined* balance must be ≥ 0, and then
   **every ship in it is deemed compliant.**

Pooling is the one that matters. A ship in deficit pays a surplus holder some
negotiated share of the €2,400 it would otherwise lose; both sides end up better
off than the penalty. The pool must be registered in the FuelEU Database by
**30 April** of the following year — and after that date, for that compliance
year, the penalty is the only remaining option.

**The market imbalance is the opportunity.** Our scan of the whole EU-trading
register finds roughly **5,200 tCO₂e of surplus** — against a single container
manager carrying a **20,800 t deficit**. Surplus is scarce; deficit is
everywhere. Whoever signs the surplus holders controls the trade.

Other FuelEU pieces worth knowing exist: **shore power (OPS)** becomes mandatory
for container and passenger ships at major EU ports from 2030, and an **RFNBO**
sub-target may trigger for 2034.

> **Do today:** run `python scripts/daily.py --surplus`. Those LNG operators are
> the scarce side. Then run `--targets 5` and look at the deficit numbers. That
> contrast *is* the business.

---

## Day 12 · The IMO Net-Zero Framework

A global FuelEU with a price. Measures **GFI** (GHG Fuel Intensity, well-to-wake)
against two targets: miss the *base* target and you buy Tier 2 remedial units at
roughly **$380/tCO₂e**; sit between base and *direct* and you buy Tier 1 at about
**$100**. Beat the direct target and you *earn* surplus units you can bank or
sell.

Crucially it covers **all international voyages**, not just European ones. For an
owner trading globally, it is a far bigger number than ETS.

Status: approved in principle at MEPC 83 (April 2025); the adoption vote was
adjourned in October 2025 by 57 votes to 49 after US pressure, and reconvenes
**this month**. We model it as a clearly-labelled scenario until it is adopted.
Both announcement drafts are already written — see
`outreach/NZF_vote_announcements.md`.

---

## Day 13 · Speak the language

Say these naturally and you stop sounding like a software person:

**Units & measures** — DWT (deadweight, cargo capacity), GT (gross tonnage,
enclosed volume — ro-ro, ro-pax and cruise ships are rated on GT, not DWT),
AER (Annual Efficiency Ratio, essentially CII for bulk/tanker),
EEOI (operational indicator per tonne of actual cargo).

**Fuels** — HFO (heavy fuel oil), VLSFO (very low sulphur, the post-2020
default), MGO/LSMGO (marine gas oil, the distillate), LNG, methanol,
B24/B100 (biofuel blends), **BOG** (boil-off gas — what LNG carriers burn,
which is why they are in FuelEU surplus).

**Documents** — **BDN** (Bunker Delivery Note: proves what you bunkered),
**PoS** (Proof of Sustainability: proves a biofuel is certified),
**SoC** (Statement of Compliance: the annual DCS/CII certificate),
**DoC** (Document of Compliance: the FuelEU one), **SEEMP** (Ship Energy
Efficiency Management Plan — Part I measures, Part II data collection,
**Part III** the CII plan).

**People & bodies** — **DPA** (Designated Person Ashore, the ISM safety link),
**RO** (Recognised Organisation — a class society acting for the flag state),
**flag** (the state of registry), **P&I club** (insurance mutual),
**charterer** (whoever hires the ship).

**Operations** — laden vs ballast (loaded vs empty), slow steaming,
**EPL/ShaPoLi**, **ESD** (energy-saving device), hull and propeller fouling,
**ECA/SECA/NECA** (emission control areas — the Mediterranean SOx ECA started
1 May 2025), **TEN-T** ports (the EU core network, relevant for shore power).

**Commercial** — **time charter** (charterer directs the ship and usually buys
the fuel), **voyage charter** (owner keeps operational control), **EUA**,
**BIMCO clause** (the standard contract wording allocating ETS/FuelEU cost).

---

## Day 14 · Three things that make you sound experienced

1. **"CII punishes port time and short-sea trades."** True, widely resented,
   and under review by the IMO. Saying it shows you know the metric's politics,
   not just its formula.
2. **"FuelEU and ETS use different greenhouse-gas weightings."** FuelEU uses the
   older AR4 global-warming potentials (methane ×25); EU ETS uses AR5 (×28). The
   same methane slip is counted differently by two EU regulations. Nobody expects
   a vendor to know this.
3. **"Your charter party decides who actually pays."** Immediately moves the
   conversation from compliance theatre to money, and tells you whether you are
   talking to the person with the budget.

---

## Primary sources, when you need the actual text

- **IMO** — MEPC resolutions on `imo.org`: MEPC.352(78) is the CII formula,
  .353(78) the reference lines, .354(78) the rating boundaries, .355(78) the
  correction factors. All free PDFs.
- **EU** — EUR-Lex: Regulation (EU) 2023/1805 (FuelEU, Annex II is the fuel
  table), Directive 2003/87/EC (ETS), Regulation (EU) 2015/757 (MRV).
- **The data** — `mrv.emsa.europa.eu`, every EU-trading ship's verified
  emissions, public and free.
- **Plain-English updates** — DNV, Lloyd's Register, ClassNK and ABS all publish
  free regulatory news. DNV's is the best written. Subscribe to one; fifteen
  minutes a month keeps you current.

## And the honest limits

Know where you *stop* — being straight about this earns more trust than bluffing:

- Our EEXI reference tables are **not yet line-by-line verified** against the
  consolidated MARPOL text. Don't present an EEXI verdict as certification-grade.
- Public-data figures assume a fuel (LNG for LNG carriers, HFO otherwise) because
  the register does not publish fuel type. Biofuel and methanol burners are
  therefore invisible to us — and they are surplus holders. **Always ask what
  they bunkered.**
- We are not a verifier and do not issue certificates. We compute, we show our
  work, and their verifier checks it. That boundary is a feature.
