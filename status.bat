@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_PID_FILE=%ROOT%backend.pid"
set "FRONTEND_PID_FILE=%ROOT%frontend.pid"

echo ==============================
echo SeeDance status
echo ==============================

call :show_one "backend" "%BACKEND_PID_FILE%" 8000
echo.
call :show_one "frontend" "%FRONTEND_PID_FILE%" 5173
exit /b 0

:show_one
set "SVC=%~1"
set "PID_FILE=%~2"
set "PORT=%~3"

echo %SVC%:
set "PID="
if exist "%PID_FILE%" set /p PID=<"%PID_FILE%"

if defined PID (
  powershell -NoProfile -Command "if (Get-Process -Id !PID! -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
  if errorlevel 1 (
    echo   process: not running, stale pid !PID!
  ) else (
    echo   process: running, pid !PID!
  )
) else (
  echo   process: no pid file
)

call :is_port_listening %PORT%
if errorlevel 1 (
  echo   port %PORT%: not listening
) else (
  echo   port %PORT%: listening
)

if defined PID (
  call :is_port_listening %PORT%
  if errorlevel 1 (
    echo   note: pid exists but port is down. service likely failed.
  )
) else (
  call :is_port_listening %PORT%
  if not errorlevel 1 (
    echo   note: port is up but pid file is missing. service may be unmanaged.
  )
)
exit /b 0

:is_port_listening
set "PORT=%~1"
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>nul
if errorlevel 1 (
  exit /b 1
)
exit /b 0