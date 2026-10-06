"""Rules shared by the EU ETS and UK ETS maritime engines.

Both schemes count the same three gases with the same global-warming
potentials and the same monitoring formula, so that logic lives here once.
Every value below was checked against the primary text on 6 Oct 2026:

EU   Directive 2003/87/EC (consolidated 1 Mar 2024): Art. 3ga (scope shares),
     Art. 3gb (phase-in), Art. 12(3) and (3-b) to (3-e) (surrender date and
     exceptions), Art. 3(z) (port of call), Annex I (gases, from 1 Jan 2026).
     Regulation (EU) 2015/757 as amended by Reg. (EU) 2023/957: Art. 2 (scope),
     Annex I Part A (emission factors, slip, formulae).
     Delegated Regulation (EU) 2023/2776: the amended Annex I formulae.
     Delegated Regulation (EU) 2020/1044: global-warming potentials (28, 265).
UK   The Greenhouse Gas Emissions Trading Scheme (Amendment) (Extension to
     Maritime Activities) Order 2026, SI 2026/392, Schedule 2A: paras 5, 7, 8
     (scope), 15 (surrender), 14 (report date), Table C1 (GWPs).

The monitoring formula (Reg. 2015/757 Annex I Part A, as amended) is, per fuel i:
    CO2  = sum (M_i - M_i,NC) x EF_CO2,i       combusted mass only
    CH4  = sum (M_i - M_i,NC) x EF_CH4,i  +  CH4 slip (= M_i,NC)
    N2O  = sum (M_i - M_i,NC) x EF_N2O,i
where M_i,NC is fuel released un-burned (slip), a percentage of fuel mass.
"""
from dataclasses import dataclass, field
from typing import Optional

from .cii import CF_TCO2_PER_T
from .schema import EngineType, FuelType

GWP_CH4, GWP_N2O = 28.0, 265.0           # AR5, Delegated Reg. 2020/1044; UK Order Table C1

# (t CH4 per t fuel, t N2O per t fuel) of the fuel that is combusted.
# Reg. 2015/757 Annex I Part A table: liquid fuels 0.00005 / 0.00018; LNG 0 / 0.00011.
NON_CO2_EF = {
    FuelType.HFO: (0.00005, 0.00018),
    FuelType.LFO: (0.00005, 0.00018),
    FuelType.MDO_MGO: (0.00005, 0.00018),
    FuelType.LNG: (0.0, 0.00011),
    FuelType.METHANOL: (0.00005, 0.00018),     # TBM in the table: highest value of the class
    FuelType.BIOFUEL_B24: (0.00005, 0.00018),
    FuelType.BIOFUEL_B100: (0.00005, 0.00018),
}

# Slip, as a share of the fuel mass used (Annex I column 6, at 50% engine load).
LNG_SLIP_BY_ENGINE = {
    EngineType.OTTO_MS: 0.031,
    EngineType.OTTO_SS: 0.017,
    EngineType.DIESEL_DF: 0.002,
    EngineType.LBSI: 0.026,
}

# Directive Art. 3gb: share of verified emissions to surrender, by emissions year.
PHASE_IN = {2024: 0.40, 2025: 0.70}      # 1.0 from 2026; no obligation before 2024
EU_FIRST_SURRENDER_YEAR = 2024
EU_NON_CO2_FROM_YEAR = 2026              # Directive Annex I: "From 1 January 2026, methane and nitrous oxide"
EU_DEROGATIONS_END_YEAR = 2030           # Art. 12(3-b) to (3-e): "until 31 December 2030"
ICE_CLASS_DISCOUNT = 0.05                # Art. 12(3-e): 5% fewer allowances
EU_EXCESS_PENALTY_EUR_PER_T = 100.0      # Art. 16(3), indexed to inflation
UK_FIRST_SCHEME_YEAR = 2026              # scheme starts 1 July 2026
UK_GB_NI_SHARE = 0.5                     # Order para 15(1)(a)


def eu_phase_in(year: int) -> float:
    if year < EU_FIRST_SURRENDER_YEAR:
        return 0.0
    return PHASE_IN.get(year, 1.0)


def slip_share(fuel: FuelType, engine: EngineType) -> float:
    return LNG_SLIP_BY_ENGINE[engine] if fuel == FuelType.LNG else 0.0


def non_co2(fuel: FuelType, engine: EngineType) -> tuple:
    """(CH4 factor, N2O factor) for the fuel that is combusted. Kept for the
    older callers; slip is handled separately in `gas_emissions`."""
    ch4, n2o = NON_CO2_EF[fuel]
    return ch4, n2o


@dataclass
class GasEmissions:
    co2_t: float
    ch4_t: float
    n2o_t: float

    def co2e(self, include_non_co2: bool) -> float:
        e = self.co2_t
        if include_non_co2:
            e += self.ch4_t * GWP_CH4 + self.n2o_t * GWP_N2O
        return e


def gas_emissions(fuel: FuelType, tonnes: float, engine: EngineType,
                  tonnes_are_combusted: bool = False) -> GasEmissions:
    """Emissions of one fuel by the Reg. 2015/757 Annex I formula.

    `tonnes` is the fuel mass used (M_i), which includes any slipped fuel. The
    public register only lets us back fuel out of the reported CO2, which is
    already a combusted-mass figure; pass tonnes_are_combusted=True for that
    and the slipped mass is added on top rather than taken off.
    """
    s = slip_share(fuel, engine)
    if tonnes_are_combusted:
        combusted = tonnes
        slipped = tonnes * s / (1.0 - s) if s < 1.0 else 0.0
    else:
        slipped = tonnes * s
        combusted = tonnes - slipped
    ef_ch4, ef_n2o = NON_CO2_EF[fuel]
    return GasEmissions(combusted * CF_TCO2_PER_T[fuel],
                        combusted * ef_ch4 + slipped,
                        combusted * ef_n2o)


@dataclass
class ETSExceptions:
    """EU ETS exceptions that depend on facts the public register does not show.

    ice_class_ia          ship has ice class IA or IA Super (or equivalent, HELCOM
                          25/7): 5% fewer allowances until 31 Dec 2030 (Art. 12(3-e)).
    derogation_share      share (0 to 1) of the ship's in-scope emissions that fall
                          under an implementing act made under Art. 12(3-c) or (3-d)
                          (island ro-pax and non-cruise passenger services; transnational
                          public-service routes) or Art. 12(3-b) (voyages between a port
                          in an outermost region and a port of the same Member State),
                          until 31 Dec 2030. The user states it; we cannot infer it.
    """
    ice_class_ia: bool = False
    derogation_share: float = 0.0

    def clean(self) -> "ETSExceptions":
        return ETSExceptions(bool(self.ice_class_ia), max(0.0, min(1.0, float(self.derogation_share or 0.0))))


@dataclass
class UKETSExceptions:
    """UK ETS exclusions (Order Schedule 2A para 5(1) and 8): a ship in an excluded
    class, for example one operating a Scottish ferry service, is outside the scheme."""
    excluded_ship: bool = False
    reason: str = ""
