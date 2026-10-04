#!/usr/bin/env python3
"""End-to-end demo: both data paths -> four-score vessel card + actions.

Path A (free lookup): THETIS-MRV public record -> estimated scorecard
Path B (customer data): noon-report CSV -> full scorecard

Run:  python3 demo.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ghgcore import Vessel, ShipType, build_scorecard
from ghgcore.schema import VoyageScope
from ghgcore.thetis import load_thetis_csv, record_to_activity
from ghgcore.ingest import ingest_noon_csv
from ghgcore.projection import annualise

BAR = "=" * 72


def show(sc, header):
    print(f"\n{BAR}\n{header}\n{BAR}")
    print(f"Vessel: {sc.vessel_name} (IMO {sc.imo_number})  |  Year: {sc.year}")
    print(f"\n  [1] Regulatory Health Score : {sc.regulatory_health}/100")
    print(f"      CII: {sc.cii.rating}  (attained {sc.cii.attained} vs required "
          f"{sc.cii.required} gCO2/dwt-nm, Z={sc.cii.z_factor_pct}%)")
    print(f"  [2] Cost Exposure           : EUR {sc.cost_exposure_eur:,.0f}")
    print(f"      ETS {sc.ets.allowances_due:,.0f} EUAs (EUR {sc.ets.cost_eur:,.0f} @ "
          f"{sc.ets.eua_price_used}/t)  |  FuelEU penalty risk EUR {sc.fueleu.penalty_eur:,.0f}")
    print(f"  [3] Compliance Asset Score  : EUR {sc.compliance_asset_eur:,.0f}")
    print(f"      FuelEU balance: {sc.fueleu.compliance_balance_tco2e:+,.1f} tCO2e "
          f"({sc.fueleu.ghg_intensity} vs target {sc.fueleu.target} gCO2e/MJ)")
    print(f"  [4] Future Readiness (NZF)  : {sc.future_readiness}")
    print(f"\n  NEXT ACTIONS:")
    for i, a in enumerate(sc.actions, 1):
        print(f"   {i}. {a}")


def main():
    fx = os.path.join(os.path.dirname(__file__), "fixtures")

    # ---- Path A: free public-data lookup (the marketing funnel) ----
    records = load_thetis_csv(os.path.join(fx, "sample_thetis.csv"))
    rec = records["9700001"]
    act = record_to_activity(rec, year=2026, dwt=61_000)
    show(build_scorecard(act), "PATH A - FREE LOOKUP (THETIS-MRV public data, ESTIMATE)")

    # ---- Path B: customer noon reports (the paid product) ----
    vessel = Vessel("9700001", "MV TEST TRADER", ShipType.BULK_CARRIER, dwt=61_000, gt=34_000)
    activity, report = ingest_noon_csv(os.path.join(fx, "sample_noon_reports.csv"),
                                       vessel, 2026, scope=VoyageScope.INTRA_EEA)
    print(f"\n[Ingestion report] rows={report['rows']}  mapped={report['mapping']}"
          f"  unmapped={report['unmapped_columns']}")
    for flag in report["flags"]:
        print(f"[Data-quality flag] {flag}")
    proj = annualise(activity, days_observed=report["rows"])
    show(proj.scorecard, f"PATH B - CUSTOMER NOON REPORTS (annualised from "
                         f"{report['rows']} days, confidence {proj.confidence})")
    print()
    for n in proj.notes:
        print(f"[Projection note] {n}")


if __name__ == "__main__":
    main()
