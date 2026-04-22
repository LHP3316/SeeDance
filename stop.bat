@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_PID=%ROOT%backend.pid"
set "FRONTEND_PID=%ROOT%frontend.pid"

echo ==============================
echo SeeDance 停止脚本
echo ==============================

call :stop_one "前端" "%FRONTEND_PID%"
call :stop_one "后端" "%BACKEND_PID%"
call :kill_port 5173
call :kill_port 8000

echo [完成] 停止命令执行结束。
exit /b 0

:stop_one
set "SVC=%~1"
set "PIDFILE=%~2"
if not exist "%PIDFILE%" (
  echo [提示] %SVC%未运行（无PID文件）。
  exit /b 0
)
set "PID="
set /p PID=<"%PIDFILE%"
if not defined PID (
  del /q "%PIDFILE%" >nul 2>nul
  echo [提示] %SVC%的PID文件为空，已清理。
  exit /b 0
)
powershell -NoProfile -Command "if (Get-Process -Id !PID! -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
  del /q "%PIDFILE%" >nul 2>nul
  echo [提示] %SVC%进程不存在，已清理失效PID：!PID!
  exit /b 0
)
echo [处理中] 正在停止 %SVC%，PID=!PID!
taskkill /PID !PID! /T /F >nul 2>nul
if errorlevel 1 (
  echo [警告] 停止 %SVC% 失败，可能是权限不足，请用管理员PowerShell重试。
) else (
  echo [成功] %SVC%已停止。
)
del /q "%PIDFILE%" >nul 2>nul
exit /b 0

:kill_port
set "PORT=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$pids=Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if($pids){ foreach($pid in $pids){ Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } }" >nul 2>nul
exit /b 0