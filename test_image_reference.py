"""
测试即梦平台的@图片引用功能
用于验证是否支持多图引用生成视频
"""

from jimeng_api_client import JimengAPIClient
import json

# 您的sessionid
sessionid = "eccb32e0b3ccbd3464dc0cc90dbcdca4"

print("=" * 60)
print("即梦平台 @图片引用功能调研")
print("=" * 60)

# 您提供的图片ID列表
image_ids = [
    "e5402556-3ebe-4d87-b28f-30d4a2b65e32",  # 奶奶
    "c33045f1-8e4f-426a-a795-f7b2b2dc9200",  # 狐小九
    "f8321157-96b3-4000-8d6a-005bf49bf20b",  # 铁爪
    "33fa7f18-f404-4c1a-9ac4-996b3ce03204",  # 包子铺内
]

print("\n图片ID列表：")
for i, img_id in enumerate(image_ids, 1):
    print(f"  {i}. {img_id}")

print("\n" + "=" * 60)
print("调研问题：")
print("=" * 60)
print("""
1. 即梦平台的 @UUID 格式是否支持多图引用？
2. 这些UUID是即梦平台内部图片ID还是外部图片URI？
3. 视频生成API是否支持这种多图引用方式？
4. 如果支持，需要如何构造draft_content？
""")

print("\n建议的调研步骤：")
print("1. 在即梦网页端手动测试这个提示词")
print("2. 打开F12开发者工具，查看实际发送的请求")
print("3. 对比draft_content中material_list的结构")
print("4. 确认是否需要先上传图片获取URI")

print("\n" + "=" * 60)
print("注意事项：")
print("=" * 60)
print("""
- UUID格式看起来是即梦平台的内部图片ID
- 可能需要通过API先上传图片获取image_uri
- video_base_component中的material_list可能需要特殊构造
- 不同模型对多图引用的支持可能不同
""")

# 测试：尝试使用普通文生视频（不带@引用）
print("\n" + "=" * 60)
print("测试普通文生视频（验证2.0模型）")
print("=" * 60)

client = JimengAPIClient(sessionid=sessionid)

# 使用普通2.0模型（非VIP）
result = client.generate_text_to_video(
    prompt="赛璐璐风格动画，奶奶保护狐小九",
    model="s2.0",  # 普通2.0模型
    ratio="16:9",
    duration=4
)

print(f"\n测试结果：")
print(json.dumps(result, ensure_ascii=False, indent=2))
