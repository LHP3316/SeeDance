@echo off
REM ========================================
REM SeeDance 完整启动脚本 (Windows)
REM 启动: 后端 + 前端 + 任务执行器
REM ========================================

echo ========================================
echo   SeeDance 完整启动
echo ========================================
echo.

cd /d "%~dp0"

REM 1. 启动后端
echo [1/3] 启动后端服务...
start "SeeDance Backend" cmd /k "call start.bat"
timeout /t 3 /nobreak >nul

REM 2. 启动前端（如果存在）
if exist "frontend\package.json" (
    echo [2/3] 启动前端服务...
    cd frontend
    start "SeeDance Frontend" cmd /k "npm run dev"
    cd ..
    timeout /t 2 /nobreak >nul
) else (
    echo [2/3] 前端不存在，跳过...
)

REM 3. 启动任务执行器
echo [3/3] 启动任务执行器...
start "SeeDance Task Executor" cmd /k "call run-task-executor.bat"

echo.
echo ========================================
echo   所有服务已启动
echo ========================================
echo   后端: http://localhost:8000
echo   API 文档: http://localhost:8000/docs
echo   前端: http://localhost:5173 (如果启动)
echo ========================================
echo.
echo 按任意键退出此窗口...
pause >nul
