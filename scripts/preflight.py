#!/usr/bin/env python3
"""Publish gate — one command that says whether it is safe to put this online.

    python scripts/preflight.py            full check (runs both test suites)
    python scripts/preflight.py --quick    skip the test suites, check the rest

Three outcomes per line:
    PASS     fine
    FAIL     do not publish until this is fixed — exit code 1
    TODO     only the founder can resolve this (a name, a decision) — also
             blocks publishing, but it is not a bug

Everything here is something that went wrong, or nearly did, during the
build: a syntax error that killed every button, secrets one `git add` away
from a public repo, a rate limiter that would have locked out all visitors on
a shared proxy address.
"""
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

results = []          # (status, area, message)


def add(status, area, msg):
    results.append((status, area, msg))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def exists(path):
    return os.path.exists(os.path.join(ROOT, path))


def run(cmd, timeout=900):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, cwd=ROOT)


# --------------------------------------------------------------- tests ----
def gate_tests():
    r = run([sys.executable, "tests/test_engines.py"])
    last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    if r.returncode == 0 and "All checks passed" in last:
        add("PASS", "tests", f"engine suite - {last}")
    else:
        add("FAIL", "tests", f"engine suite failed: {last}")
    r = run([sys.executable, "tests/test_smoke.py"])
    lines = r.stdout.strip().splitlines()
    summary = next((l for l in reversed(lines) if "passed" in l), "(no summary)")
    if r.returncode == 0:
        add("PASS", "tests", f"smoke suite - {summary}")
    else:
        failed = next((l for l in lines if l.startswith("FAILED")), summary)
        add("FAIL", "tests", f"smoke suite failed - {failed}")


# ----------------------------------------------------- founder blanks -----
def gate_placeholders():
    """Anything still in [[DOUBLE BRACKETS]] is a blank only the founder can fill."""
    pat = re.compile(r"\[\[[^\]]+\]\]")
    found = {}
    for path in ["site/index.html", "site/privacy.html", "api/static/index.html",
                 "docs/DATA_AND_PRIVACY.md", "docs/CALCULATION_NOTES.md"]:
        if exists(path):
            hits = sorted(set(pat.findall(read(path))))
            if hits:
                found[path] = hits
    if not found:
        add("PASS", "founder", "no unfilled [[placeholders]] in any public page")
    else:
        for path, hits in found.items():
            add("TODO", "founder", f"{path}: fill in {', '.join(hits)}")


# --------------------------------------------------------------- secrets --
SECRET_FILES = ["data/access_keys.txt", "data/privacy/requests.jsonl",
                "outreach/pipeline.csv"]


def gate_secrets():
    gi = read(".gitignore") if exists(".gitignore") else ""
    for f in SECRET_FILES:
        if f in gi:
            add("PASS", "secrets", f"{f} is gitignored")
        else:
            add("FAIL", "secrets", f"{f} is NOT in .gitignore")
    if exists(".git"):
        r = run(["git", "ls-files"])
        tracked = set(r.stdout.split())
        leaked = [f for f in SECRET_FILES if f in tracked]
        if leaked:
            add("FAIL", "secrets", f"already tracked by git: {', '.join(leaked)} "
                                   "(git rm --cached them before pushing)")
        else:
            add("PASS", "secrets", "no secret file is tracked by git")
        personal = [f for f in tracked
                    if re.search(r"(^|[/_\-. ])(cv|resume|curriculum|passport)([_\-. ]|$)",
                                 f, re.I)]
        if personal:
            add("FAIL", "secrets", "personal document(s) tracked by git: "
                                   + ", ".join(personal[:3]))
        else:
            add("PASS", "secrets", "no CV / resume / passport file is tracked")
        # a key pasted into any tracked text file
        keyhits = []
        for f in tracked:
            if f.endswith((".py", ".md", ".yaml", ".yml", ".html", ".txt", ".json")):
                try:
                    if re.search(r"\bck-[0-9a-f]{16}\b", read(f)):
                        keyhits.append(f)
                except (OSError, UnicodeDecodeError):
                    pass
        if keyhits:
            add("FAIL", "secrets", f"an access key appears in tracked file(s): {', '.join(keyhits)}")
        else:
            add("PASS", "secrets", "no access key written into any tracked file")
    else:
        add("TODO", "secrets", "no git repository yet - run `git init` first")


# ------------------------------------------------------------ deploy ------
def gate_deploy():
    for f in ["requirements.txt", "render.yaml", "Procfile", "site/index.html",
              "site/privacy.html", "api/main.py"]:
        add("PASS" if exists(f) else "FAIL", "deploy", f"{f} present")
    req = read("requirements.txt")
    unpinned = [l for l in req.splitlines()
                if l.strip() and not l.startswith("#") and "==" not in l]
    add("FAIL" if unpinned else "PASS", "deploy",
        "all dependencies pinned" if not unpinned else f"unpinned: {unpinned}")
    ry = read("render.yaml")
    for var in ["CARBONKEEL_PROXY_HOPS", "CARBONKEEL_ACCESS_KEYS"]:
        add("PASS" if var in ry else "FAIL", "deploy", f"render.yaml sets {var}")
    add("FAIL" if re.search(r"\bck-[0-9a-f]{8,}", ry) else "PASS", "deploy",
        "render.yaml contains no literal key")
    import glob
    xlsx = glob.glob(os.path.join(ROOT, "fixtures", "thetis_mrv_*.xlsx"))
    add("PASS" if xlsx else "FAIL", "deploy",
        f"register export present ({len(xlsx)} file(s))" if xlsx
        else "no fixtures/thetis_mrv_*.xlsx - the app would serve nothing")
    pkl = glob.glob(os.path.join(ROOT, "fixtures", "*.pkl"))
    add("PASS" if pkl else "TODO", "deploy",
        "register cache present (fast cold start)" if pkl
        else "no .pkl cache - first request will take ~20s; run the app once to build it")


def gate_links():
    """The static HTML must never hard-wire a local address."""
    for f in ["site/index.html", "site/privacy.html"]:
        html = read(f)
        # strip the script (it legitimately names localhost for the dev rewrite)
        body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
        bad = re.findall(r'(?:href|action)="(?:https?://)?(?:localhost|127\.0\.0\.1)[^"]*"', body)
        add("FAIL" if bad else "PASS", "links",
            f"{f}: no hard-wired localhost link" if not bad else f"{f}: {bad[:2]}")
    html = read("site/index.html")
    n = html.count("https://app.carbonkeel.com")
    add("PASS" if n >= 3 else "FAIL", "links",
        f"landing points at app.carbonkeel.com ({n} places)")


def gate_size():
    total = 0
    skip = {".git", "__pycache__", ".arena", "node_modules"}
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    mb = total / 1048576
    add("PASS" if mb < 100 else "FAIL", "deploy",
        f"repository payload {mb:.0f} MB (GitHub hard limit is 100 MB per file, "
        "soft 1 GB per repo)")


# -------------------------------------------------------------- report ----
def main():
    quick = "--quick" in sys.argv
    if not quick:
        gate_tests()
    gate_placeholders()
    gate_secrets()
    gate_deploy()
    gate_links()
    gate_size()

    order = {"FAIL": 0, "TODO": 1, "PASS": 2}
    print("\nPUBLISH GATE")
    print("=" * 74)
    area = None
    for st, ar, msg in sorted(results, key=lambda r: (order[r[0]], r[1])):
        if st != "PASS" or "-v" in sys.argv:
            print(f"  {st:<5} [{ar}] {msg}")
    passed = sum(1 for r in results if r[0] == "PASS")
    fails = [r for r in results if r[0] == "FAIL"]
    todos = [r for r in results if r[0] == "TODO"]
    print("-" * 74)
    print(f"  {passed} passed   {len(fails)} failed   {len(todos)} waiting on you")
    if fails:
        print("\n  NOT SAFE TO PUBLISH - fix the FAIL lines above.")
        sys.exit(1)
    if todos:
        print("\n  Code is ready. Complete the TODO lines (they are yours), then re-run.")
        sys.exit(2)
    print("\n  GREEN - safe to publish.")


if __name__ == "__main__":
    main()
