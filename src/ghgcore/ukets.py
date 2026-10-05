"""UK ETS maritime engine — Greenhouse Gas ETS (Amendment) (Extension to
Maritime Activities) Order 2026, in force 1 July 2026.

Scope (verified 8 Jul 2026 vs GOV.UK / legislation.gov.uk / DNV & LR class
news): ships >=5,000 GT; DOMESTIC voyages only (UK port -> UK port, incl.
same-port) at 100%, voyages between Great Britain and Northern Ireland at
50%, at berth in UK ports 100%. CO2 + CH4 + N2O tank-to-wake from the start
(aligned with EU ETS 2026 gas coverage). No surrender phase-in. First
scheme period is the half-year 1 Jul-31 Dec 2026, calendar years from 2027 —
callers must pass only in-scope-period activity; the engine does not prorate.

Per-leg UK share comes from VoyageLeg.uk_share (see ports.uk_share_for_leg).
UKA price is a market input; default is indicative — VERIFY at use time.
"""
from dataclasses import dataclass
from .schema import AnnualActivity
from .cii import CF_TCO2_PER_T
from .euets import _non_co2, GWP_CH4, GWP_N2O

DEFAULT_UKA_PRICE_GBP = 40.0   # indicative mid-2026 — VERIFY live price


@dataclass
class UKETSResult:
    co2e_in_scope_t: float
    allowances_due: float          # UKAs (100% surrender, no phase-in)
    cost_gbp: float
    uka_price_used: float
    notes: list[str]


def compute_ukets(activity: AnnualActivity,
                  uka_price_gbp: float = DEFAULT_UKA_PRICE_GBP) -> UKETSResult:
    notes = ["UK ETS covers domestic UK voyages and time at berth only (voyages between Great "
             "Britain and Northern Ireland count at 50%). International voyages are under "
             "consultation and are not yet in scope."]
    co2e = 0.0
    any_uk = False
    for leg in activity.legs:
        share = leg.uk_share or 0.0
        if share <= 0:
            continue
        any_uk = True
        for fc in leg.fuel_consumed:
            t = fc.tonnes * share
            ch4, n2o = _non_co2(fc.fuel, activity.vessel.engine_type)
            co2e += t * (CF_TCO2_PER_T[fc.fuel] + ch4 * GWP_CH4 + n2o * GWP_N2O)
    if not any_uk:
        notes.append("No UK domestic voyages were found in this ship's data.")
    if activity.year == 2026:
        notes.append("The 2026 UK ETS period runs only from 1 July to 31 December. Enter "
                     "second-half activity; this estimate does not pro-rate.")
    return UKETSResult(round(co2e, 1), round(co2e, 1),
                       round(co2e * uka_price_gbp, 0), uka_price_gbp, notes)
