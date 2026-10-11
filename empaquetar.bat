@echo off
rem Genera dist\WotS4-Espanol.exe (instalador de un solo archivo) con PyInstaller.
rem Requiere: python -m pip install pyinstaller
setlocal
cd /d "%~dp0"
if not defined PYTHON set "PYTHON=python"
"%PYTHON%" -m PyInstaller --onefile --console --clean --noconfirm ^
  --name WotS4-Espanol ^
  --add-data "traduccion;traduccion" ^
  --add-data "datos;datos" ^
  --add-data "tools\wos4;tools\wos4" ^
  --exclude-module numpy --exclude-module PIL --exclude-module tkinter ^
  parchear.py
if errorlevel 1 exit /b 1
echo.
echo Listo: dist\WotS4-Espanol.exe
