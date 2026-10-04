"""CII engine — MARPOL Annex VI Reg. 28, per IMO guidelines G1–G4.

G1 MEPC.352(78): attained CII = (Σ fuel_j × CF_j) / (Capacity × Distance)
G2 MEPC.353(78): reference lines  CII_ref = a × Capacity^(-c)
G3 MEPC.338(76) as amended by MEPC.400(83): Z reduction factors
G4 MEPC.354(78): rating boundaries (dd vectors)

G2/G4 tables below were verified line-by-line against the official resolution
PDFs (wwwcdn.imo.org, MEPC.353(78) Annex 15 Table 1 and MEPC.354(78) Annex 16
Table 1) on 8 Jul 2026, including the gas-carrier 65,000 dwt split and the
general-cargo 20,000 dwt split. Types not yet in the ShipType enum (LNG
carrier, ro-ro, ro-pax, cruise — GT-based) have their official parameters
noted in comments pending D0.5.2.
"""
from dataclasses import dataclass
from .schema import AnnualActivity, FuelType, ShipType

# CF: tonnes CO2 per tonne fuel (2018 DCS Guidelines / G1)
CF_TCO2_PER_T = {
    FuelType.HFO: 3.114,
    FuelType.LFO: 3.151,
    FuelType.MDO_MGO: 3.206,
    FuelType.LNG: 2.750,
    FuelType.METHANOL: 1.375,
    # Biofuel tank-to-wake CO2 per MEPC.1/Circ.905: sustainable biofuel share
    # may be counted at 0 gCO2 TtW if certified (WtW ≥65% below fossil).
    FuelType.BIOFUEL_B24: 3.114 * 0.76,   # simplified: fossil share only — VERIFY
    FuelType.BIOFUEL_B100: 0.0,
}

# G2 reference lines (a, c), capacity = DWT. Verified vs MEPC.353(78) Table 1.
# Types with a DWT-threshold split are handled in _g2_params below.
REFERENCE_LINES = {
    ShipType.BULK_CARRIER: (4745.0, 0.622),       # capacity capped at 279,000
    ShipType.TANKER: (5247.0, 0.610),
    ShipType.CONTAINER: (1984.0, 0.489),
    ShipType.GENERAL_CARGO: (31948.0, 0.792),     # >=20,000 dwt; <20k in _g2_params
    ShipType.GAS_CARRIER: (8104.0, 0.639),        # <65,000 dwt; >=65k in _g2_params
    ShipType.REFRIGERATED_CARGO: (4600.0, 0.557),
    ShipType.COMBINATION_CARRIER: (5119.0, 0.622),
    ShipType.RO_RO: (1967.0, 0.485),              # GT capacity
    ShipType.RO_PAX: (2023.0, 0.460),             # GT capacity
    ShipType.CRUISE: (930.0, 0.383),              # GT capacity
    # LNG carrier and vehicle carrier have threshold splits — see _g2_params.
}
GENERAL_CARGO_LT20K = (588.0, 0.3885)
GAS_CARRIER_GE65K = (14405e7, 2.071)
LNG_GE100K = (9.827, 0.0)          # constant reference line
LNG_65_100K = (14479e10, 2.673)
LNG_LT65K = (14779e10, 2.673)      # reference evaluated at fixed capacity 65,000
VEHICLE_GE30K_GT = (3627.0, 0.590)  # reference capped at 57,700 GT
VEHICLE_LT30K_GT = (330.0, 0.329)

# Types whose CII capacity basis is gross tonnage (MEPC.353/354(78) Table 1)
GT_CAPACITY_TYPES = {ShipType.RO_RO, ShipType.RO_PAX, ShipType.CRUISE,
                     ShipType.VEHICLE_CARRIER}

# G3 Z factors (% vs 2019 reference). 2027-2030 adopted MEPC.400(83).
Z_FACTORS = {2023: 5.0, 2024: 7.0, 2025: 9.0, 2026: 11.0,
             2027: 13.625, 2028: 16.25, 2029: 18.875, 2030: 21.5}

# G4 dd vectors exp(d1..d4). Verified vs MEPC.354(78) Table 1.
DD_VECTORS = {
    ShipType.BULK_CARRIER: (0.86, 0.94, 1.06, 1.18),
    ShipType.TANKER: (0.82, 0.93, 1.08, 1.28),
    ShipType.CONTAINER: (0.83, 0.94, 1.07, 1.19),
    ShipType.GENERAL_CARGO: (0.83, 0.94, 1.06, 1.19),
    ShipType.GAS_CARRIER: (0.85, 0.95, 1.06, 1.25),   # <65,000 dwt
    ShipType.REFRIGERATED_CARGO: (0.78, 0.91, 1.07, 1.20),
    ShipType.COMBINATION_CARRIER: (0.87, 0.96, 1.06, 1.14),
    ShipType.LNG_CARRIER: (0.78, 0.92, 1.10, 1.37),   # <100,000 dwt
    ShipType.RO_RO: (0.76, 0.89, 1.08, 1.27),
    ShipType.RO_PAX: (0.76, 0.92, 1.14, 1.30),
    ShipType.CRUISE: (0.87, 0.95, 1.06, 1.16),
    ShipType.VEHICLE_CARRIER: (0.86, 0.94, 1.06, 1.16),
}
GAS_CARRIER_GE65K_DD = (0.81, 0.91, 1.12, 1.44)
LNG_GE100K_DD = (0.89, 0.98, 1.06, 1.13)


def _g2_params(ship_type: ShipType, dwt: float, gt: float) -> tuple[float, float]:
    if ship_type == ShipType.GAS_CARRIER and dwt >= 65_000:
        return GAS_CARRIER_GE65K
    if ship_type == ShipType.GENERAL_CARGO and dwt < 20_000:
        return GENERAL_CARGO_LT20K
    if ship_type == ShipType.LNG_CARRIER:
        if dwt >= 100_000:
            return LNG_GE100K
        return LNG_65_100K if dwt >= 65_000 else LNG_LT65K
    if ship_type == ShipType.VEHICLE_CARRIER:
        return VEHICLE_GE30K_GT if gt >= 30_000 else VEHICLE_LT30K_GT
    return REFERENCE_LINES[ship_type]


def _dd(ship_type: ShipType, dwt: float) -> tuple[float, float, float, float]:
    if ship_type == ShipType.GAS_CARRIER and dwt >= 65_000:
        return GAS_CARRIER_GE65K_DD
    if ship_type == ShipType.LNG_CARRIER and dwt >= 100_000:
        return LNG_GE100K_DD
    return DD_VECTORS[ship_type]


def _capacities(ship_type: ShipType, dwt: float, gt: float) -> tuple[float, float]:
    """(attained_capacity, reference_capacity) per G1/G2 capacity rules."""
    if ship_type in GT_CAPACITY_TYPES:
        if gt <= 0:
            raise ValueError(f"{ship_type.value} uses GT capacity — vessel.gt "
                             "must be set (> 0).")
        ref = min(gt, 57_700) if ship_type == ShipType.VEHICLE_CARRIER else gt
        return gt, ref
    cap = min(dwt, 279_000) if ship_type == ShipType.BULK_CARRIER else dwt
    ref = 65_000 if (ship_type == ShipType.LNG_CARRIER and dwt < 65_000) else cap
    return cap, ref


@dataclass
class CIICorrections:
    """G5 (MEPC.355(78)) corrections, supplied as certified/documented values.

    The engine applies them arithmetically and records them in the audit
    notes; deriving them (ice-class factors, STS voyage exclusions, shuttle-
    tanker fj, reefer/cargo-heating fc, etc.) is the operator's evidence per
    the guidelines — we never invent a correction.
    """
    excluded_co2_t: float = 0.0       # voyage-adjustment CO2 exclusions
    excluded_distance_nm: float = 0.0  # matching distance exclusions
    capacity_correction: float = 1.0   # fj x fm x fi x fc ... combined factor
    basis: str = ""                    # documentation reference (SEEMP/verifier)


@dataclass
class CIIResult:
    attained: float          # gCO2 / dwt-nm
    required: float
    reference: float
    z_factor_pct: float
    rating: str              # A-E
    ratio: float             # attained / required
    co2_tonnes: float
    notes: list[str]
    # Absolute rating boundaries (gCO2/capacity-nm): attained <= boundaries[X]
    # rates X (E above 'D'). dd vector x required, per G4.
    boundaries: dict = None


def compute_cii(activity: AnnualActivity,
                corrections: "CIICorrections | None" = None) -> CIIResult:
    v = activity.vessel
    notes: list[str] = []

    co2_t = sum(t * CF_TCO2_PER_T[f] for f, t in activity.total_fuel_by_type().items())
    dist = activity.total_distance_nm
    capacity, ref_capacity = _capacities(v.ship_type, v.dwt, v.gt)

    if corrections is not None:
        co2_t = max(0.0, co2_t - corrections.excluded_co2_t)
        dist = max(1e-9, dist - corrections.excluded_distance_nm)
        capacity *= corrections.capacity_correction
        notes.append(
            f"G5 corrections applied (MEPC.355(78)): -{corrections.excluded_co2_t} t "
            f"CO2, -{corrections.excluded_distance_nm} nm, capacity factor "
            f"{corrections.capacity_correction}. Basis: {corrections.basis or 'not documented'}.")

    attained = (co2_t * 1e6) / (capacity * dist)  # gCO2 / (dwt|gt)-nm

    a, c = _g2_params(v.ship_type, v.dwt, v.gt)
    reference = a * ref_capacity ** (-c)
    z = Z_FACTORS.get(activity.year)
    if z is None:
        z = Z_FACTORS[max(Z_FACTORS)]
        notes.append(f"No Z factor for {activity.year}; using {z}% (latest adopted).")
    required = reference * (1 - z / 100)

    ratio = attained / required
    d1, d2, d3, d4 = _dd(v.ship_type, v.dwt)
    if ratio <= d1:
        rating = "A"
    elif ratio <= d2:
        rating = "B"
    elif ratio <= d3:
        rating = "C"
    elif ratio <= d4:
        rating = "D"
    else:
        rating = "E"

    return CIIResult(attained=round(attained, 3), required=round(required, 3),
                     reference=round(reference, 3), z_factor_pct=z, rating=rating,
                     ratio=round(ratio, 3), co2_tonnes=round(co2_t, 1), notes=notes,
                     boundaries={"A": round(d1 * required, 3),
                                 "B": round(d2 * required, 3),
                                 "C": round(d3 * required, 3),
                                 "D": round(d4 * required, 3)})
