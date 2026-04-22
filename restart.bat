@echo off
setlocal
chcp 65001 >nul

echo ==============================
echo SeeDance 重启脚本
echo ==============================

call "%~dp0stop.bat"
timeout /t 1 /nobreak >nul
call "%~dp0start.bat"

echo [完成] 重启命令执行结束。
exit /b 0