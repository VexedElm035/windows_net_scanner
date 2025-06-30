@echo off
:: Verifica si el script se está ejecutando con privilegios de administrador
:: El script necesita permisos de administrador para ejecutar correctamente
if not "%1"=="am_admin" (
    echo Este script necesita permisos de administrador.
    echo.
    :: Ejecuta el script con privilegios de administrador
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~f0 am_admin' -Verb RunAs"
    exit /b
)

:: Verifica si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python no esta instalado. Instalando Python...
    :: Cambia la URL a la última versión de Python si es necesario
    set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
    set "PYTHON_INSTALLER=python_installer.exe"
    powershell -Command "Invoke-WebRequest -Uri %PYTHON_INSTALLER_URL% -OutFile %PYTHON_INSTALLER%"
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
    del %PYTHON_INSTALLER%
    echo Python ha sido instalado.
) else (
    echo Python ya esta instalado.
)

:: Verifica si pip está instalado
python -m ensurepip --default-pip >nul 2>nul
if %errorlevel% neq 0 (
    echo Pip no se pudo instalar automaticamente. Instalando pip manualmente...
    python -m ensurepip --upgrade
    python -m pip install --upgrade pip
) else (
    echo Pip ya está instalado.
)

:: Instalar las bibliotecas requeridas
echo Instalando bibliotecas necesarias...
python -m pip install signal subprocess sys threading re time colorama datetime argparse

:: Configura la ruta del script
set "SCRIPT_PATH=%~dp0"

:: Añadir la ruta del script al PATH
echo Agregando %SCRIPT_PATH% al PATH...
setx PATH "%PATH%;%SCRIPT_PATH%"

:: Crear el alias
set "ALIAS_NAME=escaner"
set "TARGET_SCRIPT=%SCRIPT_PATH%main.py"

echo @echo off > "%WINDIR%\System32\%ALIAS_NAME%.bat"
echo python "%TARGET_SCRIPT%" %%* >> "%WINDIR%\System32\%ALIAS_NAME%.bat"

echo Alias '%ALIAS_NAME%' creado para '%TARGET_SCRIPT%'.

echo Hecho.
pause
