"""Build the shareable walkthrough: one self-contained HTML file (images embedded)
and a PDF made from it with the system Edge."""
import base64, html, os, sys

SP = os.path.dirname(__file__)
pass  # needs: pip install playwright (uses the installed Microsoft Edge; no browser download)

ROOT = sys.argv[1]
IMG = os.path.join(ROOT, "docs", "walkthrough", "img")
OUT_HTML = os.path.join(ROOT, "docs", "walkthrough", "CarbonKeel-walkthrough.html")
OUT_PDF = os.path.join(ROOT, "docs", "walkthrough", "CarbonKeel-walkthrough.pdf")


def img(name):
    data = open(os.path.join(IMG, name + ".jpg"), "rb").read()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


def fig(name, caption, cls=""):
    return f'<figure class="{cls}"><img src="{img(name)}" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure>'


def step(n, title, what, why, figs):
    return f"""<section class="step">
  <div class="head"><span class="n">{n}</span><h3>{title}</h3></div>
  <p><b>What you see.</b> {what}</p>
  <p><b>Why it is there.</b> {why}</p>
  {figs}
</section>"""


CSS = """
:root{--ink:#0b2545;--muted:#46607e;--blue:#0a5aa0;--line:rgba(11,37,69,.14);--soft:#f1f6fb}
*{box-sizing:border-box}
body{font-family:"Segoe UI",system-ui,-apple-system,sans-serif;color:var(--ink);line-height:1.55;margin:0;background:#fff}
.wrap{max-width:900px;margin:0 auto;padding:0 28px 60px}
header.cover{background:linear-gradient(135deg,#0b2545,#0a5aa0 60%,#7c3aed);color:#fff;padding:54px 0 46px}
header.cover .wrap{padding-bottom:0}
header.cover h1{font-size:40px;margin:0 0 8px;letter-spacing:-.02em;line-height:1.1}
header.cover p{margin:6px 0 0;font-size:18px;color:#dbe9fb;max-width:36em}
.badge{display:inline-block;margin-top:18px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:5px 14px;font-size:13.5px}
h2{font-size:27px;margin:46px 0 6px;letter-spacing:-.01em;border-top:3px solid var(--blue);padding-top:14px}
h2 small{display:block;font-size:14px;font-weight:500;color:var(--muted);margin-top:4px}
h3{font-size:20px;margin:0}
p{margin:8px 0}
.lead{font-size:18px;color:var(--muted)}
.box{background:var(--soft);border-radius:14px;padding:18px 22px;margin:18px 0}
.box h4{margin:0 0 6px;font-size:15px;text-transform:uppercase;letter-spacing:.08em;color:var(--blue)}
.box ul{margin:6px 0 0;padding-left:20px}
.box li{margin:4px 0}
.map{display:grid;grid-template-columns:1fr 60px 1.4fr;gap:10px;align-items:center;margin:20px 0}
.node{border:2px solid var(--blue);border-radius:14px;padding:14px 16px;background:#fff}
.node b{display:block;font-size:16px}
.node span{font-size:13.5px;color:var(--muted)}
.arrow{text-align:center;font-size:30px;color:var(--blue)}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.tabs i{font-style:normal;font-size:12.5px;font-weight:700;background:#e3eefa;color:var(--blue);padding:4px 10px;border-radius:12px}
.step{margin:30px 0;page-break-inside:avoid}
.step .head{display:flex;align-items:center;gap:12px;margin-bottom:6px}
.step .n{flex:none;width:34px;height:34px;border-radius:50%;background:var(--blue);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center}
figure{margin:14px 0;page-break-inside:avoid}
figure img{width:100%;height:auto;border:1px solid var(--line);border-radius:10px;display:block;box-shadow:0 4px 16px rgba(11,37,69,.12)}
figcaption{font-size:13.5px;color:var(--muted);margin-top:6px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid2 figure{margin:6px 0}
.stack figure{margin:12px 0}
.phones{display:flex;gap:14px;align-items:flex-start}
.phones figure{flex:1;max-width:30%}
.tour li{margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:14.5px;margin:10px 0}
td,th{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--soft)}
.gloss td:first-child{font-weight:700;white-space:nowrap;width:150px}
.note{font-size:13.5px;color:var(--muted)}
footer{border-top:1px solid var(--line);margin-top:40px;padding-top:14px;font-size:13px;color:var(--muted)}
@media print{
  .wrap{padding:0 6px 20px}
  h2{page-break-after:avoid}
  header.cover{padding:36px 0 30px}
}
"""

parts = []

parts.append(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CarbonKeel: a guided tour</title><style>{CSS}</style></head><body>
<header class="cover"><div class="wrap">
<h1>CarbonKeel: a guided tour</h1>
<p>What it is, how to move around it, and what every page is for. Written for someone who has not seen it before.</p>
<span class="badge">Preview build, shown from the founder&rsquo;s computer. Not public yet. Screenshots taken 5 October 2026.</span>
</div></header><div class="wrap">""")

# ------------------------------------------------------------------ in one minute
parts.append("""
<h2>The idea in one minute</h2>
<p class="lead">Shipping now pays real money for the carbon it emits, and the rules are spread across several regulations. CarbonKeel puts them in one place and answers one question: <b>what is carbon costing this ship, in euros?</b></p>
<div class="box"><h4>The short version</h4><ul>
<li><b>Who it is for:</b> companies that manage or own ships trading into Europe.</li>
<li><b>What you do:</b> type a ship&rsquo;s name or IMO number. No account, nothing to upload.</li>
<li><b>What you get:</b> the yearly carbon bill under the EU and UK emissions trading schemes, the FuelEU Maritime penalty, the ship&rsquo;s CII rating (an A to E efficiency grade), and what would move them.</li>
<li><b>Where the data comes from:</b> the emissions each ship has already reported, which the EU publishes by law. About 16,700 ships are loaded.</li>
<li><b>How honest it is about it:</b> everything rebuilt from public data is labelled <b>ESTIMATE</b>, and the page shows how well our rebuild matches the official figure.</li>
</ul></div>
""")

# --------------------------------------------------------------------- map
parts.append("""
<h2>How the pieces fit together<small>Two parts: a page that explains, and a tool that calculates.</small></h2>
<div class="map">
  <div class="node"><b>1. The opening page</b><span>Explains the idea, shows what comes back, and lets you search a ship straight away.</span></div>
  <div class="arrow">&rarr;</div>
  <div class="node"><b>2. The app</b><span>Where the calculation happens. Seven tabs along the top:</span>
    <div class="tabs"><i>Check a ship</i><i>EEXI</i><i>CII calculator</i><i>My fleet</i><i>Calendar</i><i>Method</i><i>Your data</i></div></div>
</div>
<div class="box"><h4>Things that appear on every page</h4><ul>
<li><b>The logo</b> always takes you back to the start.</li>
<li><b>&ldquo;Talk to us&rdquo;</b> (orange button, bottom right) opens a short form that hands your message to your email app. It is one person, not a chatbot.</li>
<li><b>The footer</b> says that figures are estimates, names the public source (EMSA) and links the privacy notice.</li>
</ul></div>
""")

# ------------------------------------------------------------------ part 1
parts.append('<h2>Part 1: The opening page<small>Scroll from top to bottom. The page tells a story: from sunrise at the harbour to night.</small></h2>')

parts.append(step(1, "The first screen",
    "A question, <i>&ldquo;What is carbon costing your ships?&rdquo;</i>, over a sunrise sea where ships sail past. Below it a search box and three ready-made examples.",
    "The visitor can get an answer in the first ten seconds without reading anything. The three examples (a bulk carrier, a cruise ship, an IMO number) are there for someone with no ship in mind. The moving ships and the CO&#8322; puffs are decoration that makes the subject memorable.",
    fig("L01-hero", "Type a ship name and press Check. The app opens with the answer already on screen.")))

parts.append(step(2, "The numbers behind it",
    "Four figures that count up as they scroll into view: the ships and companies in the public register, the CO&#8322; they report under the EU scheme in a year, and what that adds up to in euros.",
    "It shows the size of the subject and that real data is loaded. The euro figure uses an assumed allowance cost of &euro;70 a tonne and is marked ESTIMATE.",
    fig("L02-numbers", "Source line at the bottom: EMSA, under Article 21 of Regulation (EU) 2015/757.")))

parts.append(step(3, "What CarbonKeel is, in three steps",
    "&ldquo;One ship in. The whole carbon bill out.&rdquo; Then three cards: type a ship, see the bill, decide.",
    "A plain statement of the product for anyone who skipped the first screen.",
    fig("L03-intro", "Intro and the three-step summary.")))

parts.append(f"""<section class="step"><div class="head"><span class="n">4</span><h3>How we get to the number (the voyage)</h3></div>
<p><b>What you see.</b> A ship sails a route on a sea chart <i>as you scroll</i>. It stops at four numbered ports, and the text beside the chart changes at each stop.</p>
<p><b>Why it is there.</b> It answers &ldquo;where does this come from, and can I trust it?&rdquo; as a journey rather than a wall of text. The four stops are:</p>
<ol><li><b>Public register.</b> The EU publishes each ship&rsquo;s verified emissions by law.</li>
<li><b>The rulebooks.</b> EU ETS, UK ETS, FuelEU, IMO CII and EEXI, each coded from the regulation. No AI touches a number.</li>
<li><b>Verifier check.</b> We rebuild each ship&rsquo;s official CO&#8322; figure and compare. On a 400-ship sample we match it exactly for about two ships in three.</li>
<li><b>Your decision.</b> Euros, a rating and the lever that moves it.</li></ol>
<div class="stack">{fig("L04-voyage-1", "Stop 1: the public register.")}{fig("L04-voyage-2", "Stop 2: the rulebooks.")}{fig("L04-voyage-3", "Stop 3: the verifier check.")}{fig("L04-voyage-4", "Stop 4: your decision.")}</div></section>""")

parts.append(step(5, "What we do",
    "Six cards, ranked by how much money is involved: EU and UK emissions trading, FuelEU Maritime, the CII rating, EEXI (marked &ldquo;mostly settled&rdquo;), a whole-fleet view, and deadlines with worksheets. Each has a small graphic that animates in.",
    "It shows the full scope at a glance and, by the order, which rule matters most to a ship manager in 2026.",
    fig("L05-services", "Every carbon rule that touches a ship, in one place.")))

parts.append(step(6, "Where we are strongest",
    "Five tiles on a colourful band: answers in seconds, maths you can audit, honest about limits, four rule-books in one number, your data stays yours.",
    "Each tile is something the product can show, rather than a claim. For example, &ldquo;about two in three ships match to the tonne&rdquo; is a measured result.",
    fig("L06-strengths", "The five strengths.")))

parts.append(step(7, "What comes back",
    "An example result card: a bulk carrier&rsquo;s yearly cost, CII rating, EEXI result, where it sits on the A to E scale, and how its rating slides from C to E by 2030 if nothing changes. Beside it, the three things that usually drive the bill.",
    "It shows the output before the visitor has typed anything. The card is labelled ILLUSTRATION because it is not a real ship&rsquo;s filing.",
    fig("L07-result", "&ldquo;Is that a lot? Usually, yes.&rdquo; The &euro;367k is the average across the whole register (an estimate).")))

parts.append(step(8, "How the numbers are worked out",
    "The actual arithmetic behind a CII rating, drawn as real fractions, followed by four expandable explanations (verifier check, regulation sources, what is an estimate, your data stays yours).",
    "For the sceptical reader, and for a verifier who wants to check the working.",
    fig("L08-maths", "Equations drawn the way they are written on paper.")))

parts.append(step(9, "Talk to someone, not a form",
    "A box to start a conversation about your fleet, plus the orange &ldquo;Talk to us&rdquo; button that is on every page. It offers six topics and opens your email app with the message ready. Nothing is sent from the page itself.",
    "The founder wants to hear from operators personally. It never asks about budget.",
    f'<div class="grid2">{fig("L09-talk", "The contact section.")}{fig("L13-chat", "The chat panel, opened from the orange button.")}</div>'))

parts.append(step(10, "The night harbour",
    "The page ends at night with a lighthouse, a moored ship and a second search box.",
    "A last, clear invitation: <i>&ldquo;Start with one ship.&rdquo;</i>",
    fig("L10-finale", "Footer: estimates, source (EMSA, Article 21), not endorsed by EMSA, privacy notice.")))

parts.append(f"""<div class="box"><h4>On a phone</h4>
<p>The same page works at phone width: the voyage stacks the chart above the text.</p>
<div class="phones">{fig("M01-landing-phone", "Opening screen.")}{fig("M02-voyage-phone", "The voyage, stacked.")}{fig("M03-app-phone", "The app&rsquo;s result on a phone.")}</div></div>""")

# ------------------------------------------------------------------ part 2
parts.append('<h2>Part 2: The app<small>Seven tabs. The first two need nothing from you; the CII calculator is for operators.</small></h2>')

parts.append(step("A", "Check a ship (the main tab)",
    "A search box. Start typing a name and suggestions appear (use the arrow keys and Enter, or click). Typing a 7-digit IMO number goes straight through.",
    "This is the whole point of the product: one box, one answer.",
    fig("A01-home", "The starting screen. The three buttons are examples to try.")))

parts.append(step("B", "The result: the carbon bill",
    "<b>Owner / CFO view.</b> One large number, <i>this year&rsquo;s carbon bill</i>, then a bar for each part: EU ETS, FuelEU, UK ETS, and the IMO Net-Zero Framework shown as a scenario only (it has not been adopted). Under each bar: the working in a line, such as how many allowances and by when.",
    "A finance reader wants the total first and the pieces second. Bars make the biggest cost obvious without reading numbers.",
    fig("A02-owner-view", "Top: the ESTIMATE tag. Then the three views, the value banner, the big number, the bars.")))

parts.append(step("C", "The value banner and the what-if",
    "The green banner appears by itself: <i>&ldquo;Value identified: up to &euro;275,548 a year could be saved&hellip;&rdquo;</i>. Click it and the page applies a standard package (20% biofuel on EU voyages and a 10% lower speed) and shows the saving against today.",
    "It turns a cost into a decision. A &ldquo;What would biofuel or slowing down save?&rdquo; panel lets you try your own percentages.",
    fig("A03-value-lever", "After clicking the banner. The bill falls from &euro;510,798 to &euro;235,250.")))

parts.append(step("D", "Add the ship&rsquo;s size to see the CII rating",
    "The register does not publish deadweight, so the page asks for it. Enter it and the A to E rating, a coloured band showing where the ship sits, and a chart of the company&rsquo;s other ships appear. A list of next actions follows.",
    "CII needs the ship&rsquo;s capacity, and we will not guess it. The chart compares the ship&rsquo;s emissions per mile with its sister ships.",
    fig("A04-cii-and-fleet", "The CII band, the fleet chart (hover a dot for a ship&rsquo;s name) and the ranked actions.") + fig("A05-fleet-context", "The orange marker is the selected ship; the dashed grey line is the median for its type.")))

parts.append(step("E", "Three views of the same ship",
    "Switch between <b>Owner / CFO</b> (the money), <b>Technical / Ops</b> (the rating and the levers that improve it) and <b>Verifier</b> (the working: our rebuild beside the official figure).",
    "Different people at a shipping company need different things from the same ship.",
    f'<div class="grid2">{fig("A06-technical-view", "Technical / Ops.")}{fig("A07-verifier-view", "Verifier: provenance and our check against the official number.")}</div>'))

parts.append(step("F", "EEXI (free)",
    "Two checks. First, for a ship in the register: its required EEXI against the value it reported. Second, for any ship not in the register or a design: pick the type, enter the size, then give either its attained EEXI or the engine power and speed for an estimate.",
    "EEXI is a one-off design check that most ships passed in 2023, so it is kept free and is not the headline.",
    f'<div class="grid2">{fig("A08-eexi-registry", "A ship in the register.")}{fig("A09-eexi-custom", "A custom ship, using the example button. The verdict is labelled INDICATIVE.")}</div>'))

parts.append(step("G", "CII calculator (for operators)",
    "Locked behind an access key. The operator enters their own fuel and distance (or an estimate from speed) and gets the rating, the tightening trajectory to 2030, and how much CO&#8322; to cut to reach the next band.",
    "This is the owner-data tool. It is the step from an estimate on public data to the operator&rsquo;s own verified position.",
    f'<div class="grid2">{fig("A10-cii-locked", "Locked: it asks for a key.")}{fig("A11-cii-result", "Unlocked, with the example ship.")}</div>'))

parts.append(step("H", "My fleet",
    "Paste anything that contains IMO numbers. You get fleet totals, a sortable table with a bill for each ship (click a row to open it), and the FuelEU pooling position. Two extra buttons make a printable report and a draft pooling agreement.",
    "A manager wants the whole fleet at once, ranked, in one place.",
    fig("A12-fleet", "Four ships analysed. Free use is capped at eight ships at a time.")))

parts.append(step("I", "Calendar",
    "Every dated obligation for the year with its legal basis, drawn on a timeline with a marker for today. A download button produces a file that adds the dates to Outlook or Google Calendar with a 14-day reminder.",
    "Deadlines are where penalties are actually incurred.",
    fig("A13-calendar", "Eight obligations for compliance year 2026.")))

parts.append(step("J", "Method: check our working",
    "Every formula and parameter, its regulatory source, and a worked example you can recompute by hand. The two core CII equations are drawn at the top.",
    "A verifier or a sceptical customer can audit it. Trust comes from being checkable.",
    fig("A14-method", "The Method tab.")))

parts.append(step("K", "Your data: control for the operator",
    "Explains where the data comes from and gives the operator three choices: <b>claim</b> their ships, <b>correct</b> a figure, or <b>hide</b> our estimates from other people. Hiding takes effect straight away.",
    "Shipping companies worry that competitors will see their numbers. The emissions themselves are public by law, but our calculations about them are ours to withhold, and this tab is where we offer that.",
    fig("A15-your-data", "The claim form and the policy beneath it.")))

# ------------------------------------------------------------------ numbers
parts.append("""
<h2>Where the numbers come from<small>In plain English.</small></h2>
<table>
<tr><th>Question</th><th>Answer</th></tr>
<tr><td>Where does the data come from?</td><td>The EU&rsquo;s public emissions register, run by the European Maritime Safety Agency (EMSA). Article 21 of Regulation (EU) 2015/757 requires the Commission to publish each ship&rsquo;s name, company, verified emissions and fuel use every year. Anyone can download it without a login.</td></tr>
<tr><td>Are we allowed to use it?</td><td>Yes. EMSA&rsquo;s own page says it can be exported &ldquo;for further analysis&rdquo; and its copyright notice authorises reproduction provided the source is acknowledged. We acknowledge EMSA everywhere and say it does not endorse us. One item is still open: a written confirmation from EMSA&rsquo;s helpdesk.</td></tr>
<tr><td>Does AI work out the numbers?</td><td>No. Ordinary calculation code built from the regulations produces every figure. AI is never used for a compliance number.</td></tr>
<tr><td>How accurate is it?</td><td>We compare our rebuild of each ship&rsquo;s EU ETS CO&#8322; with the official figure its verifier reported. On a random sample of 400 ships we match exactly on about two in three, and to within 2% on about four in five. The rest differ, usually because the filed figure covers only part of the year. That is why everything is labelled ESTIMATE and why the Verifier view shows both numbers.</td></tr>
<tr><td>What is assumed?</td><td>An EU allowance cost of &euro;70 a tonne (the page also shows &euro;60 and &euro;100), a heavy-fuel-oil mix unless the operator says otherwise, and a deadweight the visitor must supply. These are inputs, not facts.</td></tr>
<tr><td>Is the data current?</td><td>It is the 2025 report, version 6. EMSA has since published a newer version, and a tool to refresh it is built and waiting for approval to run.</td></tr>
</table>
""")

# ------------------------------------------------------------------ tour
parts.append("""
<h2>A five-minute tour to follow along<small>For when you see it live, or to read the screenshots in order.</small></h2>
<ol class="tour">
<li><b>Opening page:</b> read the first screen, then scroll slowly through &ldquo;How we get to the number&rdquo; and watch the ship sail between the four stops.</li>
<li><b>Search a ship:</b> type <i>PETER OLDENDORFF</i> (a bulk carrier) and note the big number and the bars.</li>
<li><b>Click the green value banner</b> and watch the bill fall.</li>
<li><b>Add a deadweight</b> (try 50,000) to see the CII rating and the chart of sister ships.</li>
<li><b>Switch to Verifier</b> and compare our rebuild with the official figure.</li>
<li><b>Open Calendar</b> and Method.</li>
<li><b>Try the contact button</b> (bottom right).</li>
</ol>
""")

# ------------------------------------------------------------------ limits
parts.append("""
<h2>Honest limits and status</h2>
<div class="box"><ul>
<li><b>Preview.</b> Running on one computer. The public website, domain and hosting are not set up yet.</li>
<li><b>Estimates, not filings.</b> Figures built from public data are estimates. Operators who supply their own data move from estimate to verified position.</li>
<li><b>Not legal or investment advice.</b> It explains obligations and costs; it does not advise on what to buy or trade.</li>
<li><b>Not endorsed by EMSA or the European Commission.</b> The source is acknowledged; the calculations are our own.</li>
<li><b>Deliberately left out of the front page:</b> prices and fees, and any push to trade carbon. The pooling and deadline features exist in the app but are not the headline.</li>
<li><b>Known next steps:</b> refresh the data to EMSA&rsquo;s latest version; test whether reading EMSA&rsquo;s separate partial-reports sheet improves the match rate; set up the domain and hosting.</li>
</ul></div>
""")

# ------------------------------------------------------------------ glossary
parts.append("""
<h2>Glossary</h2>
<table class="gloss">
<tr><td>IMO</td><td>The International Maritime Organization, the UN body that sets global shipping rules. Also: the 7-digit <b>IMO number</b> that identifies one ship for life.</td></tr>
<tr><td>EMSA</td><td>The European Maritime Safety Agency. It runs the system (THETIS-MRV) that publishes ships&rsquo; verified emissions.</td></tr>
<tr><td>MRV</td><td>Monitoring, reporting and verification: the EU rule that makes ships report their emissions each year and have them checked by an accredited <b>verifier</b>.</td></tr>
<tr><td>EU ETS / UK ETS</td><td>The EU and UK emissions trading schemes. Shipping companies must buy and hand in allowances for emissions. From 2026 the EU scheme covers 100% of in-scope emissions.</td></tr>
<tr><td>EUA</td><td>An EU allowance: the right to emit one tonne of CO&#8322;e. We assume &euro;70 each, as an input.</td></tr>
<tr><td>FuelEU Maritime</td><td>An EU rule limiting how much greenhouse gas the energy a ship burns may produce. Running conventional fuel puts a ship over the limit, and the shortfall is charged as a penalty.</td></tr>
<tr><td>Pooling</td><td>Ships whose fuel is cleaner than the limit can share their surplus with ships that are over it, so the pool avoids penalties. Shown in the app but not the headline.</td></tr>
<tr><td>CII</td><td>Carbon Intensity Indicator: an A to E grade for how efficiently a ship operates, against a limit that tightens every year to 2030. Three years at D or one year at E requires a corrective plan.</td></tr>
<tr><td>EEXI</td><td>Energy Efficiency Existing Ship Index: a one-off design check most ships passed in 2023.</td></tr>
<tr><td>DWT / GT</td><td>Deadweight tonnage (cargo capacity) and gross tonnage (internal volume). CII needs one of them, and neither is in the public register.</td></tr>
<tr><td>NZF</td><td>The IMO Net-Zero Framework, a proposed global scheme. Not adopted yet; the adoption vote is expected in October 2026, so the app shows it only as a scenario.</td></tr>
<tr><td>ESTIMATE</td><td>Our label for any figure rebuilt from public data rather than supplied by the operator.</td></tr>
</table>
""")

parts.append("""<footer>Prepared from the CarbonKeel preview build, 5 October 2026. Figures shown are estimates rebuilt from public EU MRV data published by EMSA under Article 21 of Regulation (EU) 2015/757, and are not endorsed by EMSA or the European Commission. This guide describes how the tool works; it is not legal or investment advice.</footer>
</div></body></html>""")

html_doc = "\n".join(parts)
open(OUT_HTML, "w", encoding="utf-8").write(html_doc)
print("html", round(os.path.getsize(OUT_HTML) / 1e6, 2), "MB")

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page()
    pg.goto("file:///" + OUT_HTML.replace("\\", "/"))
    pg.wait_for_timeout(1500)
    pg.pdf(path=OUT_PDF, format="A4", print_background=True,
           margin={"top": "12mm", "bottom": "14mm", "left": "10mm", "right": "10mm"})
    b.close()
print("pdf", round(os.path.getsize(OUT_PDF) / 1e6, 2), "MB")
