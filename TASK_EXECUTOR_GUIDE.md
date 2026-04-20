# 任务执行器使用说明

## 功能说明

任务执行器（task_executor.py）是一个自动化执行定时任务的脚本，主要功能包括：

1. **定时检测任务** - 检测任务列表中到达执行时间的任务
2. **调用API执行** - 调用即梦AI API生成图片/视频
3. **下载保存结果** - 自动下载生成的图片/视频到本地
4. **更新任务状态** - 更新数据库中的任务状态
5. **详细日志记录** - 记录执行时间、状态、文件名、API响应等

## 使用方法

### 环境准备

**在Windows中启动WSL Ubuntu：**

```powershell
# 1. 启动Ubuntu环境（会自动启动MySQL和Redis）
D:\Project\start-ubuntu.ps1
```

**在WSL Ubuntu中：**

```bash
# 2. 进入项目目录
cd /mnt/d/Project/seedance

# 3. 激活conda环境
conda activate video
```

### 方式一：使用启动脚本（推荐）

```bash
# 启动任务执行器（默认5分钟间隔）
./run-task-executor.sh start

# 自定义检测间隔（如10分钟）
./run-task-executor.sh start 600

# 执行单次检测
./run-task-executor.sh once

# 查看运行状态
./run-task-executor.sh status

# 查看实时日志
./run-task-executor.sh log

# 停止执行器
./run-task-executor.sh stop
```

### 方式二：直接运行Python脚本

#### 1. 单次执行（测试用）

```bash
conda activate video
cd /mnt/d/Project/seedance
python task_executor.py --once
```

执行一次任务检测，立即退出。适合测试和调试。

#### 2. 持续运行（生产用）

```bash
conda activate video
cd /mnt/d/Project/seedance
python task_executor.py
```

持续运行，默认每5分钟检测一次待执行任务。

#### 3. 自定义检测间隔

```bash
# 每10分钟检测一次
python task_executor.py --interval 600

# 每1分钟检测一次（测试用）
python task_executor.py --interval 60
```

## 日志文件

### 1. 执行日志文件

位置：`logs/task_executor_YYYYMMDD.log`

日志格式（详细）：
```
2024-04-16 10:30:15,123 - TaskExecutor - INFO - [execute_task:395] - 开始执行任务 [ID:1] - 风景图片生成
```

包含信息：
- 执行时间（精确到毫秒）
- 日志级别（DEBUG/INFO/WARNING/ERROR）
- 函数名和行号
- 详细执行信息

### 2. 控制台日志

简洁格式，实时显示执行状态：
```
2024-04-16 10:30:15,123 - INFO - 开始执行任务 [ID:1] - 风景图片生成
```

## 输出文件

### 图片保存位置

目录：`output/`

文件名格式：
```
task{任务ID}_{任务名称}_{时间戳}_{图片索引}.png
```

示例：
```
task1_风景图片生成_20240416_103015_0.png
task1_风景图片生成_20240416_103015_1.png
```

### 视频保存位置

目录：`output/`

文件名格式：
```
task{任务ID}_{任务名称}_{时间戳}.mp4
```

示例：
```
task2_动画视频_20240416_103045.mp4
```

## 任务执行流程

```
1. 检测待执行任务
   ↓
2. 查询条件：
   - status = 'pending'
   - scheduled_time <= now
   - is_deleted = false
   ↓
3. 更新任务状态为 'running'
   ↓
4. 调用API执行任务
   - 图片任务：generate_text_to_image()
   - 视频任务：generate_text_to_video()
   ↓
5. 下载生成结果
   - 图片：保存到 output/ 目录
   - 视频：保存到 output/ 目录
   ↓
6. 更新任务状态
   - 成功：'completed'
   - 失败：'failed'
   ↓
7. 保存执行日志
   - 数据库：task_executions 表
   - 文件：logs/task_executor_YYYYMMDD.log
```

## 数据库记录

### 任务状态更新

- `status` - 任务状态（pending/running/completed/failed）
- `last_run_time` - 最后执行时间
- `run_count` - 执行次数
- `error_message` - 错误信息（失败时）

### 执行日志记录

表：`task_executions`

字段：
- `task_id` - 任务ID
- `status` - 执行状态（success/failed）
- `started_at` - 开始时间
- `finished_at` - 结束时间
- `duration_seconds` - 耗时（秒）
- `history_id` - API返回的history_id
- `error_message` - 错误信息

## 日志内容示例

```
============================================================
开始任务检测 - 2024-04-16 10:30:00
============================================================
查询到 2 个待执行任务
============================================================
开始执行任务 [ID:1] - 风景图片生成
任务类型: image
计划执行时间: 2024-04-16 10:00:00
============================================================
任务 [ID:1] 状态已更新为: running
开始执行图片任务 [ID:1] - 风景图片生成
  - 模型: 1.5_pro
  - 比例: 16:9
  - 提示词: 一幅美丽的风景画，有山有水...
使用文生图模式
API调用成功，生成 4 张图片
正在下载图片: https://...
图片保存成功: D:\Project\seedance\output\task1_风景图片生成_20240416_103015_0.png
  ✓ 图片已保存: D:\Project\seedance\output\task1_风景图片生成_20240416_103015_0.png
正在下载图片: https://...
图片保存成功: D:\Project\seedance\output\task1_风景图片生成_20240416_103015_1.png
  ✓ 图片已保存: D:\Project\seedance\output\task1_风景图片生成_20240416_103015_1.png
任务 [ID:1] 状态已更新为: completed
✓ 任务 [ID:1] 执行成功
执行日志已保存 [Task:1, Execution:5]
------------------------------------------------------------
任务执行完成 [ID:1]
  - 状态: 成功
  - 耗时: 45.23秒
  - 保存文件: ['D:\\Project\\seedance\\output\\task1_风景图片生成_20240416_103015_0.png', 'D:\\Project\\seedance\\output\\task1_风景图片生成_20240416_103015_1.png']
------------------------------------------------------------
```

## 配置说明

### 依赖安装

**首次运行前，请确保已安装所需依赖：**

```bash
# 激活conda环境
conda activate video

# 安装依赖
cd /mnt/d/Project/seedance
pip install -r requirements.txt
```

所需依赖包括：
- `sqlalchemy` - 数据库ORM
- `pymysql` - MySQL驱动
- `requests` - HTTP请求
- `pydantic-settings` - 配置管理
- 等其他依赖...

### 环境变量（.env文件）

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=seedance
DB_PASSWORD=seedance123
DB_NAME=seedance_db

# 即梦API配置
SESSION_ID=your_session_id_here

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
```

### 代码配置

在 [backend/config.py](file:///d:/Project/seedance/backend/config.py) 中：

```python
class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "seedance"
    DB_PASSWORD: str = "seedance123"
    DB_NAME: str = "seedance_db"
    SESSION_ID: Optional[str] = None  # 即梦API的session_id
    ...
```

## 常见问题

### 1. 模块导入错误

**错误信息：** `ModuleNotFoundError: No module named 'xxx'`

**解决方法：**
```bash
# 确保在conda video环境中
conda activate video

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 任务未执行

检查：
- 任务状态是否为 `pending`
- `scheduled_time` 是否已到达
- 任务是否被删除（`is_deleted = false`）

### 3. API调用失败

检查：
- `SESSION_ID` 是否正确配置
- 网络连接是否正常
- API额度是否充足

查看日志文件获取详细错误信息。

### 4. 文件未下载

检查：
- `output/` 目录是否存在且有写权限
- 网络连接是否正常
- 图片/视频URL是否有效

### 5. 数据库连接失败

检查：
- 数据库服务是否运行
- 数据库配置是否正确
- 数据库用户权限是否足够

### 6. 启动脚本权限问题

**错误信息：** `Permission denied`

**解决方法：**
```bash
# 添加执行权限
chmod +x run-task-executor.sh
```

### 7. 路径问题

**重要：** 在WSL Ubuntu中，Windows路径 `D:\Project\seedance` 对应的是 `/mnt/d/Project/seedance`

```bash
# ✓ 正确
cd /mnt/d/Project/seedance

# ✗ 错误（这个路径不存在）
cd /d/Project/seedance
```

按 `Ctrl+C` 即可安全停止持续运行的任务执行器。

```
^C
收到停止信号，任务执行器已退出
```

## 最佳实践

1. **生产环境** - 使用 `--interval 300`（5分钟间隔）
2. **测试环境** - 使用 `--once` 或 `--interval 60`
3. **日志管理** - 定期清理旧的日志文件（`logs/` 目录）
4. **文件管理** - 定期备份或清理生成的文件（`output/` 目录）
5. **监控** - 定期检查日志文件，确保任务正常执行

## 注意事项

1. 脚本需要在项目根目录运行：`cd d:\Project\seedance`
2. 确保已安装所有依赖：`pip install -r requirements.txt`
3. 确保 `.env` 文件配置正确
4. 确保数据库服务正常运行
5. 确保有可用的API额度

## 相关文件

- 主脚本：[task_executor.py](file:///d:/Project/seedance/task_executor.py)
- API客户端：[jimeng_api_client.py](file:///d:/Project/seedance/jimeng_api_client.py)
- 配置文件：[backend/config.py](file:///d:/Project/seedance/backend/config.py)
- 任务模型：[backend/models/task.py](file:///d:/Project/seedance/backend/models/task.py)
- 执行日志模型：[backend/models/task_execution.py](file:///d:/Project/seedance/backend/models/task_execution.py)
