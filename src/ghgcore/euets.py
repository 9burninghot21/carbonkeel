"""EU ETS maritime engine — Directive 2003/87/EC as amended.

Scope: 100% intra-EEA voyages + at berth, 50% extra-EEA voyages (ships >=5,000 GT).
Phase-in of surrender: 40% (2024), 70% (2025), 100% (2026+).
From 2026 reporting year: CH4 and N2O included as CO2e (GWP100: CH4=28, N2O=265).

CH4/N2O emission factors are simplified prototype values (per tonne fuel);
production must follow MRV Regulation implementing acts per fuel/engine type.
"""
from dataclasses import dataclass
from .schema import AnnualActivity, EngineType, FuelType, VoyageScope
from .cii import CF_TCO2_PER_T

PHASE_IN = {2024: 0.40, 2025: 0.70}          # else 1.0 from 2026
GWP_CH4, GWP_N2O = 28.0, 265.0

# (t CH4/t fuel, t N2O/t fuel). Liquid-fuel factors match the Annex II /
# MRV defaults (0.00005 / 0.00018, verified 8 Jul 2026 vs Reg. 2023/1805
# Annex II, which cites Reg. 2015/757 for the Cf values). LNG: combustion
# CH4 is zero but slip dominates — 3.1% of fuel mass for Otto dual-fuel
# medium-speed (Annex II col. 9; was 0.0031 here, a 10x error caught in
# verification). Engine-type split (Otto SS 1.7% / Diesel DF 0.2% /
# LBSI 2.6%) still to plumb — VERIFY per-engine before customer-facing
# LNG numbers.
NON_CO2_EF = {
    FuelType.HFO: (0.00005, 0.00018),
    FuelType.LFO: (0.00005, 0.00018),
    FuelType.MDO_MGO: (0.00005, 0.00018),
    FuelType.LNG: (0.031, 0.00011),           # Otto DF medium-speed slip default
    FuelType.METHANOL: (0.00005, 0.00018),    # class default per TBM rule
    FuelType.BIOFUEL_B24: (0.00005, 0.00018),
    FuelType.BIOFUEL_B100: (0.00005, 0.00018),
}

# LNG methane slip (t CH4/t fuel) by consumer-unit class, Annex II col. 9.
LNG_SLIP_BY_ENGINE = {
    EngineType.OTTO_MS: 0.031,
    EngineType.OTTO_SS: 0.017,
    EngineType.DIESEL_DF: 0.002,
    EngineType.LBSI: 0.026,
}


def _non_co2(fuel: FuelType, engine: EngineType) -> tuple[float, float]:
    ch4, n2o = NON_CO2_EF[fuel]
    if fuel == FuelType.LNG:
        ch4 = LNG_SLIP_BY_ENGINE[engine]
    return ch4, n2o


@dataclass
class ETSResult:
    co2e_in_scope_t: float
    surrender_share: float
    allowances_due: float          # EUAs
    cost_eur: float
    eua_price_used: float
    notes: list[str]


def compute_ets(activity: AnnualActivity, eua_price_eur: float = 70.0) -> ETSResult:
    notes = []
    year = activity.year
    include_non_co2 = year >= 2026
    if not include_non_co2:
        notes.append("Pre-2026: CO2 only in ETS scope.")

    co2e = 0.0
    for leg in activity.legs:
        share = {VoyageScope.INTRA_EEA: 1.0, VoyageScope.AT_BERTH_EEA: 1.0,
                 VoyageScope.EXTRA_EEA: 0.5, VoyageScope.OUT_OF_SCOPE: 0.0}[leg.scope]
        if share == 0:
            continue
        for fc in leg.fuel_consumed:
            t = fc.tonnes * share
            e = t * CF_TCO2_PER_T[fc.fuel]
            if include_non_co2:
                ch4, n2o = _non_co2(fc.fuel, activity.vessel.engine_type)
                e += t * ch4 * GWP_CH4 + t * n2o * GWP_N2O
            co2e += e

    surrender = PHASE_IN.get(year, 1.0)
    allowances = co2e * surrender
    notes.append("Biofuel share may qualify for zero-rating under MRV rules if RED-certified — "
                 "prototype applies fossil-share CF only.")
    return ETSResult(round(co2e, 1), surrender, round(allowances, 1),
                     round(allowances * eua_price_eur, 0), eua_price_eur, notes)
