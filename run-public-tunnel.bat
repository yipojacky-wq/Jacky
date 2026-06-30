@echo off
setlocal
cd /d "%~dp0"

echo.
echo Disclosure Completion AI - Public Share Tunnel
echo.
echo This requires cloudflared to be installed and available in PATH.
echo Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
echo.

where cloudflared >nul 2>nul
if errorlevel 1 (
  echo cloudflared was not found.
  echo Install cloudflared first, then run this file again.
  pause
  exit /b 1
)

echo Keep run-windows.bat running first.
echo A public https://*.trycloudflare.com link will appear below.
echo Share that link with other devices outside your Wi-Fi.
echo.
cloudflared tunnel --url http://127.0.0.1:8010

pause
