"""
单独测试视频下载功能
使用已有的history_id获取视频并下载到本地
"""

from jimeng_api_client import JimengAPIClient
import json
import time
from typing import Dict, Optional


QUEUE_CHECK_INTERVAL = 30       # 排队时每30秒查询一次
DOWNLOAD_CHECK_INTERVAL = 300   # 可下载后每5分钟尝试下载一次
DOWNLOAD_MAX_ATTEMPTS = 12      # 下载最多尝试12次


def _get_history_data(client_obj: JimengAPIClient, target_history_id: str) -> Dict:
    url = f"{client_obj.base_url}/mweb/v1/get_history_by_ids"
    token_info = client_obj.token_manager.get_token('/mweb/v1/get_history_by_ids')
    params = {
        "aid": client_obj.aid,
        "device_platform": "web",
        "region": "cn",
        "web_id": client_obj.token_manager.web_id,
        "da_version": "3.3.12",
        "web_component_open_flag": "1",
        "web_version": "7.5.0",
        "aigc_features": "app_lip_sync"
    }
    if token_info.get("msToken"):
        params["msToken"] = token_info["msToken"]
    if token_info.get("a_bogus"):
        params["a_bogus"] = token_info["a_bogus"]

    data = {
        "history_ids": [target_history_id],
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

    result = client_obj._send_request("POST", url, params=params, json=data)
    if not result or result.get("ret") != "0":
        raise RuntimeError(f"查询失败: {result}")
    history_data = result.get("data", {}).get(target_history_id, {})
    if not history_data:
        raise RuntimeError(f"未找到 history_id={target_history_id} 的数据")
    return history_data


def _extract_video_url(history_data: Dict) -> Optional[str]:
    resources = history_data.get("resources", [])
    for res in resources:
        if res.get("type") == "video":
            video_url = res.get("video_info", {}).get("video_url")
            if video_url:
                return video_url

    item_list = history_data.get("item_list", [])
    for item in item_list:
        video_data = item.get("video", {})
        if not video_data:
            continue

        transcoded = video_data.get("transcoded_video")
        if isinstance(transcoded, dict):
            for quality in ["origin", "720p", "480p", "360p"]:
                if quality in transcoded:
                    candidate = transcoded[quality].get("video_url")
                    if candidate:
                        return candidate

        candidate = video_data.get("origin_video") or video_data.get("video_url")
        if candidate:
            return candidate

    return None


def run_two_stage_polling(client_obj: JimengAPIClient, target_history_id: str) -> None:
    print("=" * 60)
    print("视频下载测试（排队3分钟轮询 -> 下载5分钟轮询*12次）")
    print("=" * 60)
    print(f"history_id: {target_history_id}")

    queue_count = 0
    video_url = None
    while True:
        queue_count += 1
        history_data = _get_history_data(client_obj, target_history_id)
        status = history_data.get("status")
        fail_code = history_data.get("fail_code")
        pre_gen_item_ids = history_data.get("pre_gen_item_ids")
        video_url = _extract_video_url(history_data)

        print(f"\n[排队轮询 #{queue_count}] status={status}, fail_code={fail_code}, pre_gen_item_ids={pre_gen_item_ids}")
        if fail_code:
            raise RuntimeError(f"任务失败: status={status}, fail_code={fail_code}")
        if video_url:
            print("[阶段1] 检测到可用视频URL，进入下载轮询阶段")
            break

        print(f"[阶段1] 仍在排队/处理中，{QUEUE_CHECK_INTERVAL}秒后继续...")
        time.sleep(QUEUE_CHECK_INTERVAL)

    for attempt in range(1, DOWNLOAD_MAX_ATTEMPTS + 1):
        print(f"\n[下载轮询 #{attempt}/{DOWNLOAD_MAX_ATTEMPTS}] 尝试下载...")
        latest_history_data = _get_history_data(client_obj, target_history_id)
        latest_video_url = _extract_video_url(latest_history_data) or video_url
        saved_path = client_obj.download_video(latest_video_url, save_dir="output_video")
        if saved_path:
            print(f"[成功] 视频下载完成: {saved_path}")
            return
        if attempt < DOWNLOAD_MAX_ATTEMPTS:
            print(f"[阶段2] 本次下载失败，{DOWNLOAD_CHECK_INTERVAL}秒后重试...")
            time.sleep(DOWNLOAD_CHECK_INTERVAL)

    raise TimeoutError(f"下载超时: 已重试 {DOWNLOAD_MAX_ATTEMPTS} 次")


if __name__ == "__main__":
    _client = JimengAPIClient(sessionid="eccb32e0b3ccbd3464dc0cc90dbcdca4")
    _history_id = "34199679261452"
    try:
        run_two_stage_polling(_client, _history_id)
    except Exception as e:
        print(f"\n[失败] {e}")
    raise SystemExit(0)

# 您的sessionid
client = JimengAPIClient(sessionid="eccb32e0b3ccbd3464dc0cc90dbcdca4")

print("=" * 60)
print("视频下载功能测试")
print("=" * 60)

# 方式1：如果您已经有history_id，直接测试
# 请替换为您刚才生成成功的history_id
history_id = "34199679261452"  # 从终端输出中获取的

print(f"\n使用history_id: {history_id}")
print("=" * 60)

# 测试：通过history_id获取视频
print("\n[测试1] 通过history_id获取视频URL...")

# 先手动调用API查看完整数据结构
print("\n正在查询API完整返回...")
import json as json_module

url = f"{client.base_url}/mweb/v1/get_history_by_ids"
token_info = client.token_manager.get_token('/mweb/v1/get_history_by_ids')
params = {
    "aid": client.aid,
    "device_platform": "web",
    "region": "cn",
    "web_id": client.token_manager.web_id,
    "da_version": "3.3.12",
    "web_component_open_flag": "1",
    "web_version": "7.5.0",
    "aigc_features": "app_lip_sync"
}

if token_info.get("msToken"):
    params["msToken"] = token_info["msToken"]
if token_info.get("a_bogus"):
    params["a_bogus"] = token_info["a_bogus"]

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

result = client._send_request("POST", url, params=params, json=data)

# 打印完整数据结构
print("\n" + "=" * 60)
print("API完整返回数据：")
print("=" * 60)

# 只打印关键字段，避免太长
history_data = result.get("data", {}).get(history_id, {})
print(f"\nstatus: {history_data.get('status')}")
print(f"fail_code: {history_data.get('fail_code')}")
print(f"pre_gen_item_ids: {history_data.get('pre_gen_item_ids')}")

# 查找item_list
item_list = history_data.get("item_list", [])
print(f"\nitem_list 数量: {len(item_list)}")

for i, item in enumerate(item_list):
    print(f"\n{'='*40}")
    print(f"Item {i} 的keys: {list(item.keys())}")
    
    # 如果有video字段
    if "video" in item:
        print(f"  ✓ 找到video字段")
        print(f"  video的keys: {list(item['video'].keys())}")
        if "video_url" in item["video"]:
            print(f"  ✓✓✓ 视频URL: {item['video']['video_url']}")
    
    # 如果有image字段
    if "image" in item:
        print(f"  找到image字段")

# 查找resources
resources = history_data.get("resources", [])
print(f"\n{'='*40}")
print(f"resources 数量: {len(resources)}")
for j, res in enumerate(resources):
    print(f"  Resource {j}: type={res.get('type')}")
    if res.get('type') == 'video':
        video_info = res.get('video_info', {})
        print(f"  ✓✓✓ 视频URL: {video_info.get('video_url')}")

print("\n" + "=" * 60)
print("完整item_list[0]数据：")
print("=" * 60)
if item_list:
    print(json_module.dumps(item_list[0], ensure_ascii=False, indent=2))

# 尝试从返回数据中提取视频URL
video_url = None

# 方式1：从item_list的video字段中提取
for item in item_list:
    if "video" in item:
        video_data = item["video"]
        
        # transcoded_video是一个字典，包含多种分辨率
        transcoded = video_data.get("transcoded_video")
        if transcoded and isinstance(transcoded, dict):
            # 选择最高画质：origin > 720p > 480p > 360p
            for quality in ['origin', '720p', '480p', '360p']:
                if quality in transcoded:
                    video_url = transcoded[quality].get('video_url')
                    if video_url:
                        print(f"\n✅ 从item_list.video找到视频URL ({quality}): {video_url[:100]}...")
                        break
        
        # 如果不是字典，直接尝试获取
        if not video_url:
            video_url = (
                video_data.get("origin_video") or
                video_data.get("video_url") or
                None
            )
            if video_url:
                print(f"\n✅ 从item_list.video找到视频URL: {video_url[:100]}...")
        
        if video_url:
            break

# 方式2：从resources中提取
if not video_url:
    for res in resources:
        if res.get('type') == 'video':
            video_url = res.get('video_info', {}).get('video_url')
            if video_url:
                print(f"\n✅ 从resources找到视频URL: {video_url}")
                break

if video_url:
    print(f"\n{'='*60}")
    print("✅ 成功获取视频URL！")
    print(f"{'='*60}")
    print(f"视频URL: {video_url}")
    
    # 测试下载
    print("\n[测试2] 下载视频到本地...")
    saved_path = client.download_video(video_url, save_dir="output_video")
    
    if saved_path:
        print(f"\n✅ 视频下载成功！")
        print(f"保存路径: {saved_path}")
    else:
        print(f"\n❌ 视频下载失败")
else:
    print(f"\n❌ 未找到视频URL")
    print(f"status: {history_data.get('status')}")
    print(f"请检查上面的数据结构，确认视频URL在哪个字段")

print("\n" + "=" * 60)
print("提示：")
print("=" * 60)
print("1. 如果history_id对应的视频已过期，请重新生成")
print("2. 视频会保存到 output_video 文件夹")
print("3. 请检查 output_video 文件夹确认视频已下载")
