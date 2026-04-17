# 即梦AI API 诊断报告

## 📊 问题分析

### 测试结果
- ✅ **SessionID有效**：API认证成功
- ✅ **提交成功**：`history_id: 34168772863756`
- ❌ **生成失败**：任务状态变为 30（失败）

### 失败详情

从API响应中提取的关键信息：

```json
{
  "status": 30,  // 失败状态
  "fail_code": "2036",
  "fail_msg": "GenerateFail",
  "fail_starling_message": "生成失败，本次不消耗积分",
  "model_info": {
    "model_name": "图片5.0 Lite",
    "model_req_key": "high_aes_general_v50"
  }
}
```

### 状态码说明

| 状态码 | 含义 |
|--------|------|
| 10 | 排队中 |
| 20 | 处理中 |
| 30 | **失败** ❌ |
| 40 | 已取消 |
| 50 | **完成** ✅ |

---

## 🔍 失败原因分析

### 可能的原因

1. **模型版本不匹配**
   - 请求使用的模型：`high_aes_general_v20:general_3.0`
   - 实际响应的模型：`high_aes_general_v50` (5.0 Lite)
   - **问题**：代码中请求的模型key可能不正确

2. **错误码 2036**
   - 这是即梦AI内部的错误码
   - 可能原因：
     - 模型参数不正确
     - 提示词违规
     - 账号权限问题
     - 模型服务异常

3. **请求参数问题**
   - 查看 `draft_content` 中的参数格式
   - 可能与官方API的最新要求不一致

---

## 💡 解决方案

### 方案1: 修改模型参数（推荐）

从响应中看到，实际使用的是 `图片5.0 Lite` 模型，我们需要调整代码中的模型配置。

**修改前：**
```python
model_req_key = f"high_aes_general_v20:general_{model}"
```

**修改后：**
```python
# 根据模型名称选择正确的key
model_map = {
    "2.0": "high_aes_general_v20",
    "2.1": "high_aes_general_v21",
    "3.0": "high_aes_general_v30",
    "4.0": "high_aes_general_v40",
    "5.0": "high_aes_general_v50"
}
model_req_key = model_map.get(model, "high_aes_general_v50")
```

### 方案2: 检查提示词

某些提示词可能触发审核导致失败，尝试使用更简单的提示词测试：
```python
prompt = "一只猫"  # 简单提示词
```

### 方案3: 在浏览器中手动测试

1. 打开 https://jimeng.jianying.com
2. 使用相同的提示词手动生成
3. 观察是否成功，以及使用的模型版本

---

## 🛠️ 需要修改的代码

### jimeng_api_client.py

#### 1. 修改模型映射

找到 `generate_text_to_image` 方法中的模型配置部分：

```python
# 约第120行
# 获取模型配置
model_req_key = f"high_aes_general_v20:general_{model}"  # 旧的
if model == "4.0":
    model_req_key = "high_aes_general_v40"
```

改为：

```python
# 新的模型映射
model_map = {
    "2.0": "high_aes_general_v20",
    "2.1": "high_aes_general_v21", 
    "3.0": "high_aes_general_v30",
    "4.0": "high_aes_general_v40",
    "5.0": "high_aes_general_v50"
}
model_req_key = model_map.get(model, "high_aes_general_v50")
```

#### 2. 增加失败重试机制

在轮询方法中增加失败后的详细错误输出。

---

## 📝 下一步行动

1. **立即测试**：修改模型参数后重新测试
2. **对比参考项目**：查看 `Comfyui_Free_Jimeng` 中使用的模型key
3. **抓包分析**：在浏览器中生成图片时，抓取实际的API请求参数
4. **联系客服**：如果问题持续，咨询即梦AI官方关于错误码2036的含义

---

## 🔧 临时解决方案

如果API调用持续失败，可以暂时使用浏览器自动化方案（Playwright）作为替代。

---

## 📞 需要帮助

请告诉我：
1. 你在浏览器中用同样的提示词能成功生成吗？
2. 你希望我帮你修改代码调整模型参数吗？
3. 还是需要我帮你实现浏览器自动化的备用方案？
