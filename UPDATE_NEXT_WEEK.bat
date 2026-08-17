@echo off
REM Opens the application directly at the guided upload and process flow
REM (Constitution Part 30.3). This is an operating run, not a code change:
REM the same quality, history and verification gates apply (Part 32.2).
setlocal
"%~dp0app\excel-intelligence.exe" --start --view=add-data
exit /b %ERRORLEVEL%
