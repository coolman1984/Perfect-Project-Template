@echo off
REM Network-disabled package and browser verification (Constitution Part 30.3).
REM
REM Blocks the network, starts the built release, then checks: health, upload,
REM a demo run, restart, zero unexpected network requests, zero JavaScript
REM errors, charts, filters, theme, RTL and print. Writes the evidence files.
REM
REM Passing on the build machine is NOT offline acceptance. The clean-PC gate
REM (Part 30.4) must also run on a machine with no Python, Node, package
REM manager, editor or compiler.
setlocal
call "%~dp0PROJECT_TOOL.bat" architecture verify --release "%~dp0release\current" || exit /b 1
echo.
echo   VERIFY_OFFLINE is not implemented yet.
echo   It must write release\ARCHITECTURE_EVIDENCE.json and
echo   release\LOCAL_TRANSPORT_EVIDENCE.json before a release is accepted.
echo.
exit /b 1
