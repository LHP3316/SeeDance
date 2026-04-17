"""
快速测试脚本 - 验证sessionid是否有效
"""

import os
import sys
import logging
from jimeng_api_client import JimengAPIClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 你的sessionid
SESSIONID = "68f94271cd6ed6554ad52735c91f47a6"


def test_sessionid():
    """测试sessionid是否有效"""
    print("=" * 60)
    print("测试即梦AI API连接")
    print("=" * 60)
    print(f"\nSessionID: {SESSIONID[:20]}...{SESSIONID[-10:]}")
    print(f"长度: {len(SESSIONID)} 字符")
    
    # 创建客户端
    print("\n[1/3] 创建API客户端...")
    try:
        client = JimengAPIClient(SESSIONID)
        print("✅ 客户端创建成功")
    except Exception as e:
        print(f"❌ 客户端创建失败: {e}")
        return False
    
    # 测试图生图
    print("\n[2/3] 测试图生图...")
    print("提示词: 我想要大橘猫，动画版本的")
    
    try:
        result = client.generate_image_to_image(
            image_paths=["/mnt/d/Project/seedance/test_output/jimeng_1776344411_0.png"],
            prompt="我想要大橘猫，动画版本的",
            model="4.0",
            ratio="1:1"
        )
        
        if result["success"]:
            print(f"✅ 图片生成成功！")
            print(f"   history_id: {result['history_id']}")
            print(f"   图片数量: {len(result['urls'])}")
            
            # 下载图片
            print("\n[3/3] 下载图片...")
            saved_paths = client.download_images(result['urls'], save_dir="test_output")
            
            if saved_paths:
                print(f"✅ 下载成功！共保存 {len(saved_paths)} 张图片")
                for path in saved_paths:
                    print(f"   - {os.path.abspath(path)}")
                
                print("\n" + "=" * 60)
                print("🎉 测试通过！API调用完全正常！")
                print("=" * 60)
                print("\n你可以开始使用了：")
                print("  - 文生图: client.generate_text_to_image(prompt='...')")
                print("  - 图生图: client.generate_image_to_image(image_paths=[...], prompt='...')")
                print("  - 下载图片: client.download_images(urls, save_dir='output')")
                return True
            else:
                print("❌ 图片下载失败")
                return False
        else:
            print(f"❌ 图片生成失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sessionid()
    
    if success:
        print("\n✅ 一切正常，可以开始使用了！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，请检查sessionid是否正确")
        sys.exit(1)
