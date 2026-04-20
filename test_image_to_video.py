"""
测试即梦AI图生视频接口
对比旧接口 (/mweb/v1/generate_video) 和新接口 (/mweb/v1/aigc_draft/generate)
"""

import sys
import os
import json
import time
import requests
from PIL import Image

# 导入我们的 jimeng_api_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jimeng_api_client import JimengAPIClient

# 配置
SESSION_ID = "eccb32e0b3ccbd3464dc0cc90dbcdca4"

# 测试图片路径（WSL路径格式）
TEST_IMAGE_PATH1 = "/mnt/d/Project/seedance/uploads/materials/7161db6c-1158-48e8-a00f-45f795c50d4a.png"  # 狐奶奶
TEST_IMAGE_PATH2 = "/mnt/d/Project/seedance/uploads/materials/bdc3e640-097b-418e-b7b4-14008f27bd8b.png"  # 包子铺内

# 提示词
TEST_PROMPT = "包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽"

# 下载目录（WSL路径格式）
DOWNLOAD_DIR = "/mnt/d/Project/seedance/output/videos"


def download_video(video_url, save_path):
    """下载视频文件"""
    print(f"\n开始下载视频...")
    print(f"  URL: {video_url}")
    print(f"  保存路径: {save_path}")
    
    try:
        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 显示进度
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r  下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='', flush=True)
        
        print(f"\n  ✓ 下载完成！文件大小: {downloaded / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"\n  ✗ 下载失败: {e}")
        return False


def extract_video_url(history_data):
    """从 history_data 中提取视频URL（多路径尝试）"""
    video_url = None
    
    # 方式1：从 resources 提取（最可靠）
    resources = history_data.get("resources", [])
    for resource in resources:
        if resource.get("type") == "video":
            video_url = resource.get("video_info", {}).get("video_url")
            if video_url:
                return video_url
    
    # 方式2：从 item_list 提取
    item_list = history_data.get("item_list", [])
    for item in item_list:
        # 尝试 video 字段
        video = item.get("video", {})
        if video and video.get("video_url"):
            return video["video_url"]
        
        # 尝试 video.transcoded_video
        if video and "transcoded_video" in video:
            transcoded = video["transcoded_video"]
            if isinstance(transcoded, dict):
                # 遍历所有分辨率（360p, 720p等）
                for quality, info in transcoded.items():
                    if isinstance(info, dict) and info.get("video_url"):
                        print(f"  ✓ 从 video.transcoded_video.{quality}.video_url 找到")
                        return info["video_url"]
        
        # 尝试 common_attr.item_urls
        common_attr = item.get("common_attr", {})
        item_urls = common_attr.get("item_urls", [])
        if item_urls and item_urls[0] and item_urls[0] != "":
            return item_urls[0]
    
    # 方式3：从 pre_gen_item_ids 查找
    pre_gen_item_ids = history_data.get("pre_gen_item_ids", [])
    if pre_gen_item_ids:
        # 遍历 item_list 查找匹配的 ID
        for item in item_list:
            common_attr = item.get("common_attr", {})
            item_id = common_attr.get("id")
            if item_id in pre_gen_item_ids:
                # 尝试 common_attr.item_urls
                item_urls = common_attr.get("item_urls", [])
                if item_urls and item_urls[0] and item_urls[0] != "":
                    return item_urls[0]
                
                # 尝试 video 字段
                video = item.get("video", {})
                if video and video.get("video_url"):
                    return video["video_url"]
                
                # 尝试 video.transcoded_video
                if "transcoded_video" in video:
                    transcoded = video["transcoded_video"]
                    if isinstance(transcoded, dict):
                        for quality, info in transcoded.items():
                            if isinstance(info, dict) and info.get("video_url"):
                                return info["video_url"]
    
    return None


def test_old_api_single_image():
    """测试旧接口（单图生视频）"""
    print("\n" + "="*80)
    print("测试1：旧接口 /mweb/v1/generate_video（单图生视频）")
    print("="*80)
    
    client = JimengAPIClient(sessionid=SESSION_ID)
    
    # 检查图片是否存在
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ 测试图片不存在: {TEST_IMAGE_PATH}")
        return
    
    print(f"\n使用图片: {TEST_IMAGE_PATH}")
    print(f"提示词: {TEST_PROMPT}")
    print(f"模型: s2.0")
    
    # 使用旧接口的单图生视频方法
    # 注意：jimeng_api_client.py 中可能没有直接暴露这个接口
    # 我们需要手动构造请求
    
    try:
        # 1. 上传图片
        print("\n[1/4] 上传图片...")
        upload_token = client.token_manager.get_upload_token()
        
        # 2. 申请上传
        file_size = os.path.getsize(TEST_IMAGE_PATH)
        apply_url = f"https://imagex.bytedanceapi.com/"
        apply_params = {
            "Action": "ApplyImageUpload",
            "FileSize": str(file_size),
            "ServiceId": upload_token['space_name'],
            "Version": "2018-08-01"
        }
        
        print("  申请上传...")
        # 这里需要实现完整的上传逻辑（参考 ComfyUI 插件）
        # 为了简化，我们直接使用 client 的上传图片方法
        
        # 3. 调用生成接口
        print("\n[2/4] 调用生成接口...")
        
        # 构造请求（参考 ComfyUI 插件的 _generate_video 方法）
        generate_url = "https://jimeng.jianying.com/mweb/v1/generate_video"
        
        token_info = client.token_manager.get_token('/mweb/v1/generate_video')
        
        # 构造 babi_param
        babi_param = {
            "scenario": "image_video_generation",
            "feature_key": "image_to_video",
            "feature_entrance": "to_video",
            "feature_entrance_detail": "to_image-text_to_video"
        }
        
        params = {
            "aid": "513695",
            "babi_param": json.dumps(babi_param),
            "device_platform": "web",
            "region": "CN",
            "web_id": client.token_manager.web_id,
            "msToken": token_info.get("msToken", ""),
            "a_bogus": token_info.get("a_bogus", "")
        }
        
        # 注意：这里需要图片上传后的 URI
        # 为了测试，我们假设已经有了 image_uri
        print("  ⚠️  需要完整的图片上传流程，这里跳过")
        print("  💡 建议直接测试新接口（多图）")
        
    except Exception as e:
        print(f"❌ 旧接口测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_new_api_multi_image_with_polling():
    """测试新接口（多图生视频）- 带轮询和下载"""
    print("\n" + "="*80)
    print("测试2：新接口 /mweb/v1/aigc_draft/generate（多图生视频）")
    print("="*80)
    
    client = JimengAPIClient(sessionid=SESSION_ID)
    
    # 检查图片是否存在
    if not os.path.exists(TEST_IMAGE_PATH1) or not os.path.exists(TEST_IMAGE_PATH2):
        print(f"❌ 测试图片不存在")
        print(f"  图片1（狐奶奶）: {TEST_IMAGE_PATH1}")
        print(f"  图片2（包子铺内）: {TEST_IMAGE_PATH2}")
        return
    
    # 构造原始 prompt（包含 @引用）
    original_prompt = "@7161db6c-1158-48e8-a00f-45f795c50d4a.png是狐奶奶，@bdc3e640-097b-418e-b7b4-14008f27bd8b.png是包子铺内，包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽"
    
    print(f"\n使用图片:")
    print(f"  图片1（狐奶奶）: {TEST_IMAGE_PATH1}")
    print(f"  图片2（包子铺内）: {TEST_IMAGE_PATH2}")
    print(f"\n原始提示词: {original_prompt}")
    print(f"模型: s2.0 (Seedance 2.0 普通版)")
    print(f"比例: 16:9")
    print(f"时长: 4秒")
    
    try:
        print("\n" + "="*80)
        print("开始调用 generate_multi_image_to_video...")
        print("="*80)
        
        # 调用多图视频生成
        result = client.generate_multi_image_to_video(
            image_paths=[TEST_IMAGE_PATH1, TEST_IMAGE_PATH2],
            prompt=original_prompt,  # 包含 @引用的原始提示词
            model="s2.0",  # Seedance 2.0 普通版
            ratio="16:9",
            duration=4
        )
        
        print("\n" + "="*80)
        print("调用结果:")
        print("="*80)
        
        if result.get("success"):
            print("✅ 视频生成成功！")
            print(f"history_id: {result.get('history_id')}")
            print(f"video_url: {result.get('url')}")
            
            # 下载视频
            video_url = result.get('url')
            if video_url:
                timestamp = int(time.time())
                filename = f"video_{result.get('history_id')}_{timestamp}.mp4"
                save_path = os.path.join(DOWNLOAD_DIR, filename)
                
                success = download_video(video_url, save_path)
                
                if success:
                    print(f"\n✅ 视频下载成功！")
                    print(f"  文件路径: {save_path}")
                else:
                    print(f"\n❌ 视频下载失败")
        else:
            print(f"❌ 视频生成失败: {result.get('error')}")
            print(f"\n完整响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 新接口测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*80)
    print("即梦AI 图生视频接口测试")
    print("="*80)
    
    # 测试新接口（多图）
    test_new_api_multi_image_with_polling()
    
    # 如果需要测试旧接口，取消注释
    # test_old_api_single_image()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
