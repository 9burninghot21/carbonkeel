#!/usr/bin/env python3
"""CarbonKeel daily console — the one command you run at the start of your hour.

    python scripts/daily.py                 what to do today + pipeline + deadlines
    python scripts/daily.py --targets 5     next targets, with their numbers and a
                                            ready-to-send message
    python scripts/daily.py --log sent --company "Technomar" [--note "..."]
    python scripts/daily.py --log reply --company "Technomar"
    python scripts/daily.py --week          the week's plan

Designed for one hour a day: it decides what you do, so the hour goes on
sending and talking rather than deciding.
"""
import argparse
import csv
import glob
import io
import os
import sys
import warnings
from datetime import date, datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

PIPELINE = os.path.join(ROOT, "outreach", "pipeline.csv")
TARGETS = os.path.join(ROOT, "outreach", "targets_2025.csv")
FIELDS = ["company", "imos", "contact_name", "contact_role", "stage",
          "last_action", "next_action", "notes"]
STAGES = ["target", "sent", "followed_up", "replied", "call_booked",
          "demo_done", "partner", "paid", "dead"]
START = date(2026, 10, 1)          # campaign day 1

# Fixed dates that drive the whole campaign.
DEADLINES = [
    (date(2026, 10, 31), "IMO NZF adoption vote reconvenes (MEPC ES, London)"),
    (date(2026, 12, 31), "FuelEU 2026 compliance year ends - balances locked"),
    (date(2027, 1, 31), "FuelEU 2026 report to verifier"),
    (date(2027, 3, 31), "EU MRV verified report + IMO DCS data"),
    (date(2027, 4, 30), "*** FuelEU POOLING REGISTRATION CLOSES ***"),
    (date(2027, 5, 31), "CII rating / Statement of Compliance issued"),
    (date(2027, 9, 30), "EU ETS surrender for 2026 emissions"),
]

# weekday -> (label, the single task for the hour)
WEEK = {
    0: ("MON - Target", "Run --targets 10. Find each contact on LinkedIn "
        "(fleet performance / technical director / DPA). Add with --contact."),
    1: ("TUE - Send 5", "Send the first 5 messages with their fleet PDF "
        "attached. Log each: --log sent --company \"...\""),
    2: ("WED - Send 5", "Send the next 5. Answer any replies first - a reply "
        "always outranks a new send."),
    3: ("THU - Follow up & talk", "Follow up everything sent 4+ days ago with "
        "no reply (listed below). Take any call booked."),
    4: ("FRI - Build", "One Claude Code session: the next roadmap feature, or "
        "whatever a prospect asked for this week."),
    5: ("SAT - Off", "Off. If you have energy: one LinkedIn post from a real "
        "finding this week."),
    6: ("SUN - Off", "Off. Rest is in the plan - this is a seven-month run."),
}

# Cold start overrides the weekly rhythm: days 1-9 are a specific sequence,
# because on day 1 there is nothing to follow up and no one to call.
LAUNCH = {
    1: ("Register the domain + pull first targets",
        "1) Buy carbonkeel.com (Cloudflare/Porkbun, ~EUR 10, WHOIS privacy ON). "
        "2) Run: python scripts/daily.py --targets 10. Read the numbers it "
        "prints - that is your pitch."),
    2: ("Find 10 humans",
        "For each of the 10 companies find ONE contact on LinkedIn: fleet "
        "performance / technical director / DPA / ESG. Log: --log target "
        "--company \"X\" --contact \"Name, Role\". No sending today."),
    3: ("Off", "Off."),
    4: ("Off", "Off."),
    5: ("Generate PDFs + send the first 5",
        "python scripts/make_reports.py --top 10 --pdf, then send 5 messages "
        "with each company's own PDF attached. Log each --log sent."),
    6: ("Send the next 5",
        "Send the remaining 5. Then stop - do not refresh your inbox for an "
        "hour, it is not a productive use of the day."),
    7: ("Next 10 targets",
        "python scripts/daily.py --targets 10, then find their contacts. "
        "Answer any reply from batch 1 before anything else."),
    8: ("Send 5 + follow up batch 1",
        "Send 5 of the new batch. Follow up anyone from days 5-6 who has not "
        "replied (this console lists them)."),
    9: ("Build + review week 1",
        "Claude Code session. Ask: what did prospects actually ask about? "
        "Build that. Then check your reply rate below."),
}

PHASES = [
    (date(2026, 10, 1), date(2026, 10, 14), "A - LAUNCH",
     "Domain live, first 20 messages out. Nothing else matters."),
    (date(2026, 10, 15), date(2026, 10, 31), "B - NZF MOMENT",
     "Publish within hours of the vote (both drafts are written). 20 more sends."),
    (date(2026, 11, 1), date(2026, 11, 30), "C - DESIGN PARTNERS",
     "Turn conversations into 3 partners sending real noon-report data."),
    (date(2026, 12, 1), date(2026, 12, 31), "D - YEAR-END POSITION",
     "Every prospect gets their near-final 2026 FuelEU position. Build the "
     "surplus/deficit book - this is the pooling pitch."),
    (date(2027, 1, 1), date(2027, 2, 28), "E - POOL BOOK",
     "Match surplus ships to deficit ships. Draft the agreements."),
    (date(2027, 3, 1), date(2027, 4, 30), "F - CLOSE POOLS",
     "Register pools before 30 April. First success fee."),
]


def load_pipeline():
    if not os.path.exists(PIPELINE):
        return []
    with open(PIPELINE, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_pipeline(rows):
    os.makedirs(os.path.dirname(PIPELINE), exist_ok=True)
    with open(PIPELINE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def phase_for(d):
    for s, e, name, focus in PHASES:
        if s <= d <= e:
            return name, focus, (e - d).days
    if d < START:
        return PHASES[0][2], PHASES[0][3], (PHASES[0][1] - d).days
    return "G - SCALE", "Past the first pooling season - scale what worked.", 0


def _wrap(text, width):
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


def today_view(_args):
    d = date.today()
    day_n = (d - START).days + 1
    week_n = max(1, (day_n - 1) // 7 + 1)
    name, focus, left = phase_for(d)
    if day_n in LAUNCH:
        label, task = LAUNCH[day_n]
        label = f"DAY {day_n} - {label}"
    else:
        label, task = WEEK[d.weekday()]

    print("=" * 68)
    print(f"  CarbonKeel - day {day_n} - week {week_n} - {d:%a %d %b %Y}")
    print("=" * 68)
    print(f"\nPHASE {name}")
    for line in _wrap(focus, 64):
        print(f"  {line}")
    if left:
        print(f"  ({left} days left in this phase)")

    print(f"\n>>> TODAY: {label}")
    for line in _wrap(task, 62):
        print(f"    {line}")

    rows = load_pipeline()
    if rows:
        counts = {}
        for r in rows:
            counts[r["stage"]] = counts.get(r["stage"], 0) + 1
        print("\nPIPELINE")
        for s in STAGES:
            if counts.get(s):
                print(f"    {s:<13} {counts[s]:>3}")
        live = sum(counts.get(s, 0) for s in
                   ["replied", "call_booked", "demo_done", "partner", "paid"])
        contacted = sum(counts.get(s, 0) for s in ["sent", "followed_up"]) + live
        if contacted:
            print(f"    {'-' * 17}")
            print(f"    reply rate  {live / contacted * 100:>4.0f}%   "
                  f"({live} live of {contacted} contacted)")
        due = []
        for r in rows:
            if r["stage"] in ("sent", "followed_up") and r.get("last_action"):
                try:
                    la = datetime.strptime(r["last_action"], "%Y-%m-%d").date()
                except ValueError:
                    continue
                if (d - la).days >= 4:
                    due.append((r["company"], (d - la).days))
        if due:
            print(f"\nFOLLOW UP  ({len(due)} waiting 4+ days)")
            for c, n in sorted(due, key=lambda x: -x[1])[:8]:
                print(f"    {c[:46]:<46} {n:>3}d")
    else:
        print("\nPIPELINE  empty")
        print("    start here:  python scripts/daily.py --targets 10")

    # Anything an operator raises about their own data comes to you, by name,
    # before anything else. A suppression already took effect automatically;
    # this is so you can follow it up personally.
    reqs = os.path.join(ROOT, "data", "privacy", "requests.jsonl")
    if os.path.exists(reqs):
        import json
        pending = []
        with open(reqs, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    pending.append(json.loads(line))
                except ValueError:
                    continue
        if pending:
            print("")
            print("OPERATORS WHO CONTACTED YOU  (%d total)" % len(pending))
            for q in reversed(pending[-6:]):
                who = q.get("company") or q.get("contact_email", "?")
                print(f"    {q.get('kind','?'):<9} {who[:32]:<32} "
                      f"{', '.join(q.get('imos', []))[:20]}")
                print(f"              reply to {q.get('contact_email','?')}")
            print("    -> someone with a problem. Answer these first.")

    print("\nDEADLINES")
    for dl, what in DEADLINES:
        n = (dl - d).days
        if n < 0:
            continue
        mark = "  <<<" if "***" in what else ""
        print(f"    {dl:%d %b %Y}  {n:>4}d  {what}{mark}")
    print()


def week_view(_args):
    d = date.today()
    monday = d - timedelta(days=d.weekday())
    name, focus, _ = phase_for(d)
    print(f"\nWEEK OF {monday:%d %b %Y}   PHASE {name}")
    for line in _wrap(focus, 66):
        print(f"  {line}")
    print()
    for i in range(7):
        day = monday + timedelta(days=i)
        label, task = WEEK[i]
        here = "->" if day == d else "  "
        print(f"{here} {day:%a %d %b}   {label}")
        for line in _wrap(task, 54):
            print(f"              {line}")
    print()


def targets_view(args):
    """Next N companies to contact, with the numbers that write the message."""
    from ghgcore.thetis import load_thetis_cached, record_to_activity
    from ghgcore.fueleu import compute_fueleu
    from ghgcore.pooling import PoolCandidate, suggest_pool

    if not os.path.exists(TARGETS):
        sys.exit("No outreach/targets_2025.csv - run scripts/build_targets.py first.")
    with open(TARGETS, newline="", encoding="utf-8-sig") as f:
        targets = list(csv.DictReader(f))
    done = {r["company"] for r in load_pipeline()}
    # Skip mega-carrier subsidiaries: procurement mazes, months of nothing.
    skip = ("CMA", "EVERGREEN", "MAERSK", "MSC ", "COSCO", "ORIENT OVERSEAS",
            "HAPAG", "YANG MING", "SHANGHAI OCEAN")
    queue = [t for t in targets if t["company"] not in done
             and not any(s in t["company"].upper() for s in skip)][:args.targets]
    if not queue:
        sys.exit("No untouched targets left in the ICP list.")

    print("\nLoading verified fleet data ...")
    path = sorted(glob.glob(os.path.join(ROOT, "fixtures", "thetis_mrv_*.xlsx")))[-1]
    recs = load_thetis_cached(path)
    by_company = {}
    for r in recs.values():
        if r.company:
            by_company.setdefault(r.company, []).append(r)

    rows = load_pipeline()
    for t in queue:
        fleet = by_company.get(t["company"], [])
        cands, surplus, deficit = [], 0.0, 0.0
        for r in fleet:
            if r.ship_type is None:
                continue
            feu = compute_fueleu(record_to_activity(
                r, year=r.reporting_period or 2025, dwt=1.0))
            cb = feu.compliance_balance_tco2e
            cands.append(PoolCandidate(r.imo, r.name, cb, feu.ghg_intensity))
            if cb > 0:
                surplus += cb
            else:
                deficit += -cb
        pool = suggest_pool(cands) if cands else None

        print("\n" + "=" * 68)
        print(f"  {t['company']}")
        print("=" * 68)
        print(f"  Fleet {t['fleet_size']} ships - {t['top_types']}")
        print(f"  Verified ETS-scope CO2 {int(t['ets_scope_co2_t']):,} t "
              f"(~EUR {int(t['est_eua_cost_eur']):,}/yr in allowances)")
        hook = ("the deficit needs an external surplus partner, which is exactly "
                "the match we make")
        if pool:
            print(f"  FuelEU 2025: surplus {surplus:,.0f} t | deficit {deficit:,.0f} t")
            if pool.avoided_penalty_eur > 0:
                print(f"  >> POOL INTERNALLY: EUR {pool.avoided_penalty_eur:,.0f} "
                      f"avoidable across {len(pool.member_imos)} ships")
                hook = (f"about EUR {pool.avoided_penalty_eur:,.0f} of it looks "
                        f"avoidable just by pooling your own ships together")
            if pool.uncovered_penalty_eur > 0:
                print(f"  >> NEEDS EXTERNAL PARTNER: EUR "
                      f"{pool.uncovered_penalty_eur:,.0f} "
                      f"({len(pool.uncovered)} ships)")
        print(f"\n  PDF:  python scripts/make_reports.py --company "
              f"\"{t['company'][:26]}\" --pdf")
        print("  MESSAGE:")
        print(_draft(t, hook))
        rows.append({"company": t["company"],
                     "imos": ",".join(r.imo for r in fleet[:12]),
                     "contact_name": "", "contact_role": "", "stage": "target",
                     "last_action": "", "next_action": str(date.today()),
                     "notes": f"ETS ~EUR {int(t['est_eua_cost_eur']):,}/yr"})
    save_pipeline(rows)
    print(f"\n{len(queue)} companies added to outreach/pipeline.csv as 'target'.")
    print("Find the contacts on LinkedIn, then log each send:")
    print('  python scripts/daily.py --log sent --company "<name>"\n')


def surplus_view(args):
    """The scarce side of the pooling market: ships likely to hold a FuelEU
    surplus. Deficit tonnage is everywhere; surplus is what you must recruit,
    and whoever holds the surplus book sets the price."""
    from ghgcore.thetis import load_thetis_cached, record_to_activity
    from ghgcore.fueleu import compute_fueleu

    print("\nScanning the register for surplus holders ...")
    path = sorted(glob.glob(os.path.join(ROOT, "fixtures", "thetis_mrv_*.xlsx")))[-1]
    recs = load_thetis_cached(path)
    by_company = {}
    for r in recs.values():
        if r.ship_type is None or not r.company:
            continue
        feu = compute_fueleu(record_to_activity(
            r, year=r.reporting_period or 2025, dwt=1.0))
        cb = feu.compliance_balance_tco2e
        if cb <= 0:
            continue
        c = by_company.setdefault(r.company, {"t": 0.0, "n": 0, "types": set()})
        c["t"] += cb
        c["n"] += 1
        c["types"].add(r.ship_type_raw)
    ranked = sorted(by_company.items(), key=lambda kv: -kv[1]["t"])[:args.surplus]

    print("\n" + "=" * 68)
    print("  FUELEU SURPLUS HOLDERS - the side you must recruit")
    print("=" * 68)
    if not ranked:
        print("  None found. With the public-data fuel assumption only LNG-fuelled")
        print("  tonnage clears the target, so surplus will be thin until owners")
        print("  send real bunker data (biofuel blends are invisible to us).")
        return
    total = 0.0
    for name, c in ranked:
        total += c["t"]
        print(f"\n  {name[:58]}")
        print(f"    {c['n']} ship(s), ~{c['t']:,.0f} t CO2e surplus "
              f"- {', '.join(sorted(c['types']))[:46]}")
    print(f"\n  Total listed surplus: ~{total:,.0f} t CO2e")
    print("\n  WHY THIS MATTERS")
    for line in _wrap(
            "A deficit ship pays EUR 2,400 per tonne of VLSFO-equivalent, or "
            "pools with a surplus holder for a negotiated fraction of that. "
            "Deficit tonnage is abundant; surplus is scarce. Sign the holders "
            "above to a non-binding 'we will consider pooling' note and you "
            "control the supply side before 30 April.", 62):
        print(f"    {line}")
    print("\n  CAVEAT")
    for line in _wrap(
            "These are estimates on an assumed fuel: LNG for LNG carriers, HFO "
            "for everything else. Real biofuel or methanol burners are "
            "invisible here and are also surplus holders - ask every prospect "
            "what they bunkered.", 62):
        print(f"    {line}")
    print()


def _draft(t, hook):
    return f"""
    Subject: {t['company'][:32]} - your 2026 FuelEU position, before the pooling window

    Hi [Name],

    I pulled your {t['fleet_size']} ships from the public EU-MRV register and ran
    the FuelEU numbers on them. On 2025 verified data, {hook}.

    The 2026 compliance year closes on 31 December, and a pool has to be
    registered by 30 April 2027 - after that the only option left is the
    EUR 2,400/t penalty. One-page breakdown of every ship attached. It is built
    entirely from figures your own verifier filed, so treat it as an estimate
    with honest labels.

    If it is roughly right, the last 20% takes one noon-report CSV. Worth 20
    minutes before the window closes?

    [Your name] - building CarbonKeel
"""


def log_action(args):
    rows = load_pipeline()
    hit = None
    for r in rows:
        if args.company.lower() in r["company"].lower():
            hit = r
            break
    if hit is None:
        hit = {"company": args.company, "imos": "", "contact_name": "",
               "contact_role": "", "stage": "target", "last_action": "",
               "next_action": "", "notes": ""}
        rows.append(hit)
    stage = args.stage or {"sent": "sent", "followup": "followed_up",
                           "reply": "replied", "call": "call_booked",
                           "demo": "demo_done", "partner": "partner",
                           "paid": "paid", "dead": "dead"}.get(args.log, args.log)
    if stage not in STAGES:
        sys.exit(f"stage must be one of {STAGES}")
    hit["stage"] = stage
    hit["last_action"] = str(date.today())
    if args.contact:
        hit["contact_name"] = args.contact
    if args.note:
        hit["notes"] = (hit.get("notes", "") + " | " + args.note).strip(" |")
    save_pipeline(rows)
    print(f"{hit['company']} -> {stage}  ({date.today()})")


def main():
    p = argparse.ArgumentParser(description="CarbonKeel daily console")
    p.add_argument("--targets", type=int, metavar="N",
                   help="pull the next N targets with their numbers")
    p.add_argument("--week", action="store_true", help="show the week plan")
    p.add_argument("--surplus", type=int, metavar="N", nargs="?", const=15,
                   help="rank the N biggest FuelEU surplus holders to recruit")
    p.add_argument("--log", help="sent|followup|reply|call|demo|partner|paid|dead")
    p.add_argument("--company")
    p.add_argument("--stage")
    p.add_argument("--contact")
    p.add_argument("--note")
    a = p.parse_args()
    if a.log:
        if not a.company:
            sys.exit("--log needs --company")
        log_action(a)
    elif a.targets:
        targets_view(a)
    elif a.surplus:
        surplus_view(a)
    elif a.week:
        week_view(a)
    else:
        today_view(a)


if __name__ == "__main__":
    main()
