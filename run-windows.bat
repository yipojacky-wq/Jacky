@echo off
setlocal
cd /d "%~dp0"

echo.
echo Disclosure Completion AI MVP - Windows Launcher
echo.

set "PYTHON_CMD="

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
  set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
  echo Python was not found.
  echo Please install Python 3.11 or 3.12 and enable "Add python.exe to PATH".
  echo Download: https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env from .env.example.
  echo Edit .env to set OPENAI_API_KEY or OPENROUTER_API_KEY for real AI inference.
  echo.
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  "%PYTHON_CMD%" -m venv .venv
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
) else (
  echo Virtual environment found.
)

if not exist ".venv\.deps-installed" (
  echo Installing dependencies...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
  )
  echo installed > ".venv\.deps-installed"
) else (
  echo Dependencies already installed.
)

echo.
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4"') do (
  set "HOST_IP=%%A"
  goto :got_ip
)
:got_ip
set "HOST_IP=%HOST_IP: =%"
if "%HOST_IP%"=="" set "HOST_IP=你的主機IP"

if not exist "outputs" mkdir "outputs"
> "outputs\Open-DisclosureCompletionAI-Local.url" echo [InternetShortcut]
>> "outputs\Open-DisclosureCompletionAI-Local.url" echo URL=http://127.0.0.1:8010/?nocache=20260630-7
> "outputs\Open-DisclosureCompletionAI-Host.url" echo [InternetShortcut]
>> "outputs\Open-DisclosureCompletionAI-Host.url" echo URL=http://%HOST_IP%:8010/?nocache=20260630-7

echo Starting local and LAN server...
echo Open on this computer: http://127.0.0.1:8010/?nocache=20260630-7
echo Open from another device on the same network: http://%HOST_IP%:8010/?nocache=20260630-7
echo.
echo If Windows Firewall asks for permission, allow Python on Private networks.
echo.
start "" "http://127.0.0.1:8010/?nocache=20260630-7"
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8010

pause
