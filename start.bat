@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "LOG_DIR=%ROOT%logs"
set "BACKEND_PID_FILE=%ROOT%backend.pid"
set "FRONTEND_PID_FILE=%ROOT%frontend.pid"

set "BACKEND_OUT=%LOG_DIR%\backend.out.log"
set "BACKEND_ERR=%LOG_DIR%\backend.err.log"
set "FRONTEND_OUT=%LOG_DIR%\frontend.out.log"
set "FRONTEND_ERR=%LOG_DIR%\frontend.err.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==============================
echo SeeDance start
echo ==============================

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not available in PATH.
  exit /b 1
)

call :ensure_service_state "backend" "%BACKEND_PID_FILE%" 8000
set "RC=%errorlevel%"
if "%RC%"=="1" exit /b 1
if "%RC%"=="2" goto backend_ready

for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -RedirectStandardOutput '%BACKEND_OUT%' -RedirectStandardError '%BACKEND_ERR%' -WindowStyle Hidden -PassThru; $p.Id"') do set "BID=%%i"
if not defined BID (
  echo [ERROR] Failed to start backend process.
  exit /b 1
)
> "%BACKEND_PID_FILE%" echo !BID!

call :wait_port 8000 25
if errorlevel 1 (
  echo [ERROR] Backend process started but port 8000 is not listening.
  echo [HINT] Check logs:
  echo        %BACKEND_OUT%
  echo        %BACKEND_ERR%
  del /q "%BACKEND_PID_FILE%" >nul 2>nul
  exit /b 1
)

:backend_ready
if not defined BID set "BID=N/A"
echo [OK] Backend is listening on port 8000. pid !BID!

if exist "%FRONTEND_DIR%\package.json" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [WARN] npm not found. Frontend skipped.
    goto done
  )

  call :ensure_service_state "frontend" "%FRONTEND_PID_FILE%" 5173
  set "RC=%errorlevel%"
  if "%RC%"=="1" exit /b 1
  if "%RC%"=="2" goto frontend_ready

  for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm run dev' -WorkingDirectory '%FRONTEND_DIR%' -RedirectStandardOutput '%FRONTEND_OUT%' -RedirectStandardError '%FRONTEND_ERR%' -WindowStyle Hidden -PassThru; $p.Id"') do set "FID=%%i"
  if not defined FID (
    echo [ERROR] Failed to start frontend process.
    exit /b 1
  )
  > "%FRONTEND_PID_FILE%" echo !FID!

  call :wait_port 5173 35
  if errorlevel 1 (
    echo [ERROR] Frontend process started but port 5173 is not listening.
    echo [HINT] Check logs:
    echo        %FRONTEND_OUT%
    echo        %FRONTEND_ERR%
    del /q "%FRONTEND_PID_FILE%" >nul 2>nul
    exit /b 1
  )

  :frontend_ready
  if not defined FID set "FID=N/A"
  echo [OK] Frontend is listening on port 5173. pid !FID!
) else (
  echo [INFO] frontend\package.json not found. Frontend skipped.
)

:done
echo [DONE] Start command finished.
exit /b 0

:ensure_service_state
set "SVC=%~1"
set "PID_FILE=%~2"
set "PORT=%~3"

call :is_port_listening %PORT%
if not errorlevel 1 (
  echo [INFO] %SVC% is already listening on port %PORT%.
  exit /b 2
)

if not exist "%PID_FILE%" exit /b 0

set "OLD_PID="
set /p OLD_PID=<"%PID_FILE%"
if not defined OLD_PID (
  del /q "%PID_FILE%" >nul 2>nul
  exit /b 0
)

powershell -NoProfile -Command "if (Get-Process -Id !OLD_PID! -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
  del /q "%PID_FILE%" >nul 2>nul
  exit /b 0
)

echo [WARN] %SVC% pid !OLD_PID! is alive but port %PORT% is down. stale pid file removed.
del /q "%PID_FILE%" >nul 2>nul
exit /b 0

:wait_port
set "PORT=%~1"
set "MAX_TRIES=%~2"
if not defined MAX_TRIES set "MAX_TRIES=20"
set /a TRY=0

:wait_loop
set /a TRY+=1
call :is_port_listening %PORT%
if not errorlevel 1 exit /b 0
if !TRY! geq !MAX_TRIES! exit /b 1
powershell -NoProfile -Command "Start-Sleep -Seconds 1" >nul 2>nul
goto :wait_loop

:is_port_listening
set "PORT=%~1"
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>nul
if errorlevel 1 (
  exit /b 1
)
exit /b 0