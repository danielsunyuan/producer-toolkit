@echo off
echo ====================================
echo Producer Toolkit - Windows Installer
echo ====================================
echo.

:: Check Python installation
python --version 2>NUL
if errorlevel 1 (
    echo Python not found. Please install Python 3.9 or newer.
    echo Visit: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Run the installer script
echo Running installation script...
python install.py

if errorlevel 0 (
    echo.
    echo Installation completed successfully!
    echo.
    echo You can now use Producer Toolkit by running:
    echo python main.py "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
    echo.
) else (
    echo.
    echo Installation encountered some issues.
    echo Please check the error messages above.
    echo.
)

pause