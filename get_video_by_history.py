"""
获取已生成的视频并下载
不二次调用API，直接通过 history_id 查询并下载
"""

import sys
import os
import json
import time
import requests
from urllib.parse import urlparse

# 导入我们的 jimeng_api_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jimeng_api_client import JimengAPIClient

# 配置
SESSION_ID = "eccb32e0b3ccbd3464dc0cc90dbcdca4"

# 已生成的视频 history_id（从终端输出中获取）
HISTORY_ID = "34351121629708"

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
        
        # 尝试 video.transcoded_video（新增）
        if video and "transcoded_video" in video:
            transcoded = video["transcoded_video"]
            if isinstance(transcoded, dict):
                # 遍历所有分辨率（360p, 720p等）
                for quality, info in transcoded.items():
                    if isinstance(info, dict) and info.get("video_url"):
                        print(f"  ✓ 从 video.transcoded_video.{quality}.video_url 找到: {info['video_url']}")
                        return info["video_url"]
        
        # 尝试 common_attr.item_urls
        common_attr = item.get("common_attr", {})
        item_urls = common_attr.get("item_urls", [])
        if item_urls and item_urls[0] and item_urls[0] != "":
            return item_urls[0]
    
    # 方式3：从 pre_gen_item_ids 查找
    pre_gen_item_ids = history_data.get("pre_gen_item_ids", [])
    if pre_gen_item_ids:
        print(f"  发现 pre_gen_item_ids: {pre_gen_item_ids}")
        # 遍历 item_list 查找匹配的 ID
        for item in item_list:
            common_attr = item.get("common_attr", {})
            item_id = common_attr.get("id")
            if item_id in pre_gen_item_ids:
                # 找到匹配的item，尝试提取视频URL
                print(f"  找到匹配的 item_id: {item_id}")
                
                # 尝试 common_attr.item_urls
                item_urls = common_attr.get("item_urls", [])
                if item_urls and item_urls[0] and item_urls[0] != "":
                    print(f"  ✓ 从 common_attr.item_urls 找到: {item_urls[0]}")
                    return item_urls[0]
                
                # 尝试 video 字段
                video = item.get("video", {})
                if video and video.get("video_url"):
                    print(f"  ✓ 从 video.video_url 找到: {video['video_url']}")
                    return video["video_url"]
                
                # 尝试 video.transcoded_video
                if "transcoded_video" in video:
                    transcoded = video["transcoded_video"]
                    if isinstance(transcoded, dict):
                        for quality, info in transcoded.items():
                            if isinstance(info, dict) and info.get("video_url"):
                                print(f"  ✓ 从 video.transcoded_video.{quality}.video_url 找到: {info['video_url']}")
                                return info["video_url"]
    
    return None


def get_video_by_history(history_id):
    """通过 history_id 获取视频信息（参考 ComfyUI 插件的轮询方式）"""
    print("="*80)
    print("获取已生成的视频")
    print("="*80)
    print(f"\nhistory_id: {history_id}")
    
    client = JimengAPIClient(sessionid=SESSION_ID)
    
    # 直接查询历史记录（不调用生成接口）
    # 参考 ComfyUI 插件的轮询逻辑
    print("\n[1/3] 查询历史记录...")
    
    max_retries = 60  # 最多重试60次
    check_interval = 5  # 每次间隔5秒
    
    for attempt in range(max_retries):
        try:
            # 调用 get_history_by_ids 接口（与 ComfyUI 插件相同）
            url = f"{client.base_url}/mweb/v1/get_history_by_ids"
            
            token_info = client.token_manager.get_token('/mweb/v1/get_history_by_ids')
            params = {
                "aid": client.aid,
                "device_platform": "web",
                "region": "cn",
                "webId": client.token_manager.web_id,
                "da_version": "3.3.12",
                "os": "windows",
                "web_component_open_flag": "1",
                "commerce_with_input_video": "1",
                "web_version": "7.5.0",
                "aigc_features": "app_lip_sync"
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            # 请求数据
            data = {
                "history_ids": [history_id],
                "image_info": {
                    "width": 2048,
                    "height": 2048,
                    "format": "webp",
                    "image_scene_list": [
                        {"scene": "normal", "width": 2400, "height": 2400, "uniq_key": "2400", "format": "webp"},
                        {"scene": "loss", "width": 1080, "height": 1080, "uniq_key": "1080", "format": "webp"},
                    ]
                }
            }
            
            # 发送请求
            headers, _ = client.token_manager.get_headers(
                '/mweb/v1/get_history_by_ids',
                referer='https://jimeng.jianying.com/ai-tool/generate?type=video',
                token_info=token_info
            )
            
            response = requests.post(url, headers=headers, params=params, json=data)
            
            if response.status_code != 200:
                print(f"  请求失败: HTTP {response.status_code}")
                time.sleep(check_interval)
                continue
            
            result = response.json()
            
            if result.get("ret") != "0":
                print(f"  API返回错误: {result.get('errmsg')}")
                time.sleep(check_interval)
                continue
            
            # 解析数据
            history_data = result.get("data", {}).get(history_id, {})
            
            if not history_data:
                print(f"  未找到 history_id 数据")
                time.sleep(check_interval)
                continue
            
            status = history_data.get("status")
            
            # 检查状态
            if status in [30, 50]:  # 30=生成完成, 50=已发布
                print(f"  ✓ 视频已生成（状态: {status}）")
                
                # 提取视频URL
                video_url = extract_video_url(history_data)
                
                if video_url:
                    # 下载视频
                    print("\n" + "="*80)
                    print("[3/3] 下载视频")
                    print("="*80)
                    
                    timestamp = int(time.time())
                    filename = f"video_{history_id}_{timestamp}.mp4"
                    save_path = os.path.join(DOWNLOAD_DIR, filename)
                    
                    success = download_video(video_url, save_path)
                    
                    if success:
                        print(f"\n✅ 视频下载成功！")
                        print(f"  文件路径: {save_path}")
                    else:
                        print(f"\n❌ 视频下载失败")
                    
                    return
                else:
                    print(f"\n❌ 未找到视频URL")
                    print("\n完整 history_data:")
                    print(json.dumps(history_data, ensure_ascii=False, indent=2))
                    return
            
            elif status == 4013:
                fail_msg = history_data.get("fail_starling_message", "未知错误")
                print(f"\n❌ 生成失败！错误代码: 4013")
                print(f"  错误信息: {fail_msg}")
                return
            
            else:
                # 还在生成中
                if attempt % 6 == 0:  # 每30秒打印一次
                    print(f"  [轮询 #{attempt+1}] 生成中...（状态: {status}）")
                time.sleep(check_interval)
        
        except Exception as e:
            print(f"  轮询异常: {e}")
            time.sleep(check_interval)
    
    print(f"\n❌ 轮询超时（已等待 {max_retries * check_interval} 秒）")


if __name__ == "__main__":
    get_video_by_history(HISTORY_ID)
