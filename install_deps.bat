@echo off
echo ========================================
echo   Install Dependencies
echo ========================================
echo.

:: Activate virtual environment
call E:\DevTools\venv\Scripts\activate.bat

:: Install PyTorch with CUDA
echo [1/6] Installing PyTorch with CUDA...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
echo [OK] PyTorch installed

:: Install PyQt6
echo [2/6] Installing PyQt6...
pip install PyQt6>=6.5.0 -q
echo [OK] PyQt6 installed

:: Install audio libraries
echo [3/6] Installing audio libraries...
pip install librosa soundfile pydub resampy -q
echo [OK] Audio libraries installed

:: Install MIDI libraries
echo [4/6] Installing MIDI libraries...
pip install pretty_midi mido -q
echo [OK] MIDI libraries installed

:: Install scientific libraries
echo [5/6] Installing scientific libraries...
pip install numpy scipy -q
echo [OK] Scientific libraries installed

:: Install other utilities
echo [6/6] Installing utilities...
pip install tqdm requests -q
echo [OK] Utilities installed

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Now run start.bat to launch the program.
echo.
pause
