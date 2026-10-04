# UAT and publish — the checklist before anyone outside sees this

Two parts. **Part A** is the test you run yourself, clicking, as a customer
would. **Part B** is the publish sequence, in order, with the points where you
stop if something fails.

Budget: Part A about 45 minutes. Part B about 45 minutes, once.

---

## Before you start: the two automated gates

Run both. If either is red, stop — do not start clicking.

```bash
python tests/test_engines.py
```
144 hand-computed checks on the regulatory maths. Each has its arithmetic
written above it, so a pass means the number was independently derived, not
just reproduced.

```bash
python tests/test_smoke.py
```
24 checks on everything the engine tests cannot see: that the page JavaScript
actually parses, that the endpoints answer correctly, that the CII calculator
is really locked, and that no customer-facing copy leaks an API path or a
price.

> **Why the second one exists.** On 3 Oct a stray apostrophe in the word
> `operator's` closed a JavaScript string early. The whole app script failed to
> parse and every button in the browser stopped working — while all 144 engine
> tests still passed and the API still answered perfectly. Nothing was watching
> the page. Now something is. The guard was verified by re-injecting that exact
> bug and confirming it fails the build.

Then start the two servers:

```bash
python -m uvicorn api.main:app --port 8000
```
```bash
cd site && python -m http.server 8112
```

---

## Part A — the UAT script

Mark each **PASS / FAIL**. Anything that makes you hesitate is a FAIL; write
down what you expected instead.

### A1 · The front door — `localhost:8112`

| # | Do this | Expect |
|---|---|---|
| 1 | Load the page cold | Headline reads *"What is carbon costing your ships?"*. No pooling, no deadline countdown, no price anywhere |
| 2 | Read for 10 seconds only, then look away | You can say what this does and who it is for |
| 3 | Click the **CarbonKeel** logo | Returns to the top; the address bar has no leftover `#anchor` |
| 4 | Click **What it costs**, **What matters first**, **Talk to us** | Each scrolls to the right section |
| 5 | Read the "What matters first" list | Order is ETS → FuelEU → CII → EEXI, and EEXI is marked *mostly settled* |
| 6 | Look at the maths block | A real fraction (one line over another) and a raised exponent. No `^` and no `/` |
| 7 | Open each disclosure under "How the numbers are worked out" | Opens and closes; the verifier claim states measured figures, not "always" |
| 8 | Type a ship name in the hero box and press Check | Lands in the app **with the result already on screen** — no second click |
| 9 | Click **a bulk carrier**, then **a cruise ship** | Both go straight to a scored result |

### A2 · The chat

| # | Do this | Expect |
|---|---|---|
| 10 | Click the bubble, bottom right | Panel opens on the right; the bubble becomes a close button |
| 11 | Press **Esc** | Panel closes, focus returns to the bubble |
| 12 | Reopen, pick a category, type a line, add a bad email, click Send | It refuses and tells you the email is wrong |
| 13 | Fix the email, click Send | Your mail app opens, pre-filled with category, company and message |
| 14 | Read every word in the panel | No mention of price, fees, budget or plans |

### A3 · The app — `localhost:8000`

| # | Do this | Expect |
|---|---|---|
| 15 | Count the tabs | Seven, ending with **Your data** — none hidden behind the search box |
| 16 | Narrow the window to about half-screen | Nav still readable; search drops to its own row; nothing overlaps |
| 17 | Search `OLDENDORFF`, use ↑ ↓ then Enter | Keyboard alone selects a ship |
| 18 | On the result, wait a moment | A green *"Value identified"* chip appears by itself |
| 19 | Click that chip | Levers fill in and a saving is shown against the baseline |
| 20 | Switch **Owner / CFO → Technical / Ops → Verifier** | Same ship, three genuinely different framings |
| 21 | On Verifier, read the banner | Either agreement within 2%, or an explanation of why it differs |
| 22 | Back on Owner, type a DWT and click Add | CII letter, the A–E bar, and the fleet-context chart appear |
| 23 | Hover dots on the fleet chart | Sister-ship names appear |
| 24 | Click the **CarbonKeel** logo | Back to a clean opening state, search cleared |

### A4 · The other tabs

| # | Do this | Expect |
|---|---|---|
| 25 | **Calendar** → Show deadlines | 8 entries; timeline dates **do not overlap**; "today" marker visible |
| 26 | Download the .ics and open it | Imports into your calendar with reminders |
| 27 | **EEXI** → check a registry ship | A verdict with a margin percentage |
| 28 | **EEXI** → custom vessel → *Try an example* | Runs; result is labelled INDICATIVE |
| 29 | Pick **Cruise** in the custom form | The capacity label changes to **GT** |
| 30 | **CII calculator** | Locked. Badge says *operators* — nothing suggesting a price |
| 31 | Enter key `<your-access-key>`, then *Try an example* | Rating **D**, and a 2025→2030 strip ending in **E** |
| 32 | **My fleet** → paste 3–5 IMO numbers → Analyse | Table with totals; click a row to drill into the vessel |
| 33 | **Method** | Formulas and sources render; no raw API paths |
| 34 | **Your data** | Explains provenance and the controls |

### A5 · Honesty and edge cases

| # | Do this | Expect |
|---|---|---|
| 35 | Search a nonsense IMO like `0000000` | A clear message, not a crash |
| 36 | Find an offshore/unsupported ship type | Error offers the custom EEXI route — never a dead end |
| 37 | Look for the ESTIMATE badge on any public-data result | Present, and clicking it explains the method |
| 38 | Read the footer on both sites | Estimate labelling, Article 21, suppression right, not-advice |
| 39 | Open the app on your phone | No sideways scrolling; buttons are thumb-sized |

**Stop and tell me if any of 1–39 fails.** Send the number and what you saw.

---

## Part B — publish, in this order

Each step has a gate. Do not pass a gate that is red.

### B1 · Legal, before anything is public
- [ ] Write the **privacy notice** — what the chat and claim forms collect
      (name, company, email), why, and how to have it deleted.
      *(From `docs/LEGAL_REVIEW.md` §4. This is the one genuine blocker.)*
- [ ] Confirm `data/access_keys.txt` and `data/privacy/requests.jsonl` are in
      `.gitignore` — they are, but confirm after any repo change.
- [ ] Start the **trademark search** (EUIPO/UKIPO, classes 9/35/42). It can run
      in the background; it blocks incorporation, not launch.

### B2 · Register the domain — about 10 minutes
- [ ] Buy `carbonkeel.com` at **Cloudflare Registrar** (~$10.44/yr, at cost).
- [ ] Turn **WHOIS privacy** on.
- [ ] Set up **Email Routing** so `hello@carbonkeel.com` forwards to your inbox.
- [ ] Send yourself a test mail and confirm it arrives.

> Until this is done, every CTA falls back to `127.0.0.1:8000` automatically,
> so nothing is broken locally — but nothing is shareable either.

### B3 · Push the code
```bash
git init && git add . && git commit -m "CarbonKeel"
```
- [ ] Push to a **private** GitHub repo.
- [ ] Verify the two secret files are **not** in the commit:
      `git log --stat | grep -E "access_keys|requests.jsonl"` returns nothing.

### B4 · Deploy
- [ ] **Render** → New → Blueprint → pick the repo. It reads `render.yaml`.
- [ ] Wait for the build, then open `/healthz`. It must report
      `"ships": 16673` — if it reports 0, the export did not ship.
- [ ] **Cloudflare Pages** → new project → same repo → output directory `site`.
- [ ] DNS: `@` → Pages, `app` → your Render hostname.

### B5 · Prove it in public
- [ ] Open `https://carbonkeel.com`. Confirm CTAs now point at
      `app.carbonkeel.com`, **not** localhost.
- [ ] Repeat UAT items **8, 10, 15, 25, 31** against the live site. The first
      load may take ~50 s while the free instance wakes.
- [ ] Check `https://app.carbonkeel.com/robots.txt` returns the disallow rules.
- [ ] Search Google for a ship name plus "carbonkeel" — nothing should appear.

### B6 · Only then, outreach
- [ ] `python scripts/daily.py` and do the day it gives you.
- [ ] Demos run **locally**, not on the free tier — the cold start will
      embarrass you mid-call.

---

## Optimisation — what I would and would not do next

**Worth doing**
1. **Keep the smoke test in front of every change.** It is now the cheapest
   insurance you own.
2. **Warm the free instance** before any scheduled call: open the app ten
   minutes early, or ping `/healthz` from a free cron.
3. **Re-run the 400-ship agreement test** after any engine change and update
   the on-page figures if they move (`docs/LEGAL_REVIEW.md` §3).

**Not worth doing yet**
- Faster search. It is already 323 ms cold and ~6 ms warm; the page loads in
  49 ms at 88 KB. Nobody will leave because of speed.
- Accounts, billing, a CDN, a database. No users yet. Every hour spent there is
  an hour not spent on the first ten emails.

**The honest state.** The product is well ahead of the market work. Nothing in
Part B takes more than an afternoon, and none of it is what is actually
stopping you — zero messages have gone out.
