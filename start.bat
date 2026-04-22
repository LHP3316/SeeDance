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

REM 确定 Python 可执行文件路径
set "PYTHON_EXE=python"
if exist "%USERPROFILE%\miniconda3\envs\seedance\python.exe" (
  set "PYTHON_EXE=%USERPROFILE%\miniconda3\envs\seedance\python.exe"
) else if exist "%USERPROFILE%\anaconda3\envs\seedance\python.exe" (
  set "PYTHON_EXE=%USERPROFILE%\anaconda3\envs\seedance\python.exe"
)

REM 使用 start /B 在后台启动（第一个空字符串是窗口标题）
pushd "%BACKEND_DIR%"
start /B "" "%PYTHON_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000 >>"%BACKEND_LOG%" 2>&1
popd

REM 等待 5 秒让服务启动
timeout /t 5 /nobreak >nul

REM 检查端口 8000 是否监听
netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>nul
if not errorlevel 1 (
  echo [成功] 后端已启动，监听端口 8000
) else (
  echo [错误] 后端启动失败，请检查日志: %BACKEND_LOG%
  exit /b 1
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

REM 确定 Node.js 可执行文件路径（使用系统 PATH 中的 npm）
set "NODE_EXE=node"
if exist "%USERPROFILE%\miniconda3\envs\seedance\node.exe" (
  set "NODE_EXE=%USERPROFILE%\miniconda3\envs\seedance\node.exe"
)

REM 使用 start /B 在后台启动
pushd "%FRONTEND_DIR%"
start /B cmd /c "npm run dev >>"%FRONTEND_LOG%" 2>&1"
popd

REM 等待 5 秒让服务启动
timeout /t 5 /nobreak >nul

REM 检查端口 5173 是否监听
netstat -ano | findstr ":5173 " | findstr "LISTENING" >nul 2>nul
if not errorlevel 1 (
  echo [成功] 前端已启动，监听端口 5173
) else (
  echo [错误] 前端启动失败，请检查日志: %FRONTEND_LOG%
  exit /b 1
)
exit /b 0
