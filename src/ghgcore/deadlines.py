"""Compliance calendar — every regime's dated obligations for a fleet.

Deadlines are anchored to a compliance (emissions) year Y; most obligations
fall in Y+1. Dates below are the standing regulatory calendar; entries carry
their legal basis so the alert text is self-justifying.
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class Deadline:
    due: date
    regime: str
    what: str
    basis: str


# (month, day, years_after_Y, regime, what, basis)
_CALENDAR = [
    (1, 31, 1, "FuelEU", "FuelEU report for year Y to the verifier",
     "Regulation (EU) 2023/1805, Article 15"),
    (3, 31, 1, "EU MRV / DCS", "Verified EU MRV emissions report for year Y submitted "
     "through THETIS-MRV; IMO DCS fuel data for year Y sent to the flag administration",
     "Regulation (EU) 2015/757, Article 11; MARPOL Annex VI, Regulation 27"),
    (4, 30, 1, "FuelEU", "FuelEU compliance balance for year Y recorded; pooling, banking and "
     "borrowing choices entered in the FuelEU Database",
     "Regulation (EU) 2023/1805, Articles 20–21"),
    (5, 31, 1, "IMO CII", "Statement of Compliance issued and CII rating for year Y set. "
     "A rating of D for three years running, or E in any year, requires a "
     "corrective action plan in SEEMP Part III", "MARPOL Annex VI, Regulation 28"),
    (6, 30, 1, "FuelEU / EU MRV", "FuelEU Document of Compliance for year Y issued and "
     "kept on board, alongside the EU MRV Document of Compliance",
     "Regulation (EU) 2023/1805, Article 24"),
    (9, 30, 1, "EU ETS", "Surrender EU allowances for verified year Y "
     "emissions (phase-in: 40% of 2024, 70% of 2025, 100% from 2026)",
     "Directive 2003/87/EC, Articles 3gb and 12(3)"),
    (3, 31, 1, "UK ETS", "UK ETS verified emissions report for year Y submitted",
     "UK ETS (Maritime) Order 2026, Schedule 2A, paragraph 14; first period is the second half of 2026"),
    (4, 30, 1, "UK ETS", "Surrender UK allowances (UKAs) for year Y domestic emissions",
     "UK ETS (Maritime) Order 2026, Schedule 2A, paragraph 15"),
]


# first emissions year each regime applies to (from the primary texts)
_REGIME_FROM_YEAR = {"EU ETS": 2024,        # Directive Art. 3gb: 40% of 2024 emissions
                     "UK ETS": 2026,        # SI 2026/392: scheme starts 1 July 2026
                     "FuelEU": 2025,        # Regulation (EU) 2023/1805 applies from 1 Jan 2025
                     "FuelEU / EU MRV": 2025}


def deadlines_for(year: int) -> list[Deadline]:
    """All dated obligations arising from compliance year `year`, sorted.

    Regimes that did not yet apply to `year` are left out. UK ETS surrender for 2026 is due
    on 30 April 2028, not 30 April 2027 (SI 2026/392 Sch. 2A para 15(2)(a)); the same date
    applies to 2027, so the first two scheme years fall due together."""
    out = []
    for m, d, off, regime, what, basis in _CALENDAR:
        if year < _REGIME_FROM_YEAR.get(regime, 0):
            continue
        due = date(year + off, m, d)
        text = what.replace("year Y", str(year))
        if regime == "UK ETS" and what.startswith("Surrender") and year == 2026:
            due = date(2028, 4, 30)
            text += " (first scheme year, 1 July to 31 December; due in 2028)"
        out.append(Deadline(due, regime, text, basis))
    return sorted(out, key=lambda x: x.due)


def to_ics(deadlines: list[Deadline], fleet_name: str = "Fleet") -> str:
    """Minimal RFC-5545 all-day events — importable into Outlook/Google."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//CarbonKeel//Compliance Calendar//EN"]
    for i, d in enumerate(deadlines):
        ymd = d.due.strftime("%Y%m%d")
        lines += ["BEGIN:VEVENT",
                  f"UID:carbonkeel-{ymd}-{i}@carbonkeel",
                  f"DTSTART;VALUE=DATE:{ymd}",
                  f"SUMMARY:[{d.regime}] {fleet_name}: {d.what[:120]}",
                  f"DESCRIPTION:{d.what} — {d.basis}",
                  "BEGIN:VALARM", "TRIGGER:-P14D", "ACTION:DISPLAY",
                  f"DESCRIPTION:14 days to: {d.what[:100]}", "END:VALARM",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
