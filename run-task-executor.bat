@echo off
REM ========================================
REM SeeDance 任务执行器启动脚本 (Windows)
REM ========================================

echo ========================================
echo   SeeDance Task Executor
echo ========================================
echo.

cd /d "%~dp0"

REM 激活虚拟环境或 Conda 环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" seedance
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" seedance
)

echo 启动任务执行器...
echo.

REM 启动任务执行器
python task_executor.py --interval 120

pause
