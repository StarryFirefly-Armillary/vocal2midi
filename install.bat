@echo off
echo ========================================
echo   Vocal2MIDI Installer
echo ========================================
echo.

:: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo [OK] Python found
echo.

:: Activate virtual environment
echo [2/5] Activating virtual environment...
call E:\DevTools\venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

:: Install dependencies
echo [3/5] Installing dependencies...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
pip install PyQt6 librosa soundfile pretty_midi mido numpy scipy tqdm requests -q
echo [OK] Dependencies installed
echo.

:: Create directories
echo [4/5] Creating directories...
if not exist "E:\DevTools\models\rmvpe" mkdir "E:\DevTools\models\rmvpe"
echo [OK] Directories created
echo.

:: Download RMVPE model
echo [5/5] Downloading RMVPE model...
if not exist "E:\DevTools\models\rmvpe\rmvpe.pt" (
    echo Downloading RMVPE model (about 100MB)...
    echo This may take a few minutes...

    powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt' -OutFile 'E:\DevTools\models\rmvpe\rmvpe.pt'"

    if errorlevel 1 (
        echo Download from HuggingFace failed, trying GitHub...
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt' -OutFile 'E:\DevTools\models\rmvpe\rmvpe.pt'"
    )

    if errorlevel 1 (
        echo.
        echo ERROR: Model download failed
        echo Please download manually:
        echo   https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
        echo   Save to: E:\DevTools\models\rmvpe\rmvpe.pt
    ) else (
        echo [OK] RMVPE model downloaded
    )
) else (
    echo [OK] RMVPE model already exists
)
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Run start.bat to launch the program.
echo.
pause
