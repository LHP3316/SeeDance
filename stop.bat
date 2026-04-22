@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_PID_FILE=%ROOT%backend.pid"
set "FRONTEND_PID_FILE=%ROOT%frontend.pid"

echo ==============================
echo SeeDance 停止脚本
echo ==============================

call :stop_one "backend" "%BACKEND_PID_FILE%" 8000
call :stop_one "frontend" "%FRONTEND_PID_FILE%" 5173

REM 清理可能残留的进程（通过端口）
call :stop_by_port "backend" 8000
call :stop_by_port "frontend" 5173

echo [完成] 停止命令执行完毕。
exit /b 0

:stop_one
set "NAME=%~1"
set "PID_FILE=%~2"

if not exist "%PID_FILE%" (
  echo [信息] %NAME% 未运行 (无 PID 文件)。
  exit /b 0
)

set "PID="
set /p PID<"%PID_FILE%"
if not defined PID (
  del /q "%PID_FILE%" >nul 2>nul
  echo [信息] %NAME% PID 文件为空，已清理。
  exit /b 0
)

REM 检查进程是否还在运行
tasklist /FI "PID eq %PID%" 2>nul | findstr "%PID%" >nul 2>nul
if errorlevel 1 (
  del /q "%PID_FILE%" >nul 2>nul
  echo [信息] %NAME% 进程不存在，已清理过期 PID (%PID%)。
  exit /b 0
)

echo [信息] 正在停止 %NAME% (进程ID: %PID%)...

REM 先尝试正常终止
taskkill /PID %PID% /T >nul 2>nul

REM 等待进程退出（最多10秒）
set /a WAIT_COUNT=0
:wait_exit
set /a WAIT_COUNT+=1
if %WAIT_COUNT% GTR 10 goto force_kill
timeout /t 1 /nobreak >nul
tasklist /FI "PID eq %PID%" 2>nul | findstr "%PID%" >nul 2>nul
if not errorlevel 1 goto wait_exit
goto cleanup

:force_kill
echo [警告] %NAME% 未在规定时间内退出，强制终止...
taskkill /PID %PID% /T /F >nul 2>nul
timeout /t 1 /nobreak >nul

:cleanup
del /q "%PID_FILE%" >nul 2>nul
echo [成功] %NAME% 已停止。
exit /b 0

:stop_by_port
set "NAME=%~1"
set "PORT=%~2"

REM 查找占用端口的进程
set "PORT_PIDS="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
  set "PORT_PIDS=!PORT_PIDS! %%p"
)

if not defined PORT_PIDS (
  exit /b 0
)

echo [信息] 发现未管理的 %NAME% 进程占用端口 %PORT%，正在停止...

REM 终止所有占用端口的进程
for %%p in (%PORT_PIDS%) do (
  taskkill /PID %%p /T /F >nul 2>nul
)

timeout /t 1 /nobreak >nul
exit /b 0
