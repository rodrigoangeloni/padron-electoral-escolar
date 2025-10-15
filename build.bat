@echo off
title Compilador del Sistema de Votacion Escolar
color 0A

echo.
echo ==========================================================
echo      COMPILADOR DEL SISTEMA DE VOTACION ESCOLAR
echo ==========================================================
echo.

echo [INFO] Verificando si el entorno virtual '.venv' existe...
if exist .\.venv\Scripts\activate (
    echo [OK] Entorno virtual encontrado. Activando...
    call .\.venv\Scripts\activate
) else (
    echo [ADVERTENCIA] No se encontro el entorno virtual '.venv'.
    echo [INFO] Se continuara usando el interprete de Python global.
)
echo.

echo [INFO] Verificando si PyInstaller esta instalado...
pip show pyinstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo [ADVERTENCIA] PyInstaller no esta instalado.
    set /p install_pyinstaller="Desea instalarlo ahora? (s/n): "
    if /i "%install_pyinstaller%"=="s" (
        echo [INFO] Instalando PyInstaller...
        pip install pyinstaller
        if %errorlevel% neq 0 (
            echo [ERROR] No se pudo instalar PyInstaller. Abortando.
            color 0C
            pause
            exit /b 1
        )
        echo [OK] PyInstaller instalado correctamente.
    ) else (
        echo [ERROR] PyInstaller es necesario para la compilacion. Abortando.
        color 0C
        pause
        exit /b 1
    )
) else (
    echo [OK] PyInstaller ya esta instalado.
)
echo.

echo [INFO] Limpiando compilaciones anteriores (directorios 'build' y 'dist')...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [OK] Limpieza completada.
echo.

echo [INFO] Iniciando el proceso de compilacion...
pyinstaller main.spec

if %errorlevel% equ 0 (
    echo.
    echo ==========================================================
    echo      COMPILACION FINALIZADA CON EXITO
    echo ==========================================================
    echo.
    echo [OK] El ejecutable 'SistemaVotacionEscolar.exe' ha sido creado en la carpeta 'dist'.
    echo.
    color 0A
) else (
    echo.
    echo ==========================================================
    echo      ERROR DURANTE LA COMPILACION
    echo ==========================================================
    echo.
    echo [ERROR] Hubo un problema al compilar el proyecto.
    echo [INFO] Revisa los mensajes de error de PyInstaller mas arriba.
    echo.
    color 0C
)

pause