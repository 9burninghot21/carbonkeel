#!/usr/bin/env python3
"""Free-lookup CLI against the real THETIS-MRV public export.

Usage:
    python scripts/lookup.py 9700001 --dwt 61000
    python scripts/lookup.py "MSC SERENA" --dwt 85000
    python scripts/lookup.py --search "MAERSK"      # find ships by name

Uses the newest fixtures/thetis_mrv_*.xlsx. All output is an ESTIMATE
reconstructed from public verified totals; owner data makes it exact.
"""
import argparse, glob, io, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from ghgcore import build_scorecard
from ghgcore.thetis import load_thetis_xlsx, record_to_activity


def newest_export() -> str:
    fx = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    files = sorted(glob.glob(os.path.join(fx, "thetis_mrv_*.xlsx")))
    if not files:
        sys.exit("No fixtures/thetis_mrv_*.xlsx found — download via the "
                 "public API (see thetis.py docstring).")
    return files[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="IMO number or exact ship name")
    ap.add_argument("--dwt", type=float, help="deadweight tonnage (needed for CII)")
    ap.add_argument("--search", help="substring search on ship names")
    ap.add_argument("--year", type=int, help="scoring year (default: reporting period)")
    args = ap.parse_args()

    path = newest_export()
    print(f"Loading {os.path.basename(path)} ...")
    records = load_thetis_xlsx(path)
    print(f"{len(records):,} ships in export.\n")

    if args.search:
        hits = [r for r in records.values() if args.search.upper() in r.name.upper()]
        print(f"{len(hits)} matches for {args.search!r}:")
        for r in hits[:25]:
            print(f"  IMO {r.imo}  {r.name}  ({r.ship_type_raw})  "
                  f"CO2 {r.co2_tonnes:,.0f} t")
        return

    if not args.query:
        sys.exit("Give an IMO number / ship name, or --search.")

    rec = records.get(args.query)
    if rec is None:
        matches = [r for r in records.values() if r.name.upper() == args.query.upper()]
        if not matches:
            sys.exit(f"No ship found for {args.query!r} — try --search.")
        rec = matches[0]

    if not args.dwt:
        sys.exit(f"Found {rec.name} (IMO {rec.imo}, {rec.ship_type_raw}). "
                 "Public data lacks DWT — pass --dwt to score CII.")

    year = args.year or rec.reporting_period or 2025
    activity = record_to_activity(rec, year=year, dwt=args.dwt)
    sc = build_scorecard(activity)

    print("=" * 70)
    print(f"ESTIMATE scorecard — {sc.vessel_name} (IMO {sc.imo_number}), "
          f"reporting period {year}")
    print("=" * 70)
    print(f"  Verified totals: CO2 {rec.co2_tonnes:,.1f} t | fuel "
          f"{rec.fuel_tonnes:,.1f} t | est. distance "
          f"{rec.est_distance_nm or 0:,.0f} nm")
    if rec.co2_ets_reported_t is not None:
        print(f"  Verifier-reported ETS-scope CO2: {rec.co2_ets_reported_t:,.1f} t "
              f"(our reconstruction: {sc.ets.co2e_in_scope_t:,.1f} t CO2e)")
    print(f"\n  [1] Regulatory Health : {sc.regulatory_health}/100  (CII {sc.cii.rating}, "
          f"ratio {sc.cii.ratio})")
    print(f"  [2] Cost Exposure     : EUR {sc.cost_exposure_eur:,.0f}  "
          f"(ETS {sc.ets.allowances_due:,.0f} EUAs + FuelEU penalty risk "
          f"EUR {sc.fueleu.penalty_eur:,.0f})")
    print(f"  [3] Compliance Asset  : EUR {sc.compliance_asset_eur:,.0f}  "
          f"(FuelEU balance {sc.fueleu.compliance_balance_tco2e:+,.1f} tCO2e)")
    print(f"  [4] Future Readiness  : {sc.future_readiness}")
    print("\n  NEXT ACTIONS:")
    for i, a in enumerate(sc.actions, 1):
        print(f"   {i}. {a}")
    print("\n  All figures are ESTIMATES from public THETIS-MRV data.")


if __name__ == "__main__":
    main()
