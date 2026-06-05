@echo off
cd /d "%~dp0"
call E:\DevTools\venv\Scripts\activate.bat
python download_model.py
