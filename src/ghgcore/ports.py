"""Port -> country -> EEA scoping for EU ETS / FuelEU per-leg jurisdiction.

Deterministic, two-tier resolution:
1. UN/LOCODE (e.g. 'NLRTM'): first two letters are the ISO country code.
2. Port-name lookup for common port spellings in noon reports.
Unknown ports resolve to None and are surfaced as data-quality flags —
never silently guessed (an LLM suggestion can be confirmed by a human in
production, but scope math only ever runs on resolved codes).

EEA = EU27 + Norway + Iceland (+ Liechtenstein, landlocked, listed for
completeness). Both regimes hinge on EEA port calls: intra-EEA voyages and
at-berth 100%, one-EEA-end voyages 50%.
"""
from typing import Optional
from .schema import VoyageScope

EEA_COUNTRIES = {
    # EU27
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
    "SI", "ES", "SE",
    # EEA EFTA
    "NO", "IS", "LI",
}

# Common port-name spellings seen in noon reports -> ISO country. Extend as
# ingestion meets new ports; unknowns are flagged, so gaps are safe.
PORT_COUNTRY = {
    # EEA
    "rotterdam": "NL", "amsterdam": "NL", "antwerp": "BE", "zeebrugge": "BE",
    "hamburg": "DE", "bremerhaven": "DE", "wilhelmshaven": "DE",
    "le havre": "FR", "marseille": "FR", "fos": "FR", "dunkirk": "FR",
    "algeciras": "ES", "valencia": "ES", "barcelona": "ES", "bilbao": "ES",
    "sines": "PT", "lisbon": "PT", "leixoes": "PT",
    "piraeus": "GR", "thessaloniki": "GR",
    "genoa": "IT", "trieste": "IT", "gioia tauro": "IT", "la spezia": "IT",
    "livorno": "IT", "venice": "IT", "taranto": "IT",
    "gdansk": "PL", "gdynia": "PL", "szczecin": "PL",
    "gothenburg": "SE", "stockholm": "SE", "malmo": "SE",
    "copenhagen": "DK", "aarhus": "DK", "fredericia": "DK",
    "helsinki": "FI", "kotka": "FI", "hamina": "FI",
    "tallinn": "EE", "riga": "LV", "klaipeda": "LT",
    "constanta": "RO", "varna": "BG", "burgas": "BG",
    "limassol": "CY", "valletta": "MT", "marsaxlokk": "MT",
    "dublin": "IE", "cork": "IE",
    "koper": "SI", "rijeka": "HR", "split": "HR",
    "oslo": "NO", "bergen": "NO", "stavanger": "NO", "mongstad": "NO",
    "reykjavik": "IS",
    # Non-EEA frequent counterparts
    "london": "GB", "felixstowe": "GB", "southampton": "GB", "immingham": "GB",
    "liverpool": "GB", "teesport": "GB", "grangemouth": "GB", "hull": "GB",
    "bristol": "GB", "milford haven": "GB", "aberdeen": "GB", "glasgow": "GB",
    "belfast": "GB", "larne": "GB", "warrenpoint": "GB", "londonderry": "GB",
    "istanbul": "TR", "izmir": "TR", "mersin": "TR", "iskenderun": "TR",
    "new york": "US", "houston": "US", "new orleans": "US", "savannah": "US",
    "los angeles": "US", "long beach": "US", "norfolk": "US", "baltimore": "US",
    "santos": "BR", "paranagua": "BR", "itaqui": "BR", "tubarao": "BR",
    "shanghai": "CN", "ningbo": "CN", "qingdao": "CN", "tianjin": "CN",
    "shenzhen": "CN", "guangzhou": "CN", "dalian": "CN",
    "singapore": "SG", "port klang": "MY", "tanjung pelepas": "MY",
    "busan": "KR", "ulsan": "KR", "yokohama": "JP", "nagoya": "JP", "tokyo": "JP",
    "mumbai": "IN", "nhava sheva": "IN", "mundra": "IN", "chennai": "IN",
    "kandla": "IN", "paradip": "IN", "visakhapatnam": "IN", "cochin": "IN",
    "jebel ali": "AE", "fujairah": "AE", "jubail": "SA", "jeddah": "SA",
    "ras tanura": "SA", "yanbu": "SA", "sohar": "OM", "salalah": "OM",
    "alexandria": "EG", "port said": "EG", "damietta": "EG",
    "casablanca": "MA", "tanger med": "MA", "tangier": "MA",
    "durban": "ZA", "richards bay": "ZA", "cape town": "ZA", "saldanha": "ZA",
    "lagos": "NG", "tema": "GH", "abidjan": "CI", "dakar": "SN",
    "novorossiysk": "RU", "st petersburg": "RU", "primorsk": "RU", "ust-luga": "RU",
    "odessa": "UA", "pivdennyi": "UA", "chornomorsk": "UA",
    "vancouver": "CA", "montreal": "CA", "halifax": "CA",
    "veracruz": "MX", "buenos aires": "AR", "san lorenzo": "AR",
    "callao": "PE", "valparaiso": "CL", "san antonio": "CL",
    "newcastle": "AU", "port hedland": "AU", "hay point": "AU", "gladstone": "AU",
    "melbourne": "AU", "brisbane": "AU", "fremantle": "AU",
    "tauranga": "NZ", "auckland": "NZ",
    "colombo": "LK", "chittagong": "BD", "karachi": "PK",
    "ho chi minh": "VN", "haiphong": "VN", "laem chabang": "TH",
    "jakarta": "ID", "surabaya": "ID", "manila": "PH",
    "kaohsiung": "TW", "hong kong": "HK",
    "batumi": "GE", "poti": "GE", "baku": "AZ",
}


def port_country(port: str) -> Optional[str]:
    """Resolve a port string (name or UN/LOCODE) to an ISO country code."""
    if not port:
        return None
    p = port.strip()
    # UN/LOCODE: 5 chars, all alnum upper, e.g. NLRTM
    if len(p) == 5 and p.isalnum() and p.isupper():
        return p[:2]
    return PORT_COUNTRY.get(p.lower())


def is_eea(country: Optional[str]) -> Optional[bool]:
    return None if country is None else country in EEA_COUNTRIES


# Northern Ireland ports (UN/LOCODE country is GB, so a named set is needed
# for the GB<->NI 50% UK ETS share).
NI_PORTS = {"belfast", "larne", "warrenpoint", "londonderry", "derry",
            "gbbel", "gblar", "gbwpt", "gbldy"}


def uk_share_for_leg(from_port: str, to_port: str) -> float:
    """UK ETS surrender share: 1.0 UK domestic, 0.5 GB<->NI, else 0.0."""
    fc, tc = port_country(from_port), port_country(to_port)
    if fc != "GB" or tc != "GB":
        return 0.0
    f_ni = from_port.strip().lower() in NI_PORTS
    t_ni = to_port.strip().lower() in NI_PORTS
    return 0.5 if f_ni != t_ni else 1.0


def scope_for_leg(from_port: str, to_port: str) -> tuple[Optional[VoyageScope], list[str]]:
    """Derive the EU jurisdictional scope of a voyage leg from its port pair.

    Returns (scope, flags). scope is None when either port is unresolvable —
    the caller decides the fallback and must surface the flag.
    """
    flags: list[str] = []
    fc, tc = port_country(from_port), port_country(to_port)
    if fc is None:
        flags.append(f"Unknown port {from_port!r} — extend PORT_COUNTRY or use UN/LOCODE.")
    if tc is None:
        flags.append(f"Unknown port {to_port!r} — extend PORT_COUNTRY or use UN/LOCODE.")
    if fc is None or tc is None:
        return None, flags

    f_eea, t_eea = fc in EEA_COUNTRIES, tc in EEA_COUNTRIES
    if f_eea and t_eea:
        return VoyageScope.INTRA_EEA, flags
    if f_eea or t_eea:
        return VoyageScope.EXTRA_EEA, flags
    return VoyageScope.OUT_OF_SCOPE, flags
