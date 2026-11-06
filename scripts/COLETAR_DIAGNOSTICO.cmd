@echo off
setlocal EnableExtensions
title Coleta de diagnostico - IED Backup Manager
set "LAUNCHER_VERSION=1.1.0"

set "COLLECTOR=%~dp0Collect-Diagnostics.ps1"
set "EXE_PATH=%~1"

if not exist "%COLLECTOR%" (
    echo ERRO: Collect-Diagnostics.ps1 deve ficar na mesma pasta deste arquivo.
    pause
    exit /b 1
)

if not defined EXE_PATH if exist "%~dp0IED_Backup_Manager.exe" set "EXE_PATH=%~dp0IED_Backup_Manager.exe"

if not defined EXE_PATH (
    echo.
    echo Cole abaixo o caminho completo do IED_Backup_Manager.exe.
    echo Voce tambem pode arrastar o EXE sobre este arquivo .cmd.
    set /p "EXE_PATH=Caminho do EXE: "
)

set "EXE_PATH=%EXE_PATH:"=%"
if not exist "%EXE_PATH%" (
    echo.
    echo ERRO: executavel nao encontrado:
    echo %EXE_PATH%
    pause
    exit /b 1
)

echo.
echo O aplicativo sera aberto por cerca de 10 segundos.
echo Ao final, envie o ZIP criado na Area de Trabalho ao responsavel pelo programa.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%COLLECTOR%" -ExecutablePath "%EXE_PATH%" -LauncherVersion "%LAUNCHER_VERSION%"
set "RESULT=%ERRORLEVEL%"

echo.
if not "%RESULT%"=="0" echo A coleta encontrou um erro. Envie uma foto desta tela ao responsavel.
pause
exit /b %RESULT%
