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
     "Reg. (EU) 2023/1805 Art. 15"),
    (3, 31, 1, "EU MRV / DCS", "Verified MRV emissions report submitted via "
     "THETIS-MRV; IMO DCS fuel data to flag administration",
     "Reg. (EU) 2015/757 Art. 11; MARPOL VI Reg. 27"),
    (4, 30, 1, "FuelEU", "Compliance balance recorded; pooling registration "
     "and banking/borrowing elections in the FuelEU Database",
     "Reg. (EU) 2023/1805 Arts. 20-21"),
    (5, 31, 1, "IMO CII", "Statement of Compliance (DCS/CII) issued; CII "
     "rating determined — 3rd consecutive D or any E triggers SEEMP III "
     "corrective plan", "MARPOL VI Reg. 28"),
    (6, 30, 1, "FuelEU / EU MRV", "FuelEU Document of Compliance issued and "
     "carried on board; MRV DoC on board",
     "Reg. (EU) 2023/1805 Art. 24"),
    (9, 30, 1, "EU ETS", "Surrender allowances covering year-Y verified "
     "emissions (40%/70%/100% phase-in)", "Directive 2003/87/EC Art. 12"),
    (3, 31, 1, "UK ETS", "UK ETS verified emissions report for year Y",
     "UK ETS (Maritime) Order 2026 — first period H2 2026"),
    (4, 30, 1, "UK ETS", "Surrender UKAs for year-Y UK domestic emissions",
     "UK ETS Order 2026"),
]


def deadlines_for(year: int) -> list[Deadline]:
    """All dated obligations arising from compliance year `year`, sorted."""
    out = [Deadline(date(year + off, m, d), regime,
                    what.replace("year Y", str(year)) + f" (compliance year {year})",
                    basis)
           for m, d, off, regime, what, basis in _CALENDAR]
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
