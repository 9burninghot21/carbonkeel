"""Wording, style and data-source guards.

The engine tests prove the numbers and the smoke tests prove the pages work.
This suite protects what a reader actually sees, and the things that went
wrong on 5 Oct 2026: a placeholder ("year-Y") shown to users, an invalid font
declaration that shrank every button, an absolute accuracy claim, a wrong
Article 21 paragraph, and file ordering that would pick the wrong data version.

Run:  python tests/test_style.py        (starts its own server on :8113)
"""
import html as htmllib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

PASS, FAIL = [], []
PORT = 8113


def ok(name):
    PASS.append(name)
    print(f"  [ok]   {name}")


def bad(name, detail=""):
    FAIL.append(name)
    print(f"  [FAIL] {name}{(' - ' + str(detail)[:160]) if detail else ''}")


def check(cond, name, detail=""):
    ok(name) if cond else bad(name, detail)


def read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read().replace("\r\n", "\n")


# ---- text extraction ------------------------------------------------------
def visible_markup_text(src):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", src, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return htmllib.unescape(s)


def script_prose(src):
    """Sentences the scripts build into the page."""
    out = []
    for sc in re.findall(r"<script>(.*?)</script>", src, re.S):
        for m in re.finditer(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|`((?:[^`\\]|\\.)*)`", sc):
            t = m.group(1) or m.group(2) or m.group(3) or ""
            t = re.sub(r"\$\{[^}]*\}", " ", t)
            t = htmllib.unescape(re.sub(r"<[^>]+>", " ", t))
            if t.count(" ") >= 3 and not re.search(r"[;{}]|=>|\bconst\b|\bfunction\b|\blet\b", t):
                out.append(t)
    return "\n".join(out)


PAGES = [("site/index.html", "landing"), ("api/static/index.html", "app"), ("site/privacy.html", "privacy")]


def check_pages():
    for rel, label in PAGES:
        src = read(rel)
        # 1. invalid shorthand: 'inherit' is not allowed as a family inside font:, so the
        #    browser drops the whole declaration and the text falls back to 13px
        bad_font = re.findall(r"font:\s*\d{3}\s+[\d.]+px\s*/\s*[\d.]+\s+inherit|font:\s*[\d.]+px\s*/\s*[\d.]+\s+inherit", src)
        check(not bad_font, f"{label}: no invalid font shorthand", bad_font[:1])

        text = visible_markup_text(src)
        prose = script_prose(src)
        both = text + "\n" + prose
        rules = [
            (r"\bregistry\b", "says 'registry' (it is a register, or the public record)"),
            (r"\bArt\. ?21", "writes 'Art. 21' (write Article 21)"),
            (r"EU-MRV", "writes 'EU-MRV' (write EU MRV)"),
            (r"→ ?PDF|\U0001F4A1", "uses an arrow or emoji where words are better"),
            (r"\s~\s?[€$\d]", "uses '~' for 'about'"),
            (r"replies same day", "missing 'the' in 'the same day'"),
            (r"Request failed:", "shows a raw error to the user"),
            (r"\bvs\.? ", "uses 'vs' in a sentence (write 'against')"),
        ]
        for pat, why in rules:
            m = re.search(pat, both)
            check(not m, f"{label}: no {why}", m.group(0) if m else "")

        # house style: 'ship', not 'vessel', in text a person reads
        m = re.search(r"\bvessels?\b", text, re.I)
        check(not m, f"{label}: markup says 'ship', not 'vessel'", text[max(0, m.start() - 30):m.end() + 20] if m else "")
        # typographic apostrophes in visible markup text
        m = re.search(r"[A-Za-z]'[A-Za-z]", text)
        check(not m, f"{label}: visible text uses typographic apostrophes", text[max(0, m.start() - 20):m.end() + 15] if m else "")

    # attribution that EMSA's copyright notice and CC BY-style reuse call for
    for rel, label in [("site/index.html", "landing"), ("api/static/index.html", "app")]:
        t = re.sub(r"\s+", " ", visible_markup_text(read(rel)))
        check("EMSA" in t and "not endorsed" in t, f"{label}: acknowledges EMSA and says it is not endorsed")


# ---- the server's own wording --------------------------------------------
def serve():
    import uvicorn
    from api.main import app
    uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")).run()


def http(path, want_json=True):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=120) as r:
            body = r.read().decode("utf-8")
            return r.status, (json.loads(body) if want_json else body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, body


def check_server_text():
    code, d = http("/api/lookup/0000000")
    msg = d.get("detail", "")
    check(code == 404 and "was not found in the public EU MRV register" in msg, "unknown IMO: plain message", msg)

    code, d = http("/api/search?q=VIKING%20R&limit=20")
    imo = next((x["imo"] for x in d.get("results", []) if not x["supported"]), None)
    if imo:
        code, d = http(f"/api/lookup/{imo}")
        msg = d.get("detail", "")
        check(code == 422 and "not yet supported" in msg and "'" not in msg and "Ship type “" in msg,
              "unsupported ship type: readable message, no Python quoting", msg)
    else:
        bad("found an unsupported ship type to test")

    year = 2026
    code, d = http(f"/api/calendar?year={year}")
    items = d["deadlines"]
    check(not any("year-Y" in x["what"] or "year Y" in x["what"] for x in items),
          "calendar: no 'year Y' placeholder reaches the user")
    check(not any("(compliance year" in x["what"] for x in items), "calendar: no repeated '(compliance year)' suffix")
    check(all(str(year) in x["what"] for x in items), "calendar: every item names its year")
    check(all("Art." not in x["basis"] and "Reg. (" not in x["basis"] for x in items),
          "calendar: legal bases are written out (Article, Regulation)")

    code, d = http("/api/lookup/9464663?dwt=50000")
    sc = d["scorecard"]
    prose = " ".join(sc["actions"] + [sc["future_readiness"]] + sc["fueleu"]["notes"] + [sc["fueleu"]["surplus_value_note"]]
                     + sc["ets"]["notes"] + sc["nzf"]["notes"] + sc["ukets"]["notes"])
    for pat, why in [(r"bank-borrow", "'bank-borrow'"), (r"\bSoC\b", "undefined 'SoC'"), (r"hedge", "trading advice ('hedge')"),
                     (r"~", "'~' for about"), (r"\bvessel", "'vessel'"), (r"uk_share", "an internal field name"),
                     (r"prototype", "'prototype'"), (r"\bT1\b|\bT2\b", "unexplained T1/T2")]:
        m = re.search(pat, prose)
        check(not m, f"engine text: no {why}", m.group(0) if m else "")
    check(any("Three years in a row at D" in a or "A rating of E requires" in a for a in sc["actions"]),
          "CII action states the rule once, without contradicting itself")

    code, m = http("/api/method", want_json=False)
    check("(144 checks)" in m and "96 checks" not in m, "method page quotes the real test count")
    check("exactly on spot" not in m and "67.5%" in m, "method page states the measured match rate, not an absolute")
    check("Art. 21(6)" not in m, "method page: no wrong Article 21(6)")
    code, pv = http("/api/privacy", want_json=False)
    check("21(6)" not in pv and "21(3)" in pv, "data page cites Article 21(3), not 21(6)")
    check("EEA port" not in pv, "data page does not misstate the scope as 'EEA port'")

    code, rep = http("/report?imos=9464663", want_json=False)
    check(code == 200 and "generated for outreach" not in rep, "printable report: no internal 'outreach' wording")
    check("spot-checks reproduce" not in rep and "two ships in three" in rep, "printable report: measured accuracy, not an absolute")
    check("not endorsed by EMSA" in rep and "Article 21" in rep, "printable report: attributes EMSA and disclaims endorsement")


# ---- data source tooling ---------------------------------------------------
def check_data_tools():
    from ghgcore.exports import latest, ordered
    d = tempfile.mkdtemp()
    for n in ["thetis_mrv_2025_v6.xlsx", "thetis_mrv_2025_v60.xlsx", "thetis_mrv_2025_v100.xlsx",
              "thetis_mrv_2024_v246.xlsx", "thetis_mrv_2025_v6.xlsx.pkl", "notes.xlsx"]:
        open(os.path.join(d, n), "w").close()
    names = [os.path.basename(p) for p in ordered(d)]
    check(os.path.basename(latest(d)) == "thetis_mrv_2025_v100.xlsx", "newest export is chosen by (year, version), not by text", names)
    check(sorted(os.listdir(d))[-1] != "thetis_mrv_2025_v100.xlsx", "(control) plain text sorting would have chosen wrongly")

    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "fetch_thetis.py"), "--download", "2025"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    check(r.returncode == 1 and "--yes" in r.stdout, "fetch tool refuses to download without --yes")

    ds = read("docs/DATA_SOURCES.md")
    check("21(3)" in ds and "mrv.emsa.europa.eu" in ds and "not endorsed" in ds,
          "DATA_SOURCES.md records the legal basis, the source and the attribution line")
    for rel in ["docs/DATA_AND_PRIVACY.md", "docs/LEGAL_REVIEW.md"]:
        t = read(rel)
        check("Article 21(6) alternative" not in t and "Art. 21(6)" not in t, f"{rel}: no wrong Article 21(6) citation")


def main():
    print("Pages: fonts, wording, attribution")
    check_pages()
    print("\nData tooling and sources")
    check_data_tools()
    print("\nServer wording")
    threading.Thread(target=serve, daemon=True).start()
    for _ in range(90):
        try:
            if http("/healthz")[0] == 200:
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        bad("server did not start on :%d" % PORT)
    check_server_text()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED: " + "; ".join(FAIL))
        sys.exit(1)
    print("Style suite green.")


if __name__ == "__main__":
    main()
