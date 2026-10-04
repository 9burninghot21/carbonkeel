"""Pool agreement draft generator — Art. 21 pooling paperwork head start.

Numbers come exclusively from the deterministic engines (PoolSuggestion);
this module only formats them. Output is a negotiation-ready DRAFT, clearly
labelled as not legal advice.
"""
from datetime import date
from .pooling import PoolSuggestion


def draft_agreement(pool: PoolSuggestion, compliance_year: int,
                    organiser: str = "[ORGANISER LEGAL NAME]") -> str:
    surplus = [m for m in pool.members if m.cb_tco2e > 0]
    deficits = [m for m in pool.members if m.cb_tco2e < 0]
    rows = "\n".join(
        f"| {m.name} | {m.imo} | {m.cb_tco2e:+,.1f} | "
        f"{'Contributor' if m.cb_tco2e > 0 else 'Beneficiary'} | "
        f"€{m.penalty_eur:,.0f} |"
        for m in pool.members)
    total_comp_low = 0.30 * pool.avoided_penalty_eur
    total_comp_high = 0.70 * pool.avoided_penalty_eur
    return f"""# FuelEU Maritime Pooling Agreement — DRAFT
**Compliance year {compliance_year} · generated {date.today().isoformat()} by CarbonKeel**

> DRAFT for negotiation. Not legal advice; execute only after review by the
> parties' counsel. Figures derive from Regulation (EU) 2023/1805 Annex I/IV
> calculations on the data stated in Schedule B.

## 1. Parties and pooled ships
Pool organiser: {organiser}

| Ship | IMO | Compliance balance (tCO₂e) | Role | Standalone penalty |
|------|-----|---------------------------:|------|-------------------:|
{rows}

## 2. Pool compliance (Art. 21)
Combined pool compliance balance: **{pool.pool_cb_tco2e:+,.1f} tCO₂e** (≥ 0,
so each member ship is deemed compliant for {compliance_year} upon valid
registration). Total penalty avoided vs standalone: **€{pool.avoided_penalty_eur:,.0f}**.

## 3. Compensation
Beneficiaries shall compensate Contributors pro-rata to absorbed deficit.
Commercial range for negotiation: **€{total_comp_low:,.0f} – €{total_comp_high:,.0f}**
(30–70% of avoided penalty). Agreed rate: €[___] per tCO₂e absorbed.
Payment within [30] days of pool verification.

## 4. Conditions
1. Registration in the FuelEU Database by **30 April {compliance_year + 1}**
   with each member's verifier confirmation (Art. 21(3)).
2. Each party warrants its reported fuel data is verifier-accepted; any
   post-verification balance restatement reopens §3 pro-rata.
3. A ship may participate in only one pool per compliance year.
4. Governing law / jurisdiction: [___].

## Schedule B — calculation basis
Balances computed per Reg. (EU) 2023/1805 Annex IV with Annex II default
emission factors{"" if not pool.notes else " — " + pool.notes[-1]}.
Full per-ship worksheets available via the CarbonKeel audit endpoint.
"""
