#!/usr/bin/env python3
"""Batch outreach-report factory — zero-cost lead magnets.

For each target company (from outreach/targets_2025.csv), renders its full
fleet health-check to outreach/reports/<company>.html and, with --pdf,
converts to real PDF using the locally installed Edge browser in headless
mode (no paid tools, no cloud).

Usage:
    python scripts/make_reports.py --top 10 --pdf
    python scripts/make_reports.py --company "OLDENDORFF" --pdf
"""
import argparse, csv, glob, io, os, re, subprocess, sys, warnings
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def company_fleets(xlsx: str) -> dict[str, list[str]]:
    """One scan of the export -> {company name: [imos]}."""
    import openpyxl
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    fleets = defaultdict(list)
    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0] is None or not row[9]:
            continue
        fleets[str(row[9]).strip()].append(str(row[0]).split(".")[0])
    wb.close()
    return fleets


def to_pdf(html_path: str) -> bool:
    edge = next((p for p in EDGE_PATHS if os.path.exists(p)), None)
    if edge is None:
        return False
    pdf_path = html_path[:-5] + ".pdf"
    subprocess.run([edge, "--headless=new", "--disable-gpu",
                    f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer",
                    "file:///" + html_path.replace("\\", "/")],
                   capture_output=True, timeout=120)
    return os.path.exists(pdf_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10, help="top N targets by exposure")
    ap.add_argument("--company", help="substring match on company name instead")
    ap.add_argument("--pdf", action="store_true", help="also render PDF via Edge headless")
    args = ap.parse_args()

    from api.report import fleet_report_html
    from ghgcore.thetis import load_thetis_xlsx

    xlsx = sorted(glob.glob(os.path.join(ROOT, "fixtures", "thetis_mrv_*.xlsx")))[-1]
    print(f"Loading {os.path.basename(xlsx)} ...")
    records = load_thetis_xlsx(xlsx)
    fleets = company_fleets(xlsx)

    targets_csv = os.path.join(ROOT, "outreach", "targets_2025.csv")
    with open(targets_csv, newline="", encoding="utf-8-sig") as f:
        targets = list(csv.DictReader(f))

    if args.company:
        chosen = [t for t in targets if args.company.upper() in t["company"].upper()]
        if not chosen:   # allow companies outside the ICP filter too
            chosen = [{"company": c} for c in fleets if args.company.upper() in c.upper()]
    else:
        chosen = targets[:args.top]

    outdir = os.path.join(ROOT, "outreach", "reports")
    os.makedirs(outdir, exist_ok=True)
    for t in chosen:
        name = t["company"]
        imos = fleets.get(name, [])
        if not imos:
            print(f"  !! no vessels found for {name!r}")
            continue
        html = fleet_report_html(records, imos)
        path = os.path.join(outdir, slug(name) + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        line = f"  {name[:50]:50} {len(imos):>3} ships -> {os.path.basename(path)}"
        if args.pdf:
            line += "  [+PDF]" if to_pdf(path) else "  [PDF FAILED — Edge not found]"
        print(line)
    print(f"\nReports in {outdir}")


if __name__ == "__main__":
    main()
