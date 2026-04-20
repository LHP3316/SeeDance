# 任务执行器快速开始

## 📋 已完成的工作

### 1. 核心脚本
- ✅ **task_executor.py** - 任务执行器主脚本（已修复导入路径）
  - 自动检测待执行任务
  - 调用即梦AI API生成图片/视频
  - 下载并保存结果到 output/ 目录
  - 更新任务状态到数据库
  - 详细日志记录（文件+控制台）

### 2. 管理脚本
- ✅ **run-task-executor.sh** - 任务执行器管理脚本
  - 启动/停止/查看状态/查看日志
  - 支持自定义检测间隔
  - 自动检查conda环境

### 3. 测试脚本
- ✅ **test-task-executor-env.sh** - 环境检测脚本
  - 检查Python环境和依赖
  - 检查数据库连接
  - 检查配置文件
  - 检查目录权限

### 4. 文档
- ✅ **TASK_EXECUTOR_GUIDE.md** - 详细使用文档
- ✅ **TASK_EXECUTOR_QUICKSTART.md** - 快速开始指南（本文件）

---

## 🚀 快速开始

### 步骤1：启动WSL Ubuntu环境

在Windows PowerShell中运行：
```powershell
D:\Project\start-ubuntu.ps1
```

这会自动启动MySQL和Redis服务。

### 步骤2：进入项目目录并激活环境

```bash
cd /mnt/d/Project/seedance
conda activate video
```

### 步骤3：运行环境检测（推荐）

```bash
chmod +x test-task-executor-env.sh
./test-task-executor-env.sh
```

这个脚本会检查：
- ✓ Python环境和conda
- ✓ 所有依赖包
- ✓ 数据库连接
- ✓ 配置文件
- ✓ 目录权限
- ✓ 脚本文件

如果所有检查通过，就可以继续了。

### 步骤4：安装依赖（如果环境检测失败）

```bash
pip install -r requirements.txt
```

### 步骤5：测试运行

```bash
# 添加执行权限
chmod +x run-task-executor.sh

# 执行单次测试
./run-task-executor.sh once
```

这会立即检测并执行所有到达时间的任务。

### 步骤6：启动持续运行

```bash
# 默认每5分钟检测一次
./run-task-executor.sh start

# 或者自定义间隔（如10分钟）
./run-task-executor.sh start 600
```

---

## 📊 日常管理

### 查看运行状态
```bash
./run-task-executor.sh status
```

### 查看实时日志
```bash
./run-task-executor.sh log
```

### 停止执行器
```bash
./run-task-executor.sh stop
```

---

## 📁 文件说明

### 脚本文件
```
task_executor.py          # 主程序
run-task-executor.sh      # 管理脚本
test-task-executor-env.sh # 环境检测
```

### 输出文件
```
output/                   # 生成的图片/视频保存目录
  ├── task1_风景图片_20240416_103015_0.png
  ├── task1_风景图片_20240416_103015_1.png
  └── task2_动画视频_20240416_103045.mp4

logs/                     # 日志目录
  ├── task_executor_20240416.log  # 今天的执行日志
  └── task_executor.log           # 管理脚本日志
```

---

## 🔍 日志示例

执行成功后，日志文件会包含：

```
============================================================
开始任务检测 - 2024-04-16 10:30:00
============================================================
查询到 1 个待执行任务
============================================================
开始执行任务 [ID:1] - 风景图片生成
任务类型: image
计划执行时间: 2024-04-16 10:00:00
============================================================
任务 [ID:1] 状态已更新为: running
开始执行图片任务 [ID:1] - 风景图片生成
  - 模型: 1.5_pro
  - 比例: 16:9
  - 提示词: 一幅美丽的风景画...
使用文生图模式
API调用成功，生成 4 张图片
正在下载图片: https://...
图片保存成功: /mnt/d/Project/seedance/output/task1_风景图片_20240416_103015_0.png
  ✓ 图片已保存: /mnt/d/Project/seedance/output/task1_风景图片_20240416_103015_0.png
任务 [ID:1] 状态已更新为: completed
✓ 任务 [ID:1] 执行成功
执行日志已保存 [Task:1, Execution:5]
------------------------------------------------------------
任务执行完成 [ID:1]
  - 状态: 成功
  - 耗时: 45.23秒
  - 保存文件: ['/mnt/d/Project/seedance/output/task1_风景图片_20240416_103015_0.png', ...]
------------------------------------------------------------
```

---

## ⚙️ 配置说明

### 环境变量（.env文件）

确保 `.env` 文件中包含：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=seedance
DB_PASSWORD=seedance123
DB_NAME=seedance_db

# 即梦API配置（重要！）
SESSION_ID=your_session_id_here
```

### 任务创建

在前端创建任务时：
1. 填写任务名称、提示词
2. 选择模型和比例
3. **设置执行时间**（scheduled_time）- 这是关键！
4. 提交任务

当到达执行时间后，任务执行器会自动检测并执行。

---

## ❓ 常见问题

### Q1: 任务没有被执行？

检查：
```bash
# 1. 查看任务状态（数据库）
mysql -u seedance -pseedance123 seedance_db -e "SELECT id, name, status, scheduled_time FROM tasks WHERE is_deleted=0 ORDER BY created_at DESC LIMIT 5;"

# 2. 查看执行日志
tail -f logs/task_executor_20240416.log

# 3. 确认执行器在运行
./run-task-executor.sh status
```

### Q2: API调用失败？

检查：
- SESSION_ID是否正确配置
- 网络连接是否正常
- API额度是否充足

### Q3: 找不到模块？

```bash
# 确保在conda video环境中
conda activate video

# 重新安装依赖
pip install -r requirements.txt
```

### Q4: 路径错误？

在WSL Ubuntu中，Windows路径 `D:\Project\seedance` 对应 `/mnt/d/Project/seedance`

```bash
# ✓ 正确
cd /mnt/d/Project/seedance

# ✗ 错误
cd /d/Project/seedance
```

---

## 🎯 下一步

1. **测试运行** - 先创建一个测试任务，scheduled_time设为当前时间之前
2. **执行单次检测** - `./run-task-executor.sh once`
3. **查看结果** - 检查output目录和日志文件
4. **启动持续运行** - `./run-task-executor.sh start`

---

## 📖 更多文档

详细文档请查看：[TASK_EXECUTOR_GUIDE.md](TASK_EXECUTOR_GUIDE.md)
