"""Which EMSA THETIS-MRV export is the newest?

Files are named  thetis_mrv_<reporting year>_v<version>.xlsx  (EMSA's own
version number, which keeps rising as operators and verifiers submit
amendments). Ordering has to be numeric: sorting the names as text would put
v100 before v60 and silently pick an older file.
"""
import glob
import os
import re

_NAME = re.compile(r"thetis_mrv_(\d{4})_v(\d+)\.xlsx$")


def parse(path: str):
    """(year, version) for an export file name, or None if it is not one."""
    m = _NAME.search(os.path.basename(path))
    return (int(m.group(1)), int(m.group(2))) if m else None


def ordered(fixtures_dir: str) -> list:
    """Every export in the folder, oldest to newest by (year, version)."""
    found = [p for p in glob.glob(os.path.join(fixtures_dir, "thetis_mrv_*.xlsx"))
             if parse(p)]
    return sorted(found, key=parse)


def latest(fixtures_dir: str):
    """The newest file (highest year, then highest version), or None."""
    files = ordered(fixtures_dir)
    return files[-1] if files else None


def newest_per_year(fixtures_dir: str) -> dict:
    """{reporting year: path of the highest version we hold for that year}."""
    out = {}
    for p in ordered(fixtures_dir):
        out[parse(p)[0]] = p
    return out
