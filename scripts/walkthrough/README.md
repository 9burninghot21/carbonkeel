# Regenerating the shareable walkthrough

The guide (PDF + one HTML file) is built from live screenshots of the running app.
Regenerate it after any visible change, and after the data refresh (numbers change).

```bash
pip install playwright          # one time; it drives the Microsoft Edge you already have
python -m uvicorn api.main:app --port 8000     # leave running (or use "Start CarbonKeel.bat")
python scripts/walkthrough/capture.py .
python scripts/walkthrough/recapture_voyage.py .
python scripts/walkthrough/build_guide.py .
```

Output: `docs/walkthrough/CarbonKeel-walkthrough.pdf` and `.html` (git-ignored; large).
`capture.py` adds a temporary access key to `data/access_keys.txt` to show the locked CII
calculator and restores the file afterwards.
