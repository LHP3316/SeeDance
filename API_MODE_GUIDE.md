# 即梦AI 图片生成 - 两种模式说明

## 📊 对比：浏览器自动化 vs 纯API调用

### 🌐 方式一：浏览器自动化 (Playwright)

**适用场景：**
- 需要模拟真实用户操作
- 需要查看网页界面
- 调试和演示用途

**优点：**
- ✅ 可以看到浏览器界面
- ✅ 模拟真实用户行为
- ✅ 适合调试

**缺点：**
- ❌ 速度慢（需要加载页面、等待元素）
- ❌ 不稳定（依赖页面结构，页面更新后可能失效）
- ❌ 资源占用大（需要启动浏览器）
- ❌ 需要处理各种异常情况（弹框、跳转等）

**相关文件：**
- `browser_manager.py` - 浏览器管理
- `image_generator.py` - 图片生成逻辑
- `main.py` - 主程序入口

**使用方法：**
```bash
python main.py --prompt "一只可爱的猫咪" --model 3.0 --ratio 1:1
```

---

### ⚡ 方式二：纯API调用 (推荐)

**适用场景：**
- 生产环境使用
- 需要高性能、高稳定性
- 批量生成图片
- 定时任务

**优点：**
- ✅ **速度快**（无需加载页面，直接调用API）
- ✅ **稳定**（不依赖页面结构，API变化少）
- ✅ **资源占用小**（不需要启动浏览器）
- ✅ **支持并发**（可以同时发起多个请求）
- ✅ **无需处理UI异常**（弹框、跳转等）

**缺点：**
- ❌ 无法看到网页界面
- ❌ 需要提取sessionid（一次性操作）

**相关文件：**
- `token_manager.py` - Token和签名管理
- `jimeng_api_client.py` - API客户端
- `test_api.py` - 测试示例

**使用方法：**

#### 步骤1: 获取sessionid（仅需一次）

1. 在浏览器中登录即梦AI: https://jimeng.jianying.com
2. 按 **F12** 打开开发者工具
3. 切换到 **Application** (或**存储**) 标签
4. 左侧找到 **Cookies** -> `https://jimeng.jianying.com`
5. 找到 **sessionid**，复制其值

#### 步骤2: 设置环境变量

**Windows:**
```powershell
$env:JIMENG_SESSIONID="你的sessionid值"
```

**Linux/Mac:**
```bash
export JIMENG_SESSIONID="你的sessionid值"
```

**或者直接修改代码** (在 test_api.py 中):
```python
sessionid = "你的sessionid值"
```

#### 步骤3: 运行

```bash
# 运行测试示例
python test_api.py

# 或在代码中使用
from jimeng_api_client import JimengAPIClient

client = JimengAPIClient(sessionid="你的sessionid")

# 文生图
result = client.generate_text_to_image(
    prompt="一只可爱的猫咪",
    model="3.0",
    ratio="1:1"
)

if result["success"]:
    # 下载图片
    client.download_images(result["urls"], save_dir="output")
```

---

## 🎯 推荐方案

### 开发/调试阶段
使用 **浏览器自动化** 方式，可以直观看到操作过程

### 生产环境/定时任务
使用 **纯API调用** 方式，性能更好、更稳定

---

## 📝 从浏览器自动化迁移到API调用

### 参数对比

| 功能 | Playwright方式 | API方式 |
|------|---------------|---------|
| 提示词 | `--prompt "文本"` | `prompt="文本"` |
| 模型 | `--model 3.0` | `model="3.0"` |
| 比例 | `--ratio 1:1` | `ratio="1:1"` |
| 图片上传 | 自动上传 | `image_paths=["path"]` |
| Cookie管理 | 自动保存 | 手动设置sessionid |
| 生成等待 | 自动轮询 | 自动轮询 |
| 图片下载 | 自动保存 | `download_images(urls)` |

### 代码示例对比

#### Playwright方式 (旧)
```python
# 需要启动浏览器、等待页面、点击按钮...
bot = JimengBot(config)
await bot.initialize()
await bot.generate_image(prompt="猫咪")
```

#### API方式 (新 - 推荐)
```python
# 直接调用API，3行代码搞定
client = JimengAPIClient(sessionid="xxx")
result = client.generate_text_to_image(prompt="猫咪")
client.download_images(result["urls"])
```

---

## 🔧 API调用完整示例

### 文生图
```python
from jimeng_api_client import JimengAPIClient

client = JimengAPIClient(sessionid="你的sessionid")

result = client.generate_text_to_image(
    prompt="一只可爱的猫咪，坐在窗台上，阳光照射进来",
    model="3.0",      # 可选: 2.0, 2.1, 3.0, 4.0
    ratio="1:1"       # 可选: 1:1, 16:9, 9:16, 4:3, 3:4
)

if result["success"]:
    print(f"生成成功！共 {len(result['urls'])} 张图片")
    # 下载图片
    saved_paths = client.download_images(result["urls"], save_dir="output")
    print(f"已保存到: {saved_paths}")
else:
    print(f"生成失败: {result['error']}")
```

### 图生图（支持多图）
```python
result = client.generate_image_to_image(
    image_paths=["image1.png", "image2.png"],  # 参考图片
    prompt="转换成水彩画风格",
    model="4.0",
    ratio="1:1"
)

if result["success"]:
    client.download_images(result["urls"], save_dir="output_i2i")
```

### 批量生成
```python
prompts = [
    "一只在花园里玩耍的小狗",
    "日落时分的海边风景",
    "未来城市的夜景"
]

for i, prompt in enumerate(prompts):
    print(f"\n生成第 {i+1} 张图片...")
    result = client.generate_text_to_image(
        prompt=prompt,
        model="3.0",
        ratio="16:9"
    )
    
    if result["success"]:
        client.download_images(result["urls"], save_dir=f"output/batch_{i+1}")
```

---

## ❓ 常见问题

### Q1: 如何获取sessionid？
A: 在浏览器登录即梦AI后，F12开发者工具 -> Application -> Cookies -> 复制sessionid

### Q2: sessionid会过期吗？
A: 会，通常有效期为60天。过期后需要重新获取

### Q3: API调用有限制吗？
A: 受账号积分限制，每个生成任务消耗1-2积分

### Q4: 可以并发调用吗？
A: 可以，但建议使用同一个sessionid串行调用，避免冲突

### Q5: 两种方式可以同时使用吗？
A: 可以，它们互不影响。推荐生产环境用API，调试用浏览器

---

## 📚 技术细节

### API签名机制
参考项目实现了完整的签名算法：
- `sign`: MD5签名，基于API路径和时间戳
- `msToken`: 107位随机字符串
- `a_bogus`: 32位随机字符串（用于反爬）
- `cookie`: 完整的Cookie构造

### 图片上传流程
1. 获取上传token (`/mweb/v1/get_upload_token`)
2. 申请上传地址 (AWS S3签名)
3. 上传图片文件
4. 确认上传完成

### 图片生成流程
1. 提交生成任务 (`/mweb/v1/aigc_draft/generate`)
2. 获取 `history_id` 和 `submit_id`
3. 轮询查询状态 (`/mweb/v1/get_history_by_ids`)
4. 状态为50时表示完成，提取图片URL
5. 下载图片到本地

---

## 🎉 总结

**纯API调用方式** 参考了成熟的开源项目 [Comfyui_Free_Jimeng](https://github.com/)，具有以下优势：

1. ✅ **不需要浏览器** - 无需Playwright/Selenium
2. ✅ **不需要截图** - 纯代码获取数据
3. ✅ **不需要元素定位** - 直接调用API
4. ✅ **更稳定** - 不受网页改版影响
5. ✅ **更快速** - 省去页面加载时间
6. ✅ **易维护** - 代码简洁，逻辑清晰

**建议立即切换到API调用方式！** 🚀
