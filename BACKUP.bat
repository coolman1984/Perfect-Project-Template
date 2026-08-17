@echo off
REM Copies database, archive, config, output and run evidence to the approved
REM protected backup destination (Constitution Part 30.3).
REM
REM WARNING: the backup contains the same extracted data as the source Excel
REM files, WITHOUT the DRM wrapper. Apply the same classification and access
REM controls as the live database (Part 27.7).
REM
REM Backup destination credentials live in the OS credential store or a
REM pre-authenticated mount - never in this file (Part 43).
setlocal
"%~dp0app\excel-intelligence.exe" --backup
exit /b %ERRORLEVEL%
