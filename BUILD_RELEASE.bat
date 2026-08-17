@echo off
REM Reproducible one-folder release (Constitution Parts 23.6, 30.7).
REM
REM Builds ONLY from pinned local inputs, with the network disabled after the
REM local cache is prepared. Never packages the developer's live virtual
REM environment or absolute workstation paths.
REM
REM Publishes ATOMICALLY: build to a new version folder, verify it, then switch
REM the current pointer. Never patch a running folder in place.
setlocal
call "%~dp0PROJECT_TOOL.bat" doctor || exit /b 1
call "%~dp0PROJECT_TOOL.bat" gates status || exit /b 1
echo.
echo   BUILD_RELEASE is not implemented yet.
echo   Implement the PyInstaller one-folder spec, then verify with:
echo     PROJECT_TOOL.bat architecture verify --release release\current
echo     VERIFY_OFFLINE.bat
echo.
exit /b 1
