#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

EXECUTOR_LOG="$LOG_DIR/task_executor.log"
PID_FILE="$SCRIPT_DIR/task_executor.pid"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

is_running() {
  local pid="$1"
  kill -0 "$pid" >/dev/null 2>&1
}

cleanup_stale_pid() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && is_running "$pid"; then
      return 0
    fi
    rm -f "$pid_file"
  fi
  return 1
}

show_usage() {
  echo -e "${CYAN}=========================================${NC}"
  echo -e "${CYAN}  SeeDance 任务执行器${NC}"
  echo -e "${CYAN}=========================================${NC}"
  echo ""
  echo "用法:"
  echo "  $0 start              - 启动任务执行器（默认5分钟间隔）"
  echo "  $0 start <seconds>    - 启动任务执行器（自定义间隔）"
  echo "  $0 once               - 执行一次检测"
  echo "  $0 stop               - 停止任务执行器"
  echo "  $0 status             - 查看运行状态"
  echo "  $0 log                - 查看实时日志"
  echo ""
  echo "示例:"
  echo "  $0 start              # 每5分钟检测一次"
  echo "  $0 start 600          # 每10分钟检测一次"
  echo "  $0 start 60           # 每1分钟检测一次（测试）"
  echo "  $0 once               # 只执行一次"
  echo ""
}

start_executor() {
  local interval="${1:-300}"
  
  if cleanup_stale_pid "$PID_FILE"; then
    echo -e "${YELLOW}任务执行器已在运行 (PID: $(cat "$PID_FILE"))${NC}"
    return 1
  fi

  echo -e "${CYAN}=========================================${NC}"
  echo -e "${CYAN}  启动任务执行器${NC}"
  echo -e "${CYAN}=========================================${NC}"
  echo -e "检测间隔: ${GREEN}${interval}秒${NC}"
  echo -e "日志文件: ${GREEN}${EXECUTOR_LOG}${NC}"
  echo -e "输出目录: ${GREEN}${SCRIPT_DIR}/output${NC}"
  echo ""

  # 检查conda环境
  if [[ -z "${CONDA_DEFAULT_ENV:-}" ]] || [[ "${CONDA_DEFAULT_ENV}" != "video" ]]; then
    echo -e "${YELLOW}警告: 当前不在 video conda 环境中${NC}"
    echo -e "${YELLOW}请先运行: conda activate video${NC}"
    echo ""
  fi

  # 启动任务执行器
  nohup python3 task_executor.py --interval "$interval" >>"$EXECUTOR_LOG" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"

  sleep 2
  
  if ! is_running "$pid"; then
    echo -e "${RED}启动失败，请查看日志: ${EXECUTOR_LOG}${NC}"
    rm -f "$PID_FILE"
    return 1
  fi

  echo -e "${GREEN}✓ 任务执行器已启动 (PID: $pid)${NC}"
  echo ""
  echo -e "使用 ${YELLOW}$0 status${NC} 查看运行状态"
  echo -e "使用 ${YELLOW}$0 log${NC} 查看实时日志"
  echo -e "使用 ${YELLOW}$0 stop${NC} 停止执行器"
}

stop_executor() {
  if ! cleanup_stale_pid "$PID_FILE"; then
    echo -e "${YELLOW}任务执行器未运行${NC}"
    return 1
  fi

  local pid
  pid="$(cat "$PID_FILE")"
  
  echo -e "${YELLOW}正在停止任务执行器 (PID: $pid)...${NC}"
  kill "$pid" 2>/dev/null || true
  sleep 2
  
  # 如果还在运行，强制停止
  if is_running "$pid"; then
    echo -e "${YELLOW}强制停止...${NC}"
    kill -9 "$pid" 2>/dev/null || true
  fi

  rm -f "$PID_FILE"
  echo -e "${GREEN}✓ 任务执行器已停止${NC}"
}

show_status() {
  echo -e "${CYAN}=========================================${NC}"
  echo -e "${CYAN}  任务执行器状态${NC}"
  echo -e "${CYAN}=========================================${NC}"
  
  if cleanup_stale_pid "$PID_FILE"; then
    local pid
    pid="$(cat "$PID_FILE")"
    echo -e "状态: ${GREEN}运行中${NC}"
    echo -e "PID: ${GREEN}$pid${NC}"
    
    # 显示运行时间
    if command -v ps >/dev/null 2>&1; then
      local elapsed
      elapsed=$(ps -o etime= -p "$pid" 2>/dev/null || echo "未知")
      echo -e "运行时间: ${GREEN}$elapsed${NC}"
    fi
  else
    echo -e "状态: ${RED}未运行${NC}"
  fi
  
  echo ""
  
  # 显示最近的日志
  if [[ -f "$EXECUTOR_LOG" ]]; then
    echo -e "${CYAN}最近日志:${NC}"
    tail -n 5 "$EXECUTOR_LOG" | while IFS= read -r line; do
      echo "  $line"
    done
  fi
}

show_log() {
  if [[ ! -f "$EXECUTOR_LOG" ]]; then
    echo -e "${YELLOW}日志文件不存在${NC}"
    return 1
  fi

  echo -e "${CYAN}=========================================${NC}"
  echo -e "${CYAN}  任务执行器日志${NC}"
  echo -e "${CYAN}=========================================${NC}"
  echo -e "按 ${YELLOW}Ctrl+C${NC} 退出"
  echo ""
  
  tail -f "$EXECUTOR_LOG"
}

run_once() {
  echo -e "${CYAN}=========================================${NC}"
  echo -e "${CYAN}  执行单次任务检测${NC}"
  echo -e "${CYAN}=========================================${NC}"
  echo ""

  # 检查conda环境
  if [[ -z "${CONDA_DEFAULT_ENV:-}" ]] || [[ "${CONDA_DEFAULT_ENV}" != "video" ]]; then
    echo -e "${YELLOW}警告: 当前不在 video conda 环境中${NC}"
    echo -e "${YELLOW}请先运行: conda activate video${NC}"
    echo ""
  fi

  python3 task_executor.py --once
}

# 主逻辑
case "${1:-}" in
  start)
    start_executor "${2:-300}"
    ;;
  stop)
    stop_executor
    ;;
  status)
    show_status
    ;;
  log)
    show_log
    ;;
  once)
    run_once
    ;;
  *)
    show_usage
    exit 1
    ;;
esac
