"""
单独测试视频下载功能
使用已有的history_id获取视频并下载到本地
"""

from jimeng_api_client import JimengAPIClient
import json

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
