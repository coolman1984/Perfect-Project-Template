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
py -3.12 -m tools.verify_offline "%~dp0release\current" || exit /b 1
echo.
echo   Local offline release verification passed.
echo   This is build-machine evidence, not the clean-PC acceptance gate.
echo.
exit /b 0
