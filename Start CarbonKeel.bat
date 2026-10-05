@echo off
rem Double-click to run CarbonKeel locally. One server, one address:
rem   http://127.0.0.1:8000/home   the opening page
rem   http://127.0.0.1:8000/       the app
cd /d "%~dp0"
echo Starting CarbonKeel ... (first start loads 16,673 ships, up to 20 seconds)
start "" /min cmd /c "timeout /t 6 >nul & start http://127.0.0.1:8000/home"
python -m uvicorn api.main:app --port 8000
pause
