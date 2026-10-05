"""Capture the walkthrough screenshots with the system Edge (no browser download)."""
import os, shutil, sys, time

SP = os.path.dirname(__file__)
pass  # needs: pip install playwright (uses the installed Microsoft Edge; no browser download)
from playwright.sync_api import sync_playwright

ROOT = sys.argv[1]
OUT = os.path.join(ROOT, "docs", "walkthrough", "img")
os.makedirs(OUT, exist_ok=True)
BASE = "http://127.0.0.1:8000"
KEYS = os.path.join(ROOT, "data", "access_keys.txt")
TEMP_KEY = "ck-walkthrough-temp-000000"

# a temporary key so the locked CII calculator can be shown; restored afterwards
backup = open(KEYS, "rb").read() if os.path.exists(KEYS) else None
with open(KEYS, "ab") as f:
    f.write(("\n" + TEMP_KEY + "  # temporary, removed after capture\n").encode())

NOSMOOTH = "html{scroll-behavior:auto!important}"
done = []


def shot(page, name, full=False):
    path = os.path.join(OUT, name + ".jpg")
    page.screenshot(path=path, type="jpeg", quality=84, full_page=full)
    done.append(name)
    print("  ", name)


def scroll_to(page, selector, offset=80):
    page.evaluate(f"""() => {{ const e = document.querySelector('{selector}');
        window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - {offset}); }}""")
    page.wait_for_timeout(500)


try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # ---------------------------------------------------------- landing, desktop
        ctx = browser.new_context(viewport={"width": 1360, "height": 860}, device_scale_factor=1.25)
        page = ctx.new_page()
        page.goto(BASE + "/home")
        page.add_style_tag(content=NOSMOOTH)
        page.wait_for_timeout(2500)
        shot(page, "L01-hero")

        # chat widget
        page.click("#ckFab")
        page.wait_for_timeout(500)
        shot(page, "L13-chat")
        page.click("#ckFab")

        page.evaluate("window.__ckRevealAll && window.__ckRevealAll()")
        scroll_to(page, ".stats", 70)
        page.wait_for_timeout(2200)
        shot(page, "L02-numbers")
        scroll_to(page, ".intro", 70)
        page.wait_for_timeout(1200)
        shot(page, "L03-intro")

        top = page.evaluate("document.getElementById('how').getBoundingClientRect().top + window.scrollY")
        dist = page.evaluate("document.getElementById('how').offsetHeight - document.getElementById('how').firstElementChild.offsetHeight")
        for i, frac in enumerate([0.02, 0.36, 0.68, 0.99], 1):
            page.evaluate(f"window.scrollTo(0, {top} - 64 + {dist} * {frac})")
            page.wait_for_timeout(1100)
            shot(page, f"L04-voyage-{i}")

        for sel, name, wait in [("#services", "L05-services", 2400), ("#best", "L06-strengths", 1600),
                                ("#cost", "L07-result", 2800), ("#trust", "L08-maths", 1200),
                                ("#talk", "L09-talk", 1200)]:
            scroll_to(page, sel, 70)
            page.evaluate("window.__ckRevealAll && window.__ckRevealAll()")
            page.wait_for_timeout(wait)
            shot(page, name)
        scroll_to(page, "#finale", 0)
        page.wait_for_timeout(1500)
        shot(page, "L10-finale")
        ctx.close()

        # ---------------------------------------------------------- landing, phone
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(BASE + "/home")
        page.add_style_tag(content=NOSMOOTH)
        page.wait_for_timeout(2500)
        shot(page, "M01-landing-phone")
        top = page.evaluate("document.getElementById('how').getBoundingClientRect().top + window.scrollY")
        dist = page.evaluate("document.getElementById('how').offsetHeight - document.getElementById('how').firstElementChild.offsetHeight")
        page.evaluate(f"window.scrollTo(0, {top} - 64 + {dist} * 0.4)")
        page.wait_for_timeout(1200)
        shot(page, "M02-voyage-phone")
        ctx.close()

        # ---------------------------------------------------------------- app, desktop
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1.25)
        page = ctx.new_page()
        page.goto(BASE + "/")
        page.add_style_tag(content=NOSMOOTH)
        page.wait_for_timeout(1500)
        shot(page, "A01-home")

        page.evaluate("pick('9464663')")
        page.wait_for_timeout(2800)
        scroll_to(page, "#out .card", 20)
        shot(page, "A02-owner-view")

        # value chip applied
        page.evaluate("applyTeaser()")
        page.wait_for_timeout(2500)
        scroll_to(page, "#out .card", 20)
        shot(page, "A03-value-lever")

        # add capacity -> CII + fleet context
        page.evaluate("document.getElementById('dwtIn') && (document.getElementById('dwtIn').value='50000')")
        page.evaluate("addDwt()")
        page.wait_for_timeout(3000)
        scroll_to(page, ".ciibar", 140)
        shot(page, "A04-cii-and-fleet")
        scroll_to(page, "#fleetCtx", 60)
        shot(page, "A05-fleet-context")

        page.evaluate("setView('tech')")
        page.wait_for_timeout(1500)
        scroll_to(page, "#out .card", 20)
        shot(page, "A06-technical-view")
        page.evaluate("setView('verifier')")
        page.wait_for_timeout(1000)
        scroll_to(page, "#out .card", 20)
        shot(page, "A07-verifier-view")

        # EEXI
        page.evaluate("showTab('eexi')")
        page.evaluate("document.getElementById('eq').value='9464663'; eexiImo='9464663'; document.getElementById('edwt').value='50000'; runEexi()")
        page.wait_for_timeout(1800)
        scroll_to(page, "#nav-eexi", 10)
        page.evaluate("window.scrollTo(0,0)")
        shot(page, "A08-eexi-registry")
        page.evaluate("fillExample()")
        page.wait_for_timeout(2200)
        scroll_to(page, "#eout", 120)
        shot(page, "A09-eexi-custom")

        # CII locked, then unlocked
        page.evaluate("localStorage.removeItem('ck_key'); showTab('cii'); lockCii && lockCii()")
        page.wait_for_timeout(700)
        page.evaluate("window.scrollTo(0,0)")
        shot(page, "A10-cii-locked")
        page.evaluate(f"document.getElementById('ciiKey').value='{TEMP_KEY}'; unlockCii()")
        page.wait_for_timeout(1200)
        page.evaluate("fillCiiExample()")
        page.wait_for_timeout(2200)
        scroll_to(page, "#ciiOut", 20)
        shot(page, "A11-cii-result")
        page.evaluate("localStorage.removeItem('ck_key')")

        # fleet
        page.evaluate("showTab('fleet'); document.getElementById('fleetImos').value='9464663, 9463633, 9448047, 9334856'; fleetDash()")
        page.wait_for_timeout(3500)
        scroll_to(page, "#fout", 10)
        shot(page, "A12-fleet")

        # calendar
        page.evaluate("showTab('cal')")
        page.wait_for_timeout(1800)
        scroll_to(page, "#calout", 10)
        shot(page, "A13-calendar")

        # method
        page.evaluate("showTab('method')")
        page.wait_for_timeout(1800)
        page.evaluate("window.scrollTo(0,0)")
        shot(page, "A14-method")

        # your data
        page.evaluate("showTab('privacy')")
        page.wait_for_timeout(1800)
        page.evaluate("window.scrollTo(0,0)")
        shot(page, "A15-your-data")
        ctx.close()

        # ---------------------------------------------------------------- app, phone
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(BASE + "/")
        page.add_style_tag(content=NOSMOOTH)
        page.wait_for_timeout(1500)
        page.evaluate("pick('9464663')")
        page.wait_for_timeout(3000)
        scroll_to(page, ".bill", 90)
        shot(page, "M03-app-phone")
        ctx.close()
        browser.close()
finally:
    if backup is None:
        os.remove(KEYS)
    else:
        open(KEYS, "wb").write(backup)
    print("key file restored; temp key lines:", (open(KEYS, "rb").read().count(TEMP_KEY.encode()) if os.path.exists(KEYS) else 0))

print(len(done), "screenshots in", OUT)
