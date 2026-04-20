"""
测试即梦AI 旧接口多图生视频（破解版）
尝试在旧接口中传入多张图片
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
IMAGE_PATHS = [
    "/mnt/d/Project/seedance/uploads/materials/7161db6c-1158-48e8-a00f-45f795c50d4a.png",  # 狐奶奶
    "/mnt/d/Project/seedance/uploads/materials/bdc3e640-097b-418e-b7b4-14008f27bd8b.png"   # 包子铺内
]

def test_old_api_multi_image_hack():
    """测试旧接口多图生视频（破解版）"""
    print("=" * 80)
    print("即梦AI 旧接口多图生视频测试（破解版）")
    print("=" * 80)
    print(f"\n使用图片:")
    for i, path in enumerate(IMAGE_PATHS, 1):
        print(f"  图片{i}: {path}")
    print(f"\n提示词: 包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽")
    print(f"模型: s2.0 (使用 dreamina_ic_generate_video_model_vgfm_lite)")
    print(f"时长: 4秒")
    print(f"\n" + "=" * 80)
    
    # 创建客户端
    client = JimengAPIClient(sessionid=SESSION_ID)
    
    # 手动构造请求
    import uuid
    import random
    
    # 上传图片
    print(f"\n[1/4] 正在上传图片...")
    upload_token = client._get_upload_token()
    if not upload_token:
        print("❌ 获取上传token失败")
        return
    
    image_uris = []
    for i, img_path in enumerate(IMAGE_PATHS, 1):
        print(f"  上传第 {i}/{len(IMAGE_PATHS)} 张图片: {img_path}")
        image_uri = client._upload_image(img_path, upload_token)
        if not image_uri:
            print(f"  ❌ 上传失败")
            return
        print(f"  ✓ 上传成功，URI: {image_uri}")
        image_uris.append(image_uri)
    
    # 获取图片尺寸
    from PIL import Image
    image_sizes = []
    for img_path in IMAGE_PATHS:
        with Image.open(img_path) as img:
            image_sizes.append({"width": img.width, "height": img.height})
    
    # 模型配置
    model_config = {
        "model_req_key": "dreamina_ic_generate_video_model_vgfm_lite",
        "benefit_type": "basic_video_operation_vgfm_lite",
        "fps": 24
    }
    
    duration_ms = 4000
    submit_id = str(uuid.uuid4())
    
    url = f"{client.base_url}/mweb/v1/generate_video"
    
    babi_param = {
        "scenario": "image_video_generation",
        "feature_key": "image_to_video",
        "feature_entrance": "to_video",
        "feature_entrance_detail": "to_video-image_to_video"
    }
    
    # 【破解尝试】构造多个 video_gen_inputs
    print(f"\n[2/4] 构造请求数据（尝试多图）...")
    
    # 方案1：在 video_gen_inputs 数组中传入多个元素
    video_gen_inputs = []
    for i, (image_uri, image_size) in enumerate(zip(image_uris, image_sizes)):
        if i == 0:
            # 第一个作为 first_frame_image
            video_gen_inputs.append({
                "prompt": "包子铺内，狐奶奶正在做着包子，包子铺内的锅上冒着蒸汽",
                "first_frame_image": {
                    "width": image_size["width"],
                    "height": image_size["height"],
                    "image_uri": image_uri
                },
                "fps": model_config["fps"],
                "duration_ms": duration_ms,
                "video_mode": 1,
                "template_id": ""
            })
        else:
            # 后续图片作为 additional_images（如果支持的话）
            # 注意：这只是尝试，不一定支持
            video_gen_inputs[-1]["additional_images"] = video_gen_inputs[-1].get("additional_images", [])
            video_gen_inputs[-1]["additional_images"].append({
                "width": image_size["width"],
                "height": image_size["height"],
                "image_uri": image_uri
            })
    
    print(f"[DEBUG] video_gen_inputs 数量: {len(video_gen_inputs)}")
    print(f"[DEBUG] first_frame_image: {video_gen_inputs[0].get('first_frame_image', {}).get('image_uri', '')}")
    if 'additional_images' in video_gen_inputs[0]:
        print(f"[DEBUG] additional_images 数量: {len(video_gen_inputs[0]['additional_images'])}")
    
    data = {
        "submit_id": submit_id,
        "task_extra": json.dumps({
            "promptSource": "custom",
            "originSubmitId": str(uuid.uuid4()),
            "isDefaultSeed": 1
        }),
        "http_common_info": {"aid": client.aid},
        "input": {
            "video_gen_inputs": video_gen_inputs,
            "priority": 0,
            "model_req_key": model_config["model_req_key"]
        },
        "mode": "workbench",
        "commerce_info": {
            "resource_id": "generate_video",
            "resource_id_type": "str",
            "resource_sub_type": "aigc",
            "benefit_type": model_config["benefit_type"]
        }
    }
    
    # 发送请求
    print(f"\n[3/4] 发送API请求...")
    token_info = client.token_manager.get_token('/mweb/v1/generate_video')
    params = {
        "babi_param": json.dumps(babi_param),
        "aid": client.aid,
        "device_platform": "web",
        "region": "CN",
        "web_id": client.token_manager.web_id,
    }
    
    if token_info.get("msToken"):
        params["msToken"] = token_info["msToken"]
    if token_info.get("a_bogus"):
        params["a_bogus"] = token_info["a_bogus"]
    
    headers, _ = client.token_manager.get_headers(
        '/mweb/v1/generate_video',
        referer='https://jimeng.jianying.com/ai-tool/video/generate'
    )
    
    print(f"\n[DEBUG] 完整请求体:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    response = client._send_request("POST", url, params=params, json=data, headers=headers)
    
    print(f"\n[DEBUG] API响应:")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
    if not response or str(response.get('ret')) != '0':
        print(f"\n❌ 视频提交失败！")
        print(f"  - 返回状态: {response.get('ret')}")
        print(f"  - 错误信息: {response.get('errmsg')}")
        return
    
    # 获取 task_id
    task_id = response.get('data', {}).get('aigc_data', {}).get('task', {}).get('task_id')
    if not task_id:
        print(f"\n❌ 未获取到 task_id！")
        return
    
    print(f"\n[SUCCESS] 视频任务提交成功！")
    print(f"  - task_id: {task_id}")
    
    # 轮询等待
    print(f"\n[4/4] 开始轮询视频生成状态...")
    print(f"  - task_id: {task_id}")
    print(f"  - 最大等待时间: 600秒")
    print()
    
    # 使用轮询函数
    result = client._poll_video_result(task_id, max_wait_time=600, check_interval=10)
    
    print("\n" + "=" * 80)
    print("调用结果:")
    print("=" * 80)
    
    if result.get("success"):
        print("✅ 视频生成成功！")
        print(f"\n视频信息:")
        print(f"  - video_url: {result.get('video_url')}")
        
        # 保存视频
        if result.get('video_url'):
            video_path = f"test_old_api_multi_hack_{int(time.time())}.mp4"
            print(f"\n正在下载视频到: {video_path}")
            
            import requests
            video_response = requests.get(result['video_url'])
            with open(video_path, 'wb') as f:
                f.write(video_response.content)
            
            print(f"✅ 视频已保存: {video_path}")
    else:
        print(f"❌ 视频生成失败: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_old_api_multi_image_hack()
