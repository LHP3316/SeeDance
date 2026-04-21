# Linux 服务器部署指南

## 1. 安装 Git

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install git -y

# CentOS/RHEL
sudo yum update
sudo yum install git -y

# 验证
git --version
```

## 2. 配置 Git

```bash
git config --global user.name "LHP3316"
git config --global user.email "1833706710@qq.com"

# 克隆项目
git clone https://github.com/LHP3316/SeeDance.git
cd SeeDance
```

## 3. 安装 Miniconda

```bash
# 下载
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装
bash Miniconda3-latest-Linux-x86_64.sh

# 按提示操作：
# 1. 按 Enter 阅读协议
# 2. 输入 yes 接受协议
# 3. 按 Enter 使用默认安装路径
# 4. 输入 yes 初始化 conda

# 刷新配置
source ~/.bashrc

# 验证
conda --version
```

## 4. 创建 Python 环境

```bash
# 创建环境（Python 3.12）
conda create -n video python=3.12 -y

# 激活环境
conda activate video

# 验证
python --version
```

## 5. 配置 Conda 镜像源

```bash
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/main
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/free
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/conda-forge
conda config --set show_channel_urls yes

# 验证
conda config --show channels
```

## 6. 配置 Pip 淘宝镜像源

```bash
# 创建 pip 配置文件
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.taobao.org/simple
trusted-host = pypi.taobao.org

[install]
trusted-host = pypi.taobao.org
EOF

# 验证
pip config list
```

## 7. 安装 Python 依赖

```bash
# 确保在 conda 环境中
conda activate video

# 安装依赖
pip install -r requirements.txt
```

## 8. 安装 Playwright

```bash
# 安装 Python 包
pip install playwright

# 安装浏览器
playwright install chromium

# 安装系统依赖（Ubuntu/Debian）
playwright install-deps chromium

# 安装系统依赖（CentOS/RHEL）
sudo yum install -y atk at-spi2-atk libdrm libXcomposite libXcursor libXdamage libXext libXi libXrandr libXScrnSaver libXtst pango atkmm cairo-gobject cups-libs gdk-pixbuf2 libgio libnotify libXt libgbm mesa-libgbm
```

## 9. 配置数据库

```bash
# 安装 MySQL（如果需要）
# Ubuntu/Debian
sudo apt install mysql-server -y

# CentOS/RHEL
sudo yum install mysql-server -y
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 创建数据库
mysql -u root -p
CREATE DATABASE seedance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'seedance'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON seedance.* TO 'seedance'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 10. 配置环境变量

```bash
# 复制环境配置文件
cp backend/.env.example backend/.env

# 编辑配置
nano backend/.env

# 修改以下内容：
# DATABASE_URL=mysql+pymysql://seedance:your_password@localhost:3306/seedance
# 其他配置...
```

## 11. 初始化数据库

```bash
# 激活环境
conda activate video

# 进入 backend 目录
cd backend

# 执行初始化脚本
mysql -u seedance -p seedance < init_database_full.sql

# 或者使用 SQLAlchemy 自动创建
python -c "from database import engine; from models import *; Base.metadata.create_all(bind=engine)"
```

## 12. 启动服务

```bash
# 返回项目根目录
cd ..

# 启动后端
cd backend
python main.py

# 或使用启动脚本（如果有）
./start.sh
```

## 13. 验证安装

```bash
# 检查 Python 版本
python --version

# 检查依赖
pip list | grep -E "playwright|sqlalchemy|fastapi"

# 检查浏览器
playwright install --dry-run chromium

# 检查数据库连接
python -c "from database import SessionLocal; db = SessionLocal(); print('数据库连接成功'); db.close()"
```

## 常用命令

```bash
# 激活环境
conda activate video

# 退出环境
conda deactivate

# 查看环境列表
conda env list

# 安装新依赖
pip install package_name

# 查看已安装依赖
pip list

# 查看 conda 镜像源
conda config --show channels

# 查看 pip 配置
pip config list
```

## 注意事项

1. 所有命令必须在 `conda activate video` 后执行
2. Playwright 必须先安装 Python 包，再安装浏览器
3. 数据库密码需要替换为实际密码
4. 确保服务器防火墙开放必要端口（如 8000、3306）
5. 生产环境建议使用 systemd 或 supervisor 管理进程
