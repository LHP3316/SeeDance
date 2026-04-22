# Windows 直接部署指南（使用 Conda）

## 1. 安装 Python 环境

### 1.1 安装 Miniconda（推荐）

1. 下载 Miniconda Windows 版本：
   - 地址：https://docs.conda.io/en/latest/miniconda.html
   - 下载：`Miniconda3 Windows 64-bit`

2. 运行安装程序，按提示安装
   - 建议勾选"Add to PATH"
   - 或使用 Anaconda Prompt

### 1.2 或使用 Python 官方安装包

- 下载：https://www.python.org/downloads/
- 安装时勾选"Add Python to PATH"

## 2. 创建虚拟环境

```powershell
# 打开 PowerShell 或 Anaconda Prompt

# 创建环境
conda create -n seedance python=3.12 -y

# 激活环境
conda activate seedance

# 验证
python --version
```

## 3. 克隆项目

```powershell
# 使用 Git 克隆
git clone https://github.com/LHP3316/SeeDance.git
cd SeeDance

# 或如果已有项目，直接进入目录
cd d:\Project\seedance
```

## 4. 安装 Python 依赖

```powershell
# 确保已激活环境
conda activate seedance

# 安装依赖
pip install -r requirements.txt

# 配置 pip 镜像（可选，加速下载）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 5. 安装 Playwright 浏览器

```powershell
# 安装 Chromium 浏览器
playwright install chromium

# 注意：Windows 不需要执行 playwright install-deps
# 这个命令只用于 Linux 安装系统依赖
```

### 5.1 使用已安装的 Chrome/Edge（可选）

如果你本地已经安装了 Chrome 或 Edge，可以直接使用：

```python
# 在代码中指定浏览器路径
plugin = JimengWebVideoPlugin(
    browser_exe=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    headless=False
)
```

常见浏览器路径：
- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Edge: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

## 6. 安装 MySQL 数据库

### 6.1 下载 MySQL Installer

1. 访问：https://dev.mysql.com/downloads/installer/
2. 下载 `mysql-installer-community`（约 300MB）
3. 选择 `mysql-installer-web-community`（在线安装，体积小）

### 6.2 安装步骤

1. 运行安装程序
2. 选择"Server only"或"Custom"
3. 设置 root 密码（记住这个密码）
4. 其他选项保持默认
5. 完成安装

### 6.3 验证安装

```powershell
# 检查 MySQL 服务
Get-Service MySQL*

# 或使用命令行
mysql -u root -p
```

### 6.4 创建数据库

```powershell
# 登录 MySQL
mysql -u root -p

# 在 MySQL 中执行
CREATE DATABASE seedance_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
EXIT;
```

### 6.5 替代方案：MariaDB

如果 MySQL 安装遇到问题，可以使用 MariaDB（完全兼容）：
- 下载：https://mariadb.org/download/
- 安装方式类似

## 7. 配置环境变量

```powershell
# 复制配置文件
cd backend
copy .env.example .env

# 编辑配置文件（使用记事本或 VSCode）
notepad .env
```

修改数据库连接：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=seedance_backend
```

## 8. 初始化数据库

```powershell
# 确保在 backend 目录
cd backend

# 初始化数据库表
python -c "from database import engine; from models import *; Base.metadata.create_all(bind=engine)"
```

## 9. 启动服务

### 9.1 启动后端 API

```powershell
# 在 backend 目录
cd backend

# 启动后端
python main.py

# 或使用 uvicorn 直接启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 9.2 使用启动脚本

如果项目有 `run.bat`，直接双击运行即可。

## 10. 验证安装

```powershell
# 检查 Python 版本
python --version

# 检查依赖
pip list | Select-String -Pattern "playwright|sqlalchemy|fastapi"

# 检查 Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright 安装成功')"

# 检查数据库连接
cd backend
python -c "from database import SessionLocal; db = SessionLocal(); print('数据库连接成功'); db.close()"
```

## 11. 配置 Windows 防火墙

```powershell
# 以管理员身份运行 PowerShell

# 开放 8000 端口（后端 API）
New-NetFirewallRule -DisplayName "SeeDance Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# 开放 3306 端口（MySQL，仅本地访问可不开放）
# New-NetFirewallRule -DisplayName "MySQL" -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow
```

## 12. 设置开机自启动（可选）

### 12.1 使用 Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：计算机启动时
4. 操作：启动程序
   - 程序：`C:\Path\To\Miniconda3\envs\seedance\python.exe`
   - 参数：`main.py`
   - 起始于：`d:\Project\seedance\backend`

### 12.2 使用 NSSM（推荐）

```powershell
# 下载 NSSM
# https://nssm.cc/download

# 安装服务
nssm install SeeDance-Backend
nssm set SeeDance-Backend Application "C:\Path\To\Miniconda3\envs\seedance\python.exe"
nssm set SeeDance-Backend ApplicationParameters "main.py"
nssm set SeeDance-Backend AppDirectory "d:\Project\seedance\backend"
nssm set SeeDance-Backend DisplayName "SeeDance Backend Service"

# 启动服务
nssm start SeeDance-Backend
```

## 13. 常见问题

### Q1: Playwright 安装失败

```powershell
# 清理缓存重试
playwright install --force chromium

# 或使用国内镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
playwright install chromium
```

### Q2: MySQL 连接失败

```powershell
# 检查 MySQL 服务是否运行
Get-Service MySQL*

# 启动服务
Start-Service MySQL*

# 检查端口
netstat -ano | findstr :3306
```

### Q3: 浏览器无法启动

```powershell
# 检查浏览器路径
# 在代码中打印浏览器路径
print(self.browser_exe)

# 使用绝对路径
browser_exe=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### Q4: 依赖安装失败

```powershell
# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 14. Windows vs Linux 差异对比

| 组件 | Windows | Linux (Ubuntu) | 说明 |
|------|---------|----------------|------|
| Python | ✅ Conda | ✅ Conda | 完全一致 |
| Playwright | ✅ 支持 | ✅ 支持 | Windows 不需要 install-deps |
| MySQL | 图形化安装 | apt 安装 | 功能完全一致 |
| 文件路径 | `\` 或 `/` | `/` | Python 自动处理 |
| 环境变量 | `.env` | `.env` | 完全一致 |
| 服务管理 | NSSM/任务计划 | systemd | 方式不同 |

## 15. 性能建议

1. **项目文件位置**：
   - 建议放在 SSD 硬盘
   - 避免放在 OneDrive 同步目录

2. **防病毒软件**：
   - 将项目目录添加到白名单
   - 避免实时扫描影响性能

3. **浏览器自动化**：
   - 开发时使用 `headless=False` 方便调试
   - 生产环境使用 `headless=True`

4. **数据库性能**：
   - 确保 MySQL 数据文件在 SSD
   - 定期优化表：`OPTIMIZE TABLE table_name;`

## 16. 开发工具推荐

- **IDE**: VS Code / PyCharm
- **数据库管理**: DBeaver / Navicat / MySQL Workbench
- **API 测试**: Postman / Apifox
- **终端**: Windows Terminal / PowerShell 7

## 17. 总结

✅ **Windows 部署完全可行**  
✅ **所有依赖都支持 Windows**  
✅ **Playwright 在 Windows 上表现良好**  
✅ **MySQL 图形化安装更简单**  
✅ **开发体验更好（IDE 支持）**  

唯一的区别是服务管理方式（Windows 用 NSSM，Linux 用 systemd），但核心功能完全一致。

---

**文档版本**: v1.0  
**更新日期**: 2026-04-22  
**适用范围**: Windows 10/11 直接部署
