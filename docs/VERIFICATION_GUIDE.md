# How to verify the numbers yourself

You should not take my word that the engines are right, and neither will a
customer's verifier. This is the sequence I would follow, in order of how much
it proves per hour spent. Work through it with a calculator and the primary
texts open; everything is designed so you *can*.

---

## Level 0 — the five-minute smoke test (do this every session)

```bash
python tests/test_engines.py      # 137 hand-computed checks
python demo.py                    # both data paths end to end
```
If either fails, stop and fix before anything else. Every check in that file
has its arithmetic written above it as a comment — they are hand computations,
not snapshots of whatever the code happened to output. That distinction is the
whole point: a snapshot test passes even when the code is wrong.

## Level 1 — recompute one CII by hand (30 minutes, highest value)

Take the worked example in `docs/CALCULATION_NOTES.md` §1 and redo it on a
calculator:

1. **CO₂**: 3,000 t HFO × 3.114 = **9,342 t**
   → check CF 3.114 against MEPC.352(78) (G1), Table 1.
2. **Attained**: 9,342 × 10⁶ / (50,000 dwt × 50,000 nm) = **3.737** gCO₂/dwt·nm
3. **Reference**: 4,745 × 50,000^(−0.622) = **5.669**
   → check *a* and *c* against MEPC.353(78) Annex 15, Table 1, "Bulk carrier".
4. **Required (2026)**: 5.669 × (1 − 0.11) = **5.045**
   → check Z = 11% for 2026 against MEPC.338(76) as amended by MEPC.400(83).
5. **Rating**: 3.737 / 5.045 = 0.741 ≤ d1 (0.86) → **A**
   → check the dd vector (0.86, 0.94, 1.06, 1.18) against MEPC.354(78)
   Annex 16, Table 1.

Now open the **CII calculator** tab, enter the same numbers, and confirm you
get A with attained 3.737 and required 5.045. If your hand figure and the tool
disagree, the tool is wrong — tell me and I will fix it.

Repeat once for a **GT-based type** (cruise, ro-ro, ro-pax, vehicle carrier),
because that path uses gross tonnage and a different reference line. Worked
example: cruise, 100,000 GT, 9,000 t HFO, 60,000 nm → attained 4.671,
reference 930 × 100,000^(−0.383) = 11.31.

## Level 2 — verify against the outside world (the strongest evidence)

The public register contains a figure computed by someone else: each ship's
**"CO₂ emissions to be reported under Directive 2003/87/EC"**, calculated by
that ship's accredited verifier. We reconstruct the same quantity from the
scope splits. They should match.

1. Open any vessel, switch to the **Verifier** view.
2. Compare "ETS-scope CO₂, verifier-reported" with "our reconstruction".
3. Spot-check 10 ships across types. Investigate anything off by >2%.

This is the single most persuasive artefact you have: an independent,
accredited party's number, reproduced by your engine.

## Level 3 — audit the parameter tables against primary sources

Each table lives in one named place. Open the resolution PDF beside the file
and read them line by line.

| Table | File | Primary source |
|---|---|---|
| CF factors | `cii.py: CF_TCO2_PER_T` | MEPC.352(78) (G1) |
| Reference lines (a, c) | `cii.py: REFERENCE_LINES` + split constants | MEPC.353(78) Annex 15 Table 1 |
| Z factors | `cii.py: Z_FACTORS` | MEPC.338(76) / MEPC.400(83) |
| dd vectors | `cii.py: DD_VECTORS` | MEPC.354(78) Annex 16 Table 1 |
| Fuel LCV / WtW | `fueleu.py: FUEL_PROPS` | Reg. (EU) 2023/1805 **Annex II** |
| CH₄ / N₂O factors | `euets.py: NON_CO2_EF` | Annex II cols. 7–9 + MRV acts |
| EEXI reference lines & X | `eexi.py: EEDI_REF, EEXI_X` | MARPOL Reg. 24–25, MEPC.231(65), MEPC.328(76) |

**Known open items — do these before any customer-facing EEXI verdict:**
- `eexi.py` tables are VERIFY-tagged. The reduction-factor bands and reference
  lines need a line-by-line check against the consolidated MARPOL text. This is
  the biggest remaining accuracy risk in the product.
- Biofuel WtW values are pathway-specific; ours is a UCOME default. A real
  certificate (PoS) should replace it per bunker.
- G5 correction *factors* are operator-supplied by design — we apply and
  record, never derive. That is a deliberate limitation, not a gap.

## Level 4 — behavioural checks (catch logic errors tables can't)

Verify the engine responds correctly to change, not just to one input:

- **Monotonic**: more fuel, same distance → worse rating. Never the reverse.
- **Scale-invariant**: double fuel *and* distance → attained CII unchanged
  (it is a ratio). Cost figures should double. `test_projection` pins this.
- **Year sensitivity**: same ship, 2026 → 2030 must get worse (Z rises).
  The trajectory strip shows it; a flat trajectory means Z is not applied.
- **Threshold behaviour**: a gas carrier at 64,999 vs 65,001 dwt must switch
  reference line *and* dd vector. Same for general cargo at 20,000, LNG at
  65,000/100,000, vehicle carriers at 30,000 GT.
- **Fuel discrimination**: swap HFO for LNG at equal tonnes — CO₂ falls (CF
  2.750 vs 3.114) but methane slip must raise the ETS CO₂e. If LNG looks
  strictly better everywhere, the slip is not wired in.

## Level 5 — the reality checks the maths cannot give you

1. **Ask a superintendent** to run three of their own ships and tell you where
   the number feels wrong. Domain instinct catches what arithmetic cannot.
2. **Compare against a class tool** (DNV, ClassNK, LR calculators are free) on
   the same inputs. Differences are usually capacity basis, correction factors,
   or year — chase each to ground.
3. **Have one verifier look at the audit worksheet** (`/api/audit/{imo}?dwt=…`).
   Their objections become your VERIFY list, and their acceptance is a
   reference you can sell with.

---

## When you find a discrepancy

1. Isolate: which layer — input, parameter table, or formula?
2. Reproduce in the smallest possible case (one fuel, round numbers).
3. Check the primary source *before* changing code — usually the expectation
   is wrong, not the engine. (That happened in this build: my own test expected
   a 2030 required CII of 3.96 when the correct figure was 4.45.)
4. Fix the table or formula, add a hand-computed test that would have caught
   it, cite the source in the commit.
5. Never "fix" a number to make a test pass. Fix the understanding first.

## Priority order if time is short

1. Level 0 (always) → 2. Level 2 verifier cross-check (10 ships) →
3. Level 1 by hand (twice) → 4. EEXI table verification (the open risk) →
5. Level 4 behavioural → 6. Level 5 outside opinion.
