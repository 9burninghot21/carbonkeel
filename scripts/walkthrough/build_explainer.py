"""Build 'What CarbonKeel provides and what it computes' (HTML + PDF).

Every number in the worked examples comes from the live engines (checked on
6 Oct 2026 against the 2025 report, version 6, for IMO 9464663). Re-run the
engines before regenerating if the data or the rules change.
Needs: pip install playwright (uses the installed Microsoft Edge).
"""
import os, sys

SP = os.path.dirname(__file__)
ROOT = sys.argv[1]
OUT_HTML = os.path.join(ROOT, "docs", "WHAT_WE_PROVIDE_AND_COMPUTE.html")
OUT_PDF = os.path.join(ROOT, "docs", "WHAT_WE_PROVIDE_AND_COMPUTE.pdf")


def frac(n, d):
    return f'<span class="frac"><span class="n">{n}</span><span class="d">{d}</span></span>'


def eq(*parts, note=""):
    body = " ".join(f"<span>{x}</span>" for x in parts)
    n = f'<div class="eqnote">{note}</div>' if note else ""
    return f'<div class="eq">{body}</div>{n}'


def tbl(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{r}</table>'


def sec(n, title, body):
    return f'<section class="sec"><h2><span class="num">{n}</span>{title}</h2>{body}</section>'


def block(label, body):
    return f'<div class="blk"><h4>{label}</h4>{body}</div>'


CSS = """
:root{--ink:#0b2545;--muted:#46607e;--blue:#0a5aa0;--line:rgba(11,37,69,.14);--soft:#f1f6fb;--amber:#fff6e0}
*{box-sizing:border-box}
body{font-family:"Segoe UI",system-ui,sans-serif;color:var(--ink);line-height:1.55;margin:0;font-size:15px}
.wrap{max-width:880px;margin:0 auto;padding:0 26px 50px}
header.cover{background:linear-gradient(135deg,#0b2545,#0a5aa0 62%,#7c3aed);color:#fff;padding:46px 0 38px}
header.cover h1{font-size:36px;margin:0 0 8px;letter-spacing:-.02em;line-height:1.12}
header.cover p{margin:6px 0 0;font-size:17px;color:#dbe9fb;max-width:38em}
.badge{display:inline-block;margin-top:16px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:5px 14px;font-size:13px}
h2{font-size:25px;margin:40px 0 6px;letter-spacing:-.01em;border-top:3px solid var(--blue);padding-top:12px;display:flex;align-items:baseline;gap:10px}
h2 .num{flex:none;background:var(--blue);color:#fff;border-radius:8px;font-size:15px;padding:2px 9px}
h3{font-size:18px;margin:22px 0 4px}
h4{font-size:12.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--blue);margin:14px 0 4px}
p{margin:7px 0}
.lead{font-size:17px;color:var(--muted)}
.box{background:var(--soft);border-radius:12px;padding:14px 18px;margin:14px 0}
.warn{background:var(--amber);border:1px solid #f1d38a;border-radius:12px;padding:12px 16px;margin:14px 0}
.box ul,.warn ul{margin:4px 0;padding-left:20px}
li{margin:3px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:10px 0}
td,th{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--soft)}
table.num td:last-child{text-align:right;font-variant-numeric:tabular-nums}
.blk{border-left:4px solid var(--blue);padding:2px 0 2px 14px;margin:16px 0}
.eq{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;background:var(--soft);border-radius:10px;padding:14px 10px;margin:10px 0 2px;font-size:16px}
.eqnote{font-size:12.5px;color:var(--muted);text-align:center;margin-bottom:8px}
.frac{display:inline-flex;flex-direction:column;align-items:center;vertical-align:middle;text-align:center;line-height:1.25}
.frac .n{padding:0 8px 3px}.frac .d{padding:3px 8px 0;border-top:2px solid var(--ink)}
.eq var{font-style:italic;color:#6d28d9;font-weight:700}.eq sup,.eq sub{line-height:0}
.flow{display:grid;grid-template-columns:1fr 26px 1fr 26px 1fr 26px 1fr;gap:6px;align-items:stretch;margin:16px 0}
.flow .b{border:2px solid var(--blue);border-radius:10px;padding:9px 10px;font-size:12.5px;background:#fff}
.flow .b b{display:block;font-size:13.5px;margin-bottom:3px}
.flow .a{display:flex;align-items:center;justify-content:center;color:var(--blue);font-size:22px}
.tag{display:inline-block;font-size:11.5px;font-weight:800;border-radius:10px;padding:1px 8px;white-space:nowrap}
.hi{background:#dcf5ea;color:#0b6b49}.me{background:#fff1cc;color:#7a4a00}.lo{background:#fde3e0;color:#9a1c12}
.sec{page-break-inside:auto}
.blk,table,.eq,.warn,.box{page-break-inside:avoid}
h2,h3,h4{page-break-after:avoid}
footer{border-top:1px solid var(--line);margin-top:34px;padding-top:12px;font-size:12.5px;color:var(--muted)}
@media print{.wrap{padding:0 4px 20px}header.cover{padding:30px 0 26px}}
"""

P = []
P.append(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>What CarbonKeel provides and what it computes</title>
<style>{CSS}</style></head><body>
<header class="cover"><div class="wrap">
<h1>What CarbonKeel provides, and what it computes</h1>
<p>A plain-English reference with the working shown: what goes in, what is calculated, how, and how far to trust each result.</p>
<span class="badge">6 October 2026 &middot; worked examples use EMSA&rsquo;s 2025 report, version 6</span>
</div></header><div class="wrap">""")

# ------------------------------------------------------------------ 1
P.append(sec(1, "The short version", """
<p class="lead">CarbonKeel turns a ship&rsquo;s publicly reported emissions into the money and ratings that follow from them, using the actual rules. Every figure comes from ordinary calculation code built from the regulations. No AI produces a number.</p>
<div class="box"><ul>
<li><b>Input:</b> a ship name or IMO number. Optionally its size (deadweight), or the operator&rsquo;s own fuel and distance data.</li>
<li><b>Output:</b> the carbon bill under the EU and UK emissions trading schemes and FuelEU Maritime, a CII efficiency grade (A to E), an EEXI design check, a scenario for the IMO Net-Zero Framework, the effect of two standard levers, and a fleet view with deadlines.</li>
<li><b>Honest about its basis:</b> results rebuilt from public data are labelled <b>ESTIMATE</b>. Where the operator supplies its own data, the result is labelled <b>OWNER DATA</b>.</li>
</ul></div>
<div class="warn"><b>Read this first: which year is the bill for?</b> The headline figure is the obligation for the <b>latest reported year in the register (2025)</b>, under that year&rsquo;s rules. For 2025 only <b>70%</b> of emissions is surrendered; from 2026 it is <b>100%</b>. The app therefore shows both: the 2025 bill, and what the same emissions would cost under the 2026 rules (see 4.2). Sections 6 and 7 list every basis and limit.</div>
"""))

# ------------------------------------------------------------------ 2
P.append(sec(2, "What we provide", tbl(
    ["Deliverable", "What you give it", "What you get", "Where in the app"],
    [
        ["<b>Ship check</b> (free, public data)", "A ship name or IMO number", "The carbon bill by regime for the latest reported year, the same emissions under 2026 rules, an IMO NZF scenario, a check against the verifier&rsquo;s own figure, a chart of the company&rsquo;s other ships", "Check a ship"],
        ["<b>CII rating</b> (estimate)", "+ the ship&rsquo;s deadweight (or gross tonnage)", "An A to E grade, the band boundaries and where the ship sits, ranked actions", "Check a ship"],
        ["<b>Three views</b>", "&mdash;", "Owner/CFO (money), Technical/Ops (rating and levers), Verifier (our working beside the official figure)", "Check a ship"],
        ["<b>Levers</b>", "Percentages, or one click", "The change in carbon cost from biofuel and from slower speed", "Check a ship"],
        ["<b>EEXI check</b> (free)", "A ship in the register, or a custom ship", "Required EEXI, the verdict and the margin", "EEXI"],
        ["<b>CII calculator</b> (operators, by key)", "The operator&rsquo;s own fuel and distance, or speed data", "Verifier-grade rating, the path to 2030, the cut needed to reach each band", "CII calculator"],
        ["<b>Fleet analysis</b>", "Any text containing IMO numbers", "Fleet totals, a table by ship, the pooling position, a printable report, a draft pooling agreement", "My fleet"],
        ["<b>Compliance calendar</b>", "A year", "Eight dated obligations with their legal basis, and a file for Outlook or Google Calendar", "Calendar"],
        ["<b>Method and worksheet</b>", "&mdash;", "Every formula, parameter and source; a full worksheet for any ship", "Method; Verifier view"],
        ["<b>Data controls</b>", "IMO numbers and a work email", "Claim ships, correct a figure, or hide our estimates from other people", "Your data"],
    ]) + """
<h3>What we do not provide (yet)</h3>
<div class="box"><ul>
<li>Live allowance prices. The EU and UK allowance costs are fixed assumptions (see 3).</li>
<li>Voyage-by-voyage or port-by-port analysis.</li>
<li>Accounts, billing, or a pooling marketplace that matches counterparties. The pooling optimiser works inside one fleet only.</li>
<li>Certified or verifier-signed outputs. Nothing here is legal, investment or compliance advice.</li>
</ul></div>"""))

# ------------------------------------------------------------------ 3
P.append(sec(3, "How the pieces connect", """
<div class="flow">
<div class="b"><b>1. Public file</b>EMSA&rsquo;s verified emissions for each ship, published under Article 21 of the EU MRV Regulation</div><div class="a">&rarr;</div>
<div class="b"><b>2. Rebuild the year</b>Split the ship&rsquo;s year into legs by scope; work out fuel and distance (4.1)</div><div class="a">&rarr;</div>
<div class="b"><b>3. Apply the rules</b>EU ETS, FuelEU, UK ETS, NZF scenario, CII, EEXI &mdash; each from its regulation</div><div class="a">&rarr;</div>
<div class="b"><b>4. Show the result</b>Bill, rating, levers, fleet view, deadlines; labelled ESTIMATE or OWNER DATA</div>
</div>
<p>The operator&rsquo;s own data can replace step 1 and 2, which turns an estimate into an owner-data result (the CII calculator).</p>

<h3>What goes in</h3>""" + tbl(
    ["Source", "Items"],
    [
        ["<b>From EMSA&rsquo;s file</b>, for each ship", "IMO number, name, ship type, company; total CO&#8322;; CO&#8322; split by scope (voyages inside the EU, voyages leaving, voyages arriving, time at berth); the verifier&rsquo;s ETS-scope CO&#8322;; total fuel; CO&#8322; per nautical mile; the reported technical efficiency (EEXI or EEDI); the reporting year"],
        ["<b>From the user</b>", "Deadweight or gross tonnage; an attained EEXI, or engine power and service speed; for the CII calculator: fuel by type, distance or speed and days at sea, and any verifier-accepted corrections; lever percentages; a list of IMO numbers"],
        ["<b>Fixed rule tables</b> (cited line by line on the Method page)", "Carbon factors per fuel; CII reference lines, Z factors and rating boundaries per ship type; EEXI reference lines and reduction factors; fuel energy content and well-to-wake intensity; FuelEU targets and penalty; NZF targets"],
        ["<b>Assumptions we set</b>", "EU allowance <b>&euro;70</b> per tonne; UK allowance <b>&pound;40</b>; &euro;/&pound; <b>1.15</b>; NZF scenario year <b>2028</b> with remedial units at <b>$100</b> (Tier 1) and <b>$380</b> (Tier 2); fuel assumed to be <b>heavy fuel oil</b> (LNG for LNG carriers)"],
    ])))

# ------------------------------------------------------------------ 4 worked example intro
P.append(sec(4, "What is computed, step by step", """
<p>Each part below states the purpose, the method (with the maths written out), a worked example, and the limits. <b>The example ship throughout is PETER OLDENDORFF</b> (IMO 9464663, a bulk carrier), using EMSA&rsquo;s 2025 report, version 6. It is a real, public ship, used only to show the working; the figures are estimates.</p>
"""))

# 4.1
P.append("""<section class="sec"><h3>4.1 Rebuilding the ship&rsquo;s year from the public file</h3>
<div class="blk"><h4>Purpose</h4><p>The file gives totals, not voyages. To apply rules that treat voyages differently (full, half, or not at all), we split the year into legs.</p></div>
<div class="blk"><h4>Method</h4><ul>
<li>One leg per scope: <b>inside the EU</b>, <b>to or from the EU</b> (departed plus arrived), <b>at berth</b>, and <b>outside scope</b> (whatever remains of the total).</li>
<li><b>Fuel in each leg</b> = that leg&rsquo;s CO&#8322; divided by the carbon factor of the assumed fuel.</li>
<li><b>Distance</b> = total CO&#8322; (in kg) divided by the reported CO&#8322; per nautical mile, shared between legs in proportion to their CO&#8322;. Berth has no distance.</li></ul>""" + eq(
    "distance", "=", frac("total CO<sub>2</sub> (kg)", "reported CO<sub>2</sub> per nautical mile"), "&nbsp;&nbsp;&nbsp;fuel", "=", frac("CO<sub>2</sub> of the leg (t)", "carbon factor (t CO<sub>2</sub> per t fuel)")) + """</div>""" + tbl(
    ["Leg (example)", "CO&#8322; (t)", "Fuel (t HFO, factor 3.114)", "Distance (nm)"],
    [["Inside the EU", "603", "193.6", "1,417"],
     ["To or from the EU (5,347 + 7,494)", "12,840", "4,123.4", "30,191"],
     ["At berth", "386", "124.0", "&mdash;"],
     ["<b>Total</b>", "<b>13,829</b>", "<b>4,441</b>", "<b>31,608</b>"]], "num") + """
<div class="warn"><b>Limits.</b> The file covers voyages that touch EU ports, not the ship&rsquo;s whole year. Fuel type and distance are inferred, not published. Owner data replaces all of this.</div></section>""")

# 4.2 ETS
P.append("""<section class="sec"><h3>4.2 EU Emissions Trading System (ETS)</h3>
<div class="blk"><h4>Purpose</h4><p>Shipping companies buy and hand in EU allowances for emissions in scope. This is usually the largest single number.</p></div>
<div class="blk"><h4>Method</h4>""" + eq(
    "allowances", "=", "&Sigma;<sub>legs</sub> (CO<sub>2</sub>e of the leg &times; <var>scope share</var>)", "&times;", "<var>phase-in</var>", note="Scope share: voyages inside the EU 100%, to or from the EU 50%, at berth 100%, outside scope 0%. Phase-in of what is surrendered: 40% for 2024, 70% for 2025, 100% from 2026.") + eq(
    "cost", "=", "allowances", "&times;", "allowance price (&euro;70 assumed)") + """
<p>From 2026, methane and nitrous oxide count as well. CO&#8322;e = CO&#8322; + CH&#8324; &times; 28 + N&#8322;O &times; 265 (the global-warming potentials used by the EU ETS). For liquid fuels CH&#8324; is 0.00005 and N&#8322;O is 0.00018 tonnes per tonne of fuel; for LNG the methane slip depends on the engine type.</p></div>""" + tbl(
    ["Step (example)", "Working", "Result"],
    [["ETS-scope CO&#8322;", "603 + 0.5 &times; (5,347 + 7,494) + 386", "<b>7,409 t</b> (the verifier reported 7,409)"],
     ["Allowances due, 2025 rules", "7,409 &times; 70%", "<b>5,186</b>"],
     ["Cost", "5,186 &times; &euro;70", "<b>&euro;363,039</b>"],
     ["Same emissions, 2026 rules", "CO&#8322;e 7,526 t (incl. CH&#8324;, N&#8322;O) &times; 100% &times; &euro;70", "<b>&euro;526,805</b>"]], "num") + """
<div class="warn"><b>Be clear about what this is.</b> For a ship in the public file, the ETS figure is essentially the <b>verifier&rsquo;s own scope CO&#8322;, weighted by the scope rules, then multiplied by the phase-in and the assumed price</b>. Our value is the rule application, the 2026 view and the levers, not an independent measurement. The price is an assumption; the app also shows the result at &euro;60 and &euro;100.</div></section>""")

# 4.3 FuelEU
P.append("""<section class="sec"><h3>4.3 FuelEU Maritime</h3>
<div class="blk"><h4>Purpose</h4><p>FuelEU limits the greenhouse-gas <i>intensity</i> of the energy a ship uses (not its tonnes). A ship above the limit has a deficit and a penalty; below it, a surplus.</p></div>
<div class="blk"><h4>Method</h4>""" + eq(
    "intensity", "=", frac("&Sigma; (fuel t &times; energy per t &times; well-to-wake gCO<sub>2</sub>e/MJ)", "&Sigma; (fuel t &times; energy per t)"), note="Counted over the energy in scope: voyages inside the EU 100%, to or from the EU 50%, berth 100%.") + eq(
    "balance", "=", "(<var>target</var> &minus; intensity)", "&times;", "energy in scope", "&nbsp;&nbsp;&nbsp;penalty", "=", frac("|balance|", "intensity &times; 41,000"), "&times; &euro;2,400", note="Penalty applies only to a deficit (balance below zero). 41,000 MJ is the energy of one tonne of very-low-sulphur fuel oil.") + """
<p>The target is the 2020 baseline of 91.16 gCO&#8322;e/MJ reduced by 2% from 2025, 6% from 2030, 14.5% from 2035, 31% from 2040, 62% from 2045 and 80% from 2050. The fuel values are the defaults in Annex II of the regulation:</p>""" + tbl(
    ["Fuel", "Energy (MJ per t)", "Well-to-wake (gCO&#8322;e/MJ)"],
    [["Heavy fuel oil", "40,500", "91.74"], ["Low-sulphur fuel oil", "41,000", "91.39"], ["Marine diesel / gas oil", "42,700", "90.77"],
     ["LNG (medium-speed dual-fuel)", "49,100", "89.20"], ["Methanol (fossil)", "19,900", "103.15"], ["Biofuel 24% blend", "40,040", "74.8"], ["Biofuel 100%", "37,000", "16.4"]], "num") + """</div>""" + tbl(
    ["Step (example)", "Working", "Result"],
    [["Energy in scope", "(193.6 + 0.5 &times; 4,123.4 + 124.0) t &times; 40,500 MJ/t", "<b>96.36 million MJ</b>"],
     ["Intensity", "heavy fuel oil", "<b>91.74</b> gCO&#8322;e/MJ"],
     ["Target, 2025", "91.16 &times; (1 &minus; 2%)", "<b>89.34</b>"],
     ["Balance", "(89.34 &minus; 91.74) &times; 96.36 million MJ", "<b>&minus;231.6 t CO&#8322;e</b> (a deficit)"],
     ["Penalty", "231.6 million g &divide; (91.74 &times; 41,000) &times; &euro;2,400", "<b>&euro;147,759</b>"]], "num") + """
<div class="warn"><b>Limit that matters.</b> The public file does not say which fuel a ship burned, so we assume heavy fuel oil. Its intensity (91.74) is above every FuelEU target, so <b>almost every ship in the register shows a deficit</b>. The figure is best read as <i>the exposure if the ship ran on conventional fuel</i>, not its actual position. LNG carriers are assumed to burn LNG (89.20) and can show a small surplus. An operator&rsquo;s own fuel data corrects this.</div></section>""")

# 4.4 UK
P.append("""<section class="sec"><h3>4.4 UK Emissions Trading Scheme</h3>
<div class="blk"><h4>Purpose</h4><p>The UK scheme covers shipping from 1 July 2026. It applies to <b>domestic UK voyages only</b>: UK port to UK port at 100%, voyages between Great Britain and Northern Ireland at 50%, and time at berth in UK ports at 100%. It counts CO&#8322;, methane and nitrous oxide from the start and has no phase-in.</p></div>
<div class="blk"><h4>Method</h4>""" + eq("cost (&pound;)", "=", "&Sigma;<sub>legs</sub> (CO<sub>2</sub>e &times; <var>UK share</var>)", "&times;", "UK allowance price (&pound;40 assumed)", note="Shown in euros in the combined figure at &euro;1.15 per &pound;. The first scheme period is the second half of 2026.") + """</div>
<div class="warn"><b>Limit.</b> The EU register does not show UK domestic voyages, so <b>from public data this line is normally zero</b> (&ldquo;No UK domestic voyages found&rdquo;). It becomes meaningful only with the operator&rsquo;s own voyage data.</div></section>""")

# 4.5 NZF
P.append("""<section class="sec"><h3>4.5 IMO Net-Zero Framework (scenario only)</h3>
<div class="blk"><h4>Purpose</h4><p>A proposed global scheme, approved in principle in April 2025, with the adoption vote expected in October 2026. Because it is not adopted, <b>it is shown only as a scenario</b>, and the parameters are provisional.</p></div>
<div class="blk"><h4>Method</h4>""" + eq(
    "GFI", "=", frac("&Sigma; (fuel t &times; energy per t &times; well-to-wake)", "&Sigma; (fuel t &times; energy per t)"), note="Counted over all fuel burned on all voyages, not only the EU part. Reference: 93.3 gCO<sub>2</sub>e/MJ.") + """
<p>Two targets fall each year from the 93.3 reference (2028: Base &minus;4%, Direct &minus;17%; 2030: &minus;8% and &minus;21%; 2035: &minus;30% and &minus;43%). Above the Base target the ship buys <b>Tier 2</b> remedial units ($380 per tonne) and also <b>Tier 1</b> for the band between the two targets ($100); between the targets only Tier 1; below Direct it earns surplus units.</p></div>""" + tbl(
    ["Step (example, 2028)", "Working", "Result"],
    [["Energy, all voyages", "4,441 t &times; 40,500 MJ/t", "<b>179.9 million MJ</b>"],
     ["GFI against targets", "91.74 against Base 89.57 and Direct 77.44", "above Base"],
     ["Tier 2", "(91.74 &minus; 89.57) &times; 179.9 million MJ", "<b>391 t</b>"],
     ["Tier 1", "(89.57 &minus; 77.44) &times; 179.9 million MJ", "<b>2,182 t</b>"],
     ["Cost", "2,182 &times; $100 + 391 &times; $380", "<b>$366,599</b>"]], "num") + """
<p>Shown in dollars because the scheme is priced in dollars. It is a scenario on <i>today&rsquo;s</i> fuel mix, not a forecast, and it is not added into the carbon bill.</p></section>""")

# 4.6 CII
P.append("""<section class="sec"><h3>4.6 CII: the A to E efficiency grade</h3>
<div class="blk"><h4>Purpose</h4><p>The Carbon Intensity Indicator grades how much CO&#8322; a ship emits to move its capacity over a distance, against a limit that tightens every year to 2030. Three years at D, or one at E, requires a corrective plan.</p></div>
<div class="blk"><h4>Method (IMO guidelines G1 to G4)</h4>""" + eq(
    "attained", "=", frac("&Sigma; (fuel t &times; carbon factor) &times; 10<sup>6</sup>", "capacity &times; distance (nm)"), "&nbsp;&nbsp;&nbsp;reference", "=", "<var>a</var> &times; capacity<sup>&minus;<var>c</var></sup>") + eq(
    "required", "=", "reference", "&times;", "(1 &minus;", frac("<var>Z</var>", "100"), ")", "&nbsp;&nbsp;&nbsp;ratio", "=", frac("attained", "required"), note="The rating is the first band whose boundary the ratio does not exceed. Boundaries = required &times; d1, d2, d3, d4.") + """
<ul><li><b>Capacity</b> is deadweight for most ship types and gross tonnage for ro-ro, ro-pax, cruise and vehicle carriers.</li>
<li><b>Z</b> (the reduction against the 2019 reference): 5% (2023), 7%, 9%, 11% (2026), 13.625% (2027), 16.25%, 18.875%, 21.5% (2030).</li>
<li><b>a, c and d1 to d4</b> depend on the ship type. For bulk carriers: a = 4,745, c = 0.622; boundaries at 0.86, 0.94, 1.06 and 1.18 of the required value.</li></ul></div>""" + tbl(
    ["Step (public-data estimate, 50,000 dwt typed in)", "Working", "Result"],
    [["Attained", "13,829 t &times; 10<sup>6</sup> &divide; (50,000 &times; 31,608 nm)", "<b>8.750</b>"],
     ["Reference", "4,745 &times; 50,000<sup>&minus;0.622</sup>", "<b>5.669</b>"],
     ["Required, 2025 (Z = 9%)", "5.669 &times; 0.91", "<b>5.158</b>"],
     ["Ratio", "8.750 &divide; 5.158", "<b>1.696</b>"],
     ["Boundaries", "A &le; 4.436, B &le; 4.849, C &le; 5.468, D &le; 6.087", "ratio above 1.18: <b>E</b>"]], "num") + """
<div class="warn"><b>Limits of the public-data estimate.</b> Deadweight is not published, so the user types it. The emissions and distance cover only voyages touching EU ports, so the grade describes <i>that part</i> of the operation, while the real CII covers the whole year. Treat it as a screening grade, not a certified rating.</div>
<div class="blk"><h4>The operator&rsquo;s calculator (owner data)</h4>
<p>The operator enters fuel by type and distance sailed, <b>or</b> estimates from speed. The speed route uses the cube law: main-engine fuel per day = reference consumption &times; (actual speed &divide; reference speed)<sup>3</sup>; distance = speed &times; 24 &times; days at sea; auxiliary fuel is added. Voyage adjustments (the G5 corrections) are applied only if the operator supplies documented values; we never invent one. The result adds:</p>
<ul><li><b>The path to 2030</b>: the same performance against each year&rsquo;s tighter limit.</li>
<li><b>The cut needed</b> to reach each band: (1 &minus; boundary &divide; attained) &times; 100%.</li></ul></div>""" + tbl(
    ["Example (owner data)", "Working", "Result"],
    [["Attained, 2026", "4,300 t HFO &times; 3.114 = 13,390 t; 13,390 &times; 10<sup>6</sup> &divide; (50,000 &times; 50,000 nm)", "<b>5.356</b>"],
     ["Required, 2026 (Z = 11%)", "5.669 &times; 0.89", "<b>5.045</b>"],
     ["Rating", "ratio 1.062 is above 1.06", "<b>D</b>"],
     ["Path, 2023 to 2030", "same ship, same operation", "C, C, C, D, D, D, D, <b>E</b>"],
     ["To reach C", "(1 &minus; 5.348 &divide; 5.356) &times; 100%", "a cut of <b>0.2%</b>"]], "num") + "</section>")

# 4.7 EEXI
P.append("""<section class="sec"><h3>4.7 EEXI: the design check</h3>
<div class="blk"><h4>Purpose</h4><p>The Energy Efficiency Existing Ship Index is a one-off design check that most ships passed in 2023. It matters again for newbuildings, conversions and changes to engine power limits, so it is free and not the headline.</p></div>
<div class="blk"><h4>Method</h4>""" + eq(
    "required EEXI", "=", "(1 &minus;", frac("<var>X</var>", "100"), ")", "&times;", "<var>a</var> &times; capacity<sup>&minus;<var>c</var></sup>", note="X is the reduction factor for the ship type and size (MARPOL Annex VI, Regulation 25, Table 3). The verdict is: attained at or below required passes.") + """
<ul><li><b>For a ship in the register:</b> compare the value it reported against the required value. If it reported an EEDI rather than an EEXI, the verdict is labelled <b>INDICATIVE</b>.</li>
<li><b>Capacity basis:</b> deadweight for most types; gross tonnage for passenger and cruise ships; for container ships, 70% of deadweight for the attained value but the full deadweight for the required value (a rule that, applied the other way, would let a failing ship look compliant).</li>
<li><b>For a custom ship</b>, give an attained EEXI, or let us estimate it from engine power and speed:</li></ul>""" + eq(
    "attained", "&asymp;", frac("(<var>P</var><sub>ME</sub> &times; CF &times; SFOC<sub>ME</sub>) + (<var>P</var><sub>AE</sub> &times; CF &times; SFOC<sub>AE</sub>)", "capacity &times; speed"), note="Main engine power = 75% of MCR; auxiliary power = 2.5% of MCR + 250 kW (5% below 10,000 kW); specific fuel consumption 175 and 215 g/kWh (for heavy fuel oil).") + "</div>" + tbl(
    ["Example (custom bulk carrier)", "Working", "Result"],
    [["Inputs", "93,000 dwt; MCR 12,000 kW; service speed 14.2 kn; heavy fuel oil", ""],
     ["Attained (estimated)", "(9,000 &times; 3.114 &times; 175 + 550 &times; 3.114 &times; 215) &divide; (93,000 &times; 14.2)", "<b>3.99</b>"],
     ["Reference", "961.79 &times; 93,000<sup>&minus;0.477</sup>", "<b>4.10</b>"],
     ["Required (X = 20%)", "4.10 &times; 0.80", "<b>3.28</b>"],
     ["Verdict", "3.99 above 3.28", "<b>INDICATIVE, above required</b>"]], "num") + """
<p>The estimate leaves out power take-off, shaft generators, ice class, innovative technologies and the weather factor, so the certified Technical File value will differ. That is why the verdict says INDICATIVE.</p></section>""")

# 4.8 levers
P.append("""<section class="sec"><h3>4.8 The levers: biofuel and slower speed</h3>
<div class="blk"><h4>Purpose</h4><p>To show, in euros, what two standard operational changes would do to the carbon bill. The one-click &ldquo;Value identified&rdquo; uses a standard package: <b>20% of fossil energy replaced by 100% biofuel (B100) on EU voyages, and a 10% lower speed</b>.</p></div>
<div class="blk"><h4>Method</h4>
<ul><li><b>Slower speed</b> (distance unchanged): fuel for the same distance scales with the <i>square</i> of speed, because engine power rises with the cube of speed while the passage takes proportionally longer. So tonnes &times; (1 + speed change)<sup>2</sup>; a 10% cut gives &times; 0.81.</li>
<li><b>Biofuel:</b> the chosen share of each fossil fuel&rsquo;s <i>energy</i> is replaced by B100, with the tonnage corrected for its lower energy content (about 10% more tonnes). B100 is treated as zero-rated under the EU ETS and CII (this assumes it is certified), and has a well-to-wake intensity of 16.4 under FuelEU.</li></ul></div>""" + tbl(
    ["Example", "Working", "Result"],
    [["ETS after the levers", "&euro;363,039 falls to &euro;235,250", "<b>&minus;&euro;127,789</b>"],
     ["FuelEU penalty", "the deficit becomes a surplus, so the penalty goes to zero", "<b>&minus;&euro;147,759</b>"],
     ["<b>Carbon cost avoided</b>", "", "<b>&euro;275,548 a year</b>"],
     ["Biofuel needed", "", "about 787 t of B100"]], "num") + """
<div class="warn"><b>What this figure is not.</b> It is a reduction in <i>carbon cost</i>. It does <b>not</b> subtract the cost of buying the biofuel, which is the main cost of the lever, nor the effect of slower sailing on voyage time and chartering, nor certification. It assumes the biofuel is certified. The app says &ldquo;before the cost of the biofuel itself&rdquo; for this reason. Read it as the size of the prize, not a net saving.</div></section>""")

# 4.9 fleet and pooling
P.append("""<section class="sec"><h3>4.9 Fleet analysis and pooling</h3>
<div class="blk"><h4>Purpose</h4><p>A manager wants the whole fleet at once. Fleet totals are the sums of the per-ship figures. The pooling step looks at FuelEU, where ships may pool their balances: if the pool&rsquo;s total balance is zero or better, every member is treated as compliant.</p></div>
<div class="blk"><h4>Method</h4>
<ul><li>All ships with a <b>surplus</b> contribute their surplus tonnes to the pool&rsquo;s capacity.</li>
<li>Choosing which <b>deficit</b> ships to admit is a classic knapsack problem: each costs |deficit| tonnes of capacity and would otherwise pay its own penalty. We choose the set that avoids the most penalty without exceeding the capacity. It is solved exactly at 1-tonne steps for fleets up to a large size, with a fast approximation above that.</li>
<li>The registration deadline is 30 April of the following year.</li></ul></div>
<div class="warn"><b>Limit.</b> Because the public estimate assumes conventional fuel (4.3), a fleet of ordinary ships usually has no surplus, and the app then says there is no spare pooling capacity inside the fleet. We do <b>not</b> match counterparties between companies. The &ldquo;draft pooling agreement&rdquo; is a template, not legal advice.</div></section>""")

# 4.10 indicators
P.append("""<section class="sec"><h3>4.10 Our own indicators</h3>
<p>Three figures on the full result are <b>our own simple scores</b>, not regulatory quantities:</p>""" + tbl(
    ["Indicator", "How it is made"],
    [["<b>Cost exposure</b>", "EU ETS cost + FuelEU penalty + UK ETS cost (converted at &euro;1.15 per &pound;)"],
     ["<b>Regulatory health</b> (0 to 100)", "Points for the CII grade (A 100, B 85, C 65, D 35, E 10), minus 15 if FuelEU is in deficit, kept between 0 and 100"],
     ["<b>Compliance asset</b>", "For a FuelEU <i>surplus</i> only: half of the penalty another ship would avoid by using it. The one-half is a rule of thumb, not a market price"]]) + """
<p>They are meant for quick comparison. They have no legal meaning and should not be quoted as a valuation.</p></section>""")

# 4.11 verifier match
P.append("""<section class="sec"><h3>4.11 The check against the verifier</h3>
<p>Each ship&rsquo;s file carries the ETS-scope CO&#8322; its accredited verifier reported. We compare it with our own figure (4.2). If we are within 2%, the Verifier view says so. On a random sample of 400 ships:</p>""" + tbl(
    ["Agreement with the verifier", "Share of ships"],
    [["The same tonne (within 0.05%)", "<b>67.5%</b>"], ["Within 1%", "76.0%"], ["Within 2%", "78.2%"], ["More than 2% apart", "<b>21.8%</b>"]], "num") + """
<p>The other 21.8% usually differ because the filed figure covers only part of the year or part of the operator&rsquo;s obligation, which the public record does not break out. EMSA also publishes a separate sheet of partial-year reports that we do not yet read; testing whether it explains the gap is on the list (section 7).</p></section>""")

# 4.12 calendar
P.append("""<section class="sec"><h3>4.12 The compliance calendar</h3>
<p>This is reference data, not a calculation: the standing regulatory dates for a compliance year, each with its legal basis. A downloadable file adds them to Outlook or Google Calendar with a reminder 14 days before each date.</p>""" + tbl(
    ["Date (after the year)", "Obligation", "Basis"],
    [["31 Jan", "FuelEU report for the year to the verifier", "Regulation (EU) 2023/1805, Art. 15"],
     ["31 Mar", "Verified EU MRV report; IMO fuel data to the flag state", "Regulation (EU) 2015/757, Art. 11; MARPOL Annex VI, Reg. 27"],
     ["31 Mar", "UK ETS verified emissions report", "UK ETS (Maritime) Order 2026"],
     ["30 Apr", "FuelEU balance recorded; pooling, banking and borrowing choices entered", "Regulation (EU) 2023/1805, Arts. 20&ndash;21"],
     ["30 Apr", "Surrender UK allowances", "UK ETS Order 2026"],
     ["31 May", "Statement of Compliance and CII rating", "MARPOL Annex VI, Reg. 28"],
     ["30 Jun", "FuelEU Document of Compliance kept on board", "Regulation (EU) 2023/1805, Art. 24"],
     ["30 Sep", "Surrender EU allowances (phase-in 40% / 70% / 100%)", "Directive 2003/87/EC, Art. 12"]]) + "</section>")

# ------------------------------------------------------------------ 5 example summary
P.append(sec(5, "The example ship, end to end", tbl(
    ["Output", "Result for PETER OLDENDORFF (2025 report)", "Section"],
    [["EU ETS, 2025 rules", "5,186 allowances, <b>&euro;363,039</b>", "4.2"],
     ["EU ETS, same emissions on 2026 rules", "<b>&euro;526,805</b>", "4.2"],
     ["FuelEU", "deficit 231.6 t, penalty <b>&euro;147,759</b> (assumes heavy fuel oil)", "4.3"],
     ["UK ETS", "&euro;0 (no UK domestic voyages in public data)", "4.4"],
     ["Carbon bill, 2025 emissions", "<b>&euro;510,798</b> (ETS + FuelEU)", "&mdash;"],
     ["The same on 2026 rules", "about <b>&euro;666,386</b>", "&mdash;"],
     ["IMO NZF scenario, 2028", "<b>$366,599</b> (scenario only, not in the bill)", "4.5"],
     ["CII (typed 50,000 dwt)", "<b>E</b>, ratio 1.696 (EU-related voyages only)", "4.6"],
     ["Lever package", "<b>&euro;275,548</b> a year of carbon cost, before biofuel cost", "4.8"],
     ["Check against verifier", "7,409 t and 7,409 t: exact match", "4.11"]])
    + "<p class=\"note\">The 2026-rules total is the 2025 total with the ETS line moved from 70% to 100% of the same emissions, as the app shows it. The separate &euro;526,805 in 4.2 also adds methane and nitrous oxide, which count from 2026.</p>"))

# ------------------------------------------------------------------ 6 trust
P.append(sec(6, "How far to trust each result", tbl(
    ["Result", "Basis", "Trust", "What would improve it"],
    [["EU ETS (public data)", "The verifier&rsquo;s own scope CO&#8322;, re-weighted by the rules", '<span class="tag hi">High on volume</span>', "A live, licensed allowance price. The 2026 view"],
     ["FuelEU (public data)", "Assumes heavy fuel oil", '<span class="tag lo">Low as a position</span>', "The operator&rsquo;s actual fuel"],
     ["UK ETS (public data)", "No UK voyages in the file", '<span class="tag lo">Normally zero</span>', "Owner voyage data"],
     ["IMO NZF", "Provisional rules; scenario on today&rsquo;s fuel mix", '<span class="tag me">Scenario</span>', "The adopted text"],
     ["CII (public data)", "Typed capacity; EU-related voyages only; derived distance", '<span class="tag me">Screening only</span>', "The CII calculator with the operator&rsquo;s data"],
     ["CII calculator (owner data)", "The operator&rsquo;s fuel and distance, IMO rules in full", '<span class="tag hi">High</span>', "Verified fuel records"],
     ["EEXI (registry ship)", "The ship&rsquo;s own reported value against our reference tables", '<span class="tag me">Medium to high</span>', "A certified EEXI (if it reported an EEDI the verdict is INDICATIVE)"],
     ["EEXI (custom estimate)", "Simplified engine-power estimate", '<span class="tag lo">Indicative</span>', "The Technical File value"],
     ["Levers", "Two standard changes; carbon cost only", '<span class="tag me">Size of prize</span>', "Biofuel cost, certificates, voyage effects"],
     ["Our indicators", "Simple scores", '<span class="tag me">Comparison only</span>', "&mdash;"],
     ["Calendar", "Reference dates", '<span class="tag hi">Reference</span>', "Checking against official notices"]])))

# ------------------------------------------------------------------ 7 open
P.append(sec(7, "Known limits and open items", """
<div class="box"><ul>
<li><b>Data version.</b> The figures use the 2025 report, version 6. EMSA has published version 60. A refresh tool is built and waits for approval; numbers will change.</li>
<li><b>Partial-year reports.</b> EMSA&rsquo;s file has a separate sheet of partial reports that we do not yet read. We will test whether it explains part of the 21.8% mismatch.</li>
<li><b>Fuel type.</b> Inferred, not published. This drives FuelEU, NZF and the methane and nitrous-oxide line from 2026.</li>
<li><b>Capacity.</b> Deadweight and gross tonnage are not in the public file; CII needs them.</li>
<li><b>Allowance prices</b> are fixed assumptions. We do not use live market prices.</li>
<li><b>Biofuel</b> in the levers is assumed certified and zero-rated; real certification and pathway values vary.</li>
<li><b>Ship types.</b> Twelve types are supported. Others (for example offshore and generic passenger ships) are not scored; a custom EEXI check is offered instead.</li>
<li><b>Methane slip for LNG</b> depends on the engine type, which the public file does not give; the default is the medium-speed dual-fuel value.</li>
<li><b>NZF</b> parameters follow the April 2025 approval and must be checked against the adopted text.</li>
</ul></div>"""))

# ------------------------------------------------------------------ 8 terms
P.append(sec(8, "Key terms", tbl(
    ["Term", "Meaning"],
    [["Allowance (EUA / UKA)", "The right to emit one tonne of CO&#8322;e under the EU or UK scheme"],
     ["CO&#8322;e", "CO&#8322; plus methane and nitrous oxide, scaled by their warming potential"],
     ["Well-to-wake", "Emissions from producing and delivering a fuel plus burning it"],
     ["Capacity", "Deadweight (cargo capacity) or gross tonnage (volume), as the rule requires"],
     ["Scope", "Which voyages count: inside the EU (full), to or from the EU (half), at berth (full)"],
     ["Phase-in", "The share of emissions that must be surrendered in a given year (40%, 70%, 100%)"],
     ["Verifier", "The accredited body that checks a company&rsquo;s emissions report"],
     ["MCR, SFOC", "Maximum continuous rating (engine power); specific fuel consumption (fuel per unit of energy)"],
     ["ESTIMATE / OWNER DATA", "Our labels for results built from public data, and from the operator&rsquo;s own data"]], "")))

P.append("""<footer>Source data: EMSA THETIS-MRV public report, published under Article 21 of Regulation (EU) 2015/757. CarbonKeel&rsquo;s calculations are our own and are not endorsed by EMSA or the European Commission. All results built from public data are estimates. This document explains how the tool works; it is not legal or investment advice. Full formulas and sources: the Method page and docs/CALCULATION_NOTES.md.</footer></div></body></html>""")

html_doc = "\n".join(P)
open(OUT_HTML, "w", encoding="utf-8").write(html_doc)
print("html", round(os.path.getsize(OUT_HTML) / 1e3), "KB")

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page()
    pg.goto("file:///" + OUT_HTML.replace("\\", "/"))
    pg.wait_for_timeout(800)
    pg.pdf(path=OUT_PDF, format="A4", print_background=True,
           margin={"top": "12mm", "bottom": "14mm", "left": "10mm", "right": "10mm"})
    b.close()
print("pdf", round(os.path.getsize(OUT_PDF) / 1e3), "KB")
