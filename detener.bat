@echo off
rem apaga y borra los contenedores; las imagenes quedan guardadas para el proximo arranque
setlocal
set "DISTRO=Debian"
for /f "delims=" %%i in ('wsl -d %DISTRO% wslpath -a "%~dp0."') do set "PROJECT=%%i"
wsl -d %DISTRO% -u root -- bash -c "cd '%PROJECT%' && docker compose down"
echo.
echo  Contenedores apagados.
pause
