@echo off
REM PROJECT_TOOL - Windows wrapper (Constitution Part 37.2).
REM Adds nothing but interpreter discovery and argument pass-through:
REM   PROJECT_TOOL.bat map verify  ==  ./project_tool.sh map verify
REM
REM This is the DEVELOPER/AGENT tool surface. The employee never types it
REM (Part 0.2). The employee runtime is START_APP.bat and its bundled runtime.
setlocal

set "HERE=%~dp0"

REM 1) Bundled private project-tool runtime, when the release provides one.
if exist "%HERE%runtime\python\python.exe" (
    "%HERE%runtime\python\python.exe" "%HERE%tools\project_tool.py" %*
    exit /b %ERRORLEVEL%
)

REM 2) Development fallback: any discoverable Python 3.11+.
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py -3 "%HERE%tools\project_tool.py" %*
    exit /b %ERRORLEVEL%
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
    python "%HERE%tools\project_tool.py" %*
    exit /b %ERRORLEVEL%
)

echo BLOCKED: no Python 3.11+ interpreter found. 1>&2
echo   Install one for development, or build the release so that 1>&2
echo   runtime\python\python.exe exists (Part 37.2). 1>&2
exit /b 3
