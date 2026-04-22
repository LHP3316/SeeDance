@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "LOG_DIR=%ROOT%logs"
set "BACKEND_PID_FILE=%ROOT%backend.pid"
set "FRONTEND_PID_FILE=%ROOT%frontend.pid"

set "BACKEND_LOG=%LOG_DIR%\backend.log"
set "FRONTEND_LOG=%LOG_DIR%\frontend.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==============================
echo SeeDance 启动脚本
echo ==============================

where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 在 PATH 中找不到 Python。
  exit /b 1
)

REM 启动后端
call :start_backend
if errorlevel 1 exit /b 1

REM 启动前端（如果存在）
if exist "%FRONTEND_DIR%\package.json" (
  call :start_frontend
) else (
  echo [信息] 未找到 frontend\package.json，跳过前端启动。
)

echo [完成] 启动命令执行完毕。
echo [提示] 使用 status 命令检查运行状态。
exit /b 0

:start_backend
REM 检查是否已经在运行
if exist "%BACKEND_PID_FILE%" (
  set "PID="
  set /p PID<"%BACKEND_PID_FILE%"
  if defined PID (
    tasklist /FI "PID eq !PID!" 2>nul | findstr "!PID!" >nul 2>nul
    if not errorlevel 1 (
      echo [信息] 后端已在运行 (进程ID: !PID!)
      exit /b 1
    )
  )
  del /q "%BACKEND_PID_FILE%" >nul 2>nul
)

echo [信息] 正在启动后端...

REM 使用 start /B 在后台启动
start /B cmd /c "cd /d "%BACKEND_DIR%" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 >>"%BACKEND_LOG%" 2>&1"

REM 获取最后启动的进程 PID
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO TABLE /NH ^| findstr /R /C:"python.exe"') do (
  set "LAST_PID=%%i"
)

REM 保存 PID
if defined LAST_PID (
  >"%BACKEND_PID_FILE%" echo !LAST_PID!
)

REM 等待 2 秒让服务启动
timeout /t 2 /nobreak >nul

REM 检查进程是否还在运行
if defined LAST_PID (
  tasklist /FI "PID eq !LAST_PID!" 2>nul | findstr "!LAST_PID!" >nul 2>nul
  if errorlevel 1 (
    echo [错误] 后端启动失败，请检查日志: %BACKEND_LOG%
    del /q "%BACKEND_PID_FILE%" >nul 2>nul
    exit /b 1
  )
  echo [成功] 后端已启动 (进程ID: !LAST_PID!)
) else (
  echo [警告] 无法获取后端进程ID，但启动命令已执行。
)
exit /b 0

:start_frontend
REM 检查是否已经在运行
if exist "%FRONTEND_PID_FILE%" (
  set "PID="
  set /p PID<"%FRONTEND_PID_FILE%"
  if defined PID (
    tasklist /FI "PID eq !PID!" 2>nul | findstr "!PID!" >nul 2>nul
    if not errorlevel 1 (
      echo [信息] 前端已在运行 (进程ID: !PID!)
      exit /b 1
    )
  )
  del /q "%FRONTEND_PID_FILE%" >nul 2>nul
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [错误] 未找到 npm。
  exit /b 1
)

echo [信息] 正在启动前端...

REM 使用 start /B 在后台启动
start /B cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev >>"%FRONTEND_LOG%" 2>&1"

REM 获取最后启动的 node 进程 PID
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq node.exe" /FO TABLE /NH ^| findstr /R /C:"node.exe"') do (
  set "LAST_PID=%%i"
)

REM 保存 PID
if defined LAST_PID (
  >"%FRONTEND_PID_FILE%" echo !LAST_PID!
)

REM 等待 2 秒让服务启动
timeout /t 2 /nobreak >nul

REM 检查进程是否还在运行
if defined LAST_PID (
  tasklist /FI "PID eq !LAST_PID!" 2>nul | findstr "!LAST_PID!" >nul 2>nul
  if errorlevel 1 (
    echo [错误] 前端启动失败，请检查日志: %FRONTEND_LOG%
    del /q "%FRONTEND_PID_FILE%" >nul 2>nul
    exit /b 1
  )
  echo [成功] 前端已启动 (进程ID: !LAST_PID!)
) else (
  echo [警告] 无法获取前端进程ID，但启动命令已执行。
)
exit /b 0
