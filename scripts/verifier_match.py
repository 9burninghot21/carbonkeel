#!/usr/bin/env python3
"""How well does our own rebuild of the EU ETS scope CO2 agree with the verifier's figure?

Runs over EVERY ship in the newest register export (not a sample) and writes
data/verifier_match.json. The copy on the site and in the documents quotes these
figures, and tests/test_style.py checks that it still does.

The bill itself uses the verifier-reported figure (see ghgcore.euets); this
comparison is a cross-check on our rule application, and it surfaces the ships
where something we cannot see (ship size, transhipment stops, derogations) matters.

Usage: python scripts/verifier_match.py
"""
import io, json, os, statistics, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from ghgcore.exports import latest, parse                      # noqa: E402
from ghgcore.thetis import load_thetis_cached, rebuilt_ets_co2  # noqa: E402


def main():
    path = latest(os.path.join(ROOT, "fixtures"))
    year, version = parse(path)
    recs = load_thetis_cached(path)
    c, over, ratios = Counter(), 0, []
    for r in recs.values():
        rebuilt, rep = rebuilt_ets_co2(r), r.co2_ets_reported_t
        if rebuilt is None:
            continue
        c["ships"] += 1
        if rep is None:
            c["no_reported_figure"] += 1
        elif rep == 0 and rebuilt > 0:
            c["reported_zero_rebuilt_positive"] += 1
        elif rep == 0:
            c["both_zero"] += 1
        else:
            d = abs(rebuilt - rep) / rep
            if d < 5e-4:
                c["exact"] += 1
            elif d < 0.01:
                c["within_1pct"] += 1
            elif d < 0.02:
                c["within_2pct"] += 1
            else:
                c["outside_2pct"] += 1
                ratios.append(rebuilt / rep)
                over += rebuilt > rep
    # ships with nothing in EU scope on either side "agree" trivially, so they are left out of the shares
    n = c["ships"] - c["both_zero"] - c["no_reported_figure"]
    cum1 = c["exact"] + c["within_1pct"]
    cum2 = cum1 + c["within_2pct"]
    out = {
        "source": os.path.basename(path), "reporting_year": year, "version": version,
        "ships_in_report": c["ships"], "ships_with_eu_scope_activity": n,
        "counts": dict(c),
        "share_exact": round(c["exact"] / n, 4),
        "share_within_1pct": round(cum1 / n, 4),
        "share_within_2pct": round(cum2 / n, 4),
        "share_outside_2pct": round(c["outside_2pct"] / n, 4),
        "share_reported_zero_rebuilt_positive": round(c["reported_zero_rebuilt_positive"] / n, 4),
        "rebuilt_above_reported_share_of_outside": round(over / len(ratios), 3) if ratios else None,
        "median_ratio_when_outside": round(statistics.median(ratios), 3) if ratios else None,
    }
    with open(os.path.join(ROOT, "data", "verifier_match.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
