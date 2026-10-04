# The plan — 1 hour a day, 1 Oct 2026 → 30 Apr 2027

Run `python scripts/daily.py` at the start of every hour. It tells you the
day's single task, your pipeline, who needs a follow-up, and the countdown.
This document is the reasoning behind it; the console is the thing you obey.

## Why these seven months

The 30 September ETS surrender just passed — that hook is spent for a year.
What replaces it is better:

| Date | Days | What happens |
|---|---|---|
| **Oct 2026** | ~30 | IMO NZF adoption vote reconvenes (adjourned Oct 2025). A media moment either way; both announcements are pre-written. |
| **31 Dec 2026** | 91 | FuelEU 2026 compliance year closes. Every owner's balance is then **fixed** — surplus or deficit, nothing more can change it. |
| **31 Jan 2027** | 122 | FuelEU reports go to verifiers. Owners learn their real number. |
| **30 Apr 2027** | **211** | **Pooling registration closes.** After this the only exit from a deficit is the €2,400/t penalty. |

That last line is the whole business. A deficit becomes unavoidable money on
1 May 2027. Everything between now and then is about being the person holding
both sides of that trade when owners go looking for a way out.

## The one number that defines the strategy

`python scripts/daily.py --surplus` scans the whole register:

- **Surplus across every LNG operator in the EU trade: ~5,200 tCO₂e.**
- **Technomar alone is short 20,800 t.** Anglo-Eastern, 12,400 t.

Demand for surplus exceeds supply by orders of magnitude. So:

> **Recruit the surplus side first.** Knutsen, Nakilat, MOL, Maran Gas and the
> other LNG operators are scarce, have pricing power they probably have not
> priced, and are the inventory your marketplace sells. Sign them to a
> non-binding "we would consider pooling" note before anyone else asks.

Deficit owners will come to you — they have a bill. Surplus owners need to be
told they are sitting on an asset. That asymmetry is your opening line to each.

---

## Week 1 — cold start (the console walks you through days 1–9)

| Day | Date | The hour |
|---|---|---|
| 1 | Thu 1 Oct | Buy carbonkeel.com (~€10, WHOIS privacy on). Run `--targets 10`. |
| 2 | Fri 2 Oct | Find one named contact per company on LinkedIn. No sending. |
| 3–4 | weekend | Off. |
| 5 | Mon 5 Oct | `make_reports.py --top 10 --pdf`, send the first 5 with PDFs. |
| 6 | Tue 6 Oct | Send the other 5. Then close the laptop. |
| 7 | Wed 7 Oct | `--targets 10` again + contacts. Answer replies first. |
| 8 | Thu 8 Oct | Send 5 new. Follow up days 5–6 non-repliers. |
| 9 | Fri 9 Oct | Build session with me. Review week-1 reply rate. |

**Day 1 non-negotiable:** the domain. Everything else can slip a day; a
registered domain cannot be bought back once someone else takes the name.

## The weekly rhythm (from day 10 onward)

| | Task |
|---|---|
| **Mon** | `--targets 10` + find contacts |
| **Tue** | Send 5 (with PDFs) |
| **Wed** | Send 5. Replies always outrank new sends. |
| **Thu** | Follow-ups + any call |
| **Fri** | Build session with me |
| **Sat/Sun** | Off — this is a seven-month run, not a sprint |

**10 sends per week ≈ 40 a month.** At a 10–15% reply rate that is 4–6 live
conversations a month, which is enough to hit the gates below and few enough
to handle personally in an hour a day.

---

## Phases and the gate that ends each

### A · LAUNCH — 1–14 Oct
Domain live, 20 messages out.
**Gate:** 20 sent, ≥1 reply. No reply from 20 personalised messages means the
message is wrong, not the market — we rewrite before sending more.

### B · NZF MOMENT — 15–31 Oct
The vote reconvenes this month. `outreach/NZF_vote_announcements.md` holds
both versions, written in advance.
**On the day:** publish within hours (speed is the entire advantage), then
email every live contact their updated number. 20 more sends.
**Gate:** published same day; 40 total sent; ≥3 replies.

### C · DESIGN PARTNERS — November
Convert conversations into **3 partners sending real noon-report data**, free,
in exchange for feedback and a testimonial.
**Why it matters:** owner data removes the ESTIMATE label, and real bunker
data is the only way to find biofuel/methanol surplus holders the public data
cannot see.
**Gate:** 3 partners, ≥1 fleet's real data ingested.

### D · YEAR-END POSITION — December
The compliance year closes 31 Dec. Send **every** contact their near-final
2026 position: deficit size, penalty exposure, pooling alternative.
**Gate:** every live contact has received a year-end position; the surplus
book has ≥3 named holders.

### E · POOL BOOK — Jan–Feb 2027
Verifier numbers land in January. Match surplus to deficit with the optimiser;
generate agreements with `/api/pool-agreement`.
**Gate:** ≥1 pool agreed in principle between two parties.

### F · CLOSE POOLS — Mar–Apr 2027
Registration closes 30 April. Hard deadline, no extension.
**Gate:** ≥1 pool registered, first success fee invoiced.

---

## Money: spend nothing until the market says otherwise

| Trigger | Spend |
|---|---|
| Day 1 | Domain ~€10 |
| First reply asking for a link | Email on the domain ~€5/mo |
| A prospect wants self-serve access | Free-tier hosting (Render/Railway) |
| A pilot wants a contract | Incorporate — not before |

## Rules that keep the hour honest

1. **A reply outranks everything.** Never send new messages with an unanswered
   reply in the inbox.
2. **Never send a report you have not looked at.** The numbers are estimates;
   you are the last check.
3. **Log every action** (`--log sent|reply|call|...`). An unlogged send is an
   invisible pipeline and you will lose track by week 3.
4. **Friday builds only.** Building on a Tuesday is procrastination wearing a
   productive costume. The product is already ahead of the market work.
5. **If a week produces zero replies twice running, stop sending** and spend
   the Friday hour rewriting the message with me instead.

## What is already built and waiting

- 311 ICP companies ranked by verified exposure (`outreach/targets_2025.csv`)
- 10 fleet PDFs pre-generated (`outreach/reports/`)
- Live demo: vessel lookup → value chip → Owner/Technical/Verifier views
- CII calculator (locked, key `<your-access-key>`), EEXI free check,
  pooling optimiser, agreement generator, compliance calendar, audit worksheets
- 143 hand-computed engine tests, green

Nothing on that list is the bottleneck. **The bottleneck is that zero messages
have been sent.** Day 1 fixes that.
