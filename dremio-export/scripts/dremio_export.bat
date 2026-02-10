@echo off
REM Wrapper script for dremio_export.py on Windows that finds the correct Python installation

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%dremio_export.py"

REM Function to check if a Python executable has requests installed
REM We'll check each candidate and use the first one that works

set "PYTHON_BIN="

REM Try different Python installations in order of preference
set "CANDIDATES=python py python3 C:\Python3\python.exe C:\Python39\python.exe C:\Python310\python.exe C:\Python311\python.exe C:\Python312\python.exe"

for %%P in (%CANDIDATES%) do (
    where %%P >nul 2>&1
    if !errorlevel! == 0 (
        %%P -c "import requests" >nul 2>&1
        if !errorlevel! == 0 (
            set "PYTHON_BIN=%%P"
            goto :found
        )
    )
)

REM If no Python with requests found, show error
echo ERROR: No Python installation with 'requests' package found.
echo.
echo Please install the requests package:
echo   pip install requests
echo.
echo Or if using Python from Microsoft Store:
echo   python -m pip install requests
exit /b 1

:found
REM Run the Python script with the correct interpreter
"%PYTHON_BIN%" "%PYTHON_SCRIPT%" %*
