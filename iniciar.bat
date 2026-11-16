@echo off
rem levanta los tres contenedores dentro de debian (wsl2) y abre el panel
title FTP y TFTP en vivo - Grupo 1
setlocal

set "DISTRO=Debian"
for /f "delims=" %%i in ('wsl -d %DISTRO% wslpath -a "%~dp0."') do set "PROJECT=%%i"

echo.
echo  Levantando Docker y los contenedores en %DISTRO% (WSL2)...
echo.
wsl -d %DISTRO% -u root -- bash -c "systemctl start docker && cd '%PROJECT%' && docker compose up --build -d"
if errorlevel 1 (
  echo.
  echo  No se pudo levantar el proyecto. Revisa el mensaje de arriba.
  pause
  exit /b 1
)

timeout /t 2 /nobreak >nul
start "" http://localhost:8080

echo.
echo  Panel abierto en http://localhost:8080
echo  Deja esta ventana abierta durante la exposicion: muestra el registro en vivo.
echo  Para apagar todo, ejecuta detener.bat
echo.
wsl -d %DISTRO% -u root -- bash -c "cd '%PROJECT%' && docker compose logs -f --tail 20"
