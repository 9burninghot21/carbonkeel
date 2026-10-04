# CarbonKeel (prototype v0.2)

One-stop vessel compliance scoring: IMO CII | EU ETS | UK ETS | FuelEU
Maritime | IMO Net-Zero Framework scenarios. Focus ship types: container,
bulk carrier, tanker (general cargo, gas, reefer, combination also live).

Quick start:

    python tests/test_engines.py                # validate engines (45 checks)
    python demo.py                              # scorecard, both data paths
    python scripts/lookup.py --search "MAERSK"  # search the real EU fleet
    python scripts/lookup.py 9464663 --dwt 93000

Free-lookup web app (needs `pip install fastapi uvicorn openpyxl`):

    python -m uvicorn api.main:app --port 8000
    # open http://127.0.0.1:8000

Real data: `fixtures/thetis_mrv_*.xlsx` are the EMSA THETIS-MRV public
verified-emissions exports (2024 + 2025, ~16.7k ships each). Refresh via the
public API documented in `src/ghgcore/thetis.py`.

See CLAUDE.md for architecture rules, VERIFY backlog, and the phase roadmap;
docs/IMPLEMENTATION_ROADMAP.md + docs/GTM_Plan_0_to_Max.md for the plan.
