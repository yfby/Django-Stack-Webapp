@echo off
setlocal
title PrintPilot - Setup
pushd "%~dp0"
echo ============================================
echo   PRINTPILOT SETUP  (run this once)
echo ============================================
echo.
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 scripts\bootstrap.py
goto finished
:use_python
where python >nul 2>nul
if errorlevel 1 goto no_python
python scripts\bootstrap.py
:finished
set "FLOWDESK_RESULT=%ERRORLEVEL%"
echo.
if "%FLOWDESK_RESULT%"=="0" (
  echo ============================================
  echo   Setup finished. Now double-click START.bat
  echo ============================================
) else (
  echo Setup could not finish. Read the message above, fix it, then run SETUP.bat again.
)
pause
popd
exit /b %FLOWDESK_RESULT%
:no_python
echo Python was not found. Install Python 3.12 or 3.13 from python.org
echo ^(tick "Add python.exe to PATH"^), then run SETUP.bat again.
echo.
pause
popd
exit /b 2
