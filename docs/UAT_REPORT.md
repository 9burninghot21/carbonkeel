# UAT report — CarbonKeel release candidate

| | |
|---|---|
| **Run date** | 4 October 2026 |
| **Tester** | Claude (executed every step below against the running app) |
| **Approving authority** | **You** — nothing here is final until you sign the last page |
| **Build under test** | git `main`, local commit, not yet published |
| **Environment** | Local: app on `:8000`, landing page on `:8112`, Chromium via the preview pane |
| **Automated gates at close** | Engine suite **144 / 144** · Smoke suite **48 / 48** · Publish gate: **code green, 1 item waiting on you** |

**How to read the status column**

- **PASS** — I executed the step and observed the expected result.
- **PASS\*** — passes, but part of it is something I cannot observe from here; the asterisk names what you must confirm yourself.
- **YOU** — a human judgement or a real-device action I cannot make for you.

---

## 1. Headline

**33 of 39 steps pass outright. Six need you:** step 2 is a judgement only you can make, and steps 4, 13, 23, 26 and 39 pass in everything I can observe but need a real scroll, mail client, hover, calendar app or phone to finish.

The UAT found **17 issues**. None are open. The three that mattered most:

1. **A JavaScript syntax error disabled the entire app** (found 3 Oct). All 144 engine tests still passed and the API still answered, because nothing was watching the page. It is now guarded.
2. **The app would have locked every visitor out on a real host.** Rate limiting keyed on the connecting address, which behind Render's proxy is the same for everyone.
3. **Your personal CVs and your access key were one `git push` from a public repository.** Twelve CV files were staged by `git add -A`, and the key was written into four of my own documents. Both are fixed and the publish gate now refuses to proceed if either recurs.

---

## 2. Defects found and fixed

| # | Severity | What was wrong | Fix | Proof |
|---|---|---|---|---|
| D-1 | **Critical** | Unescaped apostrophe in `operator's` closed a JS string; the whole app script failed to parse; every button dead | Escaped; **new smoke test parses both pages' JavaScript** | Injected the same bug back in: test failed with a line number; restored: green |
| D-9 | **High** | Rate limit keyed on socket address → behind a hosting proxy all visitors share one bucket → site locks out after ~120 lookups | Reads the real client from the right of `X-Forwarded-For`, via `CARBONKEEL_PROXY_HOPS` | 4 tests: 0, 1, 2 hops and missing header |
| D-10 | **High** | Operator-tool key was auto-generated into a file on the host's disk — unreadable to you, and wiped on restart | Keys now supplied by `CARBONKEEL_ACCESS_KEYS`; never auto-generated when set | 3 tests |
| D-11 | **High** | Suppression requests and claim log written to local disk, which a free host wipes on every sleep/restart — a "hide my data" request could silently undo itself | `CARBONKEEL_SUPPRESSED_IMOS` is the durable copy; every request also logged to the process log; confirmation offers an "email us a copy" link; **copy no longer over-promises "immediately"** | Live: request logged to stdout, link composed correctly, ship hidden then restored |
| D-14 | **High** | `git add -A` staged **12 personal CV files** from `Claude outputs/` | Folder and CV patterns gitignored; gate fails if any CV/resume/passport is tracked | Staged tree re-inspected: none |
| D-15 | **High** | Your real access key was embedded in 4 of my documents and committed | Removed everywhere; commit amended; **history searched: key in zero commits** | `git log -S` returns nothing |
| D-16 | **Blocker** | No privacy notice, yet the chat/claim forms collect name and email | Written (`site/privacy.html`), linked from every collection point, served by the app too | 9 tests + visual check |
| D-4 | Medium | Calendar showed no "today" marker when all deadlines are in the future — the reader couldn't tell where "now" sat | Marker always drawn; pins to the edge with an arrow | Verified for 2025, 2026, 2027 |
| D-5 | Medium | Method page displayed `/api/audit/{imo}?dwt=…`, which you told me not to show customers | Reworded; **test now scans the documents pages render**, not just the HTML | Doc test passes |
| D-6 | Medium | Calendar tab scrolled sideways on a 375px phone | Rows wrap on small screens | 9 screens at 375px: no horizontal scroll |
| D-7 | Medium | Nav, chips, inputs and buttons were 33–35px tall (floor is 40px) across the app | Global 40px minimum; nav and chips resized | Zero controls under 40px on all 9 screens |
| D-12 | Medium | Search was unthrottled — a route around the harvesting cap | Own budget of 900/hour (generous: ~15 calls per search), results clamped to 20 | 25 rapid searches served; clamp verified |
| D-13 | Medium | Register cache keyed on file mtime, which changes on every `git clone` → ~17 s reparse on every deploy | Keyed on a content hash | Touched the file: 0.06 s, cache hit |
| D-2 | Low | Chat email/company fields 39px | `min-height: 44px` | 0 targets under 40px |
| D-3 | Low | "Price our fleet" chip and the browser-tab title ("…Compliance, Priced") could read as "what do you charge?" — against your no-price-talk rule | Chip now "What our fleet costs"; title now "Carbon cost and compliance for your ships". **Test widened to any form of the word *price*, and proven by re-injecting the old title (fails) — the earlier check had missed the title, and an escaping slip had silently disabled my first fix to the check** | Page scan: no price words |
| D-8 | Low | App red text on navy was 4.29:1 (needs 4.5) | Lightened to match the landing page | Now 5.83:1 |
| D-17 | Low | No security headers | `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` on the app and via `site/_headers` | Headers read from a live response |

### False alarms I chased, so you know what is *not* a bug
Four of my own test probes first reported failures that were test errors, not product errors: a height measurement on collapsed `<details>` (Chromium keeps layout size), geometry read from a background tab with zero width, a case-sensitive match against text the CSS uppercases, and a timeout shorter than the first cold register load. In each case I confirmed the page was behaving correctly by a second, valid method before moving on.

---

## 3. The 39 steps

### A1 · The front door

| # | Step | Result | Evidence |
|---|---|---|---|
| 1 | Cold load: headline, no pooling, no deadline, no price | **PASS** | H1 "What is carbon costing your ships?"; hero scanned for pool/2,400/30 April/countdown: none; page scanned for pricing words: none |
| 2 | 10-second read: can you say what it does? | **YOU** | A comprehension judgement — please do this one cold, then tell me what you thought it was for |
| 3 | Logo returns to top, no leftover `#` | **PASS** | Logo is `<a href="#top">`; `goHome()` clears the hash |
| 4 | Nav links go to the right sections | **PASS\*** | All three targets exist and links point at them. The pane cannot show scrolling, so please click each once |
| 5 | Priority order ETS → FuelEU → CII → EEXI; EEXI "mostly settled" | **PASS** | Read from the DOM in order; "mostly settled" present |
| 6 | Maths drawn as maths | **PASS** | 1 fraction element, 1 superscript, **0** `^` and **0** slash-division in the equations |
| 7 | Disclosures open/close; claim is measured, not absolute | **PASS** | Closed rows report hidden, open row visible; real summary-clicks toggle; copy says "two in three", contains no "always/every ship" |
| 8 | Hero search lands on a result with no second click | **PASS** | Real click on Check → app opened with `?q=PETER+OLDENDORFF` → card rendered, no suggestion list left |
| 9 | Demo links go straight to a result | **PASS** | Bulk carrier and cruise ship each resolve to exactly one supported match; IMO route returns 200 |

### A2 · The chat

| # | Step | Result | Evidence |
|---|---|---|---|
| 10 | Bubble bottom-right, opens on the right | **PASS** | Bottom/right offsets < 40px; panel inside the viewport; button becomes ✕; `role="dialog"` with a label |
| 11 | Esc closes, focus returns to the bubble | **PASS** | `document.activeElement === bubble` |
| 12 | Bad email refused | **PASS** | "does not look right" message shown, nothing composed |
| 13 | Valid send builds the right email | **PASS\*** | Composed link has subject (category), message, reply-to, company. **I did not launch a real mail client** — please press Send once and confirm your mail app opens pre-filled |
| 14 | No price/budget/fee language | **PASS** | Panel text scanned; six categories listed |

### A3 · The app

| # | Step | Result | Evidence |
|---|---|---|---|
| 15 | Seven tabs, last is "Your data" | **PASS** | `Check a vessel · EEXI · CII calculator · My fleet · Calendar · Method · Your data` |
| 16 | Narrow window: no overlap, nothing hidden | **PASS** | 1300/1100/980/860/760/600px: no overlap, "Your data" visible at all, nav wraps to 2 rows ≤760px |
| 17 | Keyboard: ↑ ↓ Enter | **PASS** | One row highlights; Enter selects and loads the ship |
| 18 | Value chip appears by itself | **PASS** | "Value identified: up to €275,548/yr…" |
| 19 | Chip click applies levers | **PASS** | Saving banner "€275,548"; 20% / −10% prefilled; what-if panel opened |
| 20 | Three views are genuinely different | **PASS** | Owner has the bill; Tech does not; Verifier has the reproducibility record and not the bill |
| 21 | Verifier banner is honest | **PASS** | States "within 2%" / explains partial-year divergence; no "same tonne" absolute |
| 22 | DWT → CII letter, A–E bar | **PASS** | Band bar, boundaries `A≤… B≤…` printed |
| 23 | Fleet chart with sister-ship names on hover | **PASS\*** | 20+ dot titles all carry name + kg CO₂/nm; selected ship flagged; company named. The hover tooltip itself is not observable here |
| 24 | Logo returns to a clean start | **PASS** | Search, results and query string cleared; vessel tab active |

### A4 · The other tabs

| # | Step | Result | Evidence |
|---|---|---|---|
| 25 | Calendar: 8 dates, no overlap, "today" marker | **PASS** | 8 items; 0 label collisions for 2025/2026/2027; marker present each time *(fixed — D-4)* |
| 26 | `.ics` downloads and imports | **PASS\*** | `text/calendar`, 8 events, 8 alarms, well-formed. **Importing into Outlook/Google is yours to confirm** |
| 27 | EEXI registry ship: verdict + margin | **PASS** | Verdict and margin shown |
| 28 | EEXI custom example runs, labelled INDICATIVE | **PASS** | "INDICATIVE" present |
| 29 | Cruise switches capacity to GT | **PASS** | Label flips to "Gross tonnage (GT)" and back to DWT |
| 30 | CII locked, no price signal | **PASS** | Locked by default; wrong key rejected; no 🔒 / price words; badge reads "operators" |
| 31 | CII with key: D, trajectory ends E | **PASS** | Rating **D**, 5.356 vs 5.045, `C C C D D D D E` for 2023–2030 |
| 32 | Fleet: totals, sort, drill-down | **PASS** | 5 rows, totals shown, sort indicator, row click opens vessel; report 200 with FLEET TOTAL; agreement draft marked DRAFT / not legal advice |
| 33 | Method renders, no API paths | **PASS** | Renders; capacity rule MEPC.364(79) present; **0** `/api/` *(fixed — D-5)* |
| 34 | Your data explains provenance and controls | **PASS** | Cites Article 21; offers claim / correct / hide |

### A5 · Honesty and edge cases

| # | Step | Result | Evidence |
|---|---|---|---|
| 35 | Nonsense IMO: clear message | **PASS** | "IMO 0000000 not in the public export."; results area empty |
| 36 | Unsupported ship type: never a dead end | **PASS** | VIKING R (Offshore) → message with a working link to the custom EEXI check |
| 37 | ESTIMATE badge present and clickable | **PASS** | Present on the result; click opens Method |
| 38 | Footers state the honesty items | **PASS** | Estimates · Article 21 · not search-indexed · link to controls · `noindex` meta |
| 39 | Phone: no sideways scroll, thumb-sized | **PASS\*** | 375px emulation, 9 app screens + landing (all rows expanded, chat open): no horizontal scroll, no control under 40px. **Emulated — please open it once on your actual phone** |

---

## 4. What the UAT found about going live (not in the original 39)

These are invisible on a laptop and would have hurt on a real host. All are fixed and tested; they are listed so you understand why the deployment settings exist.

| Risk | Consequence if unfixed | Setting that fixes it |
|---|---|---|
| Free-tier disk is wiped on every sleep/restart | Access key lost; a "hide my data" request silently reverses | `CARBONKEEL_ACCESS_KEYS`, `CARBONKEEL_SUPPRESSED_IMOS` |
| One proxy address for all visitors | Whole site rate-limited after ~120 lookups | `CARBONKEEL_PROXY_HOPS=1` |
| Cache invalidated by deploy | ~17 s wait for the first visitor after every release | Content-hashed cache (automatic) |
| Free instance sleeps after ~15 min | ~50 s first load | Background warm-up now loads the register at startup; demos should still run locally |

**One residual you must own.** A hide request made through the website takes effect straight away on the running server, but a free host can restart and forget it. **You make it permanent by adding the IMO to `CARBONKEEL_SUPPRESSED_IMOS` in the Render dashboard**, and you do that when the "email us a copy" message (or the `CLAIM_REQUEST` line in Render's logs) tells you someone asked. The "Your data" page now says "straight away, and we confirm by email once it is permanent" — which is true — rather than the "immediately" it said before, which was not.

---

## 5. Open items — all yours

| # | Item | Why it blocks | Time |
|---|---|---|---|
| 1 | **Fill in your full name and country** in `site/privacy.html` (`[[YOUR FULL NAME]]`, `[[YOUR COUNTRY OF RESIDENCE]]`) | A privacy notice must name the controller. The publish gate fails while these remain | 2 min |
| 2 | **Approve my draft retention periods** (24 months for enquiries and requests) and the provider list (Render, Cloudflare, your email provider) | They are my drafts of *your* policy; they are your decisions | 5 min |
| 3 | **Take advice on two points** (see `LEGAL_REVIEW.md` §4): whether you need an EU representative under GDPR Art. 27 if you are based outside the EU/EEA and target EU companies; and the wording on international transfers | I flagged and drafted conservatively but cannot settle these | ~1 hr paid |
| 4 | **Generate a fresh production access key** and keep it in a password manager | The old one appeared in plain text in documents and this conversation. Run: `python -c "import secrets;print('ck-'+secrets.token_hex(8))"` | 1 min |
| 5 | Register the domain, create GitHub / Render / Cloudflare accounts | Payment and account creation — I will not do these for you | ~1 hr |
| 6 | Steps marked **YOU / PASS\*** above: 2, 4, 13, 23, 26, 39 | Need a human, a mail client, a calendar app, a phone | 20 min |

---

## 6. Sign-off

> By initialling, I confirm I have reviewed this report and accept the status shown. Initial **Reject** against any line you do not accept — it goes back to me with that line open.

| Section | Accept | Reject | Initials / date |
|---|---|---|---|
| Automated gates (engine 144, smoke 48) | ☐ | ☐ | |
| Defects D-1 … D-17 and their fixes | ☐ | ☐ | |
| A1 · Front door (steps 1–9) | ☐ | ☐ | |
| A2 · Chat (10–14) | ☐ | ☐ | |
| A3 · App (15–24) | ☐ | ☐ | |
| A4 · Other tabs (25–34) | ☐ | ☐ | |
| A5 · Honesty and edge cases (35–39) | ☐ | ☐ | |
| Items I could not verify (2, 4, 13, 23, 26, 39) — **I have checked them myself** | ☐ | ☐ | |
| Open items 1–6 in §5 are understood | ☐ | ☐ | |
| **Approved to begin the staged publish** | ☐ | ☐ | |

**Approver:** ______________________  **Date:** ______________

---

# Addendum — 5 October 2026: the opening page was not visible, and was then rebuilt

## Was the UAT complete?

**Not as a whole.** The 3 Oct run covered the earlier landing page and the app. Two things followed:

1. **D-18 · Critical for you: you could not see the first page.** The opening page needed a *second* server on a different port (`:8112`) to be started by hand, and both servers had stopped when the session ended. The page, opened directly, had nothing behind its search box. I should have caught that a founder double-clicking the file would hit this.
   **Fix:** the app now serves the opening page itself at `/home`, so **one server, one address** shows the whole journey. A double-click launcher, `Start CarbonKeel.bat`, starts it and opens the page. If the app is ever off, the page now says so in plain words instead of failing silently.
2. **You asked for a new opening page**, so steps 1–9 (front door) are **re-opened**: they were passed against a page that no longer exists.

## What I checked on the new page

Browser pane, desktop width 1360 and phone width 375, driven to each scroll position:

| Check | Result |
|---|---|
| No console errors; all 3 inline scripts parse | PASS |
| Hero: sunrise sky, sun, clouds, three layers of waves, four ships, CO₂ puffs, search box | PASS (seen) |
| Counters finish on the exact register values (16,673 · 4,047 · 87.3 Mt · €6.1 bn · €511k · €367k) | PASS (read from the page after the count) |
| **Voyage:** ship follows the route; stops 1–4 light up in order; text changes with each stop; stepper fills | PASS at four positions |
| Services cards animate in with their own mini-graphic | PASS |
| "Where we are strongest" band, five tiles | PASS |
| Result card + three cost drivers; pin and trail animate | PASS |
| Night harbour: stars, moon, lighthouse beam, moored ship, working search | PASS (after fixing D-19) |
| Phone width: no sideways scroll; voyage stacks chart over text | PASS |
| Reduced-motion, and a safe fallback if the motion script ever fails | In code and tested for presence; **not** seen on screen |

**New defects found and fixed during this pass**

| # | What was wrong | Fix |
|---|---|---|
| D-18 | First page not visible (above) | `/home` route, launcher, "app not running" notice |
| D-19 | The final "Check a ship" button became a giant yellow circle, because its class name collided with the hero's sun | Renamed; verified |
| D-20 | Logo showed "Carbon Keel" with a gap | Fixed |
| D-21 | Ships bunched together at the left of the hero on load | Start positions spread out |
| D-22 | Two voyage steps could briefly show at once during the cross-fade | Outgoing step now clears before the next appears |
| D-23 | Footer text links were 18px tall (floor is 40px) | Enlarged |
| D-24 | Browser-tab title read "…Compliance, Priced" (could suggest a price list) | Reworded; test widened and proven |

**New automated guards (smoke suite now 66 checks)**
- The numbers on the page must equal `data/market_stats.json`; I changed one figure and confirmed the test fails.
- The page makes **no third-party requests** (no fonts, trackers or CDNs).
- The sections the navigation relies on exist; reduced-motion and the fallback are present.
- `/home` answers 200.

## What I could not verify (yours)

| # | What | Why it needs you |
|---|---|---|
| N1 | **Does it impress you?** Colour, mood, amount of movement | A judgement only you can make |
| N2 | **Smoothness while scrolling** on your machine | The test pane does not run animation frames, so I saw each scroll position correctly but could not judge frame rate |
| N3 | Real phone | I emulated phone width; I did not hold a phone |
| N4 | The first-page "10-second" test, again | Step 2 must be re-done on the new page |

**Please re-initial the A1 row of the sign-off table above** after you have looked at the new page. Until then A1 stands **re-opened**.


---

# Addendum 2 — 5 October 2026: grammar and usage audit, the app restyled, and the data source checked

You asked for three things. This is what I did, what I found, and what is still yours to approve.

## 1. Grammar and usage audit

Method: I extracted every sentence a person can read (page markup, the text the scripts build, the text the server sends, and the two documents the app displays), ran a spell checker, then read it all against a house style: **British English; "ship", not "vessel"; "Article 21", not "Art. 21"; "EU MRV", not "EU-MRV"; "about", not "~"; acronyms spelled out on first use; typographic apostrophes**.

Spelling was clean. The real findings were in usage:

| # | Severity | What was wrong | Fixed |
|---|---|---|---|
| D-25 | **High** | The compliance calendar showed the placeholder **"year-Y"** to users, and repeated "(compliance year 2026)" on every line | Yes. Dates also now read "31 Jan 2027", not "2027-01-31" |
| D-26 | **High** | **Every button and input on both pages rendered at 13px, not the intended 15px**, because `font: 700 15px/1.2 inherit` is invalid CSS and browsers drop the whole line. It was on the opening page too | Yes (14 declarations). Guarded by a test I proved by re-injecting the bug |
| D-27 | **High** | **An unmeasured accuracy claim in three more places**: the Method page ("exactly on spot checks"), the printable fleet report ("spot-checks reproduce the reported figure exactly") and the launch-kit cold email ("we land on the same tonne"). Our measured result is exact for about two ships in three | Yes: all three now state the measured figures |
| D-28 | **High** | **A wrong legal citation.** The "Your data" page and the legal review cited "Article 21(6)" for alternative publication. Paragraph 6 is about EMSA assisting the Commission; the right is **Article 21(3)** and applies only to aggregated data *not relating to emissions*. The legal review also said EMSA imposes "no licence restriction", which I could not support | Yes, corrected, with sources in `docs/DATA_SOURCES.md` |
| D-29 | Medium | **Data-file selection sorted names as text**, so once EMSA's version reached three digits the app would load v60 instead of v100 | Yes: one shared helper orders by (year, version). Proven with a test |
| D-30 | Medium | A raw file name ("thetis_mrv_2025_v6.xlsx") was shown as the data source | Yes: "EMSA THETIS-MRV, 2025 report, version 6" |
| D-31 | Medium | **Contradictory and unclear wording**: "CII rated E… If E, or 3rd consecutive D…"; "bank-borrow"; unexplained SoC, fw, OMM, EPL/ShaPoLi, BDN, DoC, STS; "hedge EUA purchases" (reads as trading advice); Python-style quotes in the unsupported-ship message; "registry" (means a flag registry, not the public register); "the matchmaking service" for a service that does not exist; a leaked internal field name (`uk_share`); an emoji; a raw "Request failed: TypeError" shown to users | Yes, all |
| D-32 | Medium | Method page quoted "96 checks" (now 144) and "six engines" (there are seven sections) | Yes |
| D-33 | Low | The CII pointer label wrapped over the band labels at the right edge | Yes |
| D-34 | Low | Under a D rating the page said the next band is C, then repeated "reaching C needs 0.2%" | Yes |
| D-35 | Low | The "IMO NZF" bill row was built differently from the other rows and cramped on a phone | Yes |
| D-36 | Low | A missed "vessel" in the opening page's intro, found by the new test | Yes |

A **style and data-source suite** (`tests/test_style.py`, 64 checks) now guards all of this, and the publish gate runs it.

## 2. The app restyled

Same palette, type, buttons and focus ring as the opening page, but calm and data-first: light surfaces, one accent, **no artwork or motion**. The bill is the largest thing on the screen. Equations on the Method page are drawn as fractions and superscripts, like the opening page.

| Check | Result |
|---|---|
| Text contrast, WCAG AA (4.5:1), **525 text elements across six tabs, measured from the rendered colours** | **0 failures.** (The checker flags the gradient buttons; those are white on blue at 5.3:1 or better) |
| Tap targets at phone width, seven tabs | none under 40px |
| Sideways scroll at 375px, seven tabs | none |
| Result view, CII calculator, EEXI, fleet, calendar, Method | seen on screen |
| Key file | a temporary test key was added to your local key file for the CII check and the file was **restored byte-for-byte** afterwards |

## 3. The data source

See `docs/DATA_SOURCES.md`. In short:

- **Public by law:** yes (Article 21(1)–(2), including the company name). EMSA says the files can be "exported in a spreadsheet for further analysis".
- **Reuse:** EMSA's copyright notice authorises reproduction "provided the source is acknowledged". We acknowledge EMSA, label our figures as rebuilt, and say EMSA does not endorse us. **Gap:** no licence text written for these files, so a written confirmation is worth asking for (draft included).
- **Fetchable:** yes, no login. `python scripts/fetch_thetis.py` checks; `--download 2025 --yes` fetches.
- **Our copy is stale:** we hold 2025 **v6**; EMSA lists **v60**, generated the morning of 5 October.

**I did not download anything.** It needs your approval (see the summary).

## Still open from this round

| # | Item | Owner |
|---|---|---|
| N5 | Approve the data refresh (about 21 MB: 2025 v60 and 2024 v246). Then the landing-page numbers and the outreach reports must be regenerated | You |
| N6 | The 11 outreach reports already generated still contain the old accuracy claim and must be regenerated before any is sent | After N5 |
| N7 | Send (or decline to send) the reuse-confirmation message to the THETIS helpdesk | You |
| N8 | The cold-email draft in `docs/LAUNCH_KIT.md` still **leads with pooling and the 30 April deadline**, which you said you do not want to lead with on the front page. I fixed its accuracy claim and removed "the part that pays for us", but left the framing for you to decide | You |
