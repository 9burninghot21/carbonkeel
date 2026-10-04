"""FuelEU pooling optimizer — Regulation (EU) 2023/1805 Art. 21.

Rule: ships may pool their compliance balances; if the pool's total CB >= 0,
every member is deemed compliant for the period. So a surplus ship can
absorb deficit ships' penalties — the economic core of the marketplace.

Optimization: all surplus ships contribute capacity; choosing which deficit
ships to admit is a 0/1 knapsack (weight = |deficit| tonnes, value = the
penalty that ship would otherwise pay). Solved exactly by DP at 1-tonne
granularity for realistic fleet sizes, greedy density fallback above that.

Registration deadline: pools must be notified in the FuelEU Database by
30 April of the verification year.
"""
from dataclasses import dataclass
from .fueleu import penalty_equiv


@dataclass
class PoolCandidate:
    imo: str
    name: str
    cb_tco2e: float          # FuelEU compliance balance, tonnes CO2e
    ghg_intensity: float     # attained gCO2e/MJ (for penalty math)

    @property
    def penalty_eur(self) -> float:
        if self.cb_tco2e >= 0:
            return 0.0
        return penalty_equiv(self.cb_tco2e * 1e6, self.ghg_intensity)


@dataclass
class PoolSuggestion:
    members: list[PoolCandidate]         # surplus ships + admitted deficits
    pool_cb_tco2e: float
    avoided_penalty_eur: float
    uncovered: list[PoolCandidate]       # deficit ships left out
    uncovered_penalty_eur: float
    notes: list[str]


DP_CAPACITY_LIMIT = 500_000   # tonnes; above this fall back to greedy


def suggest_pool(candidates: list[PoolCandidate]) -> PoolSuggestion:
    surplus = [c for c in candidates if c.cb_tco2e > 0]
    deficits = [c for c in candidates if c.cb_tco2e < 0]
    capacity = sum(c.cb_tco2e for c in surplus)
    notes = ["Pool valid iff total CB >= 0 (Art. 21(2)); register in the "
             "FuelEU Database by 30 April.",
             "Suggested surplus compensation: 30-70% of the avoided penalty "
             "(negotiated; bounded by the deficit ship's alternative cost)."]

    if not deficits:
        return PoolSuggestion(surplus, round(capacity, 1), 0.0, [], 0.0,
                              notes + ["No deficit ships — surplus is bankable "
                                       "(Art. 20) or sellable to third parties."])
    if capacity <= 0:
        pen = sum(d.penalty_eur for d in deficits)
        return PoolSuggestion([], round(capacity, 1), 0.0, deficits, round(pen),
                              notes + ["No surplus capacity in this fleet — "
                                       "seek an external pooling partner."])

    weights = [max(1, round(-d.cb_tco2e)) for d in deficits]
    values = [d.penalty_eur for d in deficits]
    cap = int(capacity)

    if cap <= DP_CAPACITY_LIMIT:
        chosen = _knapsack(weights, values, cap)
    else:
        chosen = _greedy(weights, values, cap)

    admitted = [deficits[i] for i in chosen]
    left = [d for i, d in enumerate(deficits) if i not in set(chosen)]
    avoided = sum(d.penalty_eur for d in admitted)
    pool_cb = capacity + sum(d.cb_tco2e for d in admitted)
    return PoolSuggestion(surplus + admitted, round(pool_cb, 1), round(avoided),
                          left, round(sum(d.penalty_eur for d in left)), notes)


def _knapsack(weights: list[int], values: list[float], cap: int) -> list[int]:
    """Exact 0/1 knapsack via DP; returns chosen item indexes."""
    n = len(weights)
    dp = [[0.0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        row, prev = dp[i], dp[i - 1]
        for c in range(cap + 1):
            row[c] = prev[c]
            if w <= c and prev[c - w] + v > row[c]:
                row[c] = prev[c - w] + v
    chosen, c = [], cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    return chosen[::-1]


def _greedy(weights: list[int], values: list[float], cap: int) -> list[int]:
    order = sorted(range(len(weights)), key=lambda i: -values[i] / weights[i])
    chosen, used = [], 0
    for i in order:
        if used + weights[i] <= cap:
            chosen.append(i)
            used += weights[i]
    return chosen
