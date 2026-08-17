@echo off
REM Offline verification suite (Constitution Parts 20.9, 30.3).
REM Runs the map, architecture and constitution gates plus the test suite.
REM A material change cannot be committed or released while this fails.
setlocal
call "%~dp0PROJECT_TOOL.bat" doctor || exit /b 1
py -3 -m unittest discover -s "%~dp0tests" -t "%~dp0." || exit /b 1
echo.
echo All checks passed.
exit /b 0
