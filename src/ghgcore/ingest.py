"""Agentic ingestion — "data in their format" -> canonical schema.

Two stages, by design:
1. DETERMINISTIC first pass: column-synonym matching handles the ~80% of
   noon-report Excels/CSVs that use recognisable headers. Free, auditable.
2. LLM fallback (production): when columns are unrecognised, the file sample
   + MAPPING_PROMPT is sent to the Claude API, which must return ONLY a JSON
   column-mapping. The mapping is then applied by deterministic code — the
   LLM never touches a number used in a compliance calculation.
"""
import csv
from .schema import (AnnualActivity, Vessel, VoyageLeg, FuelConsumption,
                     FuelType, ShipType, VoyageScope)
from .ports import scope_for_leg, uk_share_for_leg

SYNONYMS = {
    "date": {"date", "report date", "noon date", "day"},
    "distance_nm": {"distance", "dist", "distance sailed", "obs distance",
                    "observed distance", "steamed", "distance (nm)", "nm"},
    "hfo_t": {"hfo", "hfo cons", "hfo consumption", "hsfo", "fo cons", "hfo (mt)"},
    "lfo_t": {"lfo", "vlsfo", "lsfo", "ulsfo", "lfo cons", "vlsfo (mt)"},
    "mgo_t": {"mgo", "mdo", "do", "mgo cons", "gasoil", "mdo/mgo", "mgo (mt)"},
    "lng_t": {"lng", "lng cons", "bog", "lng (mt)"},
    "from_port": {"from", "departure", "port from", "last port"},
    "to_port": {"to", "arrival", "port to", "next port"},
}

MAPPING_PROMPT = """You are a maritime data-mapping assistant. You will receive
the header row and 3 sample data rows of a vessel operational report in an
unknown format. Map the columns to this canonical schema and respond ONLY with
JSON, no prose, no markdown fences:

{"mapping": {"<source column name>": "<canonical field>"}, "unmapped": [...],
 "warnings": [...]}

Canonical fields: date, distance_nm, hfo_t, lfo_t, mgo_t, lng_t,
methanol_t, biofuel_t, from_port, to_port, position_lat, position_lon,
speed_kn, me_hours. Units must be metric tonnes for fuel and nautical miles
for distance; add a warning if the source appears to use other units
(e.g. litres, km) and note the conversion factor. Never invent columns.
"""


CANONICAL_FIELDS = {"date", "distance_nm", "hfo_t", "lfo_t", "mgo_t", "lng_t",
                    "methanol_t", "biofuel_t", "from_port", "to_port",
                    "position_lat", "position_lon", "speed_kn", "me_hours"}


def match_columns_llm(headers: list[str], sample_rows: list[list[str]],
                      client=None) -> tuple[dict[str, str], list[str], list[str]]:
    """Stage-2 mapper: ask Claude for a column mapping when synonyms fail.

    The LLM returns ONLY a JSON mapping (MAPPING_PROMPT contract); this
    function validates it — unknown canonical fields are rejected, columns
    it didn't map stay unmapped — and deterministic code applies it. The
    LLM never sees or produces a compliance number.

    `client` is injectable for tests; default requires the `anthropic`
    package and ANTHROPIC_API_KEY in the environment.
    Returns (mapping, unmapped, warnings).
    """
    import json, os
    if client is None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "LLM mapping fallback needs ANTHROPIC_API_KEY set (and "
                "`pip install anthropic`). Deterministic mapping already "
                "failed; fix headers manually or set the key.")
        import anthropic
        client = anthropic.Anthropic()

    sample = "\n".join(",".join(str(c) for c in r) for r in sample_rows[:3])
    msg = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        system=MAPPING_PROMPT,
        messages=[{"role": "user",
                   "content": f"HEADERS: {','.join(headers)}\nSAMPLE ROWS:\n{sample}"}],
    )
    raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    data = json.loads(raw)   # contract: pure JSON, no fences

    mapping, warnings = {}, list(data.get("warnings", []))
    for src, canon in data.get("mapping", {}).items():
        if src not in headers:
            warnings.append(f"LLM invented column {src!r} — ignored.")
        elif canon not in CANONICAL_FIELDS:
            warnings.append(f"LLM mapped {src!r} to unknown field {canon!r} — ignored.")
        else:
            mapping[src] = canon
    unmapped = [h for h in headers if h not in mapping]
    return mapping, unmapped, warnings


def match_columns(headers: list[str]) -> tuple[dict[str, str], list[str]]:
    """Deterministic pass. Returns ({source_col: canonical}, unmapped)."""
    mapping: dict[str, str] = {}
    unmapped: list[str] = []
    for h in headers:
        key = h.strip().lower()
        hit = next((canon for canon, syns in SYNONYMS.items() if key in syns), None)
        if hit:
            mapping[h] = hit
        else:
            unmapped.append(h)
    return mapping, unmapped


def ingest_noon_csv(path: str, vessel: Vessel, year: int,
                    scope: VoyageScope = VoyageScope.EXTRA_EEA) -> tuple[AnnualActivity, dict]:
    """Ingest a noon-report CSV via the deterministic mapper.

    Returns (activity, report) where report carries mapping + data-quality
    flags. When from/to port columns are mapped, each row's EU scope is
    derived from the port pair (ports.scope_for_leg); rows with unresolvable
    ports fall back to `scope` and are flagged for review.
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        headers = next(reader)
        mapping, unmapped = match_columns(headers)
        idx = {canon: headers.index(src) for src, canon in mapping.items()}

        needed = {"distance_nm"} - set(idx)
        if needed:
            raise ValueError(f"Cannot ingest: missing required fields {needed}. "
                             f"Unmapped columns {unmapped} -> send to LLM mapper.")

        have_ports = "from_port" in idx and "to_port" in idx
        # accumulate per (eu_scope, uk_share): [distance, {fuel: t}]
        acc: dict[tuple, list] = {}
        flags: list[str] = []
        rows = fallback_rows = 0
        for row in reader:
            rows += 1
            uk = 0.0
            if have_ports:
                row_scope, row_flags = scope_for_leg(row[idx["from_port"]],
                                                     row[idx["to_port"]])
                uk = uk_share_for_leg(row[idx["from_port"]], row[idx["to_port"]])
                for fl in row_flags:
                    if fl not in flags:
                        flags.append(fl)
                if row_scope is None:
                    row_scope = scope
                    fallback_rows += 1
            else:
                row_scope = scope
                fallback_rows += 1
            bucket = acc.setdefault((row_scope, uk), [0.0, {}])
            bucket[0] += _f(row, idx.get("distance_nm"))
            for canon, ft in (("hfo_t", FuelType.HFO), ("lfo_t", FuelType.LFO),
                              ("mgo_t", FuelType.MDO_MGO), ("lng_t", FuelType.LNG)):
                if canon in idx:
                    bucket[1][ft] = bucket[1].get(ft, 0.0) + _f(row, idx[canon])

    legs = [VoyageLeg(s, d, [FuelConsumption(k, v) for k, v in fuel.items() if v > 0],
                      f"Aggregated noon reports ({s.value})", uk_share=uk)
            for (s, uk), (d, fuel) in acc.items()]
    activity = AnnualActivity(vessel, year, legs)
    if not have_ports:
        flags.append("No port columns mapped — default scope "
                     f"'{scope.value}' applied to all legs.")
    elif fallback_rows:
        flags.append(f"{fallback_rows}/{rows} rows had unresolvable ports — "
                     f"default scope '{scope.value}' applied to those rows.")
    report = {"rows": rows, "mapping": mapping, "unmapped_columns": unmapped,
              "flags": flags}
    return activity, report


def _f(row, i) -> float:
    if i is None:
        return 0.0
    try:
        return float(str(row[i]).replace(",", "").strip() or 0)
    except (ValueError, IndexError):
        return 0.0
