@echo off
REM 即梦AI爬虫启动脚本

echo ========================================
echo 即梦AI图片生成爬虫
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

REM 检查依赖是否已安装
echo 检查依赖...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
    
    echo.
    echo 安装Playwright浏览器...
    playwright install chromium
)

echo.
echo 请选择运行模式:
echo 1. 单次执行（首次登录需要扫码）
echo 2. 定时任务（每2小时执行一次）
echo 3. 自定义定时任务
echo.
set /p choice=请输入选项 (1/2/3): 

if "%choice%"=="1" (
    echo.
    echo 启动单次执行模式...
    python main.py --prompt "一只可爱的猫咪"
) else if "%choice%"=="2" (
    echo.
    echo 启动定时任务模式（每2小时）...
    python main.py --prompt "一只可爱的猫咪" --schedule interval --interval 120
) else if "%choice%"=="3" (
    echo.
    set /p cron=请输入Cron表达式 (例如: 0 */2 * * *): 
    set /p prompt=请输入提示词: 
    python main.py --prompt "%prompt%" --schedule cron --cron "%cron%"
) else (
    echo 无效选项
)

echo.
pause
