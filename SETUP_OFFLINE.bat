@echo off
REM SETUP_OFFLINE.bat - integrity check and repair (Constitution Part 30.3).
REM
REM This is NOT an installer. It never runs pip, never downloads anything, and
REM never writes a secret. It verifies the release against its checksum
REM manifest and restores damaged files from the SEALED REPAIR PAYLOAD only.
REM
REM The wheelhouse in offline_packages\ is for DEVELOPER rebuilds. Employee
REM repair never touches it (Part 23.12).
setlocal
"%~dp0app\excel-intelligence.exe" --verify-and-repair
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo   Repair could not complete. Give the support code above to IT.
    echo   Your data has not been changed.
    echo.
    pause
)
exit /b %ERRORLEVEL%
