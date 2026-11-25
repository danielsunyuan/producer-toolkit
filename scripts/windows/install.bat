@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0..\.." || exit /b 1

if exist ".venv\Scripts\python.exe" goto install
if exist ".venv" goto failed

:: Prefer the tested Python version; fall back to a compatible Python on PATH.
py -3.11 -c "import sys" >nul 2>&1
if errorlevel 1 goto python_on_path
py -3.11 -m venv ".venv"
if errorlevel 1 goto failed
goto install

:python_on_path
python -c "import sys; sys.exit(sys.version_info[:2] != (3, 11))" >nul 2>&1
if errorlevel 1 goto missing_python
python -m venv ".venv"
if errorlevel 1 goto failed

:install
".venv\Scripts\python.exe" -c "import sys; sys.exit(sys.version_info[:2] != (3, 11))"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install --require-hashes -r requirements\windows-amd64-py311.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install --no-deps .
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m producer_toolkit --version
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m producer_toolkit doctor
if errorlevel 1 goto failed

echo Installation completed successfully.
echo Run scripts\windows\run_toolkit.bat --help to get started.
popd
exit /b 0

:missing_python
echo Python 3.11 is required for the tested Windows dependency set. Install it from python.org. 1>&2
popd
exit /b 1

:failed
echo PTK setup failed. Check the error above and repair any incomplete .venv before retrying. 1>&2
popd
exit /b 1
