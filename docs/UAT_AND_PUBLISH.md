# UAT and publish — the checklist before anyone outside sees this

Two parts. **Part A** is the test you run yourself, clicking, as a customer
would. **Part B** is the publish sequence, in order, with the points where you
stop if something fails.

Budget: Part A about 45 minutes. Part B about 45 minutes, once.

---

## Before you start: the two automated gates

Run the one-command publish gate. It runs both suites and the publish checks
(placeholders, secrets, personal files, deploy files). Red means stop.

```bash
python scripts/preflight.py -v
```

Exit 0 = ready, 1 = a check failed, 2 = code is fine but something is waiting
on you (e.g. your name in the privacy notice). The two suites on their own:

```bash
python tests/test_engines.py
```
144 hand-computed checks on the regulatory maths. Each has its arithmetic
written above it, so a pass means the number was independently derived, not
just reproduced.

```bash
python tests/test_smoke.py
```
48 checks on everything the engine tests cannot see: that the page JavaScript
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

## Part B — publish, slowly, in stages

Each stage has a gate and a rollback. Do not start a stage until the one before
it is green. **Nothing below happens without you.** Claude does not buy, sign up,
push or deploy for you.

### Stage 0 · Local — DONE
UAT passed (see `docs/UAT_REPORT.md`). Preflight: code green.

### Stage 1 · Your blockers (before anything is public) — about 15 minutes
- [ ] Edit `site/privacy.html`: replace `[[YOUR FULL NAME]]` and
      `[[YOUR COUNTRY OF RESIDENCE]]`.
- [ ] Read the retention (24 months) and provider list in the notice; change
      anything you do not want to promise.
- [ ] Generate a **new** access key and store it in a password manager:
      `python -c "import secrets;print('ck-'+secrets.token_hex(8))"`
      (the old one appeared in plain text — treat it as burnt).
- [ ] Gate: `python scripts/preflight.py` exits **0**.
- [ ] Start the trademark search (EUIPO/UKIPO, classes 9/35/42). Background task.
- [ ] Take advice on the two flags in `docs/LEGAL_REVIEW.md` (EU representative,
      international transfers). Not needed to test privately; needed before outreach.

### Stage 2 · Private soft launch — Render's own address, only you
- [ ] Create a **private** GitHub repo, push `main`.
      Check first: `git log --stat | grep -Ei "access_keys|requests.jsonl|cv|resume"` prints nothing.
- [ ] Render → New → Blueprint → pick the repo (reads `render.yaml`).
- [ ] In the Render dashboard set the two secrets:
      `CARBONKEEL_ACCESS_KEYS` = `your-new-key:founder`
      `CARBONKEEL_SUPPRESSED_IMOS` = leave empty for now.
      (`CARBONKEEL_PROXY_HOPS` is already `1`.)
- [ ] Gate: `https://<name>.onrender.com/healthz` reports `"ships": 16673`.
- [ ] Re-run UAT items **8, 10, 15, 25, 30–31, 35, 39** on that address, on your
      phone. First load can take ~50 s while the free instance wakes.
- [ ] Gate: `/privacy.html` loads; search works twice in a row from your phone
      and your laptop (confirms the rate limit is per-visitor, not shared).
- **Rollback:** suspend the Render service. Nothing else is public yet.

### Stage 3 · Domain and landing page
- [ ] Buy `carbonkeel.com` at Cloudflare Registrar (~$10.44/yr). WHOIS privacy on.
- [ ] Email Routing: `hello@` forwards to you. Send yourself a test.
- [ ] Cloudflare Pages → same repo → output directory `site`.
- [ ] DNS: `@` → Pages, `app` → Render hostname. Add the custom domain in Render.
- [ ] **If you turn Cloudflare's orange-cloud proxy on for `app`, set
      `CARBONKEEL_PROXY_HOPS` to `2`.** Otherwise every visitor looks like
      Cloudflare and shares one rate-limit bucket.
- [ ] Gate: `https://carbonkeel.com` CTAs point at `app.carbonkeel.com`, not localhost.
- [ ] `robots.txt` on the app returns the disallow rules; a Google search for a
      ship name plus "carbonkeel" returns nothing.
- **Rollback:** pause the Pages project; the app stays private by obscurity only,
  so also suspend Render if you want it fully offline.

### Stage 4 · A few friendly contacts
- [ ] Send the link to 3–5 people you trust. Ask them the step-2 question:
      "what did you think this did?"
- [ ] Watch Render's log for `CLAIM_REQUEST` lines; reply to any within 1 working day.
- **Rollback:** as Stage 3.

### Stage 5 · Outreach
- [ ] `python scripts/daily.py` and do the day it gives you.
- [ ] Demos run **locally**, not on the free tier — the cold start will
      embarrass you mid-call.

---

## Operating procedure: when someone asks to hide their ships

The website hides the figures **immediately** but a free host forgets on restart.
To make it permanent:

1. `scripts/daily.py` (local) or Render → Logs → search `CLAIM_REQUEST`.
2. Render → Environment → `CARBONKEEL_SUPPRESSED_IMOS` → append the IMO,
   comma-separated. Save (redeploys in ~2 min).
3. Email the requester: "done — your figures are hidden."
4. Also append to `data/privacy/suppressed_imos.txt` and commit, so a future
   redeploy from git keeps it.

The "Your data" page promises "straight away, and we confirm by email once it
is permanent". This procedure is how that stays true.

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
