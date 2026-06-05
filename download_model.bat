@echo off
echo ========================================
echo   Download RMVPE Model
echo ========================================
echo.

call E:\DevTools\venv\Scripts\activate.bat

echo Downloading RMVPE model (about 100MB)...
echo This may take a few minutes...
echo.

python -c "
import urllib.request
import os
import sys

url = 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt'
url_backup = 'https://github.com/yxlllc/RMVPE/releases/download/v1.0/rmvpe.pt'
output = r'E:\DevTools\models\rmvpe\rmvpe.pt'

os.makedirs(os.path.dirname(output), exist_ok=True)

print('Trying HuggingFace...')
try:
    urllib.request.urlretrieve(url, output)
    print('[OK] Model downloaded from HuggingFace!')
except Exception as e:
    print(f'HuggingFace failed: {e}')
    print('Trying GitHub...')
    try:
        urllib.request.urlretrieve(url_backup, output)
        print('[OK] Model downloaded from GitHub!')
    except Exception as e2:
        print(f'GitHub failed: {e2}')
        print('Please download manually:')
        print(f'  {url}')
        print(f'  Save to: {output}')
        sys.exit(1)

file_size = os.path.getsize(output) / 1024 / 1024
print(f'File size: {file_size:.1f} MB')
"

echo.
pause
