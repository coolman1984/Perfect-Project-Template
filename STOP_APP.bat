@echo off
REM Graceful shutdown (Constitution Part 30.3).
REM Requests a clean stop: reject new work, finish or roll back at a safe
REM boundary, stop the listener, release the instance lock.
REM Never kills unrelated processes. Never mass-kills EXCEL.EXE - some Excel
REM processes belong to the employee (Part 23.5).
setlocal
"%~dp0app\excel-intelligence.exe" --stop
exit /b %ERRORLEVEL%
