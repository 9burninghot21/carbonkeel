# Data sources: where every input comes from, and whether we may use it

Checked on 5 October 2026 against primary sources. This is engineering diligence,
not legal advice. Items marked **ASK** are cheap questions worth answering in
writing before outreach.

---

## 1. The short answers

| Your question | Answer |
|---|---|
| **Is the data public?** | **Yes, by law.** Article 21 of Regulation (EU) 2015/757 requires the Commission to make it publicly available by 30 June each year. |
| **Are we aligned to use it?** | **Yes, with conditions we already meet:** acknowledge EMSA as the source, say that our figures are rebuilt and changed, do not distort the meaning, and do not imply EMSA endorses us. **One gap:** we found no licence text written specifically for the THETIS-MRV files, so we rely on EMSA's general copyright notice (see 3). Ask the helpdesk to confirm in writing (draft in 6). |
| **Can you fetch it yourself?** | **Yes.** No login, no key. Run `python scripts/fetch_thetis.py` (metadata only) or add `--download 2025 --yes` to fetch a file. |
| **Is what we hold current?** | **No.** We hold 2025 **v6** and 2024 **v228**. EMSA now lists 2025 **v60** (generated 5 Oct 2026) and 2024 **v246**. EMSA regenerates files as operators and verifiers submit amendments, so our figures lag. |

---

## 2. The source

**EMSA THETIS-MRV, "GHG Emission Report" page**, `https://mrv.emsa.europa.eu/#public/emission-report`.
EMSA's own text on that page (read on 5 October 2026):

> "Publication of information in accordance with Article 21 of Regulation (EU) 2015/757 on the monitoring, reporting and verification of greenhouse gas emissions from maritime transport. Information is accessible through the search tool or can be exported in a spreadsheet for further analysis."

It also states that **2024 is the first reporting period** that includes methane and nitrous oxide, that **for 2024 and 2025 only CO₂ counts under the EU ETS**, and that from 2024 the spreadsheet carries a **separate sheet for partial emissions reports** (Article 11(2)).

### The legal basis, from the primary text

Article 21 as consolidated on 1 January 2024 (EUR-Lex, CELEX 02015R0757-20240101):

- **21(1):** "By 30 June each year, the Commission shall make publicly available the information on greenhouse gas emissions reported in accordance with Article 11 as well as the information set out in paragraph 2."
- **21(2):** the list includes (a) the identity of the ship, **including the company**; (b) technical efficiency; (c) annual emissions; (d) annual fuel consumption; (e) emissions and fuel per distance; (g) time at sea; (i) document of compliance dates; (j) the verifier's identity.
- **21(3):** a company may ask for a *different level of aggregation* only for categories of **aggregated data "which does not relate to greenhouse gas emissions"**, where disclosure would harm a legitimate commercial interest.
- **21(6):** EMSA assists the Commission with this Article.

**What that means for us.**
- Showing a ship's company name is lawful: 21(2)(a) requires it to be public.
- A company has **no legal right to have its emissions or fuel figures hidden**. (Our earlier wording cited "Article 21(6)" for alternative publication. That was wrong, and is corrected in `docs/DATA_AND_PRIVACY.md` and `docs/LEGAL_REVIEW.md`.)
- What we *can* offer, and do, is to hide **our own derived figures** on request. That is our choice, not theirs.

---

## 3. Reuse terms: what we found, and the gap

| Source | What it says | Confidence |
|---|---|---|
| EMSA copyright notice (`emsa.europa.eu/disclaimer.html`) | "Reproduction is authorised, provided the source is acknowledged, save where otherwise stated." | Read directly |
| Same page | EMSA accepts "no responsibility or liability whatsoever" for the material and says it is "not necessarily comprehensive, complete, accurate or up to date." | Read directly |
| EU institutions' reuse policy (Commission Decision 2011/833/EU; CC BY 4.0 for Commission content) | Reuse allowed with credit, changes indicated, meaning not distorted. | From search summaries of EU legal notices; **EMSA is an agency, not the Commission**, so treat as supporting, not decisive |
| THETIS-MRV site | No terms-of-use or licence text found on the public emission-report page | Page read in full |

**The gap.** Nothing on the THETIS-MRV page restricts reuse, and EMSA invites "further analysis", but we found no licence written for these files. The position is strong and the risk low. **ASK** the helpdesk to confirm in writing (draft in 6).

**Conditions we follow**, all met today:
1. **Acknowledge the source.** Every page and every result names EMSA THETIS-MRV and Article 21, and each result shows the report year and version.
2. **Indicate changes.** Everything we derive is labelled ESTIMATE, and the page says the figures are rebuilt.
3. **No endorsement.** Footers say CarbonKeel is not endorsed by EMSA or the European Commission.
4. **Do not distort.** We show the verified figure next to our rebuild, and say when they differ.
5. **Accuracy disclaimer.** EMSA disclaims accuracy; our ESTIMATE labelling and verifier-match statistics are consistent with that.

**Personal data.** Companies are legal entities. A sole trader trading under a personal name is the edge case. Article 21(2)(a) makes the company name public, and our privacy notice gives an objection route.

---

## 4. How to fetch it

Two public endpoints, no authentication (the server sets a session cookie; it is not needed):

| What | URL |
|---|---|
| List the files | `https://mrv.emsa.europa.eu/api/public-emission-report/downloadable-files` (JSON) |
| Download one | `https://mrv.emsa.europa.eu/api/public-emission-report/reporting-period-document/binary/{year}/{version}` |

**The tool.**

```bash
python scripts/fetch_thetis.py                          # check only: nothing is downloaded
python scripts/fetch_thetis.py --download 2025 2024 --yes   # fetch the newest files (about 10 MB each)
```

- Check mode compares what we hold with what EMSA lists and exits with code 3 if a newer version exists.
- A download is **validated before it is kept**: a real .xlsx, the expected sheets, the columns the loader relies on, and totals within 25% of the file it replaces. A failed file is discarded.
- Old files are never deleted. The app and every script pick the highest `(year, version)` automatically (numeric order; plain alphabetical sorting would have put v100 before v60).
- Each download is recorded in `data/source_manifest.json` (version, EMSA's generation date, time retrieved, size, SHA-256).
- Manners: one request at a time, a pause between requests, a User-Agent that names us and gives an address, slow down if asked. This is about 20 MB a quarter, not scraping.

**Cadence observed (5 Oct 2026).** Several reporting years were regenerated within the previous week (2025 on 5 Oct, 2024 on 1 Oct, 2023 on 29 Sep). Check monthly, and before any outreach batch.

### What the live listing shows against what we hold

| Year | We hold | EMSA lists | EMSA generated |
|---|---|---|---|
| 2025 | v6 | **v60** | 5 Oct 2026 |
| 2024 | v228 | **v246** | 1 Oct 2026 |
| 2018–2023 | none | v275 / v228 / v210 / v219 / v241 / v92 | 29 Mar – 29 Sep 2026 |

The live 2025 file is 11.85 MB; ours is 11.41 MB. The data has changed since 8 July.

---

## 5. Validation: done, and not done

**Done**
- The listing endpoint answers without login, and the download endpoint answers a metadata request with the right type and size.
- Our loader reproduced the verifier-reported ETS-scope CO₂ exactly on spot checks against the v6 file (8 July).
- Article 21's wording and paragraph numbers were read from the primary text (above).
- `scripts/verifier_match.py` measures our rebuild against the verifier figure over every ship: 68.5% exact, 77.2% within 2% (14,734 ships with EU-scope activity).

**Not done, because it needs a download you have not yet approved**
- A like-for-like comparison of v60 against v6: how many ships changed, by how much, and whether the column layout is unchanged.
- Whether the **Partial ERs** sheet (1,505 reports in the v6 file; we read only the first sheet) explains part of the 17% of ships where our rebuild and the verifier disagree by more than 2%. This is a hypothesis to test, not a finding.

---

## 6. Everything else we rely on

| Input | Source | Status | Action |
|---|---|---|---|
| Emissions, fuel, company | EMSA THETIS-MRV (above) | Public by law; reuse with acknowledgement | Refresh; ASK helpdesk |
| EU ETS, FuelEU, MRV rules | EUR-Lex (Directive 2003/87/EC; Regulations 2015/757, 2023/1805) | EU legislation may be reused with acknowledgement | None |
| CII and EEXI parameters (MEPC.353/354/355(78), MEPC.364(79), MARPOL Annex VI Reg. 25 Table 3) | IMO publications | Parameters are regulatory facts. IMO owns the copyright in the *text*. We use numbers and cite them, and do not reproduce the text | Keep it that way; get advice only if you ever quote the resolutions |
| UK ETS rules | legislation.gov.uk (Open Government Licence) | Reuse allowed with acknowledgement | None |
| **Allowance prices** (EU €70, UK £40, €/£ 1.15) | **Assumptions, not fetched** | Live exchange prices are licensed data. We do not scrape them. The app labels these as inputs and shows €60 and €100 for sensitivity | Do not display a "market price" without a licensed feed |
| Port-to-country mapping | Our own table; only the UN/LOCODE *code format* is used | No dataset copied | None |

### Attribution line (use exactly)

> Contains data from EMSA THETIS-MRV (reporting year {year}, version {n}), published under Article 21 of Regulation (EU) 2015/757. CarbonKeel's figures are our own calculations from that data and are not endorsed by EMSA or the European Commission.

### Draft message to the THETIS helpdesk

*(A search summary gave the address as THETIS@emsa.europa.eu. Confirm it on the THETIS-MRV site before sending.)*

> Subject: Reuse of the public THETIS-MRV publication files
>
> Hello. I am building a free tool that reads the public "EU MRV Publication of information" spreadsheets (for example 2025 v60) and shows each ship's estimated carbon costs. It acknowledges EMSA as the source, labels every derived figure as our own estimate, and states that EMSA does not endorse it.
>
> Please confirm that reuse of these files for this purpose, including commercially, is permitted on the basis of Article 21 of Regulation (EU) 2015/757 and EMSA's copyright notice, and tell me if there is a preferred form of attribution or any condition I should know about.
>
> Thank you.

---

## 7. What would change this assessment

- EMSA adds terms to the THETIS-MRV page or files.
- The Commission amends Article 21 (it was last changed by Regulation (EU) 2023/957).
- A reply to the helpdesk message that imposes a condition.
- We start to publish a downloadable copy of the register (we deliberately do not).
