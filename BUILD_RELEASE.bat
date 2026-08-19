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
set "PROJECT_NAME=%~1"
if "%PROJECT_NAME%"=="" set "PROJECT_NAME=Excel Intelligence"
set "PROJECT_ID=%~2"
call "%~dp0PROJECT_TOOL.bat" doctor || exit /b 1
call "%~dp0PROJECT_TOOL.bat" gates status || exit /b 1
py -3.12 -m tools.build_release || exit /b 1
call "%~dp0PROJECT_TOOL.bat" architecture verify --release "%~dp0release\current" || exit /b 1
call "%~dp0VERIFY_OFFLINE.bat" || exit /b 1
if "%PROJECT_ID%"=="" (
  call "%~dp0PROJECT_TOOL.bat" package build --project-name "%PROJECT_NAME%" --app-dir "%~dp0release\current" --output-dir "%~dp0release\operator" || exit /b 1
) else (
  call "%~dp0PROJECT_TOOL.bat" package build --project-name "%PROJECT_NAME%" --project-id "%PROJECT_ID%" --app-dir "%~dp0release\current" --output-dir "%~dp0release\operator" || exit /b 1
)
call "%~dp0PROJECT_TOOL.bat" package verify --zip "%~dp0release\operator\%PROJECT_NAME%.zip" || exit /b 1
echo.
echo   Release candidate built and verified at release\current.
echo   Final operator package: release\operator\%PROJECT_NAME%.zip
echo   Clean offline PC, protected workbook and operator gates remain conditional.
echo.
exit /b 0
