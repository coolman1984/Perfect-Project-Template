@echo off
REM Connected Windows commissioning: build and verify both delivery ZIP files.
setlocal
set "TEMPLATE_VERSION=%~1"
set "PROJECT_ID=%~2"
set "PROJECT_NAME=%~3"

if "%TEMPLATE_VERSION%"=="" goto :usage
if "%PROJECT_ID%"=="" goto :usage
if "%PROJECT_NAME%"=="" goto :usage

echo [1/9] Checking the connected Windows build machine...
py -3.12 -c "import os,struct,sys; assert os.name=='nt' and struct.calcsize('P')*8==64 and sys.version_info[:2]==(3,12)" || (
  echo BLOCKED: Windows x64 with 64-bit Python 3.12 is required.
  exit /b 3
)
call "%~dp0PROJECT_TOOL.bat" doctor || exit /b 1

echo [2/9] Preparing the exact local dependency cache...
call "%~dp0PROJECT_TOOL.bat" wheelhouse prepare --output-dir "%~dp0offline_packages" || exit /b 1

echo [3/9] Validating the adapted project and reuse boundary...
call "%~dp0PROJECT_TOOL.bat" adaptation validate --project "%PROJECT_ID%" || exit /b 1
call "%~dp0PROJECT_TOOL.bat" adaptation core-guard --project "%PROJECT_ID%" || exit /b 1
call "%~dp0PROJECT_TOOL.bat" adaptation reuse-report --project "%PROJECT_ID%" || exit /b 1

echo [4/9] Sealing the Git-independent master baseline...
call "%~dp0PROJECT_TOOL.bat" template-baseline seal --version "%TEMPLATE_VERSION%" || exit /b 1

echo [5/9] Refreshing context and verifying the sealed source...
call "%~dp0PROJECT_TOOL.bat" map refresh --review || exit /b 1
call "%~dp0PROJECT_TOOL.bat" template-baseline verify || exit /b 1
call "%~dp0RUN_TESTS.bat" || exit /b 1

echo [6/9] Building and exercising the sealed Windows application...
call "%~dp0BUILD_RELEASE.bat" "%PROJECT_NAME%" "%PROJECT_ID%" || exit /b 1

echo [7/9] Building the reusable AI master template...
call "%~dp0PROJECT_TOOL.bat" master-template build --source-root "%~dp0" --release-dir "%~dp0release\current" --output-dir "%~dp0release\operator" || exit /b 1

echo [8/9] Verifying both ZIP files from their archive contents...
call "%~dp0PROJECT_TOOL.bat" master-template verify --zip "%~dp0release\operator\MASTER_TEMPLATE.zip" || exit /b 1
call "%~dp0PROJECT_TOOL.bat" package verify --zip "%~dp0release\operator\%PROJECT_NAME%.zip" || exit /b 1

echo [9/9] Finished.
echo.
echo   MASTER TEMPLATE: release\operator\MASTER_TEMPLATE.zip
echo   END USER APP:    release\operator\%PROJECT_NAME%.zip
echo.
echo Keep MASTER_TEMPLATE.zip for ChatGPT, Claude, Gemini, or another capable agent.
echo Give only %PROJECT_NAME%.zip to the non-technical end user.
exit /b 0

:usage
echo Usage: FINALIZE_MASTER.bat template-version project-id "Project Name"
echo Example: FINALIZE_MASTER.bat 1.0.0 sales_dashboard "Sales Dashboard"
exit /b 2
