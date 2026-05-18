@echo off
echo.
echo  =====================================================
echo    AEGIS  --  Adaptive Epistemic Guard
echo  =====================================================
echo.

:: Start Ollama in background if not running
tasklist /fi "imagename eq ollama.exe" | find /i "ollama.exe" >nul 2>&1
if errorlevel 1 (
    echo  Starting Ollama...
    start "" /B "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
) else (
    echo  Ollama is running.
)

echo  Starting AEGIS web app...
echo  Open http://localhost:5001 in your browser
echo.
start "" http://localhost:5001
python app.py
