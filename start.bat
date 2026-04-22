@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "BACKEND_PID=%ROOT%backend.pid"
set "FRONTEND_PID=%ROOT%frontend.pid"

echo ==============================
echo SeeDance 启动脚本
echo ==============================

where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未检测到 Python，请先安装或激活环境。
  exit /b 1
)

call :ensure_not_running "后端" "%BACKEND_PID%"
if errorlevel 1 exit /b 1

for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -WindowStyle Hidden -PassThru; $p.Id"') do set "BID=%%i"
if not defined BID (
  echo [错误] 后端启动失败。
  exit /b 1
)
> "%BACKEND_PID%" echo !BID!
echo [成功] 后端已启动，PID=!BID!

if exist "%FRONTEND_DIR%\package.json" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [警告] 未检测到 npm，前端未启动。请先安装 Node.js。
  ) else (
    call :ensure_not_running "前端" "%FRONTEND_PID%"
    if errorlevel 1 exit /b 1
    for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/c','npm run dev' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden -PassThru; $p.Id"') do set "FID=%%i"
    if defined FID (
      > "%FRONTEND_PID%" echo !FID!
      echo [成功] 前端已启动，PID=!FID!
    ) else (
      echo [错误] 前端启动失败。
      exit /b 1
    )
  )
) else (
  echo [提示] 未检测到 frontend\package.json，已跳过前端。
)

echo [完成] 启动命令执行结束。
exit /b 0

:ensure_not_running
set "SVC=%~1"
set "PIDFILE=%~2"
if not exist "%PIDFILE%" exit /b 0
set "PID="
set /p PID=<"%PIDFILE%"
if not defined PID (
  del /q "%PIDFILE%" >nul 2>nul
  exit /b 0
)
powershell -NoProfile -Command "if (Get-Process -Id !PID! -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
  del /q "%PIDFILE%" >nul 2>nul
  exit /b 0
)
echo [提示] %SVC%已在运行，PID=!PID!
exit /b 1