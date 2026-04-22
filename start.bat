@echo off
REM ========================================
REM SeeDance 后端服务启动脚本 (Windows)
REM ========================================

echo ========================================
echo   SeeDance Backend Startup
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 或 Miniconda
    pause
    exit /b 1
)

REM 进入 backend 目录
cd /d "%~dp0backend"

REM 检查虚拟环境
if exist "..\venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call ..\venv\Scripts\activate.bat
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    echo 激活 Conda 环境...
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" seedance
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    echo 激活 Conda 环境...
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" seedance
)

echo.
echo 启动后端服务...
echo URL: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo ========================================
echo.

REM 启动后端
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
