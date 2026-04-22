# Ubuntu 服务器部署项目指南

## 1. 服务器环境准备

### 1.1 操作系统要求
- Ubuntu 20.04 LTS 或 22.04 LTS（推荐 22.04）
- 建议使用云服务器（阿里云、腾讯云、AWS 等）
- 确保服务器有足够的资源（推荐 4GB+ 内存，50GB+ 磁盘）

### 1.2 SSH 连接到服务器

```bash
# 使用 SSH 连接到服务器
ssh username@your-server-ip

# 例如：
ssh root@123.45.67.89
```

### 1.3 更新系统包

```bash
# 更新包索引
sudo apt update

# 升级已安装的包
sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git unzip
```

## 2. 安装 Git

```bash
sudo apt update
sudo apt install git -y

# 验证
git --version
```

## 3. 配置 Git

```bash
git config --global user.name "LHP3316"
git config --global user.email "1833706710@qq.com"

# 克隆项目
git clone https://github.com/LHP3316/SeeDance.git
cd SeeDance
```

## 4. 安装 Miniconda

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

## 5. 创建 Python 环境

```bash
# 创建环境（Python 3.12）
conda create -n video python=3.12 -y

# 激活环境
conda activate video

# 验证
python --version
```

## 6. 配置 Conda 镜像源

```bash
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/main
conda config --add channels https://mirrors.aliyun.com/anaconda/pkgs/free
conda config --add channels https://mirrors.aliyun.com/anaconda/cloud/conda-forge
conda config --set show_channel_urls yes

# 验证
conda config --show channels
```

## 7. 配置 Pip 淘宝镜像源

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

## 8. 安装 Python 依赖

```bash
# 确保在 conda 环境中
conda activate video

# 安装依赖
pip install -r requirements.txt
```

## 9. 安装 Playwright

```bash
# 安装 Python 包
pip install playwright

# 安装浏览器
playwright install chromium

# 安装系统依赖
playwright install-deps chromium
```

## 10. 安装 MySQL

```bash
# 安装 MariaDB（MySQL 兼容版本）
sudo apt-get update
sudo apt-get install -y mariadb-server

# 启动服务
service mariadb start

# 进入数据库
mysql
```

**在数据库中执行：**
```sql
CREATE DATABASE seedance_backend CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('root');
FLUSH PRIVILEGES;
EXIT;
```

**之后登录数据库需要密码：**
```bash
mysql -u root -proot
```

**常用数据库命令：**
```bash
# 查看所有数据库
mysql -u root -proot -e "SHOW DATABASES;"

# 进入数据库后查看
mysql -u root -proot
SHOW DATABASES;
USE seedance_backend;
SHOW TABLES;
EXIT;
```

## 11. 配置环境变量

```bash
# 复制环境配置文件到 backend 目录（后端读取）
cp backend/.env.example backend/.env

# 复制一份到根目录（可选）
cp backend/.env.example .env

# 编辑 backend 目录的配置
nano backend/.env

# 修改数据库连接：
# DATABASE_URL=mysql+pymysql://root:root@localhost:3306/seedance_backend
# 其他配置...
```

## 12. 初始化数据库

```bash
# 激活环境
conda activate video

# 进入 backend 目录
cd backend

# 初始化数据库表
python -c "from database import engine; from models import *; Base.metadata.create_all(bind=engine)"
```

## 13. 启动服务

```bash
# 返回项目根目录
cd ..

# 启动后端
cd backend
python main.py

# 或使用启动脚本（如果有）
./start.sh
```

## 14. 验证安装

```bash
# 检查 Python 版本
python --version

# 检查依赖
pip list | grep -E "playwright|sqlalchemy|fastapi"

# 检查 Playwright
python -c 'from playwright.sync_api import sync_playwright; print("Playwright 安装成功")'

# 检查数据库连接
cd backend
python -c "from database import SessionLocal; db = SessionLocal(); print('数据库连接成功'); db.close()"
```

## 15. 服务器文件管理

### 15.1 使用 SCP 上传/下载文件

```bash
# 从本地上传文件到服务器（在本地终端执行）
scp -r ./SeeDance username@your-server-ip:/home/username/

# 从服务器下载文件到本地（在本地终端执行）
scp username@your-server-ip:/home/username/SeeDance/backend/.env ./
```

### 15.2 使用 SFTP

```bash
# 连接 SFTP（在本地终端执行）
sftp username@your-server-ip

# 上传文件
put local-file.txt /remote/path/

# 下载文件
get /remote/path/file.txt local-file.txt

# 退出
exit
```

### 15.3 使用 rsync 同步文件

```bash
# 同步本地项目到服务器（在本地终端执行）
rsync -avz --exclude '.git' --exclude '__pycache__' ./SeeDance/ username@your-server-ip:/home/username/SeeDance/
```

## 16. 常用命令

### 服务器管理命令

```bash
# 查看系统信息
lsb_release -a
uname -a

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看 CPU 信息
nproc
lscpu

# 查看系统负载
top
htop
```

### Conda 环境管理

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

# 查看系统信息
lsb_release -a

# 查看磁盘使用
df -h
```

## 19. 配置系统服务自动启动

### 19.1 创建 systemd 服务文件

```bash
# 创建后端服务
sudo nano /etc/systemd/system/seedance-backend.service
```

**添加以下内容：**

```ini
[Unit]
Description=SeeDance Backend Service
After=network.target mariadb.service

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/SeeDance/backend
Environment="PATH=/home/你的用户名/miniconda3/envs/video/bin"
ExecStart=/home/你的用户名/miniconda3/envs/video/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 19.2 启用并启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务开机自启
sudo systemctl enable seedance-backend.service

# 启动服务
sudo systemctl start seedance-backend.service

# 查看服务状态
sudo systemctl status seedance-backend.service

# 查看日志
sudo journalctl -u seedance-backend.service -f
```

## 17. 配置防火墙

### 17.1 使用 UFW 防火墙

```bash
# 安装 UFW（如果未安装）
sudo apt install -y ufw

# 允许 SSH 连接（重要！）
sudo ufw allow ssh

# 开放 8000 端口（后端 API）
sudo ufw allow 8000/tcp

# 开放 80/443 端口（如果需要 Web 访问）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看防火墙状态
sudo ufw status
```

### 17.2 云服务器安全组配置

如果你使用的是云服务器（阿里云、腾讯云等），还需要在控制台配置安全组规则：

- 添加入站规则，开放端口：8000、80、443、22（SSH）
- 根据需要开放其他端口

## 18. 注意事项

1. **所有命令必须在 `conda activate video` 后执行**
2. **Playwright 必须先安装 Python 包，再安装浏览器**
3. **数据库密码需要替换为实际密码**
4. **确保防火墙和云服务器安全组都开放必要端口（如 8000、3306）**
5. **生产环境建议使用 systemd 管理进程（如第 19 节所示）**
6. **pip 镜像源**：如果淘宝源超时，可切换为阿里云或清华源
7. **Git 推送需要代理**：使用 `ssh -p 22222 -R 7897:127.0.0.1:7897 visiontree@123.191.135.94` 建立反向代理
8. **磁盘空间**：定期检查磁盘使用情况 `df -h`
9. **性能优化**：项目文件建议放在 `/home/用户名/` 目录下
10. **安全建议**：定期更新系统包 `sudo apt update && sudo apt upgrade -y`

## 19. 故障排查

### 19.1 服务无法启动

```bash
# 检查服务状态
sudo systemctl status seedance-backend.service

# 查看日志
sudo journalctl -u seedance-backend.service -f

# 检查端口占用
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000
```

### 19.2 网络连接问题

```bash
# 测试网络连接
ping google.com

# 检查 DNS 配置
cat /etc/resolv.conf

# 重启网络服务
sudo systemctl restart networking

# 检查防火墙状态
sudo ufw status
```

### 19.3 数据库无法启动

```bash
# 检查 MariaDB 状态
sudo systemctl status mariadb

# 重新启动
sudo systemctl restart mariadb

# 查看日志
sudo journalctl -u mariadb -f
```

### 19.4 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000

# 或使用
sudo netstat -tulpn | grep :8000

# 终止占用进程
sudo kill -9 <PID>
```

## 20. 备份与迁移

### 20.1 项目文件备份

```bash
# 压缩项目目录
tar -czf seedance-backup-$(date +%Y%m%d).tar.gz /home/用户名/SeeDance

# 下载备份文件到本地（在本地执行）
scp username@your-server-ip:/path/to/seedance-backup-20260422.tar.gz ./
```

### 20.3 完整备份脚本

```bash
#!/bin/bash
# backup.sh - 备份项目和数据库

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/用户名/backups"
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u root -proot seedance_backend > $BACKUP_DIR/db_seedance_$DATE.sql

# 备份项目文件
tar -czf $BACKUP_DIR/project_seedance_$DATE.tar.gz /home/用户名/SeeDance

# 删除 7 天前的备份
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

**设置定时任务：**

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /home/用户名/backup.sh
```

### 20.2 数据库备份

```bash
# 备份数据库
mysqldump -u root -proot seedance_backend > backup_seedance_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root -proot seedance_backend < backup_seedance_20260422.sql
```

## 21. 快速部署检查清单

在部署完成后,请使用以下检查清单验证一切正常:

- [ ] SSH 连接正常
- [ ] 系统已更新 (`sudo apt update && sudo apt upgrade`)
- [ ] Git 已安装并配置
- [ ] 项目代码已克隆
- [ ] Miniconda 已安装
- [ ] Python 环境已创建 (`conda activate video`)
- [ ] Python 依赖已安装 (`pip install -r requirements.txt`)
- [ ] Playwright 已安装并下载浏览器
- [ ] MySQL/MariaDB 已安装并运行
- [ ] 数据库已创建并初始化
- [ ] 环境变量已配置 (`backend/.env`)
- [ ] 后端服务可以启动
- [ ] 防火墙已配置(开放 8000 端口)
- [ ] 云服务器安全组已配置(如适用)
- [ ] systemd 服务已配置并启用(生产环境)

## 22. 生产环境建议

1. **使用 Nginx 反向代理**:配置 Nginx 作为反向代理,提供更好的性能和安全性
2. **启用 HTTPS**:使用 Let's Encrypt 免费 SSL 证书
3. **配置日志轮转**:使用 logrotate 管理日志文件
4. **定期备份**:设置自动化备份脚本和定时任务
5. **监控告警**:配置系统监控(如 Prometheus + Grafana)
6. **安全加固**:
   - 禁用 root SSH 登录
   - 使用 SSH 密钥认证
   - 配置 fail2ban 防止暴力破解
   - 定期更新系统安全补丁

---

**文档版本**: v2.0  
**更新日期**: 2026-04-22  
**适用范围**: Ubuntu 20.04/22.04 服务器直接部署