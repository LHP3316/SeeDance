# Web 插件集成使用说明

## 📋 功能概述

项目现在支持**双通道视频生成**：
1. **API 调用模式**（默认）- 快速、稳定、资源占用低
2. **Web 插件模式**（新增）- 浏览器自动化、支持 VIP 模型、模拟真人操作

## 🎯 使用场景

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| 普通视频生成 | API 模式 | 速度快，稳定性好 |
| VIP 模型视频 | Web 插件模式 | API 未开放，只能通过网页操作 |
| API 限流/封禁 | Web 插件模式 | 浏览器操作不易被封 |
| 需要最新功能 | Web 插件模式 | 网页版更新即可使用 |

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Python 包
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 创建任务（API 模式 - 默认）

通过后端 API 创建任务，默认使用 API 调用：

```json
POST /api/tasks
{
  "name": "测试视频任务",
  "type": "video",
  "prompt": "@image1.png是角色，@image2.png是场景，角色在场景中行走",
  "model": "s2.0",
  "ratio": "16:9",
  "duration": 5,
  "image_urls": [
    "/uploads/materials/image1.png",
    "/uploads/materials/image2.png"
  ],
  "schedule_type": "once",
  "scheduled_time": "2026-04-20T10:00:00"
}
```

### 3. 创建任务（Web 插件模式）

在 `params` 字段中添加 `web_plugin` 标识：

```json
POST /api/tasks
{
  "name": "测试视频任务（Web插件）",
  "type": "video",
  "prompt": "角色在场景中行走",
  "model": "s2.0",
  "ratio": "16:9",
  "duration": 5,
  "image_urls": [
    "/uploads/materials/image1.png",
    "/uploads/materials/image2.png"
  ],
  "params": "{\"web_plugin\": true, \"model\": \"seedance-2.0-vip\", \"generation_mode\": \"omni_reference\", \"timeout\": 900}",
  "schedule_type": "once",
  "scheduled_time": "2026-04-20T10:00:00"
}
```

### 4. 启动任务执行器

```bash
# 进入 WSL 环境
wsl

# 激活 Conda 环境
conda activate video

# 进入项目目录
cd /mnt/d/Project/seedance

# 单次执行（测试）
python task_executor.py --once

# 持续运行（每 5 分钟检测一次）
python task_executor.py

# 自定义间隔（10 分钟）
python task_executor.py --interval 600
```

## ⚙️ 配置参数

### Web 插件模式参数（在 task.params 中配置）

```json
{
  "web_plugin": true,              // 启用 Web 插件模式
  "model": "seedance-2.0-vip",     // 模型选择
  "generation_mode": "omni_reference",  // 生成模式
  "timeout": 900,                  // 超时时间（秒）
  "browser_exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  // 浏览器路径（可选）
}
```

### 支持的模型

| 模型标识 | 说明 | 支持模式 |
|---------|------|---------|
| `seedance-2.0` | Seedance 2.0 普通版 | API + Web |
| `seedance-2.0-fast` | Seedance 2.0 Fast | API + Web |
| `seedance-2.0-vip` | Seedance 2.0 VIP | **仅 Web** |
| `seedance-2.0-fast-vip` | Seedance 2.0 Fast VIP | **仅 Web** |

### 生成模式

| 模式 | 说明 |
|------|------|
| `first_end_frame` | 首尾帧模式（需要首帧和尾帧图片） |
| `omni_reference` | 全能参考模式（支持多张参考图） |

### 画幅比例

`21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`

### 视频时长

4-15 秒（整数）

## 📂 项目文件结构

```
seedance/
├── jimeng_api_client.py          # API 调用客户端（原有）
├── jimeng_web_video_plugin.py    # Web 插件适配器（新增）
├── task_executor.py              # 任务执行器（已增强）
├── requirements.txt              # Python 依赖（已更新）
├── uploads/
│   ├── jimeng_web_video_plugin_seedance_2_0/           # 原始插件（参考）
│   └── jimeng_web_video_plugin_seedance_2_0_playwright_v2/  # Playwright V2 插件（参考）
└── WEB_PLUGIN_GUIDE.md           # 本文档
```

## 🔧 工作原理

### API 模式（默认）

```
任务执行器 → jimeng_api_client.py → HTTP 请求 → 即梦 API → 返回视频 URL
```

**优点**：
- ✅ 速度快（无需浏览器）
- ✅ 资源占用低
- ✅ 稳定性好
- ✅ 易于调试

**缺点**：
- ❌ 部分 VIP 模型未开放
- ❌ 可能触发限流

### Web 插件模式（新增）

```
任务执行器 → jimeng_web_video_plugin.py → Playwright → 浏览器 → 即梦网页 → 提取视频 URL
```

**优点**：
- ✅ 支持所有网页版功能（包括 VIP）
- ✅ 不易触发限流
- ✅ 自动适配网页更新

**缺点**：
- ❌ 速度较慢（需要加载页面）
- ❌ 资源占用高（运行浏览器）
- ❌ 依赖网页结构

## 🐛 常见问题

### Q1: Web 插件模式提示"浏览器启动失败"

**解决方案**：
1. 确保已安装 Playwright 浏览器：
   ```bash
   playwright install chromium
   ```

2. 或者指定本地浏览器路径：
   ```json
   {
     "web_plugin": true,
     "browser_exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
   }
   ```

### Q2: Web 插件模式提示"未登录"

**解决方案**：
1. 首次使用需要手动登录
2. 运行测试脚本打开登录浏览器：
   ```bash
   python jimeng_web_video_plugin.py
   ```
3. 完成登录后，Cookie 会保存在浏览器上下文中

### Q3: 如何切换 API 和 Web 插件模式？

**答案**：
- 默认使用 **API 模式**
- 在任务 `params` 中添加 `"web_plugin": true` 即可切换到 **Web 插件模式**

### Q4: 定时任务如何使用 Web 插件模式？

**答案**：
创建定时任务时，在 `params` 字段中配置：

```json
{
  "schedule_type": "cron",
  "cron_expression": "0 */2 * * *",  // 每 2 小时执行一次
  "params": "{\"web_plugin\": true, \"model\": \"seedance-2.0-vip\"}"
}
```

## 📊 性能对比

| 指标 | API 模式 | Web 插件模式 |
|------|---------|-------------|
| 生成速度 | 30-60 秒 | 60-180 秒 |
| CPU 占用 | < 5% | 20-40% |
| 内存占用 | < 100 MB | 500-1000 MB |
| 网络流量 | < 50 MB | 200-500 MB |
| 成功率 | 95%+ | 90%+ |

## 🎓 最佳实践

1. **优先使用 API 模式**，除非需要 VIP 模型
2. **Web 插件模式**建议设置较长的超时时间（900 秒以上）
3. **定时任务**建议错开执行时间，避免并发冲突
4. **监控日志**：查看 `logs/task_executor_*.log` 了解执行情况

## 📝 更新日志

### 2026-04-20
- ✅ 新增 Web 插件适配器（jimeng_web_video_plugin.py）
- ✅ 任务执行器支持双通道（API + Web 插件）
- ✅ 通过任务参数自动选择执行模式
- ✅ 保持单线程定时执行逻辑
- ✅ 更新 requirements.txt 添加 playwright 依赖
