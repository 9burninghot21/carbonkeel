"""EEXI check — MARPOL Annex VI Reg. 23/25 (technical efficiency of the
existing fleet). THE FREE PRODUCT: the attained value is published in the
THETIS-MRV export ("Technical efficiency" column), so a required-vs-attained
verdict costs the visitor nothing.

required EEXI = (1 - X/100) x EEDI reference line(capacity)
- EEDI reference lines per MARPOL Reg. 24 table / MEPC.231(65) (a x b^-c)
- X reduction factors per Reg. 25 as amended by MEPC.328(76)
Reduction factors (Reg. 25 Table 3) were checked line-by-line against the
consolidated MARPOL Annex VI text on 2 Oct 2026 and all twelve ship types
match. Capacity bases follow MEPC.364(79) 2.2.3. Sub-threshold
sizes with linear phase-ins are implemented as linear interpolation.

Caveat surfaced in every result: THETIS may report EEXI, EEDI or EIV.
EEDI/EIV are design/estimated indices — comparable in kind but not the
certified EEXI; the verdict is then labelled indicative.
"""
import re
from dataclasses import dataclass
from typing import Optional
from .schema import FuelType, ShipType
from .cii import CF_TCO2_PER_T

# EEDI reference lines: {type: (a, c)}; ref = a * capacity^-c.
# Capacity basis per MEPC.364(79) 2.2.3 - see _capacity_attained/_capacity_required.
EEDI_REF = {
    ShipType.BULK_CARRIER: (961.79, 0.477),
    ShipType.GAS_CARRIER: (1120.00, 0.456),
    ShipType.TANKER: (1218.80, 0.488),
    ShipType.CONTAINER: (174.22, 0.201),
    ShipType.GENERAL_CARGO: (107.48, 0.216),
    ShipType.REFRIGERATED_CARGO: (227.01, 0.244),
    ShipType.COMBINATION_CARRIER: (1219.00, 0.488),
    ShipType.LNG_CARRIER: (2253.7, 0.474),
    ShipType.VEHICLE_CARRIER: (780.36, 0.471),
    ShipType.RO_RO: (1405.15, 0.498),
    ShipType.RO_PAX: (752.16, 0.381),
    ShipType.CRUISE: (170.84, 0.214),
}

# EEXI reduction factors Y%: list of (min_cap, max_cap, Y_at_min, Y_at_max)
# per Reg. 25 / MEPC.328(76); linear within a band. Capacity basis as above.
# VERIFIED 2 Oct 2026 against MARPOL Annex VI Reg. 25 Table 3 (all 12 types).
# Note: the cruise band applies to cruise passenger ships having
# non-conventional propulsion, and is measured in GT.
EEXI_X = {
    ShipType.BULK_CARRIER: [(10_000, 20_000, 0, 20), (20_000, 200_000, 20, 20),
                            (200_000, None, 15, 15)],
    ShipType.GAS_CARRIER: [(2_000, 10_000, 0, 20), (10_000, 15_000, 20, 20),
                           (15_000, None, 30, 30)],
    ShipType.TANKER: [(4_000, 20_000, 0, 20), (20_000, 200_000, 20, 20),
                      (200_000, None, 15, 15)],
    ShipType.CONTAINER: [(10_000, 15_000, 0, 20), (15_000, 40_000, 20, 20),
                         (40_000, 80_000, 30, 30), (80_000, 120_000, 35, 35),
                         (120_000, 200_000, 45, 45), (200_000, None, 50, 50)],
    ShipType.GENERAL_CARGO: [(3_000, 15_000, 0, 30), (15_000, None, 30, 30)],
    ShipType.REFRIGERATED_CARGO: [(3_000, 5_000, 0, 15), (5_000, None, 15, 15)],
    ShipType.COMBINATION_CARRIER: [(4_000, 20_000, 0, 20), (20_000, None, 20, 20)],
    ShipType.LNG_CARRIER: [(10_000, None, 30, 30)],
    ShipType.VEHICLE_CARRIER: [(10_000, None, 15, 15)],
    ShipType.RO_RO: [(1_000, 2_000, 0, 5), (2_000, None, 5, 5)],
    ShipType.RO_PAX: [(250, 1_000, 0, 5), (1_000, None, 5, 5)],
    ShipType.CRUISE: [(25_000, 85_000, 0, 30), (85_000, None, 30, 30)],
}


@dataclass
class EEXIResult:
    attained: Optional[float]      # gCO2/t-nm as reported (None if unparsable)
    attained_basis: str            # "EEXI" | "EEDI" | "EIV" | "unknown"
    required: Optional[float]
    reduction_factor_pct: Optional[float]
    reference: Optional[float]
    margin_pct: Optional[float]    # + = attained below required (good)
    verdict: str                   # "COMPLIANT" | "ABOVE REQUIRED" | "INDICATIVE ..." | "N/A ..."
    notes: list[str]


def parse_technical_efficiency(raw: Optional[str]) -> tuple[Optional[float], str]:
    """'EEXI (5.34 gCO₂/t·nm)' -> (5.34, 'EEXI'). Handles EEDI/EIV too."""
    if not raw:
        return None, "unknown"
    m = re.search(r"(EEXI|EEDI|EIV)[^\d]*([\d.]+)", raw, re.IGNORECASE)
    if not m:
        return None, "unknown"
    return float(m.group(2)), m.group(1).upper()


def _capacity_attained(ship_type: ShipType, dwt: float, gt: float) -> float:
    """Capacity in the denominator of the ATTAINED index.

    MEPC.364(79) §2.2.3, verified against the resolution text 2 Oct 2026:
      §2.2.3.1  bulk carrier, tanker, gas carrier, LNG carrier, ro-ro cargo
                (incl. vehicle carrier), ro-ro passenger, general cargo,
                refrigerated cargo, combination carrier -> DEADWEIGHT
      §2.2.3.2  passenger ships and cruise passenger ships -> GROSS TONNAGE
      §2.2.3.3  containerships -> 70% of deadweight
    """
    if ship_type == ShipType.CRUISE:
        return gt
    if ship_type == ShipType.CONTAINER:
        return 0.70 * dwt
    return dwt


def _capacity_required(ship_type: ShipType, dwt: float, gt: float) -> float:
    """Capacity fed into the REFERENCE LINE for the required value.

    Containerships are the exception that matters: §2.2.3.3.3 says the
    parameters a = 174.22 and c = 0.201 were derived by plotting the index
    against *100%* deadweight, and §2.2.3.3.4 states the required value is

        Required = (1 - X/100) x a x (100% deadweight)^(-c)

    so the reference line takes full DWT even though the attained index is
    computed on 70%. Using 70% in both places understates the required value
    and lets a non-compliant ship appear compliant.
    """
    if ship_type == ShipType.CRUISE:
        return gt
    return dwt


def _x_factor(ship_type: ShipType, capacity: float) -> Optional[float]:
    for lo, hi, x_lo, x_hi in EEXI_X.get(ship_type, []):
        if capacity >= lo and (hi is None or capacity < hi):
            if hi is None or x_lo == x_hi:
                return float(x_lo)
            return x_lo + (x_hi - x_lo) * (capacity - lo) / (hi - lo)
    return None   # below applicability threshold


DEFAULT_SFOC_ME = 175.0   # g/kWh, slow-speed 2-stroke default (no test-bed data)
DEFAULT_SFOC_AE = 215.0   # g/kWh, auxiliary engine default


def estimate_attained_eexi(ship_type: ShipType, dwt: float, gt: float,
                           mcr_kw: float, vref_kn: float,
                           main_fuel: FuelType = FuelType.HFO,
                           sfoc_me: float = DEFAULT_SFOC_ME,
                           sfoc_ae: float = DEFAULT_SFOC_AE) -> tuple[float, list[str]]:
    """SIMPLIFIED attained EEXI per the EEDI formula skeleton:

        attained ≈ (0.75·MCR·CF·SFOC_ME + P_AE·CF·SFOC_AE) / (Capacity·Vref)

    with P_AE = 0.025·MCR + 250 (MCR ≥ 10,000 kW) else 0.05·MCR, per the
    EEDI calculation guidelines. Deliberately ignored (all conservative-ish
    simplifications, listed in the returned notes): PTO/PTI, shaft
    generators/motors, dual-fuel weighting, innovative-technology terms,
    ice-class factors, fw weather factor (=1). A certified EEXI Technical
    File will differ — this is a screening estimate.
    """
    if mcr_kw <= 0 or vref_kn <= 0:
        raise ValueError("mcr_kw and vref_kn must be positive")
    cap = _capacity_attained(ship_type, dwt, gt)
    if cap <= 0:
        raise ValueError("capacity (DWT / GT for cruise) must be positive")
    cf = CF_TCO2_PER_T[main_fuel]          # tCO2/t fuel == gCO2/g fuel
    p_me = 0.75 * mcr_kw
    p_ae = 0.025 * mcr_kw + 250 if mcr_kw >= 10_000 else 0.05 * mcr_kw
    attained = (p_me * cf * sfoc_me + p_ae * cf * sfoc_ae) / (cap * vref_kn)
    notes = [f"Simplified estimate: P_ME=75% MCR ({p_me:,.0f} kW), "
             f"P_AE={p_ae:,.0f} kW, SFOC {sfoc_me}/{sfoc_ae} g/kWh, "
             f"CF({main_fuel.value})={cf}. Excludes PTO/PTI, shaft gen, "
             "ice class, innovative tech, fw — certified Technical File "
             "values will differ."]
    return round(attained, 2), notes


def compute_eexi_custom(ship_type: ShipType, dwt: float, gt: float,
                        attained: Optional[float] = None,
                        mcr_kw: Optional[float] = None,
                        vref_kn: Optional[float] = None,
                        main_fuel: FuelType = FuelType.HFO,
                        sfoc_me: float = DEFAULT_SFOC_ME,
                        sfoc_ae: float = DEFAULT_SFOC_AE) -> EEXIResult:
    """Custom-vessel check: pass a known attained EEXI, or MCR + Vref to
    estimate one. Verdict basis is 'EEXI' for a supplied value, 'ESTIMATED'
    (=> indicative verdict) for a computed one."""
    extra_notes: list[str] = []
    basis = "EEXI"
    if attained is None:
        if mcr_kw is None or vref_kn is None:
            raise ValueError("Supply either attained EEXI, or mcr_kw + vref_kn "
                             "to estimate it.")
        attained, extra_notes = estimate_attained_eexi(
            ship_type, dwt, gt, mcr_kw, vref_kn, main_fuel, sfoc_me, sfoc_ae)
        basis = "ESTIMATED"
    # Reuse the reference/required/verdict pipeline via a synthetic EEXI
    # string (parser only recognises EEXI/EEDI/EIV), then relabel the basis.
    result = compute_eexi(ship_type, dwt, gt, f"EEXI ({attained} gCO2/t·nm)")
    result.attained_basis = basis
    if basis == "ESTIMATED":
        if not result.verdict.startswith(("N/A", "NO REPORTED")):
            result.verdict = "INDICATIVE " + result.verdict.replace("INDICATIVE ", "")
        result.notes.extend(extra_notes)
    return result


def compute_eexi(ship_type: ShipType, dwt: float, gt: float,
                 tech_efficiency_raw: Optional[str]) -> EEXIResult:
    notes = ["Reference lines / reduction factors per MARPOL Reg. 24-25 "
             "(MEPC.231(65)); reduction factors per MARPOL Annex VI Reg. 25 "
             "Table 3, verified 2 Oct 2026."]
    attained, basis = parse_technical_efficiency(tech_efficiency_raw)

    if ship_type not in EEDI_REF:
        return EEXIResult(attained, basis, None, None, None, None,
                          "N/A — no EEDI reference line for this ship type", notes)
    cap_ref = _capacity_required(ship_type, dwt, gt)
    if cap_ref <= 0:
        return EEXIResult(attained, basis, None, None, None, None,
                          "N/A — capacity (DWT/GT) required", notes)
    # X bands are defined on DWT (GT for cruise), not the ref-line capacity
    x = _x_factor(ship_type, gt if ship_type == ShipType.CRUISE else dwt)
    if x is None:
        return EEXIResult(attained, basis, None, None, None, None,
                          "N/A — below EEXI applicability threshold for this type",
                          notes)

    a, c = EEDI_REF[ship_type]
    reference = a * cap_ref ** (-c)
    required = reference * (1 - x / 100)

    if attained is None:
        return EEXIResult(None, basis, round(required, 2), x, round(reference, 2),
                          None, "NO REPORTED VALUE — required shown for reference",
                          notes)

    margin = (required - attained) / required * 100
    if basis == "EEXI":
        verdict = "COMPLIANT" if attained <= required else "ABOVE REQUIRED"
    else:
        verdict = ("INDICATIVE " +
                   ("COMPLIANT" if attained <= required else "ABOVE REQUIRED"))
        notes.append(f"Reported value is {basis}, not certified EEXI — "
                     "design-index comparison, treat as indicative.")
    if verdict.endswith("ABOVE REQUIRED"):
        notes.append("Typical EEXI remedies: Engine/Shaft Power Limitation "
                     "(EPL/ShaPoLi), then energy-saving devices; the OMM must "
                     "document the limitation.")
    return EEXIResult(round(attained, 2), basis, round(required, 2), x,
                      round(reference, 2), round(margin, 1), verdict, notes)
