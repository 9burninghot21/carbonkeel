# What is needed next — and why the data says so

Updated 5 Oct 2026. Every market figure below is produced by
`python scripts/market_data.py` from the EMSA public register (2025 reporting
year, v6 export) and saved in `data/market_stats.json`. Euro values are
**ESTIMATES**: verifier-reported ETS-scope CO₂ × an assumed €70 per allowance
(sensitivity at the end). Nothing here is typed by hand, and the landing page
is tested against the same file.

---

## 1. The one-paragraph answer

The product is ahead of the market work. The register holds **16,673 ships**
across **4,047 companies**, with about **87 Mt of CO₂ in EU ETS scope, roughly
€6.1 bn a year** at €70. The part of that you can realistically sell to first is
**237 mid-size companies** (10–50 ships, mostly container, bulk or tanker)
operating **4,518 ships** with about **€1.4 bn** of ETS exposure. The
launch plan is on **day 5 of 9** and **zero messages have gone out**. The next
requirement is not another feature. It is: finish four founder tasks, put the
site on a private address, and send the first five messages with a report
attached.

---

## 1b. Found on 5 October: our data is stale, and that comes first

EMSA regenerates its public files as operators and verifiers submit amendments.
**We hold 2025 v6; EMSA now lists v60** (generated 5 October). 2024 is v228 against
v246. Every figure on the opening page, in the reports and in this document comes from
the older file. So before outreach:

1. **Approve and run the refresh**: `python scripts/fetch_thetis.py --download 2025 2024 --yes`
   (about 21 MB; it validates the files before keeping them).
2. `python scripts/market_data.py`, then update the numbers on the opening page (the
   test in `tests/test_smoke.py` names any that no longer match).
3. **Regenerate the outreach reports.** The 11 already generated carry the old
   accuracy claim and the old data.
4. Test the hypothesis that the **Partial ERs sheet** (1,505 reports in the v6 file,
   which the loader does not read) explains part of the 17% of ships where our
   rebuild and the verifier disagree.

Full source and licence analysis: `docs/DATA_SOURCES.md`.

---

## 2. What the data says about *who* to approach

### Where the carbon is, by company size

| Fleet size | Companies | Ships | ETS CO₂ | Share of all ETS CO₂ |
|---|---:|---:|---:|---:|
| 1 ship | 2,333 | 2,333 | 9.1 Mt | 10% |
| 2–9 ships | 1,326 | 5,387 | 21.2 Mt | 24% |
| **10–50 ships** | **366** | **6,916** | **37.6 Mt** | **43%** |
| 51+ ships | 22 | 2,037 | 19.5 Mt | 22% |

**Reading it.** 366 companies hold 43% of the carbon. They are big enough to
have a real bill and a person responsible for it, and small enough not to have
built their own tooling. That is your customer, and the data confirms the
original ICP rather than just assuming it. The 22 very large operators are
a different sale (long, enterprise, probably in-house tools). The 2,333
one-ship owners are too many, too small, and each is a separate conversation.

Concentration: the top 10% of companies (about 400) carry **76%** of the
carbon. A few hundred conversations is the whole serious market.

### Where the pain is, by ship type

| Type | Ships | ETS CO₂ | Share of CO₂ | Est. cost per ship, a year |
|---|---:|---:|---:|---:|
| Cruise | 206 | 5.3 Mt | 6.1% | €1.8 m |
| Ro-pax | 407 | 9.0 Mt | 10.4% | €1.55 m |
| LNG carrier | 406 | 5.1 Mt | 5.8% | €0.87 m |
| **Container** | **2,368** | **28.3 Mt** | **32.4%** | **€0.84 m** |
| Oil tanker | 1,990 | 9.7 Mt | 11.1% | €0.34 m |
| Chemical tanker | 1,615 | 5.5 Mt | 6.3% | €0.24 m |
| General cargo | 2,715 | 5.2 Mt | 5.9% | €0.13 m |
| **Bulk carrier** | **4,718** | **7.5 Mt** | **8.5%** | **€0.11 m** |

**Two things to notice.**

1. **Container ships are 14% of ships and 32% of the carbon.** A container
   operator's bill is more than seven times a bulk operator's, per ship. If the
   goal is the first customers, a container-heavy manager is the strongest
   opening.
2. **Bulk carriers are the largest group by count (28% of ships) but only 8.5%
   of the carbon**, about €110k each. "A six-figure bill" is true for bulk;
   for containers it is closer to seven figures. The landing page says
   "six-figure" because it is true for the largest group, and the average
   across the register is **about €367k per ship**.

**Requirement.** Re-sort the outreach list so a company's *total* exposure, not
its fleet count, decides the order, and consider a container-first first-twenty.
`outreach/targets_2025.csv` already holds 311 companies (8–60 ships, at least
half container/bulk/tanker) ranked by estimated allowance cost.

---

## 3. What the data says about *what to build*

Ranked by how much of the data's carbon and money each item touches.

| # | Requirement | Why the data says it | Size of the prize |
|---|---|---|---|
| 1 | **Make the first-contact report excellent** (`make_reports.py --top 10 --pdf`) | It is the only asset sent *before* anyone has heard of you. 311 target companies already have fleets mapped | Each report carries a real number, e.g. a top target shows **€37.9 m** of ETS exposure |
| 2 | **Close the verifier-match gap** | We match exactly on **68.5%** of ships, within 2% on 77%; **17% differ by more than 2%**, and 6% report zero. An operator who checks one of those will doubt everything | Every point of match rate is trust. Test whether the partial-reports sheet (1,505 rows, not yet read) explains the common cause, alongside part-year filings and the 50% voyage rule |
| 3 | **Remove the capacity (DWT/GT) friction for CII** | The register does not publish capacity, so every CII rating needs a typed number. CII sits third in priority but is the most-asked-about | Pre-filling capacity for the 4,518 ships in the 237 target fleets would turn a form into a result |
| 4 | **Let an operator state their fuel** | FuelEU is currently estimated by assuming heavy fuel oil (LNG for LNG carriers). It is the second-largest cash item | Any operator running LNG, methanol or biofuel will see a wrong number until they can say so |
| 5 | **Container and ro-pax drill-down** | Together 43% of all ETS CO₂ from 2,775 ships | Voyage-level views matter most where each ship's bill is seven figures |
| 6 | **NZF scenario ready for the October vote** | IMO net-zero framework vote reconvenes **31 Oct 2026**, 26 days away. `nzf.py` is parameterised but unconfirmed | A fast, correct update the week it passes is a credibility moment |

**Deliberately not on the list:** accounts, billing, a database, a CDN,
pooling. None has a customer behind it yet. Pooling stays out of the front
of the site until there is a counterparty base.

---

## 4. What is needed from *you*, in order

The launch plan (`python scripts/daily.py`) says today is **Day 5: generate
PDFs and send the first five messages**. Day 5 cannot start until the domain
and site exist. In the order that unblocks everything:

| # | Task | Why it is yours | Time |
|---|---|---|---|
| 1 | Open the first page and look at it (double-click **Start CarbonKeel.bat**, then it opens `http://127.0.0.1:8000/home`) | I cannot judge "does this impress you" | 5 min |
| 2 | Fill `[[YOUR FULL NAME]]` and `[[YOUR COUNTRY OF RESIDENCE]]` in `site/privacy.html` | Names the legal controller | 2 min |
| 3 | Generate a **new** access key, put it in a password manager | The old one was exposed in plain text | 1 min |
| 4 | Tell me: **keep the landing page `noindex` or let search engines find it?** | Today it asks search engines not to list it. Fine while private; a public marketing page usually wants to be found. Your call | decision |
| 5 | Create the private GitHub repo, Render and Cloudflare accounts; buy the domain | Account creation and payment | ~1 hr |
| 6 | Take advice on GDPR Art. 27 and international transfers | Legal judgement | ~1 hr paid |
| 7 | Send the first five messages, each with its company's own PDF | Outbound messages are yours to send | Day 5 |

---

## 5. How to know it is working, with no trackers

The site deliberately sets no cookies and runs no analytics. Measure instead
with things you already own:

| Signal | Where it shows up |
|---|---|
| Someone looked up their own ship | Render logs: searches by name or IMO |
| Someone claimed, corrected or hid a ship | `CLAIM_REQUEST` lines in Render logs, and `scripts/daily.py` |
| Someone wrote to you | Your inbox, via the chat or the contact form |
| Outreach is landing | `python scripts/daily.py --week` (replies, calls, reports sent) |

**First targets, 30 days:** 20 messages out; 5 replies; 2 calls. If 20 messages
produce no reply, change the message before changing the product.

---

## 6. Sensitivity — the euro figure depends on one assumption

| Allowance price | ETS bill, whole register (ESTIMATE) |
|---|---:|
| €60 | €5.2 bn |
| **€70 (used)** | **€6.1 bn** |
| €80 | €7.0 bn |
| €90 | €7.9 bn |

Reported CO₂ in 2025 is used as the 2026 run-rate. In 2025 only 70% of
emissions were surrendered; **from 2026 it is 100%**, so the 2026 bill is on
the 100% basis shown here.

**Limits of this analysis.** Companies are counted as the "Document of
Compliance holder" EMSA reports; a group that operates through several legal
entities appears as several companies, so the 237 and 366 counts are
approximate. Capacity is not public, so no CII distribution can be computed
from the register alone. Re-run `python scripts/market_data.py` whenever EMSA
publishes a new export.
