"""
测试多图引用视频生成功能
支持本地图片路径
"""

from jimeng_api_client import JimengAPIClient
import os

# 您的sessionid
client = JimengAPIClient(sessionid="eccb32e0b3ccbd3464dc0cc90dbcdca4")

print("=" * 60)
print("多图引用视频生成测试")
print("=" * 60)

# 使用桌面图片路径
# 注意：如果您在WSL中运行，需要使用/mnt/c/Users/...格式
# 如果您在Windows中运行，使用C:\\Users\\...格式
image_paths = [
    "/mnt/c/Users/Administrator/Desktop/狐奶奶.png",
    "/mnt/c/Users/Administrator/Desktop/狐小九.png",
    "/mnt/c/Users/Administrator/Desktop/铁爪（三视图）.png",
    "/mnt/c/Users/Administrator/Desktop/包子铺内景 (1).png"
]

# 检查文件是否存在
print("\n检查图片文件...")
for i, path in enumerate(image_paths, 1):
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"  {i}. {status} {path}")
    if not exists:
        print(f"     ⚠ 文件不存在，请修改为实际路径")

# 图片描述（对应每张图片）
image_descriptions = [
    "是奶奶",
    "是狐小九", 
    "是铁爪",
    "是包子铺内"
]

# 提示词（纯文本，不含@引用）
prompt = "赛璐璐风格动画，无字幕无配乐无标识，多景别运用，电影级运镜，焦段；场景：包子铺内，白天，铺内一片狼藉。冰刺飞向狐小九，奶奶从旁奋力冲出，挡在狐小九身前，狐小九站在奶奶身后。镜头：近景，奶奶一脸决然，奋力冲出，同时大喊：小九！镜头：中景，奶奶迅速挡在狐小九身前，张开双臂，无数冰刺迎面飞刺向奶奶"

print("\n" + "=" * 60)
print("配置信息：")
print("=" * 60)
print(f"提示词: {prompt}")
print(f"图片数量: {len(image_paths)}")
print(f"图片描述: {image_descriptions}")
print(f"模型: s2.0 (普通2.0)")
print(f"比例: 16:9")
print(f"时长: 4秒")

print("\n" + "=" * 60)
print("开始生成...")
print("=" * 60)

# 调用多图引用视频生成
result = client.generate_multi_image_to_video(
    image_paths=image_paths,
    prompt=prompt,
    image_descriptions=image_descriptions,
    model="s2.0",          # 普通2.0模型
    ratio="16:9",          # 16:9横屏
    duration=4             # 4秒
)

print("\n" + "=" * 60)
print("生成结果：")
print("=" * 60)

if result["success"]:
    print("✅ 视频生成成功！")
    print(f"视频URL: {result['url']}")
    
    # 下载视频
    if 'url' in result:
        saved_path = client.download_video(result["url"], save_dir="output_video")
        if saved_path:
            print(f"视频已保存到: {saved_path}")
else:
    print(f"❌ 视频生成失败: {result.get('error')}")

print("\n" + "=" * 60)
print("提示：")
print("=" * 60)
print("1. 如果图片路径不存在，请修改image_paths为您的实际路径")
print("2. 支持绝对路径和相对路径")
print("3. Windows路径使用 r'...' 格式，避免转义问题")
print("4. 例如: r'C:/Users/Administrator/Desktop/图片.png'")
print("5. 或者使用正斜杠: 'C:/Users/Administrator/Desktop/图片.png'")
