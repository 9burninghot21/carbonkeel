"""ghgcore — deterministic maritime GHG compliance engines.

CII (IMO Reg.28) | EU ETS | UK ETS | FuelEU Maritime | IMO NZF (scenario)
LLMs map data INTO the canonical schema; these engines do ALL calculation.
"""
from .schema import (Vessel, AnnualActivity, VoyageLeg, FuelConsumption,
                     FuelType, ShipType, VoyageScope)
from .cii import compute_cii
from .fueleu import compute_fueleu
from .euets import compute_ets
from .ukets import compute_ukets
from .nzf import compute_nzf
from .scorecard import build_scorecard, Scorecard
from .projection import annualise, Projection

__version__ = "0.2.0"
