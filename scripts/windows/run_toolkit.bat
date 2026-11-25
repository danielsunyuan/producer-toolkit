@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "PTK_PYTHON=%~dp0..\..\.venv\Scripts\python.exe"

if not exist "%PTK_PYTHON%" (
    echo PTK is not installed here. Run scripts\windows\install.bat first. 1>&2
    exit /b 1
)

"%PTK_PYTHON%" -m producer_toolkit %*
exit /b %errorlevel%
