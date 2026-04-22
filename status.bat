@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_PID=%ROOT%backend.pid"
set "FRONTEND_PID=%ROOT%frontend.pid"

echo ==============================
echo SeeDance 状态检查
echo ==============================

call :show_one "后端" "%BACKEND_PID%" 8000
echo.
call :show_one "前端" "%FRONTEND_PID%" 5173
exit /b 0

:show_one
set "SVC=%~1"
set "PIDFILE=%~2"
set "PORT=%~3"

echo %SVC%：
if exist "%PIDFILE%" (
  set "PID="
  set /p PID=<"%PIDFILE%"
  if defined PID (
    powershell -NoProfile -Command "if (Get-Process -Id !PID! -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
    if errorlevel 1 (
      echo   进程状态：未运行（PID文件失效：!PID!）
    ) else (
      echo   进程状态：运行中（PID=!PID!）
    )
  ) else (
    echo   进程状态：未运行（PID文件为空）
  )
) else (
  echo   进程状态：未运行
)

powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo   端口状态：%PORT% 未监听
) else (
  echo   端口状态：%PORT% 正在监听
)
exit /b 0