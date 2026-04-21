#!/usr/bin/env bash
set -euo pipefail

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}  数据库连接检测与修复${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""

# 检查MySQL是否运行
echo -e "${CYAN}1. 检查MySQL服务状态${NC}"
if mysqladmin -u root -proot ping 2>/dev/null | grep -q "alive"; then
    echo -e "${GREEN}✓ MySQL 正在运行${NC}"
else
    echo -e "${RED}✗ MySQL 未运行${NC}"
    echo -e "${YELLOW}请先启动MySQL: sudo service mysql start${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}2. 测试数据库连接${NC}"

# 测试root用户连接
echo -e "${YELLOW}尝试使用 root/root 连接...${NC}"
if mysql -u root -proot -e "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ root/root 连接成功${NC}"
    DB_USER="root"
    DB_PASS="root"
else
    echo -e "${RED}✗ root/root 连接失败${NC}"
    
    # 尝试seedance用户
    echo -e "${YELLOW}尝试使用 seedance/seedance123 连接...${NC}"
    if mysql -u seedance -pseedance123 -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ seedance/seedance123 连接成功${NC}"
        DB_USER="seedance"
        DB_PASS="seedance123"
    else
        echo -e "${RED}✗ seedance/seedance123 连接失败${NC}"
        echo ""
        echo -e "${YELLOW}请选择解决方案:${NC}"
        echo ""
        echo "方案1: 使用root用户（推荐用于测试）"
        echo "  修改 .env 文件中的数据库配置为:"
        echo "  DB_USER=root"
        echo "  DB_PASSWORD=root"
        echo ""
        echo "方案2: 创建seedance用户"
        echo "  运行以下SQL命令创建用户:"
        echo "  mysql -u root -proot -e \"CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';\""
        echo "  mysql -u root -proot -e \"GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';\""
        echo "  mysql -u root -proot -e \"FLUSH PRIVILEGES;\""
        echo ""
        read -p "请输入选择 (1 或 2): " choice
        
        if [[ "$choice" == "1" ]]; then
            DB_USER="root"
            DB_PASS="root"
            echo -e "${GREEN}已选择使用 root 用户${NC}"
        elif [[ "$choice" == "2" ]]; then
            echo -e "${YELLOW}正在创建seedance用户...${NC}"
            mysql -u root -proot -e "CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';" 2>/dev/null || true
            mysql -u root -proot -e "GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';" 2>/dev/null || true
            mysql -u root -proot -e "FLUSH PRIVILEGES;" 2>/dev/null || true
            
            if mysql -u seedance -pseedance123 -e "SELECT 1;" >/dev/null 2>&1; then
                echo -e "${GREEN}✓ seedance用户创建成功${NC}"
                DB_USER="seedance"
                DB_PASS="seedance123"
            else
                echo -e "${RED}✗ 用户创建失败，请使用root用户${NC}"
                exit 1
            fi
        else
            echo -e "${RED}无效选择${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${CYAN}3. 检查数据库是否存在${NC}"
if mysql -u "$DB_USER" -p"$DB_PASS" -e "USE seedance_db;" 2>/dev/null; then
    echo -e "${GREEN}✓ 数据库 seedance_db 存在${NC}"
else
    echo -e "${YELLOW}数据库 seedance_db 不存在，正在创建...${NC}"
    mysql -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS seedance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo -e "${GREEN}✓ 数据库创建成功${NC}"
fi

echo ""
echo -e "${CYAN}4. 检查数据表${NC}"
TABLE_COUNT=$(mysql -u "$DB_USER" -p"$DB_PASS" seedance_db -e "SHOW TABLES;" 2>/dev/null | wc -l)
if [[ $TABLE_COUNT -gt 0 ]]; then
    echo -e "${GREEN}✓ 数据库中有 $((TABLE_COUNT - 1)) 个表${NC}"
    echo ""
    echo -e "${CYAN}现有表:${NC}"
    mysql -u "$DB_USER" -p"$DB_PASS" seedance_db -e "SHOW TABLES;" 2>/dev/null | tail -n +2 | while read -r table; do
        echo "  - $table"
    done
else
    echo -e "${YELLOW}数据库中没有表，需要运行数据库初始化${NC}"
    echo ""
    if [[ -f "init_db.sql" ]]; then
        echo -e "${YELLOW}找到 init_db.sql，是否现在导入？(y/n)${NC}"
        read -r import_choice
        if [[ "$import_choice" == "y" ]]; then
            mysql -u "$DB_USER" -p"$DB_PASS" seedance_db < init_db.sql
            echo -e "${GREEN}✓ 数据库初始化完成${NC}"
        fi
    else
        echo -e "${RED}未找到 init_db.sql 文件${NC}"
    fi
fi

echo ""
echo -e "${CYAN}5. 更新 .env 文件${NC}"
ENV_FILE=".env"
if [[ -f "$ENV_FILE" ]]; then
    # 更新DB_USER
    sed -i "s/^DB_USER=.*/DB_USER=$DB_USER/" "$ENV_FILE"
    # 更新DB_PASSWORD
    sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASS/" "$ENV_FILE"
    echo -e "${GREEN}✓ .env 文件已更新${NC}"
    echo ""
    echo -e "${CYAN}当前配置:${NC}"
    grep "^DB_" "$ENV_FILE" | while read -r line; do
        echo "  $line"
    done
else
    echo -e "${RED}✗ .env 文件不存在${NC}"
fi

echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}  检测完成${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""
echo -e "${GREEN}现在可以重新运行任务执行器:${NC}"
echo -e "  ${YELLOW}./run-task-executor.sh once${NC}"
echo ""
