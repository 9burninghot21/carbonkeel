import os, sys
SP = os.path.dirname(__file__)
pass  # needs: pip install playwright (uses the installed Microsoft Edge; no browser download)
from playwright.sync_api import sync_playwright

OUT = os.path.join(sys.argv[1], "docs", "walkthrough", "img")
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": 1360, "height": 860}, device_scale_factor=1.5)
    pg = ctx.new_page()
    pg.goto("http://127.0.0.1:8000/home")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_timeout(2000)
    top = pg.evaluate("document.getElementById('how').getBoundingClientRect().top + window.scrollY")
    dist = pg.evaluate("document.getElementById('how').offsetHeight - document.getElementById('how').firstElementChild.offsetHeight")
    for i, frac in enumerate([0.02, 0.36, 0.68, 0.99], 1):
        pg.evaluate(f"window.scrollTo(0, {top} - 64 + {dist} * {frac})")
        pg.wait_for_timeout(1200)
        pg.locator("#how .stage").screenshot(path=os.path.join(OUT, f"L04-voyage-{i}.jpg"), type="jpeg", quality=86)
        print("voyage", i)
    b.close()
