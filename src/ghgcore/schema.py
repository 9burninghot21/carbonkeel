"""Canonical data schema — the single spine all regulation engines consume.

Every ingestion source (noon reports, DCS exports, MRV data, BDNs) is mapped
into these structures by the agentic ingestion layer. Engines never see raw
customer formats.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ShipType(str, Enum):
    BULK_CARRIER = "bulk_carrier"
    TANKER = "tanker"
    CONTAINER = "container"
    GENERAL_CARGO = "general_cargo"
    GAS_CARRIER = "gas_carrier"          # non-LNG
    REFRIGERATED_CARGO = "refrigerated_cargo"
    COMBINATION_CARRIER = "combination_carrier"
    LNG_CARRIER = "lng_carrier"          # DWT capacity, 65k/100k splits
    # GT-capacity types (CII uses gross tonnage, not DWT):
    RO_RO = "ro_ro"                      # ro-ro cargo ship
    RO_PAX = "ro_pax"                    # ro-ro passenger ship
    CRUISE = "cruise"                    # cruise passenger ship
    VEHICLE_CARRIER = "vehicle_carrier"  # ro-ro cargo (vehicle carrier)


class FuelType(str, Enum):
    HFO = "hfo"
    LFO = "lfo"
    MDO_MGO = "mdo_mgo"
    LNG = "lng"
    METHANOL = "methanol"
    BIOFUEL_B24 = "biofuel_b24"   # 24% UCOME blend w/ VLSFO (illustrative)
    BIOFUEL_B100 = "biofuel_b100"  # 100% UCOME (illustrative)


class EngineType(str, Enum):
    """Main-engine consumer-unit class — drives LNG methane slip
    (Reg. 2023/1805 Annex II column 9). Irrelevant for liquid fuels."""
    OTTO_MS = "otto_medium_speed"     # dual-fuel Otto, medium speed (3.1% slip)
    OTTO_SS = "otto_slow_speed"       # dual-fuel Otto, slow speed (1.7%)
    DIESEL_DF = "diesel_dual_fuel"    # dual-fuel Diesel, slow speed (0.2%)
    LBSI = "lbsi"                     # lean-burn spark-ignited (2.6%)


class VoyageScope(str, Enum):
    """Jurisdictional scope of a voyage leg for EU/UK regimes."""
    INTRA_EEA = "intra_eea"        # both ports EEA -> 100% EU scope
    EXTRA_EEA = "extra_eea"        # one port EEA  -> 50% EU scope
    AT_BERTH_EEA = "at_berth_eea"  # in EEA port    -> 100% EU scope
    OUT_OF_SCOPE = "out_of_scope"  # no EEA nexus


@dataclass
class FuelConsumption:
    fuel: FuelType
    tonnes: float


@dataclass
class VoyageLeg:
    """One leg: port A -> port B (or a berth stay), with fuel burned."""
    scope: VoyageScope
    distance_nm: float
    fuel_consumed: list[FuelConsumption] = field(default_factory=list)
    description: str = ""
    # UK ETS surrender share for this leg (1.0 UK domestic/berth, 0.5 GB<->NI,
    # 0.0 otherwise). None = unknown/not derived; engines treat as 0.
    uk_share: Optional[float] = None


@dataclass
class Vessel:
    imo_number: str
    name: str
    ship_type: ShipType
    dwt: float                       # deadweight tonnage
    gt: float                        # gross tonnage
    year_built: Optional[int] = None
    # Main-engine class; only matters for LNG slip. Default = Otto medium
    # speed, the most conservative common configuration.
    engine_type: EngineType = EngineType.OTTO_MS


@dataclass
class AnnualActivity:
    """One vessel-year of activity — the unit every engine scores."""
    vessel: Vessel
    year: int
    legs: list[VoyageLeg] = field(default_factory=list)

    @property
    def total_distance_nm(self) -> float:
        return sum(l.distance_nm for l in self.legs)

    def total_fuel_by_type(self) -> dict[FuelType, float]:
        out: dict[FuelType, float] = {}
        for leg in self.legs:
            for fc in leg.fuel_consumed:
                out[fc.fuel] = out.get(fc.fuel, 0.0) + fc.tonnes
        return out
