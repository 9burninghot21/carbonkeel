# Legal review — 2 October 2026

A working review of the legal exposure in what we publish and collect. This is
engineering diligence, not legal advice; the items marked **GET ADVICE** are
worth a paid hour with a lawyer before revenue.

---

## 1. Publishing other operators' emissions data — CLEAR

**What we do.** Republish verified emissions for ~16,673 ships, and publish our
own derived figures about them.

**Why it is lawful.** Article 21(1)–(2) of Regulation (EU) 2015/757 (consolidated
text of 1 January 2024) *obliges* the Commission to make this data publicly
available by 30 June each year, including each ship’s name, **company**, IMO
number, annual emissions and fuel use. EMSA publishes it for download with no
login (checked 5 October 2026). EMSA’s own page says the information "can be
exported in a spreadsheet for further analysis", and its copyright notice says
reproduction is authorised provided the source is acknowledged. We acknowledge
EMSA on every surface, say that figures are rebuilt, and say that EMSA does not
endorse them. **Full analysis, with sources: `docs/DATA_SOURCES.md`.**

**What we could not find.** A licence statement written specifically for the
THETIS-MRV files. The general EU reuse position (attribution, no distortion of
meaning) applies, but a one-line written confirmation from the THETIS helpdesk
costs nothing and closes the gap. A draft is in `docs/DATA_SOURCES.md`.

**No personal data is involved in the ship data itself.** Ships and shipping
companies are legal entities; GDPR protects natural persons. (A sole trader
operating under a personal name is a theoretical edge case; none appear in the
ICP.)

**Residual risk: low.** Keep attribution, and refresh from source
(`python scripts/fetch_thetis.py`) so corrections EMSA publishes carry through.
Note that Article 21(3) lets a company ask for a different level of
aggregation only for aggregated data *that does not relate to greenhouse-gas
emissions*; it gives no right to hide emissions or fuel figures.

## 2. Our *derived* figures about third parties — MANAGED

Our cost, rating and penalty numbers are our arithmetic about someone else's
ship. Nobody can compel us to publish them, and nobody can compel us to stop
publishing the EMSA facts.

**Controls in place:** immediate suppression on request (no human in the loop,
no negotiation), `noindex` plus robots.txt, anonymous rate limiting, a
8-ship cap on anonymous fleet analysis, and no bulk export.

**Residual risk: low**, provided the ESTIMATE labelling stays. The single
biggest legal protection we have is that we never present a derived figure as
an official one.

## 3. Advertising claims — ONE CORRECTED TODAY ⚠

Misleading commercial claims are actionable under the Unfair Commercial
Practices Directive and national equivalents, regardless of intent.

**The claim we had:** *"We rebuild your verifier's own figure — and land on the
same tonne."* Stated universally.

**What testing showed** (first on a 400-ship random sample; since re-measured on every ship with EU-scope activity, `scripts/verifier_match.py`):

| Agreement with the verifier-reported ETS figure | Share |
|---|---|
| Same tonne (within 0.05%) | **68.5%** (sample: 67.5%) |
| Within 1% | 74.6% (sample: 76.0%) |
| Within 2% | 77.2% (sample: 78.2%) |
| Outside 2% | **17.1%** (sample: 21.8%; a further 5.7% report zero) |

So the claim was **false for roughly one ship in five**. The outliers are not
calculation errors: the filed figure is typically far smaller than the ship's
EU-scope emissions because it covers only part of the year, or only part of an
operator's obligation — detail the public record does not break out.

**Corrected** on the landing page and in the app's Verifier view to state the
measured figures and explain the divergence. **Do not restore the universal
wording.** Re-run the test after any engine change; the script is in this
document's commit.

**GET ADVICE** on whether "about two in three" needs the sample size stated
on-page (we state it).

## 4. Personal data we collect — NEEDS A NOTICE ⚠

The chat widget, the claim/suppression form and the pooling-interest form
collect **name, company and email**. That *is* personal data, and we are the
controller.

- The chat widget stores **nothing** — it hands everything to the visitor's own
  email client. Lowest-risk design, keep it.
- `POST /api/claim` **does** persist company and contact email to
  `data/privacy/requests.jsonl`.

**Required before any public deployment:**
1. A short privacy notice: what we collect, why (to verify a claim and reply),
   the lawful basis (legitimate interest / performance of a request), how long
   we keep it, and how to have it deleted.
2. Keep `requests.jsonl` out of git — **already in `.gitignore`**; verify it
   stays there before the first push.
3. Honour deletion requests. Today that is deleting a line by hand.

**Residual risk: medium until the notice exists.** It is a one-page job.

## 5. Regulatory accuracy — MATERIALLY IMPROVED TODAY

We tell owners what they owe. A wrong number that someone relies on is the
sharpest commercial risk here.

**Fixed today:** containership EEXI used 70% deadweight for the *required*
value; MEPC.364(79) §2.2.3.3.4 requires 100% deadweight. The required figure
was ~7% too lenient — a non-compliant ship could have read as compliant.

**Verified today:** MARPOL Annex VI Reg. 25 Table 3 reduction factors, all
twelve ship types, line by line against the consolidated text. All matched.

**Protections:** every output labelled ESTIMATE unless owner-supplied; the
Method page publishes every formula and source; a calculation worksheet is
available per vessel; 144 hand-computed tests.

**Still open and disclosed:** the EEXI estimator ignores PTO/PTI, shaft
generators, ice class and the weather factor — stated in every result. Public
data assumes a fuel because the register does not publish fuel type.

## 6. Not holding ourselves out as a verifier — CLEAR

We do not issue certificates, do not call ourselves a verifier or accredited
body, and say the operator's verifier checks our work. Keep that boundary
exactly where it is.

"Not legal or investment advice" appears in the footer. With the pooling
material off the front page, there is also no longer anything that could read
as broking or arranging a transaction.

## 7. Trademark and name — UNRESOLVED ⚠ **GET ADVICE**

RDAP confirmed `carbonkeel.com` was unregistered and no company of that name
surfaced in search. That proves **domain availability only**. Before
incorporating or printing anything:

- EUIPO and UKIPO searches in classes 9, 35 and 42
- a check against maritime-sector marks (several firms use "Keel")

Cheap now, expensive after a rebrand.

## 8. Items with no current exposure

- **No payment processing**, so no PCI scope.
- **No accounts or passwords**, so no credential-breach surface. The CII
  calculator key is an access gate, documented as such, protecting a feature
  rather than a secret.
- **No cookies and no analytics**, so no consent banner is required. If
  analytics are ever added, that changes.
- **Accessibility**: the European Accessibility Act may reach commercial
  services. We hold 40px targets, visible focus, keyboard operation and
  contrast — worth keeping as a standard, not a retrofit.

---

## Do these before the site goes public

1. **Publish a privacy notice** covering the chat and claim forms (§4).
2. **Confirm `data/privacy/requests.jsonl` and `data/access_keys.txt` are
   gitignored** before the first push.
3. **Trademark search** before incorporation (§7).
4. **Re-run `scripts/verifier_match.py`** after any engine change or data refresh, and update
   the on-page figures if they move (§3).
