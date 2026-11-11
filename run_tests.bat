@echo off
setlocal EnableDelayedExpansion

:: Set UTF-8 encoding
chcp 65001 > nul

echo === maliphors-inator Test Runner ===
echo.

:: Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python not found! Please install Python and try again.
    exit /b 1
)

:: Parse arguments
set "MODE=all"
set "VERBOSE="
set "COVERAGE="

:parse_args
if "%~1"=="" goto :end_parse
if /I "%~1"=="--help" goto :show_help
if /I "%~1"=="-h" goto :show_help
if /I "%~1"=="--mode" (
    set "MODE=%~2"
    shift
)
if /I "%~1"=="--verbose" set "VERBOSE=--verbose"
if /I "%~1"=="--coverage" set "COVERAGE=--cov"
shift
goto :parse_args

:show_help
echo Usage: run_tests.bat [options]
echo Options:
echo   --help, -h      Show this help message
echo   --mode MODE     Test mode: all, core, gui, logging (default: all)
echo   --verbose       Show verbose output
echo   --coverage      Generate coverage report
exit /b 0

:end_parse

:: Ensure test requirements are installed
pip install -r test-requirements.txt >nul 2>nul

:: Set PYTHONPATH
set "PYTHONPATH=%CD%;%PYTHONPATH%"

:: Run pre-test checks
python debug_tests.py
if %ERRORLEVEL% neq 0 (
    echo Pre-test checks failed! Please fix the issues and try again.
    exit /b 1
)

:: Run tests based on mode
if "%MODE%"=="core" (
    pytest -v -m core %VERBOSE% %COVERAGE%
) else if "%MODE%"=="gui" (
    pytest -v -m gui %VERBOSE% %COVERAGE%
) else if "%MODE%"=="logging" (
    pytest -v -m logging %VERBOSE% %COVERAGE%
) else (
    echo Running all tests...
    python force_test_output.py
    if %ERRORLEVEL% neq 0 (
        echo Some tests failed! Check the output above for details.
        exit /b 1
    )
)

echo.
echo Test run completed.