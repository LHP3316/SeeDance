# 即梦AI图片生成爬虫 - Playwright版本

这是一个基于 Playwright 的自动化爬虫程序，可以访问即梦AI网站，通过抖音扫码登录，并自动完成图片生成任务。支持定时执行功能。

## 为什么选择 Playwright？

相比 Selenium，Playwright 有以下优势：

✅ **更快** - 执行速度更快，性能更好  
✅ **更稳定** - 自动等待机制，减少超时错误  
✅ **更现代** - 原生支持异步编程  
✅ **更好的API** - 更简洁直观的API设计  
✅ **自动等待** - 智能等待元素加载完成  
✅ **多浏览器** - 支持 Chromium、Firefox、WebKit  

## 功能特性

- ✅ 抖音扫码登录
- ✅ Cookie保存和二次登录（无需重复扫码）
- ✅ Agent模式自动切换
- ✅ 图片生成参数配置（模型、比例）
- ✅ 多图上传和提示词引用
- ✅ 自动生成任务并保存结果
- ✅ **定时任务支持**（Cron表达式和间隔模式）
- ✅ 配置文件支持（YAML格式）

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

## 使用方法

### 基础使用

#### 首次登录（需要扫码）

```bash
python main.py
```

程序会打开浏览器，请使用抖音扫描二维码完成登录。登录成功后Cookie会自动保存。

#### 使用Cookie二次登录并生成图片

```bash
python main.py --prompt "一只可爱的猫咪在阳光下玩耍" --images cat1.jpg cat2.jpg
```

### 完整参数说明

```bash
python main.py [选项]

# 任务参数
  --prompt TEXT               图片生成提示词
  --images PATH [PATH ...]    参考图片路径（支持多张）
  --model TEXT                图片模型名称
  --ratio TEXT                图片比例，如 1:1, 16:9, 9:16（默认: 1:1）
  --output DIR                生成图片保存目录（默认: generated_images）

# 浏览器参数
  --headless                  无头模式运行浏览器（不显示界面）
  --force-login               强制重新登录（忽略已保存的Cookie）
  --cookie-file PATH          Cookie文件路径（默认: cookies.json）

# 定时任务参数
  --schedule TYPE             定时任务类型: cron 或 interval
  --cron EXPRESSION           Cron表达式，如 '0 */2 * * *' (每2小时)
  --interval MINUTES          间隔时间（分钟）
  --config FILE               从配置文件加载（YAML格式）
```

### 定时任务使用示例

#### 示例1: 每2小时执行一次

```bash
python main.py --prompt "美丽的日落风景" --schedule interval --interval 120
```

#### 示例2: 使用Cron表达式（每天早上9点执行）

```bash
python main.py --prompt "清晨的阳光" --schedule cron --cron "0 9 * * *"
```

#### 示例3: 工作日每4小时执行

```bash
python main.py --prompt "办公场景图片" --schedule cron --cron "0 */4 * * 1-5"
```

#### 示例4: 使用配置文件启动定时任务

```bash
# 先编辑配置文件
notepad config_schedule.yaml

# 使用配置文件启动
python main.py --config config_schedule.yaml
```

### 更多使用示例

**示例1: 生成单张图片**
```bash
python main.py --prompt "美丽的日落海滩风景"
```

**示例2: 使用参考图片生成**
```bash
python main.py --prompt "将这个风格应用到新的场景" --images style.jpg
```

**示例3: 多图参考生成 + 指定比例**
```bash
python main.py --prompt "结合这些元素创作" --images img1.jpg img2.jpg --ratio 16:9
```

**示例4: 无头模式运行（后台执行）**
```bash
python main.py --prompt "科幻城市夜景" --headless
```

**示例5: 强制重新登录**
```bash
python main.py --force-login
```

## 配置文件示例

### 基础配置 (config_example.yaml)

```yaml
# 图片生成配置
prompt: "一只可爱的猫咪在阳光下玩耍"
images:
  - "cat1.jpg"
  - "cat2.jpg"
model: ""
ratio: "1:1"
output: "generated_images"

# 浏览器配置
headless: false
force_login: false
cookie_file: "cookies.json"
```

### 定时任务配置 (config_schedule.yaml)

```yaml
# 图片生成配置
prompt: "美丽的日落海滩风景"
images: []
model: ""
ratio: "16:9"
output: "generated_images"

# 浏览器配置
headless: true
force_login: false
cookie_file: "cookies.json"

# 定时任务配置
schedule_type: "cron"
cron_expression: "0 */2 * * *"  # 每2小时执行
```

使用配置文件：

```bash
python main.py --config config_schedule.yaml
```

## Cron表达式说明

Cron表达式格式：`分 时 日 月 周`

常用示例：

| 表达式 | 说明 |
|--------|------|
| `0 */2 * * *` | 每2小时执行一次 |
| `0 9 * * *` | 每天早上9点执行 |
| `0 */4 * * 1-5` | 工作日每4小时执行 |
| `0 9,12,18 * * *` | 每天9点、12点、18点执行 |
| `*/30 * * * *` | 每30分钟执行一次 |
| `0 9-18 * * *` | 每天9点到18点，每小时执行 |

在线Cron表达式生成器：https://crontab.guru/

## 项目结构

```
seedance/
├── main.py                  # 主程序入口
├── browser_manager.py       # 浏览器管理和登录模块（Playwright）
├── image_generator.py       # 图片生成自动化模块（Playwright）
├── requirements.txt         # Python依赖
├── config_example.yaml      # 基础配置示例
├── config_schedule.yaml     # 定时任务配置示例
├── run.bat                  # Windows启动脚本
├── cookies.json             # 自动生成的Cookie文件
└── generated_images/        # 生成的图片保存目录
```

## Windows快捷启动

双击 `run.bat` 文件，会提供交互式菜单：

```
请选择运行模式:
1. 单次执行（首次登录需要扫码）
2. 定时任务（每2小时执行一次）
3. 自定义定时任务
```

## 注意事项

1. **首次使用**: 需要手动扫码登录，请确保抖音APP已安装
2. **Cookie有效期**: Cookie可能会过期，如果登录失败请使用 `--force-login` 重新登录
3. **页面结构**: 如果网站更新导致元素定位失败，可能需要调整选择器
4. **生成时间**: 图片生成可能需要几分钟，请耐心等待
5. **网络环境**: 确保网络畅通，能够访问即梦AI网站
6. **定时任务**: 使用无头模式（`--headless`）可以在后台运行

## 常见问题

**Q: Playwright和Selenium有什么区别？**  
A: Playwright更现代、更快、更稳定，原生支持异步编程，自动等待机制更好。

**Q: 定时任务如何在后台运行？**  
A: 使用 `--headless` 参数，浏览器不会显示界面，可以在后台运行。

**Q: 如何停止定时任务？**  
A: 按 `Ctrl+C` 即可停止定时任务。

**Q: 登录失败怎么办？**  
A: 使用 `--force-login` 参数强制重新登录，并确保网络连接正常。

**Q: 图片生成超时？**  
A: 可以在 `image_generator.py` 中调整 `timeout` 参数值，默认是300秒。

**Q: 如何查看生成的图片？**  
A: 生成的图片默认保存在 `generated_images` 目录中。

## 技术栈

- **Playwright**: 现代浏览器自动化框架
- **APScheduler**: Python定时任务调度库
- **PyYAML**: YAML配置文件解析
- **Python 3.7+**: 编程语言（需要异步支持）

## 许可证

本项目仅供学习交流使用。
