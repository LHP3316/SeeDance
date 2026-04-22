@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "LOG_DIR=%ROOT%logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ==============================
echo SeeDance 启动脚本
echo ==============================

echo [1/2] 启动后端...
cd /d "%BACKEND_DIR%"
start /B "" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000" 1>>"%LOG_DIR%\backend.log" 2>>&1
echo       后端已启动

echo [2/2] 启动前端...
cd /d "%FRONTEND_DIR%"
start /B "" cmd /c "npm run dev" 1>>"%LOG_DIR%\frontend.log" 2>>&1
echo       前端已启动

echo.
echo ==============================
echo 启动完成！
echo ==============================
echo [提示] 请等待 10 秒后访问：
echo   后端：http://localhost:8000/docs
echo   前端：http://localhost:5173
echo.
echo [提示] 查看日志：
echo   Get-Content logs\backend.log -Tail 20
echo   Get-Content logs\frontend.log -Tail 20
echo.
exit /b 0
