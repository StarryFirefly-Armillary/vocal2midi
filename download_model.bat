@echo off
echo Downloading RMVPE model...
echo.

if not exist "E:\DevTools\models\rmvpe" mkdir "E:\DevTools\models\rmvpe"

echo Trying HuggingFace...
curl -L -o "E:\DevTools\models\rmvpe\rmvpe.pt" "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt"

if not exist "E:\DevTools\models\rmvpe\rmvpe.pt" (
    echo HuggingFace failed, trying GitHub...
    curl -L -o "E:\DevTools\models\rmvpe\rmvpe.pt" "https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt"
)

if exist "E:\DevTools\models\rmvpe\rmvpe.pt" (
    echo.
    echo [OK] Model downloaded successfully!
) else (
    echo.
    echo [ERROR] Download failed
    echo Please download manually:
    echo   https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt
    echo   Save to: E:\DevTools\models\rmvpe\rmvpe.pt
)

echo.
pause
