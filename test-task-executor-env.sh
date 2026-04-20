#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}  任务执行器 - 环境检测${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""

PASS=0
FAIL=0

check() {
  local name="$1"
  local result="$2"
  
  if [[ "$result" == "0" ]]; then
    echo -e "  ${GREEN}✓${NC} $name"
    PASS=$((PASS + 1))
  else
    echo -e "  ${RED}✗${NC} $name"
    FAIL=$((FAIL + 1))
  fi
}

# 1. 检查Python
echo -e "${CYAN}1. 检查Python环境${NC}"
python3 --version >/dev/null 2>&1
check "Python3 已安装" "$?"

# 2. 检查conda环境
echo ""
echo -e "${CYAN}2. 检查Conda环境${NC}"
if [[ -n "${CONDA_DEFAULT_ENV:-}" ]]; then
  echo -e "  当前环境: ${YELLOW}${CONDA_DEFAULT_ENV}${NC}"
  if [[ "${CONDA_DEFAULT_ENV}" == "video" ]]; then
    check "Conda环境是 video" "0"
  else
    echo -e "  ${YELLOW}警告: 当前不在 video 环境中${NC}"
    echo -e "  ${YELLOW}请运行: conda activate video${NC}"
    check "Conda环境是 video" "1"
  fi
else
  echo -e "  ${YELLOW}警告: 未检测到conda环境${NC}"
  check "Conda环境已激活" "1"
fi

# 3. 检查Python依赖
echo ""
echo -e "${CYAN}3. 检查Python依赖${NC}"
python3 -c "import sqlalchemy" 2>/dev/null
check "sqlalchemy" "$?"

python3 -c "import pymysql" 2>/dev/null
check "pymysql" "$?"

python3 -c "import requests" 2>/dev/null
check "requests" "$?"

python3 -c "import pydantic_settings" 2>/dev/null
check "pydantic-settings" "$?"

python3 -c "from PIL import Image" 2>/dev/null
check "Pillow" "$?"

# 4. 检查数据库连接
echo ""
echo -e "${CYAN}4. 检查数据库连接${NC}"
python3 -c "
import sys
sys.path.insert(0, 'backend')
from config import settings
import pymysql
try:
    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'  错误: {e}')
    sys.exit(1)
" 2>&1
check "MySQL数据库连接" "$?"

# 5. 检查配置文件
echo ""
echo -e "${CYAN}5. 检查配置文件${NC}"
if [[ -f "backend/config.py" ]]; then
  check "backend/config.py 存在" "0"
else
  check "backend/config.py 存在" "1"
fi

# 检查SESSION_ID
python3 -c "
import sys
sys.path.insert(0, 'backend')
from config import settings
if settings.SESSION_ID:
    print(f'  SESSION_ID: {settings.SESSION_ID[:10]}...')
    sys.exit(0)
else:
    print('  警告: SESSION_ID 未配置')
    sys.exit(1)
" 2>&1
check "SESSION_ID 已配置" "$?"

# 6. 检查目录权限
echo ""
echo -e "${CYAN}6. 检查目录权限${NC}"
mkdir -p output logs 2>/dev/null
check "output/ 目录可创建" "$?"

touch logs/test.log 2>/dev/null && rm -f logs/test.log
check "logs/ 目录可写" "$?"

# 7. 检查任务执行器脚本
echo ""
echo -e "${CYAN}7. 检查任务执行器脚本${NC}"
if [[ -f "task_executor.py" ]]; then
  check "task_executor.py 存在" "0"
  
  # 尝试导入
  python3 -c "
import sys
sys.path.insert(0, 'backend')
sys.path.insert(0, '.')
from task_executor import TaskExecutor
print('  TaskExecutor类导入成功')
" 2>&1
  check "TaskExecutor 可导入" "$?"
else
  check "task_executor.py 存在" "1"
fi

if [[ -f "run-task-executor.sh" ]]; then
  check "run-task-executor.sh 存在" "0"
  
  if [[ -x "run-task-executor.sh" ]]; then
    check "run-task-executor.sh 可执行" "0"
  else
    echo -e "  ${YELLOW}提示: 运行 chmod +x run-task-executor.sh 添加执行权限${NC}"
    check "run-task-executor.sh 可执行" "1"
  fi
else
  check "run-task-executor.sh 存在" "1"
fi

# 总结
echo ""
echo -e "${CYAN}=========================================${NC}"
echo -e "${CYAN}  检测完成${NC}"
echo -e "${CYAN}=========================================${NC}"
echo ""
echo -e "  通过: ${GREEN}${PASS}${NC}"
echo -e "  失败: ${RED}${FAIL}${NC}"
echo ""

if [[ $FAIL -eq 0 ]]; then
  echo -e "${GREEN}✓ 所有检查通过！可以运行任务执行器了${NC}"
  echo ""
  echo -e "运行命令:"
  echo -e "  ${YELLOW}./run-task-executor.sh once${NC}  - 执行单次测试"
  echo -e "  ${YELLOW}./run-task-executor.sh start${NC} - 启动持续运行"
  echo ""
else
  echo -e "${RED}✗ 存在 ${FAIL} 项检查未通过，请先解决上述问题${NC}"
  echo ""
fi
