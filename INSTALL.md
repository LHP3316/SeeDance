# 环境安装指南

本文档详细说明如何在 Conda 环境中搭建即梦AI爬虫项目。

## 前置要求

- 已安装 Anaconda 或 Miniconda
- Windows 10/11 操作系统
- 网络连接正常

## 安装步骤

### 1. 创建 Conda 环境

```bash
# 创建名为 seedance 的 Python 3.10 环境
conda create -n seedance python=3.10 -y
```

### 2. 激活环境

```bash
# Windows
conda activate seedance

# Linux/Mac
source activate seedance
```

### 3. 配置 pip 镜像源（可选但推荐）

#### 方式一：临时使用（单次安装）

```bash
# 使用阿里云镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 或使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### 方式二：永久配置（推荐）

```bash
# 配置阿里云镜像源（淘宝源）
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com

# 或配置清华镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

### 4. 安装项目依赖

```bash
# 如果已配置镜像源，直接运行
pip install -r requirements.txt

# 如果未配置镜像源，使用临时镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 5. 安装 Playwright 浏览器

```bash
# 安装 Chromium 浏览器（必需）
playwright install chromium

# 如果网络较慢，可以使用国内镜像
# 设置 Playwright 下载镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 6. 验证安装

```bash
# 检查依赖是否安装成功
python main.py --help

# 如果显示帮助信息，说明安装成功
```

## 一键安装脚本

### Windows 用户

创建 `setup.bat` 文件，内容如下：

```batch
@echo off
echo ========================================
echo 即梦AI爬虫 - 环境安装
echo ========================================
echo.

echo [1/4] 创建Conda环境...
conda create -n seedance python=3.10 -y

echo.
echo [2/4] 激活环境...
call conda activate seedance

echo.
echo [3/4] 配置镜像源并安装依赖...
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com
pip install -r requirements.txt

echo.
echo [4/4] 安装Playwright浏览器...
playwright install chromium

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用以下命令激活环境：
echo   conda activate seedance
echo.
echo 运行项目：
echo   python main.py --help
echo.
pause
```

然后双击运行：

```bash
setup.bat
```

### Linux/Mac 用户

创建 `setup.sh` 文件：

```bash
#!/bin/bash
echo "========================================"
echo "即梦AI爬虫 - 环境安装"
echo "========================================"
echo

echo "[1/4] 创建Conda环境..."
conda create -n seedance python=3.10 -y

echo
echo "[2/4] 激活环境..."
source activate seedance

echo
echo "[3/4] 配置镜像源并安装依赖..."
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com
pip install -r requirements.txt

echo
echo "[4/4] 安装Playwright浏览器..."
playwright install chromium

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "使用以下命令激活环境："
echo "  conda activate seedance"
echo
echo "运行项目："
echo "  python main.py --help"
echo
```

然后运行：

```bash
chmod +x setup.sh
./setup.sh
```

## 常见问题

### Q1: conda create 命令失败

**解决方案：**
```bash
# 检查conda是否正常
conda --version

# 更新conda
conda update conda

# 使用国内镜像源加速
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes
```

### Q2: pip install 下载很慢

**解决方案：** 使用国内镜像源（见步骤3）

### Q3: playwright install 下载失败

**解决方案：**
```bash
# 设置国内镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium

# 或手动下载浏览器
# 访问 https://playwright.dev/python/docs/browsers
```

### Q4: 激活环境失败

**解决方案：**
```bash
# Windows - 初始化conda
conda init powershell
# 然后重启终端

# 或使用完整路径激活
C:\Users\你的用户名\anaconda3\Scripts\activate.bat seedance
```

### Q5: 依赖冲突

**解决方案：**
```bash
# 清理conda缓存
conda clean --all

# 重新创建环境
conda remove -n seedance --all
conda create -n seedance python=3.10 -y
conda activate seedance
pip install -r requirements.txt
```

## 环境管理

### 查看已创建的环境

```bash
conda env list
```

### 删除环境

```bash
conda remove -n seedance --all
```

### 导出环境配置

```bash
# 导出为environment.yml
conda env export -n seedance > environment.yml

# 从配置文件创建环境
conda env create -f environment.yml
```

### 查看已安装的包

```bash
# 查看conda环境中的包
conda list

# 查看pip安装的包
pip list
```

## 快速启动

安装完成后，快速测试项目：

```bash
# 1. 激活环境
conda activate seedance

# 2. 查看帮助
python main.py --help

# 3. 首次运行（需要扫码登录）
python main.py

# 4. 生成图片
python main.py --prompt "一只可爱的猫咪" --images cat.jpg
```

## 技术支持

如遇到其他问题，请查看：
- 项目 README: [README.md](README.md)
- Playwright 文档: https://playwright.dev/python/
- Conda 文档: https://docs.conda.io/
