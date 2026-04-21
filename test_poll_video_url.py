"""
测试使用 history_record_id 轮询获取视频URL
"""
import sys
import os
import time
import json

# 添加 backend 目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from jimeng_api_client import JimengAPIClient
import json
import requests
from pathlib import Path
from datetime import datetime

# 测试用的 history_record_id
HISTORY_RECORD_ID = "34357198261772"

def get_sessionid_from_cookies():
    """从 cookies.json 中获取 sessionid"""
    cookies_file = Path(__file__).parent / "browser_data" / "cookies.json"
    
    if not cookies_file.exists():
        print(f"❌ cookies.json 文件不存在: {cookies_file}")
        return None
    
    try:
        with open(cookies_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        # 尝试多种可能的 sessionid 键名
        session_keys = ['sessionid', 'session_id', 'sessionId', 'SID']
        
        for key in session_keys:
            if key in cookies:
                sessionid = cookies[key]
                print(f"✓ 从 cookies.json 找到 sessionid (键名: {key})")
                return sessionid
        
        # 如果没找到，打印所有可用的键
        print(f"❌ 未找到 sessionid，可用的键: {list(cookies.keys())}")
        return None
        
    except Exception as e:
        print(f"❌ 读取 cookies.json 失败: {e}")
        return None

def test_poll_video_url():
    """测试轮询获取视频URL"""
    print("="*70)
    print(f"测试轮询获取视频URL")
    print(f"History Record ID: {HISTORY_RECORD_ID}")
    print("="*70)
    
    # 从 cookies.json 获取 sessionid
    print("\n从 cookies.json 获取 sessionid...")
    sessionid = get_sessionid_from_cookies()
    
    if not sessionid:
        print("❌ 未找到 sessionid")
        return None
    
    print(f"✓ 获取到 sessionid: {sessionid[:20]}...")
    
    # 初始化 API 客户端
    client = JimengAPIClient(sessionid=sessionid)
    
    # 直接调用轮询方法
    print("\n开始轮询任务状态...")
    
    try:
        # 调用 _poll_video_result_by_history 方法
        result = client._poll_video_result_by_history(
            history_id=HISTORY_RECORD_ID,
            max_wait_time=300,  # 最多等待300秒
            check_interval=10   # 每10秒检查一次
        )
        
        print(f"\n{'='*70}")
        print(f"轮询结果:")
        print(f"{'='*70}")
        print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
        print(f"{'='*70}")
        
        # 提取视频 URL
        if result.get('success'):
            video_url = result.get('url')  # 注意：字段名是 url，不是 video_url
            if video_url:
                print(f"\n✅ 成功获取视频URL!")
                
                # 如果是字典（多清晰度），提取最高清晰度
                if isinstance(video_url, dict):
                    # 优先使用 origin，其次 720p
                    for quality in ['origin', '720p', '480p', '360p']:
                        if quality in video_url:
                            final_url = video_url[quality].get('video_url')
                            if final_url:
                                print(f"  清晰度: {quality}")
                                print(f"  视频URL: {final_url}")
                                return final_url
                else:
                    # 如果是字符串，直接返回
                    print(f"  视频URL: {video_url}")
                    return video_url
            else:
                print(f"\n❌ 任务成功但未找到视频URL")
                print(f"结果 keys: {list(result.keys())}")
        else:
            print(f"\n❌ 任务失败: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ 轮询异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    video_url = test_poll_video_url()
    
    if video_url:
        print(f"\n✅ 测试成功！视频URL: {video_url}")
        
        # 下载视频到 output/videos 文件夹
        print(f"\n开始下载视频...")
        output_dir = Path(__file__).parent / "output" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名：video_{history_id}_{timestamp}.mp4
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{HISTORY_RECORD_ID}_{timestamp}.mp4"
        video_path = output_dir / video_filename
        
        try:
            # 下载视频
            response = requests.get(video_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end='', flush=True)
            
            print(f"\n\n✅ 视频下载成功！")
            print(f"保存路径: {video_path}")
            print(f"文件大小: {downloaded_size / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            print(f"\n\n❌ 视频下载失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ 测试失败！未获取到视频URL")
