@echo off
:: Verifica si el script se está ejecutando con privilegios de administrador
:: Usa un parámetro especial para verificar y evitar bucles infinitos
if not "%1"=="am_admin" (
    echo Este script necesita permisos de administrador.
    echo.
    :: Ejecuta el script con privilegios de administrador usando PowerShell
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c %~f0 am_admin' -Verb RunAs"
    exit /b
)

:: Comienza el script con privilegios elevados

setlocal

:: Define variables
set "ALIAS_NAME=escaner"
set "BATCH_FILE_PATH=%WINDIR%\System32\%ALIAS_NAME%.bat"
set "SCRIPT_PATH=%~dp0"

:: Eliminar el archivo por lotes del alias
if exist "%BATCH_FILE_PATH%" (
    echo Eliminando el alias '%ALIAS_NAME%'...
    del "%BATCH_FILE_PATH%"
    echo Alias '%ALIAS_NAME%' eliminado.
) else (
    echo Alias '%ALIAS_NAME%' no encontrado.
)

:: Eliminar la ruta del script del PATH
echo Eliminando %SCRIPT_PATH% del PATH...
set "PATH_LIST=%PATH%"
set "NEW_PATH_LIST="

for %%A in (%PATH_LIST%) do (
    if /I not "%%A"=="%SCRIPT_PATH%" (
        if defined NEW_PATH_LIST (
            set "NEW_PATH_LIST=!NEW_PATH_LIST!;%%A"
        ) else (
            set "NEW_PATH_LIST=%%A"
        )
    )
)

:: Actualiza el PATH del sistema
setx PATH "%NEW_PATH_LIST%"

echo Hecho.
pause
