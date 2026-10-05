"""Composite vessel scorecard: the product's core output.

Four scores + call-to-action list, from one AnnualActivity input.
"""
from dataclasses import dataclass, asdict
from .schema import AnnualActivity
from .cii import compute_cii, CIIResult
from .fueleu import compute_fueleu, FuelEUResult
from .euets import compute_ets, ETSResult
from .nzf import compute_nzf, NZFResult
from .ukets import compute_ukets, UKETSResult

RATING_POINTS = {"A": 100, "B": 85, "C": 65, "D": 35, "E": 10}


@dataclass
class Scorecard:
    vessel_name: str
    imo_number: str
    year: int
    regulatory_health: int          # 0-100
    cost_exposure_eur: float        # ETS cost + FuelEU penalty risk
    compliance_asset_eur: float     # tradable surplus value (FuelEU pooling proxy)
    future_readiness: str           # NZF position summary
    cii: CIIResult
    fueleu: FuelEUResult
    ets: ETSResult
    nzf: NZFResult
    ukets: UKETSResult
    actions: list[str]


def build_scorecard(activity: AnnualActivity, eua_price: float = 70.0,
                    nzf_year: int = 2028, uka_price_gbp: float = 40.0,
                    eur_per_gbp: float = 1.15) -> Scorecard:
    cii = compute_cii(activity)
    feu = compute_fueleu(activity)
    ets = compute_ets(activity, eua_price)
    nzf = compute_nzf(activity, nzf_year)
    ukets = compute_ukets(activity, uka_price_gbp)

    health = RATING_POINTS[cii.rating]
    if feu.compliance_balance_tco2e < 0:
        health -= 15
    health = max(0, min(100, health))

    # UK ETS cost converted at an indicative rate for the combined figure —
    # the GBP-native number stays on the ukets result.
    cost = ets.cost_eur + feu.penalty_eur + ukets.cost_gbp * eur_per_gbp

    # Compliance asset: FuelEU surplus valued at counterparty's avoided-penalty
    # ceiling x 0.5 (typical negotiated midpoint proxy for prototype).
    asset = 0.0
    if feu.compliance_balance_gco2e > 0:
        from .fueleu import penalty_equiv
        asset = 0.5 * penalty_equiv(feu.compliance_balance_gco2e, feu.ghg_intensity)

    if nzf.surplus_units_tco2e > 0:
        readiness = f"Compliant under the IMO NZF scenario for {nzf.year}: earns {nzf.surplus_units_tco2e:,.0f} t of Surplus Units"
    else:
        readiness = (f"IMO NZF scenario, {nzf.year}: ${nzf.remedial_cost_usd:,.0f} in remedial units "
                     f"(Tier 1: {nzf.tier1_deficit_tco2e:,.0f} t, Tier 2: {nzf.tier2_deficit_tco2e:,.0f} t)")

    actions = _actions(cii, feu, ets, nzf)
    if ukets.cost_gbp > 0:
        actions.append(f"UK ETS: {ukets.allowances_due:,.0f} UK allowances (UKAs) due, about "
                       f"£{round(ukets.cost_gbp, -3):,.0f}, for UK domestic voyages.")
    return Scorecard(activity.vessel.name, activity.vessel.imo_number, activity.year,
                     health, round(cost, 0), round(asset, 0), readiness,
                     cii, feu, ets, nzf, ukets, actions)


def _actions(cii, feu, ets, nzf) -> list[str]:
    a = []
    if cii.rating in ("D", "E"):
        need = ("A rating of E requires" if cii.rating == "E" else
                "Three years in a row at D, or one year at E, requires")
        a.append(f"CII rating {cii.rating} (ratio {cii.ratio}). {need} a corrective action "
                 "plan in SEEMP Part III. Levers: slower speed, hull and propeller cleaning, "
                 "biofuel blending, weather routing.")
    elif cii.rating == "C":
        a.append(f"CII rating C (ratio {cii.ratio}). The margin to D is thin and the "
                 "reduction factor keeps rising, so model next year now.")
    if feu.compliance_balance_tco2e < 0:
        a.append(f"FuelEU deficit of {abs(feu.compliance_balance_tco2e):,.0f} tCO₂e "
                 f"(penalty about €{feu.penalty_eur:,.0f}). Options: pool with a surplus "
                 "ship, borrow from next year (with 10% added), or use biofuel on EU voyages.")
    elif feu.compliance_balance_tco2e > 0:
        a.append(f"FuelEU surplus of {feu.compliance_balance_tco2e:,.0f} tCO₂e. It can be "
                 "pooled with another ship; register a pool in the FuelEU Database by 30 April.")
    a.append(f"EU ETS: {ets.allowances_due:,.0f} EU allowances (EUAs) due, about "
             f"€{round(ets.cost_eur, -3):,.0f}, to be surrendered by 30 September.")
    if nzf.remedial_cost_usd > 0:
        a.append(f"IMO Net-Zero Framework scenario for {nzf.year}: about "
                 f"${round(nzf.remedial_cost_usd, -3):,.0f} on today's fuel mix. The adoption vote "
                 "is expected in October 2026.")
    return a


def to_dict(sc: Scorecard) -> dict:
    return asdict(sc)
