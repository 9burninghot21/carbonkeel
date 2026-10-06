"""Annualisation — project partial-year activity to a year-end position.

CII is a ratio (CO2 / capacity·distance), so it is scale-invariant: scaling
all legs uniformly leaves attained CII unchanged. What annualisation adds is
honest COST projection (ETS EUAs, FuelEU balance grow with activity) and a
confidence label so a 5-day sample is never presented like a full year.

Method: linear extrapolation of fuel and distance by day-coverage. This
assumes the observed period is representative (no seasonality/laid-up
correction — flagged in notes; smarter models are a Phase 1 what-if concern).
"""
from dataclasses import dataclass
from .schema import AnnualActivity, VoyageLeg, FuelConsumption
from .scorecard import Scorecard, build_scorecard

DAYS_PER_YEAR = 365.0


def confidence(days: float) -> str:
    if days >= 270:
        return "HIGH"
    if days >= 90:
        return "MEDIUM"
    if days >= 30:
        return "LOW"
    return "INDICATIVE"


@dataclass
class Projection:
    days_observed: float
    scale_factor: float
    confidence: str
    scorecard: Scorecard          # built from the annualised activity
    notes: list[str]


def annualise(activity: AnnualActivity, days_observed: float,
              eua_price: float = 70.0, nzf_year: int = 2028) -> Projection:
    """Scale a partial-year activity to 365 days and score the result."""
    if days_observed <= 0:
        raise ValueError("days_observed must be positive")
    if days_observed > DAYS_PER_YEAR:
        raise ValueError("days_observed exceeds a year — pass the raw activity instead")

    k = DAYS_PER_YEAR / days_observed
    scaled_legs = [
        VoyageLeg(leg.scope, leg.distance_nm * k,
                  [FuelConsumption(fc.fuel, fc.tonnes * k) for fc in leg.fuel_consumed],
                  f"{leg.description} [annualised x{k:.2f}]")
        for leg in activity.legs
    ]
    scaled = AnnualActivity(activity.vessel, activity.year, scaled_legs,
                              activity.ets_calibration, activity.fuel_is_combusted)
    sc = build_scorecard(scaled, eua_price=eua_price, nzf_year=nzf_year)

    conf = confidence(days_observed)
    notes = [
        f"Projected from {days_observed:.0f} observed days (x{k:.2f} linear "
        f"scaling); confidence {conf}.",
        "Assumes observed period is representative of the full year — "
        "seasonality, dry-dock and idle periods are not modelled.",
    ]
    return Projection(days_observed, round(k, 4), conf, sc, notes)
