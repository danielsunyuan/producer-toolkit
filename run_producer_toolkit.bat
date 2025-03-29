@echo off
echo ===============================
echo Producer Toolkit - Windows Run
echo ===============================
echo.

:: Check if argument is provided
if "%~1"=="" (
    echo Usage: run_producer_toolkit.bat "YouTube URL" [options]
    echo.
    echo Options:
    echo  -v    Download video
    echo  -a    Download audio
    echo  -s    Extract stems (default)
    echo  -o    Specify output directory
    echo.
    echo Example: run_producer_toolkit.bat "https://www.youtube.com/watch?v=YOUTUBE_ID" -s
    echo.
    pause
    exit /b 1
)

:: If no option is provided, default to stems extraction
set OPTIONS=-s
if not "%~2"=="" set OPTIONS=%~2 %~3 %~4 %~5 %~6

:: Run the main script with provided arguments
python main.py "%~1" %OPTIONS%

echo.
echo Processing complete!
echo.
pause