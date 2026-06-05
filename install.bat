@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Vocal2MIDI Installer
echo ========================================
echo.

:: Check Python
echo [1/6] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [OK] Python %PYTHON_VERSION% installed
echo.

:: Create virtual environment
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
echo [3/6] Upgrading pip...
python -m pip install --upgrade pip -q
echo [OK] pip upgraded
echo.

:: Detect CUDA
echo [4/6] Detecting CUDA environment...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo No NVIDIA GPU detected, will install CPU version PyTorch
    set "TORCH_VERSION=cpu"
) else (
    echo [OK] NVIDIA GPU detected
    nvidia-smi --query-gpu=name --format=csv,noheader
    set "TORCH_VERSION=cu118"
)
echo.

:: Install PyTorch
echo [5/6] Installing PyTorch...
if "%TORCH_VERSION%"=="cu118" (
    echo Installing PyTorch with CUDA support (this may take a few minutes)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
) else (
    echo Installing PyTorch CPU version...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
)

if errorlevel 1 (
    echo ERROR: PyTorch installation failed
    echo Please check your network connection or install PyTorch manually
    pause
    exit /b 1
)
echo [OK] PyTorch installed
echo.

:: Install other dependencies
echo [6/6] Installing other dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Dependencies installation failed
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

:: Create directories
echo Creating tool directories...
if not exist "E:\DevTools" mkdir "E:\DevTools"
if not exist "E:\DevTools\models" mkdir "E:\DevTools\models"
if not exist "E:\DevTools\models\rmvpe" mkdir "E:\DevTools\models\rmvpe"
if not exist "E:\DevTools\ffmpeg" mkdir "E:\DevTools\ffmpeg"
echo [OK] Directories created
echo.

:: Download FFmpeg
echo Downloading FFmpeg...
if not exist "E:\DevTools\ffmpeg\bin\ffmpeg.exe" (
    echo Downloading FFmpeg (about 80MB)...

    powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'E:\DevTools\ffmpeg\ffmpeg.zip'"

    if errorlevel 1 (
        echo FFmpeg download failed. Please download manually:
        echo URL: https://www.gyan.dev/ffmpeg/builds/
        echo Extract to: E:\DevTools\ffmpeg
    ) else (
        echo Extracting FFmpeg...
        powershell -Command "Expand-Archive -Path 'E:\DevTools\ffmpeg\ffmpeg.zip' -DestinationPath 'E:\DevTools\ffmpeg' -Force"

        for /d %%i in ("E:\DevTools\ffmpeg\ffmpeg-*-essentials_build") do (
            xcopy "%%i\bin\*" "E:\DevTools\ffmpeg\bin\" /E /I /Y >nul
        )

        del "E:\DevTools\ffmpeg\ffmpeg.zip" >nul 2>&1
        for /d %%i in ("E:\DevTools\ffmpeg\ffmpeg-*-essentials_build") do (
            rmdir /s /q "%%i" >nul 2>&1
        )

        echo [OK] FFmpeg installed
    )
) else (
    echo [OK] FFmpeg already exists
)
echo.

:: Download RMVPE model
echo Downloading RMVPE model...
if not exist "E:\DevTools\models\rmvpe\rmvpe.pt" (
    echo Downloading RMVPE model (about 100MB)...
    echo This may take a few minutes...

    powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt' -OutFile 'E:\DevTools\models\rmvpe\rmvpe.pt' } catch { Write-Host 'Primary source failed, trying backup...'; Invoke-WebRequest -Uri 'https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt' -OutFile 'E:\DevTools\models\rmvpe\rmvpe.pt' }"

    if errorlevel 1 (
        echo RMVPE model download failed. Please download manually:
        echo URL 1: https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
        echo URL 2: https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt
        echo Save to: E:\DevTools\models\rmvpe\rmvpe.pt
    ) else (
        echo [OK] RMVPE model downloaded
    )
) else (
    echo [OK] RMVPE model already exists
)
echo.

:: Create start script
echo Creating start script...
(
echo @echo off
echo cd /d "%%~dp0"
echo call venv\Scripts\activate.bat
echo python main.py
echo pause
) > start.bat
echo [OK] Start script created
echo.

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Vocal2MIDI.lnk'); $Shortcut.TargetPath = '%~dp0start.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Vocal2MIDI - Vocal to MIDI Converter'; $Shortcut.Save()"

if errorlevel 1 (
    echo Failed to create desktop shortcut
) else (
    echo [OK] Desktop shortcut created
)
echo.

:: Installation complete
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo How to use:
echo   1. Double-click start.bat to launch
echo   2. Or double-click the desktop shortcut
echo.
echo Project directory: %~dp0
echo Tools directory: E:\DevTools
echo.
echo Press any key to exit...
pause >nul
