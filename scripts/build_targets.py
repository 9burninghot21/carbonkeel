#!/usr/bin/env python3
"""Build the outreach target list from the THETIS-MRV public export.

Aggregates the 2025 export by company (the DoC-holder reported to EMSA),
filters to the ICP (mid-size managers, focus ship types: container / bulk /
tanker, meaningful EU exposure), and writes:
  outreach/targets_2025.csv      full list, one row per qualifying company
  outreach/TOP_TARGETS.md        readable top-50 briefing for outreach

Usage: python scripts/build_targets.py [--min 8] [--max 60]
"""
import argparse, csv, glob, io, os, sys, warnings
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")

FOCUS_TYPES = {"container ship", "bulk carrier", "oil tanker", "chemical tanker"}
EUA_PRICE = 70.0

# Column indexes in the real export (header row 3; ship block then company block)
IMO, NAME, TYPE = 0, 1, 2
CO_NAME = 9
FUEL_TOTAL, CO2_TOTAL, CO2_ETS = 23, 28, 37


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=8, help="min fleet size")
    ap.add_argument("--max", type=int, default=60, help="max fleet size")
    args = ap.parse_args()

    import openpyxl
    root = os.path.join(os.path.dirname(__file__), "..")
    path = sorted(glob.glob(os.path.join(root, "fixtures", "thetis_mrv_*.xlsx")))[-1]
    print(f"Aggregating {os.path.basename(path)} by company ...")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]

    comp = defaultdict(lambda: {"ships": 0, "focus": 0, "co2": 0.0, "ets_co2": 0.0,
                                "types": defaultdict(int), "vessels": []})
    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[IMO] is None or not row[CO_NAME]:
            continue
        c = comp[str(row[CO_NAME]).strip()]
        stype = str(row[TYPE] or "").strip()
        c["ships"] += 1
        c["types"][stype] += 1
        if stype.lower() in FOCUS_TYPES:
            c["focus"] += 1
        c["co2"] += _f(row[CO2_TOTAL])
        c["ets_co2"] += _f(row[CO2_ETS])
        c["vessels"].append((str(row[IMO]).split(".")[0], str(row[NAME] or "").strip(), stype))
    wb.close()

    rows = []
    for name, c in comp.items():
        if not (args.min <= c["ships"] <= args.max):
            continue
        if c["focus"] / c["ships"] < 0.5:      # focus-type majority fleets
            continue
        eua_cost = c["ets_co2"] * EUA_PRICE
        rows.append({
            "company": name, "fleet_size": c["ships"], "focus_ships": c["focus"],
            "top_types": "; ".join(f"{t} x{n}" for t, n in
                                   sorted(c["types"].items(), key=lambda kv: -kv[1])[:3]),
            "total_co2_t": round(c["co2"]), "ets_scope_co2_t": round(c["ets_co2"]),
            "est_eua_cost_eur": round(eua_cost),
            "sample_imos": ",".join(v[0] for v in c["vessels"][:12]),
        })
    rows.sort(key=lambda r: -r["est_eua_cost_eur"])

    out = os.path.join(root, "outreach")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "targets_2025.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(out, "TOP_TARGETS.md"), "w", encoding="utf-8") as f:
        f.write("# Top outreach targets — from THETIS-MRV 2025 (ESTIMATE)\n\n"
                f"ICP filter: {args.min}-{args.max} ships, majority container/bulk/tanker, "
                "ranked by verifier-reported ETS-scope CO2 x EUR 70/EUA.\n"
                "Find the DPA / fleet performance / ESG contact on LinkedIn; "
                "generate their fleet report with scripts/fleet_report.py "
                "or /report?imos=... and attach it to the first message.\n\n"
                "| # | Company | Ships | Fleet mix | ETS CO2 (t) | Est. EUA cost |\n"
                "|---|---------|-------|-----------|-------------|---------------|\n")
        for i, r in enumerate(rows[:50], 1):
            f.write(f"| {i} | {r['company']} | {r['fleet_size']} | {r['top_types']} | "
                    f"{r['ets_scope_co2_t']:,} | EUR {r['est_eua_cost_eur']:,} |\n")

    print(f"{len(rows)} qualifying companies -> outreach/targets_2025.csv")
    print("Top 10 by estimated EUA cost:")
    for r in rows[:10]:
        print(f"  {r['company'][:46]:46} {r['fleet_size']:>3} ships  "
              f"EUR {r['est_eua_cost_eur']:>12,}")


def _f(x):
    try:
        return float(str(x).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
