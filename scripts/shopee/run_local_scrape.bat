@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0\..\.."

set "PYTHON=python"
set "PYTHON_ARGS="
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    if errorlevel 1 (
        echo [ERROR] Could not activate .venv.
        exit /b 1
    )
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        where py >nul 2>nul
        if errorlevel 1 (
            echo [ERROR] Python was not found. Install Python 3 or create .venv.
            exit /b 1
        )
        set "PYTHON=py"
        set "PYTHON_ARGS=-3"
    )
)

echo Make sure Chrome is open with --remote-debugging-port=9222 and logged into Shopee
echo [1/3] Scraping Shopee with local Chrome...
"%PYTHON%" %PYTHON_ARGS% scripts\shopee\scraper_local.py --config scripts\shopee\config.yaml --cdp
if errorlevel 1 goto :failed

set "LATEST_JSON="
for /f "delims=" %%F in ('dir /b /a-d /o-d ".cache\shopee\scraped\*.json" 2^>nul') do (
    if not defined LATEST_JSON set "LATEST_JSON=.cache\shopee\scraped\%%F"
)
if not defined LATEST_JSON (
    echo [ERROR] Scraper completed without a JSON output.
    exit /b 1
)

echo [2/3] Creating local candidate notes from !LATEST_JSON!...
"%PYTHON%" %PYTHON_ARGS% scripts\shopee\to_candidate.py --input "!LATEST_JSON!" --output-dir vault\candidates
if errorlevel 1 goto :failed

echo [3/3] Syncing scrape results and candidate notes to EC2...
"%PYTHON%" %PYTHON_ARGS% scripts\shopee\sync_to_ec2.py
if errorlevel 1 goto :failed

for /f %%C in ('dir /b /a-d ".cache\shopee\scraped\*.json" 2^>nul ^| find /c /v ""') do set "SCRAPED_COUNT=%%C"
for /f %%C in ('dir /b /a-d "vault\candidates\*.md" 2^>nul ^| find /c /v ""') do set "CANDIDATE_COUNT=%%C"
set "EC2_HOST_DISPLAY=%AFFILIATE_EC2_HOST%"
if not defined EC2_HOST_DISPLAY set "EC2_HOST_DISPLAY=god-of-ai"

echo.
echo [OK] Local Shopee run complete.
echo      Latest JSON: !LATEST_JSON!
echo      Cached JSON files: !SCRAPED_COUNT!
echo      Local candidate notes: !CANDIDATE_COUNT!
echo      EC2 host: !EC2_HOST_DISPLAY!
exit /b 0

:failed
echo.
echo [ERROR] Local Shopee run stopped. Review the message above.
exit /b 1
