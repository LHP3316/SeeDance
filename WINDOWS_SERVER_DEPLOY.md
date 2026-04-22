# Windows Server 部署完整指南

## 适用场景

- ✅ Windows Server 2019/2022/2025
- ✅ Windows 10/11 专业版
- ✅ 需要开机自启动服务
- ✅ 远程桌面管理

## 1. 服务器环境准备

### 1.1 系统要求

- Windows Server 2019 或更高版本
- 4GB+ 内存（推荐 8GB）
- 50GB+ 磁盘空间（推荐 SSD）
- 稳定的网络连接

### 1.2 远程连接服务器

```powershell
# 使用远程桌面连接 (RDP)
# Windows + R 输入 mstsc
# 输入服务器 IP 地址
# 输入用户名和密码
```

### 1.3 安装基础软件

#### 安装 Git

```powershell
# 方法1：使用 winget（Windows 10/11）
winget install Git.Git

# 方法2：下载安装包
# https://git-scm.com/download/win
# 下载后双击安装
```

#### 安装 Visual Studio Build Tools（编译依赖需要）

```powershell
# 下载：https://visualstudio.microsoft.com/visual-cpp-build-tools/
# 安装时勾选 "C++ build tools"
```

## 2. 安装 Python 环境

### 2.1 安装 Miniconda（推荐）

1. 下载 Miniconda：
   - https://docs.conda.io/en/latest/miniconda.html
   - 选择 Windows 64-bit 版本

2. 双击安装包，按提示安装
   - 建议勾选"Add to PATH"
   - 或记住安装路径，后续手动配置

3. 验证安装：
   ```powershell
   conda --version
   ```

### 2.2 创建项目环境

```powershell
# 打开 Anaconda Prompt 或 PowerShell

# 创建环境
conda create -n seedance python=3.12 -y

# 激活环境
conda activate seedance

# 验证
python --version
```

## 3. 部署项目代码

### 3.1 克隆项目

```powershell
# 创建项目目录
cd D:\
mkdir SeeDance
cd SeeDance

# 克隆代码
git clone https://github.com/LHP3316/SeeDance.git .

# 或复制已有代码到 D:\SeeDance
```

### 3.2 安装 Python 依赖

```powershell
# 激活环境
conda activate seedance

# 进入项目目录
cd D:\SeeDance

# 配置 pip 镜像（加速下载）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
pip install -r requirements.txt
```

## 4. 安装 Playwright

```powershell
# 安装 Python 包（已在 requirements.txt 中）
# pip install playwright

# 安装 Chromium 浏览器
playwright install chromium

# 注意：Windows 不需要执行 playwright install-deps
```

### 4.1 使用已安装的浏览器（可选）

如果服务器已安装 Chrome 或 Edge，可以直接使用：

```python
# 在代码中指定路径
browser_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
# 或
browser_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

## 5. 安装 MySQL 数据库

### 5.1 下载 MySQL Installer

1. 访问：https://dev.mysql.com/downloads/installer/
2. 下载 `mysql-installer-web-community`（在线安装，约 2MB）
3. 或下载 `mysql-installer-community`（离线安装，约 300MB）

### 5.2 安装步骤

1. 双击安装程序
2. 选择"Custom"自定义安装
3. 选择"MySQL Server 8.0.x"
4. 点击"Execute"下载并安装
5. 配置 MySQL：
   - Config Type: Server Machine
   - 设置 root 密码（例如：`root` 或自定义）
   - 勾选"Start the MySQL Server automatically"
6. 完成安装

### 5.3 验证安装

```powershell
# 检查 MySQL 服务
Get-Service MySQL*

# 应该看到状态为 Running
```

### 5.4 创建数据库

```powershell
# 打开命令行
mysql -u root -p

# 输入密码后执行 SQL
CREATE DATABASE seedance_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 设置密码认证方式（兼容 PyMySQL）
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '你的密码';
FLUSH PRIVILEGES;

EXIT;
```

## 6. 配置环境变量

```powershell
# 进入 backend 目录
cd D:\SeeDance\backend

# 复制配置文件
copy .env.example .env

# 编辑配置文件
notepad .env
```

修改数据库配置：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的密码
DB_NAME=seedance_backend

SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 7. 初始化数据库

```powershell
# 激活环境
conda activate seedance

# 进入 backend 目录
cd D:\SeeDance\backend

# 初始化数据库表
python -c "from database import engine; from models import *; Base.metadata.create_all(bind=engine)"

# 验证
python -c "from database import SessionLocal; db = SessionLocal(); print('数据库连接成功'); db.close()"
```

## 8. 测试运行

### 8.1 启动后端

```powershell
cd D:\SeeDance\backend

# 启动后端
python main.py

# 或使用 uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 8.2 访问 API

打开浏览器访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 8.3 测试 Playwright

```python
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('Playwright 正常'); p.stop()"
```

## 9. 配置 Windows 防火墙

```powershell
# 以管理员身份运行 PowerShell

# 开放 8000 端口（后端 API）
New-NetFirewallRule -DisplayName "SeeDance Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 如果需要远程访问 MySQL（不建议，仅本地访问）
# New-NetFirewallRule -DisplayName "MySQL" -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow
```

## 10. 设置开机自启动服务

### 方案 1：使用 NSSM（推荐，简单）

#### 10.1.1 下载 NSSM

```powershell
# 下载 NSSM
# https://nssm.cc/download
# 或使用 PowerShell 下载
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "nssm-2.24.zip"

# 解压
Expand-Archive nssm-2.24.zip -DestinationPath D:\SeeDance\tools\

# NSSM 路径：D:\SeeDance\tools\nssm-2.24\win64\nssm.exe
```

#### 10.1.2 安装后端服务

```powershell
# 以管理员身份运行
cd D:\SeeDance\tools\nssm-2.24\win64

# 安装后端服务
.\nssm.exe install SeeDance-Backend

# 在弹出的 GUI 中配置：
# Application -> Path: C:\Path\To\Miniconda3\envs\seedance\python.exe
# Application -> Arguments: -m uvicorn main:app --host 0.0.0.0 --port 8000
# Application -> Startup directory: D:\SeeDance\backend
# Details -> Display name: SeeDance Backend Service
# Log on -> 选择 Local System account

# 启动服务
.\nssm.exe start SeeDance-Backend

# 查看服务状态
.\nssm.exe status SeeDance-Backend
```

#### 10.1.3 安装任务执行器服务

```powershell
# 安装任务执行器服务
.\nssm.exe install SeeDance-TaskExecutor

# 配置：
# Path: C:\Path\To\Miniconda3\envs\seedance\python.exe
# Arguments: task_executor.py --interval 120
# Startup directory: D:\SeeDance

# 启动服务
.\nssm.exe start SeeDance-TaskExecutor
```

#### 10.1.4 NSSM 常用命令

```powershell
# 查看服务列表
.\nssm.exe list

# 停止服务
.\nssm.exe stop SeeDance-Backend

# 重启服务
.\nssm.exe restart SeeDance-Backend

# 编辑服务配置
.\nssm.exe edit SeeDance-Backend

# 删除服务
.\nssm.exe remove SeeDance-Backend confirm
```

### 方案 2：使用 Windows 任务计划程序

#### 10.2.1 创建启动脚本

创建 `D:\SeeDance\start-service.bat`：

```batch
@echo off
cd /d D:\SeeDance\backend
call C:\Path\To\Miniconda3\Scripts\activate.bat seedance
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 10.2.2 创建计划任务

1. 打开"任务计划程序"
2. 创建基本任务
3. 名称：SeeDance Backend
4. 触发器：计算机启动时
5. 操作：启动程序
   - 程序：`D:\SeeDance\start-service.bat`
   - 起始于：`D:\SeeDance\backend`
6. 勾选"使用最高权限运行"
7. 完成

### 方案 3：使用 Windows 服务（sc 命令）

```powershell
# 创建批处理启动文件 D:\SeeDance\backend\run-as-service.bat
@echo off
cd /d D:\SeeDance\backend
call C:\Path\To\Miniconda3\Scripts\activate.bat seedance
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 注册服务（管理员权限）
sc create SeeDance-Backend binPath= "D:\SeeDance\backend\run-as-service.bat" start= auto

# 启动服务
sc start SeeDance-Backend
```

## 11. 服务管理

### 11.1 使用 PowerShell 管理服务

```powershell
# 查看所有服务
Get-Service | Select-String "SeeDance"

# 启动服务
Start-Service SeeDance-Backend

# 停止服务
Stop-Service SeeDance-Backend

# 重启服务
Restart-Service SeeDance-Backend

# 查看服务状态
Get-Service SeeDance-Backend
```

### 11.2 使用 services.msc

1. Windows + R 输入 `services.msc`
2. 找到 SeeDance-Backend
3. 右键可以启动/停止/重启

## 12. 日志管理

### 12.1 查看服务日志

如果使用 NSSM，日志默认在：
```
D:\SeeDance\backend\logs\
```

### 12.2 查看 Windows 事件日志

```powershell
# 查看应用程序日志
Get-EventLog -LogName Application -Source "SeeDance*" -Newest 50

# 或使用事件查看器
eventvwr.msc
```

### 12.3 配置日志轮转（可选）

Windows 可以使用 PowerShell 脚本定期清理日志：

```powershell
# 创建日志清理脚本
# D:\SeeDance\cleanup-logs.ps1

$logDir = "D:\SeeDance\logs"
$daysToKeep = 30

Get-ChildItem $logDir -Recurse | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$daysToKeep)
} | Remove-Item -Force

# 添加到任务计划程序，每天执行
```

## 13. 性能优化

### 13.1 电源设置

```powershell
# 设置高性能电源计划
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```

### 13.2 防病毒软件白名单

将以下目录添加到防病毒软件白名单：
- `D:\SeeDance`
- `C:\Path\To\Miniconda3\envs\seedance`
- MySQL 数据目录

### 13.3 MySQL 优化

编辑 MySQL 配置文件（`my.ini`）：

```ini
[mysqld]
max_connections=200
innodb_buffer_pool_size=1G
query_cache_size=64M
```

## 14. 备份策略

### 14.1 数据库备份脚本

创建 `D:\SeeDance\backup-db.bat`：

```batch
@echo off
set BACKUP_DIR=D:\SeeDance\backups
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DATE=%DATE: =0%

mkdir %BACKUP_DIR% 2>nul

mysqldump -u root -p你的密码 seedance_backend > %BACKUP_DIR%\db_backup_%DATE%.sql

echo 数据库备份完成: %DATE%
```

### 14.2 设置定时备份

使用任务计划程序：
1. 创建任务：每天凌晨 2 点执行
2. 操作：运行 `D:\SeeDance\backup-db.bat`

### 14.3 项目文件备份

```powershell
# 手动备份
robocopy D:\SeeDance D:\Backup\SeeDance /MIR /XD .git __pycache__ logs

# 或使用压缩
Compress-Archive -Path D:\SeeDance -DestinationPath D:\Backup\SeeDance_$(Get-Date -Format 'yyyyMMdd').zip
```

## 15. 监控和告警

### 15.1 使用 Windows 性能监视器

```powershell
# 打开性能监视器
perfmon.msc

# 添加计数器：
# - 内存使用
# - CPU 使用率
# - 磁盘 I/O
```

### 15.2 简单的服务监控脚本

创建 `D:\SeeDance\monitor-service.ps1`：

```powershell
$serviceName = "SeeDance-Backend"
$service = Get-Service $serviceName -ErrorAction SilentlyContinue

if ($service -and $service.Status -ne "Running") {
    Write-Host "服务未运行，正在启动..."
    Start-Service $serviceName
    
    # 发送告警邮件（可选）
    # Send-MailMessage -To "admin@example.com" -Subject "SeeDance 服务已重启"
}
```

## 16. 常见问题排查

### 16.1 服务无法启动

```powershell
# 查看服务状态
Get-Service SeeDance-Backend

# 查看事件日志
Get-EventLog -LogName Application -Newest 50 | Where-Object {$_.EntryType -eq "Error"}

# 手动测试启动
cd D:\SeeDance\backend
conda activate seedance
python main.py
```

### 16.2 MySQL 连接失败

```powershell
# 检查 MySQL 服务
Get-Service MySQL*

# 检查端口
netstat -ano | findstr :3306

# 测试连接
mysql -u root -p
```

### 16.3 Playwright 浏览器问题

```powershell
# 重新安装浏览器
playwright install --force chromium

# 检查浏览器路径
python -c "import playwright; print(playwright.__file__)"
```

### 16.4 端口被占用

```powershell
# 查看端口占用
netstat -ano | findstr :8000

# 终止进程
Stop-Process -Id <PID> -Force
```

## 17. 安全检查

### 17.1 更新系统

```powershell
# Windows Update
# 设置 -> 更新和安全 -> Windows Update
```

### 17.2 配置防火墙

```powershell
# 只开放必要端口
Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True"}

# 删除不需要的规则
Remove-NetFirewallRule -DisplayName "不需要的规则"
```

### 17.3 定期更改密码

- MySQL root 密码
- Windows 管理员密码
- 应用 SECRET_KEY

## 18. 快速部署检查清单

部署完成后，请逐项检查：

- [ ] Windows Server 已更新到最新补丁
- [ ] Git 已安装
- [ ] Miniconda 已安装
- [ ] Python 环境已创建 (`conda activate seedance`)
- [ ] 项目代码已部署到 `D:\SeeDance`
- [ ] Python 依赖已安装 (`pip install -r requirements.txt`)
- [ ] Playwright 浏览器已安装
- [ ] MySQL 已安装并运行
- [ ] 数据库已创建 (`seedance_backend`)
- [ ] 环境变量已配置 (`backend/.env`)
- [ ] 数据库表已初始化
- [ ] 后端服务可以手动启动
- [ ] 防火墙已配置（开放 8000 端口）
- [ ] 服务已设置为开机自启动
- [ ] 数据库备份脚本已配置
- [ ] 日志目录已创建

## 19. 总结

✅ **Windows 服务器直接部署完全可行**  
✅ **所有组件都有 Windows 版本**  
✅ **图形化管理更方便**  
✅ **远程桌面操作简单**  
✅ **服务管理工具丰富（NSSM/任务计划/Windows 服务）**  

与 Linux 相比，Windows 部署的优势：
- 更友好的图形界面
- 远程桌面连接更稳定
- 服务管理工具多样
- 不需要学习 Linux 命令

---

**文档版本**: v1.0  
**更新日期**: 2026-04-22  
**适用范围**: Windows Server 2019/2022/2025
