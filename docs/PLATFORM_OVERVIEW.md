# What you actually own — the platform in one read

Written for you after a gap. No code required; this is the mental model.

## The one architectural decision everything hangs off

> **Deterministic engines do every calculation. AI never touches a number.**

An LLM is used in exactly one place: reading the *column headings* of a messy
noon-report spreadsheet and guessing which column is distance. Its answer is
validated and then applied by ordinary code. Every euro, tonne and letter grade
comes from a Python function you can read, with the regulation's own constants
sitting in a named table above it.

This is why you can hand a verifier a worksheet, and why the numbers are stable:
the same inputs always give the same output, and when a regulation changes it is
a one-table edit.

## The shape of it

```
            public data                     owner data
    EMSA register (16,673 ships)        noon reports / BDNs
                 |                              |
                 +--------------+---------------+
                                |
                    canonical schema (schema.py)
                    vessel · voyage legs · fuel
                                |
        +--------+--------+-----+----+--------+---------+
        |        |        |          |        |         |
       CII     EEXI    EU ETS    UK ETS   FuelEU   IMO NZF
        |        |        |          |        |         |
        +--------+--------+-----+----+--------+---------+
                                |
                        scorecard + pooling
                                |
              web app · PDF reports · audit worksheets
```

Everything enters through one canonical schema. That is why adding UK ETS took
an afternoon: it consumes the same voyage legs everything else does.

## The six engines

| Engine | What it answers | Source of truth |
|---|---|---|
| `cii.py` + `cii_calc.py` | A–E rating, and the rating every year to 2030 | MEPC.352–355(78) |
| `eexi.py` | Is the ship's *design* compliant? | MARPOL Reg. 23/25 ⚠ tables unverified |
| `euets.py` | How many EUAs, what do they cost | Directive 2003/87/EC |
| `ukets.py` | UK domestic equivalent | UK ETS Order 2026 |
| `fueleu.py` | Intensity, balance, penalty | Reg. (EU) 2023/1805 |
| `nzf.py` | 2028 global exposure | MEPC 83 — scenario only |
| `pooling.py` | Which ships to pool to kill the most penalty | Art. 21 (exact knapsack) |

Supporting: `thetis.py` (reads the EMSA register), `ingest.py` (reads customer
spreadsheets), `projection.py` (part-year → year-end), `audit.py` (the
worksheet), `deadlines.py` (the calendar), `privacy.py` (suppression and rate
limits), `access.py` (the CII calculator key).

**143 hand-computed tests** guard all of it. They are hand computations with the
arithmetic written in comments — not snapshots of whatever the code produced.
That distinction is the whole point: a snapshot test passes even when the code
is wrong.

## The product, as a visitor sees it

| Tab | Gate | What it does |
|---|---|---|
| **Check a vessel** | free | Type a name → the bill in euros, the CII band, where the ship sits among its sisters, and a value chip that silently finds what levers would save |
| **EEXI** | free | Required vs attained, for a registered ship or a custom vessel you describe |
| **CII calculator** | 🔒 key | Owner data, G1–G5, trajectory to 2030 — the paid tool |
| **My fleet** | free (≤8 ships) | Fleet totals, the pooling optimum, printable report, draft agreement |
| **Calendar** | free | Every deadline with its legal basis, as a downloadable calendar |
| **Method** | free | Every formula and source, so a verifier can check you |
| **Your data** | free | Claim, correct, or suppress our figures about your ship |

Three **persona views** on every vessel result — Owner/CFO (the bill),
Technical/Ops (the rating and levers), Verifier (provenance and the
reconstruction check). Same data, three framings, because three different people
will be in the room.

## Why anyone would pay

1. **You start with their numbers, not a demo.** Before the first call you can
   price any prospect's fleet from data their own verifier filed. No competitor
   opens a cold email with the recipient's own compliance bill.
2. **Euros, not letter grades.** Four regimes, one card, with deadlines.
3. **The balance is an asset, and you trade it.** Pooling is the only part of
   this market with network effects. Calculators do not have counterparties.

The proof line that does the most work: **our reconstruction of ETS-scope CO₂
matches the figure the ship's own accredited verifier filed, to the tonne.**

## What is deliberately *not* built

- **Accounts and billing** — no users yet, so no auth. The CII calculator is
  gated by a shared key instead, honestly labelled as such.
- **Voluntary carbon offsets** — no regime recognises them; selling them next to
  compliance numbers would cost more credibility than it earns.
- **A hosted copy of the register** — rate-limited, capped, never indexed. The
  risk to operators is bulk harvesting, not an honest lookup.

## Known weaknesses — say these out loud before a customer finds them

1. **EEXI tables are unverified.** The biggest accuracy risk in the product.
2. **Public data assumes a fuel.** The register publishes CO₂ but not fuel type,
   so we assume LNG for LNG carriers and HFO otherwise. Biofuel and methanol
   burners therefore look worse than they are — and they are exactly the surplus
   holders you want to find. Always ask what they bunkered.
3. **Distance is derived** from the filed CO₂-per-mile, and **DWT is not
   published at all** — the visitor types it in. Both are labelled estimates.
4. **Prices are assumptions.** €70/EUA, £40/UKA. The UI shows a range for this
   reason.

## Running it

```bash
python scripts/daily.py          # your day
python tests/test_engines.py     # 143 checks, run before trusting anything
python -m uvicorn api.main:app   # the app, http://127.0.0.1:8000
python scripts/daily.py --targets 10
python scripts/daily.py --surplus
python scripts/make_reports.py --top 10 --pdf
```

CII calculator key: `<your-access-key>` (in `data/access_keys.txt` — keep it
out of git).

## Where to go deeper

- `docs/DOMAIN_PRIMER.md` — the regulations, two weeks at 15 min/day
- `docs/VERIFICATION_GUIDE.md` — how to audit the maths yourself
- `docs/CALCULATION_NOTES.md` — every formula with a worked example
- `docs/OPERATING_PLAN.md` — the seven months to 30 April
- `docs/LAUNCH_KIT.md` — hosting, the cold emails, the contact list
- `docs/REGULATORY_COVERAGE_MAP.md` — what to build next and why
