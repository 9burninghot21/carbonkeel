"""Fleet health-check report — the outreach lead magnet (D1.2).

Renders a branded, print-friendly HTML page for a list of IMOs from public
THETIS data. Browser print -> PDF is the delivery format for the prototype;
a server-side PDF pipeline is a Phase 2 nicety, not a blocker.

All numbers ESTIMATE: reconstruction from verified public totals. CII shown
only when a DWT is supplied (dwts param, per-IMO), since public data lacks it.
"""
from ghgcore import build_scorecard
from ghgcore.thetis import ThetisRecord, record_to_activity
from ghgcore.fueleu import compute_fueleu
from ghgcore.euets import compute_ets
from ghgcore.nzf import compute_nzf
from ghgcore.pooling import PoolCandidate, suggest_pool

EUA_PRICE = 70.0

CSS = """
body{font-family:'Segoe UI',system-ui,sans-serif;color:#0b2239;margin:0;background:#fff}
.head{background:#0b2239;color:#fff;padding:26px 36px}
.logo{font-size:24px;font-weight:800}.logo span{color:#14b8a6}
.sub{color:#93a7bd;font-size:13px;margin-top:4px}
.band{display:inline-block;background:#fef3c7;color:#92400e;border:1px solid #f59e0b;
 padding:2px 10px;border-radius:14px;font-size:11px;font-weight:700;margin:18px 36px 0}
.wrap{padding:10px 36px 40px}
h2{font-size:17px;margin:22px 0 8px}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th{background:#f1f5f9;text-align:right;padding:7px 9px;border-bottom:2px solid #0b2239}
th:first-child,td:first-child{text-align:left}
td{padding:6px 9px;border-bottom:1px solid #e2e8f0;text-align:right;white-space:nowrap}
td.name{white-space:normal}
tr.tot td{font-weight:800;border-top:2px solid #0b2239;background:#f8fafc}
.neg{color:#dc2626;font-weight:600}.pos{color:#16a34a;font-weight:600}
.note{font-size:11px;color:#64748b;margin-top:14px;line-height:1.6}
.kpis{display:flex;gap:14px;margin:16px 0}
.kpi{flex:1;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px}
.kpi .k{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.06em}
.kpi .v{font-size:21px;font-weight:800;margin-top:4px}
@media print{.band{-webkit-print-color-adjust:exact}.head{-webkit-print-color-adjust:exact}}
"""


def _pooling_section(cands: list[PoolCandidate]) -> str:
    if not cands:
        return ""
    pool = suggest_pool(cands)
    if pool.avoided_penalty_eur > 0:
        names = ", ".join(m.name for m in pool.members)
        headline = (f"<b>€{pool.avoided_penalty_eur:,.0f} of this fleet's FuelEU "
                    f"penalty risk is avoidable by pooling internally</b> "
                    f"(Art. 21): pool {{{names}}} → combined balance "
                    f"{pool.pool_cb_tco2e:+,.0f} tCO₂e ≥ 0, so every member is "
                    "deemed compliant.")
        if pool.uncovered:
            headline += (f" Remaining €{pool.uncovered_penalty_eur:,.0f} "
                         f"({len(pool.uncovered)} ships) needs an external "
                         "pooling partner — we match those.")
    elif any(c.cb_tco2e > 0 for c in cands):
        surplus = sum(c.cb_tco2e for c in cands if c.cb_tco2e > 0)
        headline = (f"<b>This fleet holds a sellable FuelEU surplus of "
                    f"{surplus:,.0f} tCO₂e</b> — bankable (Art. 20) or poolable "
                    "with deficit fleets for compensation (Art. 21).")
    else:
        headline = ("<b>No internal pooling capacity</b> — the whole FuelEU "
                    "deficit needs an external surplus partner or biofuel; "
                    "register any pool by 30 April.")
    return f"<h2>FuelEU pooling opportunity</h2><p class=note style='font-size:12.5px'>{headline}</p>"


def fleet_report_html(records: dict, imos: list[str], year_hint: int = None,
                      dwts: dict[str, float] | None = None) -> str:
    dwts = dwts or {}
    rows, missing, cands = [], [], []
    tot = {"co2": 0.0, "euas": 0.0, "ets_eur": 0.0, "feu_pen": 0.0,
           "feu_cb": 0.0, "nzf_usd": 0.0}
    for imo in imos:
        rec: ThetisRecord = records.get(imo)
        if rec is None:
            missing.append(imo)
            continue
        year = year_hint or rec.reporting_period or 2025
        dwt = dwts.get(imo)
        supported = rec.ship_type is not None
        cii_txt = "n/a (type)" if not supported else "add DWT"
        if supported:
            act = record_to_activity(rec, year=year, dwt=dwt or 1.0)
            feu = compute_fueleu(act)
            ets = compute_ets(act, EUA_PRICE)
            nzf = compute_nzf(act)
            if dwt:
                cii_txt = build_scorecard(act).cii.rating
        else:
            act = None
            feu = ets = nzf = None
        rows.append((rec, feu, ets, nzf, cii_txt))
        if ets:
            tot["co2"] += rec.co2_tonnes
            tot["euas"] += ets.allowances_due
            tot["ets_eur"] += ets.cost_eur
            tot["feu_pen"] += feu.penalty_eur
            tot["feu_cb"] += feu.compliance_balance_tco2e
            tot["nzf_usd"] += nzf.remedial_cost_usd
            cands.append(PoolCandidate(rec.imo, rec.name,
                                       feu.compliance_balance_tco2e,
                                       feu.ghg_intensity))

    def eur(x): return f"€{x:,.0f}"
    body_rows = ""
    for rec, feu, ets, nzf, cii_txt in rows:
        if ets is None:
            body_rows += (f"<tr><td class=name>{rec.name}</td><td>{rec.imo}</td>"
                          f"<td class=name>{rec.ship_type_raw}</td>"
                          f"<td colspan=6>ship type not yet supported</td></tr>")
            continue
        cb = feu.compliance_balance_tco2e
        body_rows += (
            f"<tr><td class=name>{rec.name}</td><td>{rec.imo}</td>"
            f"<td class=name>{rec.ship_type_raw}</td>"
            f"<td>{rec.co2_tonnes:,.0f}</td><td>{cii_txt}</td>"
            f"<td>{ets.allowances_due:,.0f}</td><td>{eur(ets.cost_eur)}</td>"
            f"<td class={'neg' if cb < 0 else 'pos'}>{cb:+,.0f}</td>"
            f"<td>{eur(feu.penalty_eur)}</td></tr>")

    exposure = tot["ets_eur"] + tot["feu_pen"]
    html = f"""<!DOCTYPE html><html><head><meta charset=utf-8>
<title>CarbonKeel Fleet Health Check</title><style>{CSS}</style></head><body>
<div class=head><div class=logo>Carbon<span>Keel</span></div>
<div class=sub>Fleet compliance health check · public THETIS-MRV data ·
generated for outreach purposes</div></div>
<span class=band>ESTIMATE — reconstructed from EMSA-published verified emissions</span>
<div class=wrap>
<div class=kpis>
<div class=kpi><div class=k>Vessels analysed</div><div class=v>{len(rows)}</div></div>
<div class=kpi><div class=k>Verified CO₂ (fleet)</div><div class=v>{tot['co2']:,.0f} t</div></div>
<div class=kpi><div class=k>Est. EU ETS + FuelEU exposure</div><div class=v>{eur(exposure)}</div></div>
<div class=kpi><div class=k>FuelEU balance</div>
<div class="v {'neg' if tot['feu_cb'] < 0 else 'pos'}">{tot['feu_cb']:+,.0f} tCO₂e</div></div>
</div>
<h2>Per-vessel breakdown</h2>
<table><tr><th>Vessel</th><th>IMO</th><th>Type</th><th>CO₂ (t)</th><th>CII</th>
<th>EUAs due</th><th>ETS cost</th><th>FuelEU CB (t)</th><th>Penalty risk</th></tr>
{body_rows}
<tr class=tot><td colspan=3>FLEET TOTAL</td><td>{tot['co2']:,.0f}</td><td></td>
<td>{tot['euas']:,.0f}</td><td>{eur(tot['ets_eur'])}</td>
<td>{tot['feu_cb']:+,.0f}</td><td>{eur(tot['feu_pen'])}</td></tr></table>
{_pooling_section(cands)}
<p class=note><b>How to read this.</b> ETS figures use the per-scope CO₂ splits your
verifier reported to EMSA (spot-checks reproduce the reported ETS-scope figure
exactly); FuelEU balance assumes an HFO-equivalent mix — owner fuel data will
improve it. Negative FuelEU balance is a payable penalty OR a pooling
opportunity; positive balance is a sellable asset. CII ratings require vessel
DWT (not published by EMSA) — request the full check to add them.
IMO Net-Zero Framework 2028 scenario exposure for this fleet:
<b>${tot['nzf_usd']:,.0f}</b> in remedial units at current fuel mix.
{('Missing from public export: ' + ', '.join(missing)) if missing else ''}</p>
<p class=note>CarbonKeel · free fleet check · all figures ESTIMATE ·
EUA price assumption €{EUA_PRICE:.0f}/t</p>
</div></body></html>"""
    return html
