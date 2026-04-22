@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_PID_FILE=%ROOT%backend.pid"
set "FRONTEND_PID_FILE=%ROOT%frontend.pid"

echo ==============================
echo SeeDance 停止脚本
echo ==============================

call :stop_one "frontend" "%FRONTEND_PID_FILE%" 5173
call :stop_one "backend" "%BACKEND_PID_FILE%" 8000

echo [完成] 停止命令执行完毕。
exit /b 0

:stop_one
set "SVC=%~1"
set "PID_FILE=%~2"
set "PORT=%~3"

if exist "%PID_FILE%" (
  set "PID="
  set /p PID<"%PID_FILE%"
  if defined PID (
    echo [信息] 正在通过进程ID !PID! 停止 %SVC%
    taskkill /PID !PID! /T /F >nul 2>nul
  )
  del /q "%PID_FILE%" >nul 2>nul
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do taskkill /PID %%p /T /F >nul 2>nul

call :is_port_listening %PORT%
if errorlevel 1 (
  echo [成功] %SVC% 已停止。
) else (
  echo [警告] %SVC% 仍在端口 %PORT% 上监听。请尝试使用管理员权限运行。
)
exit /b 0

:is_port_listening
set "PORT=%~1"
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>nul
if errorlevel 1 (
  exit /b 1
)
exit /b 0
