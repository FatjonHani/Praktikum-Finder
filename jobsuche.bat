@echo off
rem Startet alle Profile und oeffnet danach den Ergebnis-Ordner.
rem Funktioniert egal, wo der Projektordner liegt.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python praktikum_finder.py %*
) else (
    py praktikum_finder.py %*
)

if exist "ergebnisse" start "" "ergebnisse"
