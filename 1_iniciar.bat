@echo off
title Sistema de Votacion Escolar
color 0A
cd /d "%~dp0"

rem Si ya existe el entorno virtual, lanza la aplicaci?n sin consola.
if exist ".venv\Scripts\pythonw.exe" goto lanzar

rem Primera ejecuci?n: crea el .venv e instala las dependencias.
echo [INFO] No se encontro el entorno virtual '.venv'.
echo [INFO] Se creara e instalaran las dependencias (puede tardar unos minutos).
echo.

where python >nul 2>nul
if %errorlevel% neq 0 goto sin_python
python run_app.py
if %errorlevel% neq 0 pause
exit /b %errorlevel%

:sin_python
echo [ERROR] No se encontro Python en el sistema.
echo [INFO] Instala Python 3.11 y vuelve a intentarlo.
color 0C
pause
exit /b 1

:lanzar
echo [INFO] Verificando dependencias del entorno virtual...
".venv\Scripts\python.exe" -c "import tkinter, PIL, matplotlib, fpdf" >nul 2>nul
if %errorlevel% neq 0 goto dependencias_faltantes

start "" ".venv\Scripts\pythonw.exe" main.py
exit /b 0

:dependencias_faltantes
echo [ERROR] Faltan dependencias en el entorno virtual.
echo [INFO] Ejecuta: .venv\Scripts\python.exe -m pip install -r requirements.txt
color 0C
pause
exit /b 1
