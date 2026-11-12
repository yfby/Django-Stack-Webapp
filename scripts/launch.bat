@echo off
setlocal
pushd "%~dp0.."
if not exist ".venv\Scripts\python.exe" goto need_setup
".venv\Scripts\python.exe" scripts\bootstrap.py --quiet
if errorlevel 1 goto need_setup
".venv\Scripts\python.exe" scripts\run.py %*
set "FLOWDESK_RESULT=%ERRORLEVEL%"
if not "%FLOWDESK_RESULT%"=="0" pause
popd
exit /b %FLOWDESK_RESULT%
:need_setup
echo.
echo PrintPilot is not set up yet ^(or setup is incomplete^).
echo Please double-click SETUP.bat first, then try again.
echo.
pause
popd
exit /b 2
