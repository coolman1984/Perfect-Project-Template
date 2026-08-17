@echo off
REM START_APP.bat - the ONLY thing the employee runs (Constitution Part 30.3).
REM
REM Runs as the invoking standard user. Never elevates, never installs a
REM service, never changes the firewall or a URL reservation, never writes
REM outside approved user-writable locations (Part 33).
REM
REM Sequence (Part 25.5.1):
REM   verify package hashes and asInvoker level
REM   -> acquire the per-user single-instance lock
REM   -> choose an OS-assigned or bounded approved high loopback port
REM   -> generate the per-launch secret in memory
REM   -> start the bundled API on 127.0.0.1 only
REM   -> health check the exact process, address and port
REM   -> open the approved renderer at the exact loopback URL
REM
REM If anything fails, fail CLOSED with a stable code and a plain-language
REM message. Never silently downgrade to a reduced product (Part 23.11).
setlocal

set "HERE=%~dp0"

if not exist "%HERE%app\excel-intelligence.exe" (
    echo.
    echo   PACKAGE_COMPONENT_MISSING
    echo.
    echo   Part of the application is missing or damaged.
    echo   Your data has not been changed.
    echo.
    echo   Next step: run SETUP_OFFLINE.bat to restore the application
    echo   from its sealed repair copy.
    echo.
    pause
    exit /b 1
)

"%HERE%app\excel-intelligence.exe" --start
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo   The application could not start. The support code is above.
    echo   Your previous dashboard and history are unchanged.
    echo.
    pause
)
exit /b %ERRORLEVEL%
