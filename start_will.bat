@echo off
setlocal

REM === Resolve absolute paths (repo root = this .bat's folder) ===
set "ROOT=%~dp0"
set "UI=%ROOT%ui\willchat"

REM === Start the ask server (mirror) in its own window ===
start "Will Ask Server" cmd /k "cd /d "%ROOT%" && python -m tools.ask_server_mirror"

REM === Start the static web server for WillChat in its own window ===
start "WillChat Web" cmd /k "cd /d "%UI%" && python -m http.server 8770"

REM === Give them a moment to bind, then open the page ===
timeout /t 2 >nul
start "" http://127.0.0.1:8770

endlocal
