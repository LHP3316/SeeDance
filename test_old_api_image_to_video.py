"""
测试即梦AI 旧接口图生视频（单图）
使用 /mweb/v1/generate_video 接口，ComfyUI 插件使用的接口
"""

import sys
import os
import json
import time

# 导入我们的 jimeng_api_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jimeng_api_client import JimengAPIClient

# 配置
SESSION_ID = "eccb32e0b3ccbd3464dc0cc90dbcdca4"

# 测试图片路径（WSL路径格式）
IMAGE_PATH = "/mnt/d/Project/seedance/uploads/materials/7161db6c-1158-48e8-a00f-45f795c50d4a.png"

def test_old_api_image_to_video():
    """测试旧接口图生视频（单图）"""
    print("=" * 80)
    print("即梦AI 旧接口图生视频测试（/mweb/v1/generate_video）")
    print("=" * 80)
    print(f"\n使用图片: {IMAGE_PATH}")
    print(f"提示词: 包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽")
    print(f"模型: s2.0 (使用 dreamina_ic_generate_video_model_vgfm_lite)")
    print(f"时长: 4秒")
    print(f"\n" + "=" * 80)
    
    # 创建客户端
    client = JimengAPIClient(sessionid=SESSION_ID)
    
    # 调用图生视频
    print(f"\n开始调用 generate_image_to_video...")
    print("=" * 80)
    
    result = client.generate_image_to_video(
        image_path=IMAGE_PATH,
        prompt="包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽",
        model="s2.0",
        duration=4
    )
    
    print("\n" + "=" * 80)
    print("调用结果:")
    print("=" * 80)
    
    if result.get("success"):
        print("✅ 视频生成成功！")
        print(f"\n视频信息:")
        print(f"  - history_id: {result.get('history_id')}")
        print(f"  - video_url: {result.get('video_url')}")
        print(f"  - duration: {result.get('duration')}秒")
        print(f"  - size: {result.get('size')} bytes")
        
        # 保存视频
        if result.get('video_url'):
            video_path = f"test_old_api_video_{int(time.time())}.mp4"
            print(f"\n正在下载视频到: {video_path}")
            
            import requests
            video_response = requests.get(result['video_url'])
            with open(video_path, 'wb') as f:
                f.write(video_response.content)
            
            print(f"✅ 视频已保存: {video_path}")
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
        print(f"\n完整响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_old_api_image_to_video()
