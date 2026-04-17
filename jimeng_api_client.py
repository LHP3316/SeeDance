"""
即梦AI API客户端
通过纯API调用实现图片生成，无需浏览器
"""

import os
import json
import uuid
import time
import random
import hashlib
import requests
import logging
from typing import Dict, List, Optional, Tuple
from token_manager import TokenManager

logger = logging.getLogger(__name__)


class JimengAPIClient:
    """即梦AI API客户端"""
    
    def __init__(self, sessionid: str):
        """
        初始化API客户端
        
        Args:
            sessionid: 从浏览器Cookie中获取的sessionid
        """
        self.base_url = "https://jimeng.jianying.com"
        self.aid = "513695"
        self.token_manager = TokenManager(sessionid)
        
        logger.info("[JimengAPIClient] 初始化成功")
    
    def _send_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET/POST)
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            响应JSON或None
        """
        try:
            # 获取URI用于生成签名
            uri = url.split(self.base_url)[-1].split('?')[0]
            
            # 获取headers
            headers, token_info = self.token_manager.get_headers(uri)
            
            # 合并自定义headers
            if 'headers' in kwargs:
                headers.update(kwargs.pop('headers'))
            
            kwargs['headers'] = headers
            
            # 发送请求
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"[Jimeng] Response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"[Jimeng] Request failed: {e}")
            return None
    
    def _get_ratio_value(self, ratio: str) -> int:
        """将比例字符串转换为数值"""
        ratio_map = {
            "4:3": 4,
            "3:4": 3,
            "1:1": 1,
            "16:9": 16,
            "9:16": 9
        }
        return ratio_map.get(ratio, 1)
    
    def _get_ratio_dimensions(self, ratio: str) -> Tuple[int, int]:
        """获取指定比例的图片尺寸"""
        ratios = {
            "1:1": (1024, 1024),
            "4:3": (1152, 896),
            "3:4": (896, 1152),
            "16:9": (1344, 768),
            "9:16": (768, 1344)
        }
        return ratios.get(ratio, (1024, 1024))
    
    def generate_text_to_image(self, prompt: str, model: str = "3.0", ratio: str = "1:1") -> Dict:
        """
        文生图
        
        Args:
            prompt: 提示词
            model: 模型名称 (2.0, 2.1, 3.0, 4.0等)
            ratio: 图片比例 (1:1, 16:9, 9:16, 4:3, 3:4)
            
        Returns:
            {
                "success": bool,
                "history_id": str,
                "submit_id": str,
                "urls": List[str],  # 图片URL列表
                "error": str  # 错误信息
            }
        """
        try:
            logger.info(f"[Jimeng] 开始文生图 - 模型: {model}, 比例: {ratio}")
            
            # 获取图片尺寸
            width, height = self._get_ratio_dimensions(ratio)
            
            # 生成随机种子
            seed = random.randint(1, 999999999)
            
            # 生成UUID
            submit_id = str(uuid.uuid4())
            draft_id = str(uuid.uuid4())
            component_id = str(uuid.uuid4())
            
            # 获取模型配置 - 使用正确的模型key（参考Comfyui_Free_Jimeng项目）
            model_map = {
                "2.0": "high_aes_general_v20:general_v2.0",
                "2.1": "high_aes_general_v21:general_v2.1",
                "3.0": "high_aes_general_v30l:general_v3.0_18b",
                "3.1": "high_aes_general_v30l_art_fangzhou:general_v3.0_18b",
                "4.0": "high_aes_general_v40",
                "4.1": "high_aes_general_v41",
                "4.5": "high_aes_general_v40l",
                "4.6": "high_aes_general_v42",
                "5.0": "high_aes_general_v50"
            }
            model_req_key = model_map.get(model, "high_aes_general_v50")
            
            # 准备请求数据
            url = f"{self.base_url}/mweb/v1/aigc_draft/generate"
            
            babi_param = {
                "scenario": "image_video_generation",
                "feature_key": "aigc_to_image",
                "feature_entrance": "to_image",
                "feature_entrance_detail": "to_image"
            }
            
            metrics_extra = {
                "templateId": "",
                "generateCount": 1,
                "promptSource": "custom",
                "templateSource": "",
                "lastRequestId": "",
                "originRequestId": "",
                "originSubmitId": "",
                "isDefaultSeed": 1,
                "originTemplateId": "",
                "imageNameMapping": {},
                "isUseAiGenPrompt": False,
                "batchNumber": 1
            }
            
            data = {
                "extend": {
                    "root_model": model_req_key,
                    "template_id": ""
                },
                "submit_id": submit_id,
                "metrics_extra": json.dumps(metrics_extra),
                "draft_content": json.dumps({
                    "type": "draft",
                    "id": draft_id,
                    "min_version": "3.0.2",
                    "min_features": [],
                    "is_from_tsn": True,
                    "version": "3.2.8",
                    "main_component_id": component_id,
                    "component_list": [{
                        "type": "image_base_component",
                        "id": component_id,
                        "min_version": "3.0.2",
                        "aigc_mode": "workbench",
                        "metadata": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "created_platform": 3,
                            "created_platform_version": "",
                            "created_time_in_ms": str(int(time.time() * 1000)),
                            "created_did": ""
                        },
                        "generate_type": "generate",
                        "abilities": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "generate": {
                                "type": "",
                                "id": str(uuid.uuid4()),
                                "core_param": {
                                    "type": "",
                                    "id": str(uuid.uuid4()),
                                    "model": model_req_key,
                                    "prompt": prompt,
                                    "negative_prompt": "",
                                    "seed": seed,
                                    "sample_strength": 0.5,
                                    "image_ratio": self._get_ratio_value(ratio),
                                    "large_image_info": {
                                        "type": "",
                                        "id": str(uuid.uuid4()),
                                        "height": height,
                                        "width": width,
                                        "resolution_type": "1k"
                                    }
                                },
                                "history_option": {
                                    "type": "",
                                    "id": str(uuid.uuid4())
                                }
                            }
                        }
                    }]
                }),
                "http_common_info": {"aid": self.aid}
            }
            
            # URL参数
            token_info = self.token_manager.get_token('/mweb/v1/aigc_draft/generate')
            params = {
                "babi_param": json.dumps(babi_param),
                "aid": self.aid,
                "device_platform": "web",
                "region": "CN",
                "web_id": self.token_manager.web_id,
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            # 发送请求
            response = self._send_request("POST", url, params=params, json=data)
            
            if not response or str(response.get('ret')) != '0':
                logger.error(f"[Jimeng] 文生图失败: {response}")
                return {
                    "success": False,
                    "error": f"API返回错误: {response}"
                }
            
            # 获取history_id
            history_id = response.get('data', {}).get('aigc_data', {}).get('history_record_id')
            if not history_id:
                return {
                    "success": False,
                    "error": "未获取到history_id"
                }
            
            logger.info(f"[Jimeng] 提交成功，history_id: {history_id}")
            
            # 轮询等待图片生成
            return self._poll_generation_result(history_id=history_id, submit_id=submit_id)
            
        except Exception as e:
            logger.error(f"[Jimeng] 文生图异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_image_to_image(self, image_paths: List[str], prompt: str, 
                                 model: str = "4.0", ratio: str = "1:1") -> Dict:
        """
        图生图（支持多图）
        
        Args:
            image_paths: 参考图片路径列表
            prompt: 提示词
            model: 模型名称
            ratio: 图片比例
            
        Returns:
            同generate_text_to_image
        """
        try:
            logger.info(f"[Jimeng] 开始图生图 - 图片数量: {len(image_paths)}, 模型: {model}")
            
            # 获取模型配置
            model_map = {
                "2.0": "high_aes_general_v20:general_v2.0",
                "2.1": "high_aes_general_v21:general_v2.1",
                "3.0": "high_aes_general_v30l:general_v3.0_18b",
                "3.1": "high_aes_general_v30l_art_fangzhou:general_v3.0_18b",
                "4.0": "high_aes_general_v40",
                "4.1": "high_aes_general_v41",
                "4.5": "high_aes_general_v40l",
                "4.6": "high_aes_general_v42",
                "5.0": "high_aes_general_v50"
            }
            model_req_key = model_map.get(model, "high_aes_general_v50")
            
            # 获取图片尺寸
            width, height = self._get_ratio_dimensions(ratio)
            
            # 获取上传token
            upload_token = self._get_upload_token()
            if not upload_token:
                return {"success": False, "error": "获取上传token失败"}
            
            # 上传图片
            image_uris = []
            image_meta = {}
            
            for img_path in image_paths:
                uri = self._upload_image(img_path, upload_token)
                if not uri:
                    return {"success": False, "error": f"上传图片失败: {img_path}"}
                
                image_uris.append(uri)
                
                # 获取图片元数据
                try:
                    from PIL import Image
                    with Image.open(img_path) as im:
                        w, h = im.size
                        fmt = (im.format or "").lower()
                except Exception:
                    w, h, fmt = 0, 0, ""
                
                image_meta[uri] = {"width": w, "height": h, "format": fmt}
            
            logger.info(f"[Jimeng] 图片上传成功，数量: {len(image_uris)}")
            
            # 生成UUID
            submit_id = str(uuid.uuid4())
            draft_id = "adffa4e0-fced-fc0c-b972-5c5a0f51cb2f"
            component_id = "c440938a-d652-fc79-1a48-c516d848094c"
            
            # 准备请求数据
            url = f"{self.base_url}/mweb/v1/aigc_draft/generate"
            
            babi_param = {
                "scenario": "image_video_generation",
                "feature_key": "aigc_to_image",
                "feature_entrance": "to_image",
                "feature_entrance_detail": "to_image"
            }
            
            metrics_extra = {
                "promptSource": "custom",
                "generateCount": 1,
                "enterFrom": "reprompt",
                "templateId": "0",
                "generateId": submit_id,
                "isRegenerate": False
            }
            
            # 构建draft_content
            draft_content = {
                "type": "draft",
                "id": draft_id,
                "min_version": "3.0.2",
                "min_features": [],
                "is_from_tsn": True,
                "version": "3.3.2",
                "main_component_id": component_id,
                "component_list": [{
                    "type": "image_base_component",
                    "id": component_id,
                    "min_version": "3.0.2",
                    "gen_type": 12,
                    "generate_type": "blend",
                    "aigc_mode": "workbench",
                    "metadata": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "created_platform": 3,
                        "created_platform_version": "",
                        "created_time_in_ms": str(int(time.time() * 1000)),
                        "created_did": ""
                    },
                    "abilities": {
                        "type": "",
                        "id": "df594b0f-9e1f-08ff-c031-54fdb2fff8b3",
                        "blend": {
                            "type": "",
                            "id": "82cebd72-65a1-cb61-e1bc-c4b79003d1d5",
                            "min_features": [],
                            "core_param": {
                                "type": "",
                                "id": "5388a3a6-d1e8-fe78-51e8-8b6e4490f21c",
                                "model": model_req_key,
                                "prompt": f"##​{prompt}",
                                "sample_strength": 0.5,
                                "image_ratio": self._get_ratio_value(ratio),
                                "large_image_info": {
                                    "type": "",
                                    "id": "364336a8-c4c7-fbaa-c876-4402656ab195",
                                    "height": height,
                                    "width": width,
                                    "resolution_type": "2k"
                                },
                                "intelligent_ratio": False
                            },
                            "ability_list": [{
                                "type": "",
                                "id": str(uuid.uuid4()),
                                "name": "byte_edit",
                                "image_uri_list": [uri],
                                "image_list": [{
                                    "type": "image",
                                    "id": str(uuid.uuid4()),
                                    "source_from": "upload",
                                    "platform_type": 1,
                                    "name": "",
                                    "image_uri": uri,
                                    "width": image_meta.get(uri, {}).get("width", 0),
                                    "height": image_meta.get(uri, {}).get("height", 0),
                                    "format": image_meta.get(uri, {}).get("format", ""),
                                    "uri": uri
                                }],
                                "strength": 0.5
                            } for uri in image_uris],
                            "history_option": {
                                "type": "",
                                "id": "6ec2e2cd-99af-0033-99a1-a325a27aad88"
                            },
                            "prompt_placeholder_info_list": [{
                                "type": "",
                                "id": str(uuid.uuid4()),
                                "ability_index": idx
                            } for idx in range(len(image_uris))],
                            "postedit_param": {
                                "type": "",
                                "id": "02518f0d-5d8f-c7d3-a8f9-d36aa3600d24",
                                "generate_type": 0
                            }
                        }
                    }
                }]
            }
            
            data = {
                "extend": {
                    "root_model": model_req_key,
                    "template_id": ""
                },
                "submit_id": submit_id,
                "metrics_extra": json.dumps(metrics_extra),
                "draft_content": json.dumps(draft_content),
                "http_common_info": {"aid": self.aid}
            }
            
            token_info = self.token_manager.get_token('/mweb/v1/aigc_draft/generate')
            params = {
                "babi_param": json.dumps(babi_param),
                "aid": self.aid,
                "device_platform": "web",
                "region": "cn",
                "web_id": self.token_manager.web_id,
                "da_version": "3.3.2",
                "web_component_open_flag": "1",
                "web_version": "7.5.0",
                "aigc_features": "app_lip_sync"
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            # 发送请求
            response = self._send_request("POST", url, params=params, json=data)
            
            if not response or str(response.get("ret")) != "0":
                logger.error(f"[Jimeng] 图生图失败: {response}")
                return {
                    "success": False,
                    "error": f"API返回错误: {response}"
                }
            
            history_id = response.get('data', {}).get('aigc_data', {}).get('history_record_id')
            if not history_id:
                return {
                    "success": False,
                    "error": "未获取到history_id"
                }
            
            logger.info(f"[Jimeng] 图生图提交成功，history_id: {history_id}")
            
            # 轮询等待图片生成
            return self._poll_generation_result(history_id=history_id, submit_id=submit_id)
            
        except Exception as e:
            logger.error(f"[Jimeng] 图生图异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_upload_token(self) -> Optional[Dict]:
        """获取上传token"""
        try:
            url = f"{self.base_url}/mweb/v1/get_upload_token"
            params = {
                "aid": self.aid,
                "device_platform": "web",
                "region": "CN"
            }
            
            data = {"scene": 2}
            
            response = self._send_request("POST", url, params=params, json=data)
            
            if not response or response.get("ret") != "0":
                logger.error(f"[Jimeng] 获取上传token失败: {response}")
                return None
            
            return response.get("data", {})
            
        except Exception as e:
            logger.error(f"[Jimeng] 获取上传token异常: {e}")
            return None
    
    def _upload_image(self, image_path: str, upload_token: Dict) -> Optional[str]:
        """
        上传图片到服务器
        
        Args:
            image_path: 图片路径
            upload_token: 上传token信息
            
        Returns:
            上传成功后的图片URI
        """
        # 简化版上传（完整实现参考Comfyui_Free_Jimeng项目）
        # 这里使用更简单的方式
        
        try:
            import datetime
            import urllib.parse
            import binascii
            import hmac
            
            file_size = os.path.getsize(image_path)
            t = datetime.datetime.utcnow()
            amz_date = t.strftime('%Y%m%dT%H%M%SZ')
            
            # 申请上传
            request_parameters = {
                'Action': 'ApplyImageUpload',
                'FileSize': str(file_size),
                'ServiceId': upload_token.get('space_name', 'tb4s082cfz'),
                'Version': '2018-08-01'
            }
            
            canonical_querystring = '&'.join([
                f'{k}={urllib.parse.quote(str(v))}' 
                for k, v in sorted(request_parameters.items())
            ])
            
            canonical_headers = (
                f'host:imagex.bytedanceapi.com\n'
                f'x-amz-date:{amz_date}\n'
                f'x-amz-security-token:{upload_token.get("session_token", "")}\n'
            )
            signed_headers = 'host;x-amz-date;x-amz-security-token'
            payload_hash = hashlib.sha256(b'').hexdigest()
            
            canonical_request = '\n'.join([
                'GET', '/', canonical_querystring,
                canonical_headers, signed_headers, payload_hash
            ])
            
            # 生成签名
            authorization = self._get_aws_authorization(
                upload_token.get('access_key_id', ''),
                upload_token.get('secret_access_key', ''),
                'cn-north-1', 'imagex', amz_date,
                upload_token.get('session_token', ''),
                signed_headers, canonical_request
            )
            
            headers = {
                'Authorization': authorization,
                'X-Amz-Date': amz_date,
                'X-Amz-Security-Token': upload_token.get('session_token', ''),
                'Host': 'imagex.bytedanceapi.com'
            }
            
            url = f'https://imagex.bytedanceapi.com/?{canonical_querystring}'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"[Jimeng] 获取上传授权失败: {response.text}")
                return None
            
            upload_info = response.json()
            if "Result" not in upload_info:
                return None
            
            # 上传图片
            store_info = upload_info['Result']['UploadAddress']['StoreInfos'][0]
            upload_host = upload_info['Result']['UploadAddress']['UploadHosts'][0]
            
            with open(image_path, 'rb') as f:
                content = f.read()
                crc32 = format(binascii.crc32(content) & 0xFFFFFFFF, '08x')
            
            upload_url = f"https://{upload_host}/upload/v1/{store_info['StoreUri']}"
            upload_headers = {
                'accept': '*/*',
                'authorization': store_info['Auth'],
                'content-type': 'application/octet-stream',
                'content-disposition': 'attachment; filename="undefined"',
                'content-crc32': crc32,
                'origin': 'https://jimeng.jianying.com',
                'referer': 'https://jimeng.jianying.com/'
            }
            
            response = requests.post(upload_url, headers=upload_headers, data=content)
            if response.status_code != 200:
                logger.error(f"[Jimeng] 上传图片失败: {response.text}")
                return None
            
            return store_info.get("StoreUri")
            
        except Exception as e:
            logger.error(f"[Jimeng] 上传图片异常: {e}")
            return None
    
    def _get_aws_authorization(self, access_key, secret_key, region, service, 
                                amz_date, security_token, signed_headers, canonical_request):
        """AWS V4签名"""
        import hashlib
        import hmac
        
        datestamp = amz_date[:8]
        canonical_request_hash = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        credential_scope = f"{datestamp}/{region}/{service}/aws4_request"
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{canonical_request_hash}"
        
        k_date = hmac.new(f"AWS4{secret_key}".encode('utf-8'), datestamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        return (
            f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
    
    def _poll_generation_result(self, history_id: str, submit_id: str = None, 
                                 max_wait_time: int = 300, check_interval: int = 5) -> Dict:
        """
        轮询等待图片生成完成
        
        Args:
            history_id: 历史记录ID
            submit_id: 提交ID
            max_wait_time: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            生成结果
        """
        logger.info(f"[Jimeng] 开始轮询，最大等待时间: {max_wait_time}秒")
        
        max_retries = max_wait_time // check_interval
        
        for attempt in range(max_retries):
            time.sleep(check_interval)
            
            # 尝试通过submit_id获取（优先）
            if submit_id:
                image_urls = self._get_images_by_submit_id(submit_id)
                if image_urls:
                    elapsed_time = (attempt + 1) * check_interval
                    logger.info(f"[Jimeng] 图片生成成功！耗时: {elapsed_time}秒，图片数量: {len(image_urls)}")
                    return {
                        "success": True,
                        "history_id": history_id,
                        "submit_id": submit_id,
                        "urls": image_urls
                    }
            
            # 回退到history_id
            image_urls = self._get_images_by_history_id(history_id)
            if image_urls:
                elapsed_time = (attempt + 1) * check_interval
                logger.info(f"[Jimeng] 图片生成成功！耗时: {elapsed_time}秒，图片数量: {len(image_urls)}")
                return {
                    "success": True,
                    "history_id": history_id,
                    "submit_id": submit_id,
                    "urls": image_urls
                }
            
            # 每30秒输出进度
            if (attempt + 1) % 6 == 0:
                elapsed_time = (attempt + 1) * check_interval
                logger.info(f"[Jimeng] 图片生成中... 已等待 {elapsed_time}秒/{max_wait_time}秒")
        
        logger.error(f"[Jimeng] 图片生成超时，已等待 {max_wait_time}秒")
        return {
            "success": False,
            "error": f"生成超时，已等待{max_wait_time}秒"
        }
    
    def _get_images_by_history_id(self, history_id: str) -> Optional[List[str]]:
        """通过history_id获取生成的图片URL"""
        try:
            url = f"{self.base_url}/mweb/v1/get_history_by_ids"
            
            token_info = self.token_manager.get_token('/mweb/v1/get_history_by_ids')
            params = {
                "aid": self.aid,
                "device_platform": "web",
                "region": "cn",
                "web_id": self.token_manager.web_id,
                "da_version": "3.3.2",
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
            
            result = self._send_request("POST", url, params=params, json=data)
            
            if not result or result.get("ret") != "0":
                return None
            
            history_data = result.get("data", {}).get(history_id, {})
            if not history_data:
                return None
            
            status = history_data.get("status")
            
            # 状态50: 任务完成
            if status == 50:
                image_urls = []
                
                # 从resources提取
                resources = history_data.get("resources", [])
                for resource in resources:
                    if resource.get("type") == "image":
                        image_info = resource.get("image_info", {})
                        image_url = image_info.get("image_url")
                        if image_url:
                            image_urls.append(image_url)
                
                # 从item_list提取（备用）
                if not image_urls:
                    item_list = history_data.get("item_list", [])
                    for item in item_list:
                        image = item.get("image", {})
                        if image and "large_images" in image:
                            for large_image in image["large_images"]:
                                if large_image.get("image_url"):
                                    image_urls.append(large_image["image_url"])
                        elif image and image.get("image_url"):
                            image_urls.append(image["image_url"])
                
                return image_urls if image_urls else None
            
            # 状态30: 任务失败
            elif status == 30:
                fail_code = history_data.get("fail_code", "unknown")
                fail_msg = history_data.get("fail_msg", "unknown")
                fail_starling_msg = history_data.get("fail_starling_message", "")
                
                logger.error(f"[Jimeng] ❌ 任务失败！")
                logger.error(f"  fail_code: {fail_code}")
                logger.error(f"  fail_msg: {fail_msg}")
                logger.error(f"  详细信息: {fail_starling_msg}")
                
                # 不返回None，而是抛出异常让上层知道失败了
                raise Exception(f"图片生成失败: {fail_msg} ({fail_code}) - {fail_starling_msg}")
            
            # 其他状态: 处理中
            else:
                logger.debug(f"[Jimeng] 任务状态: {status}（处理中）")
                return None
            
        except Exception as e:
            logger.error(f"[Jimeng] 获取图片异常: {e}")
            return None
    
    def _get_images_by_submit_id(self, submit_id: str) -> Optional[List[str]]:
        """通过submit_id获取生成的图片URL"""
        try:
            url = f"{self.base_url}/mweb/v1/get_history_by_ids"
            
            token_info = self.token_manager.get_token('/mweb/v1/get_history_by_ids')
            params = {
                "aid": self.aid,
                "device_platform": "web",
                "region": "cn",
                "web_id": self.token_manager.web_id,
                "da_version": "3.3.2",
                "web_component_open_flag": "1",
                "web_version": "7.5.0",
                "aigc_features": "app_lip_sync"
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            data = {
                "submit_ids": [submit_id],
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
            
            result = self._send_request("POST", url, params=params, json=data)
            
            if not result or result.get("ret") != "0":
                return None
            
            history_data = result.get("data", {}).get(submit_id, {})
            if not history_data:
                return None
            
            status = history_data.get("status")
            
            if status == 50:  # 任务已完成
                image_urls = []
                
                # 优先从item_list提取
                item_list = history_data.get("item_list", [])
                for item in item_list:
                    image = item.get("image", {})
                    if image and "large_images" in image:
                        for large_image in image["large_images"]:
                            if large_image.get("image_url"):
                                image_urls.append(large_image["image_url"])
                    elif image and image.get("image_url"):
                        image_urls.append(image["image_url"])
                
                # 备用从resources提取
                if not image_urls:
                    resources = history_data.get("resources", [])
                    for resource in resources:
                        if resource.get("type") == "image":
                            image_info = resource.get("image_info", {})
                            if image_info.get("image_url"):
                                image_urls.append(image_info["image_url"])
                
                return image_urls if image_urls else None
            
            return None
            
        except Exception as e:
            logger.error(f"[Jimeng] 获取图片异常: {e}")
            return None
    
    def download_images(self, urls: List[str], save_dir: str = "output") -> List[str]:
        """
        下载图片到本地
        
        Args:
            urls: 图片URL列表
            save_dir: 保存目录
            
        Returns:
            本地文件路径列表
        """
        os.makedirs(save_dir, exist_ok=True)
        
        saved_paths = []
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                # 生成文件名
                filename = f"jimeng_{int(time.time())}_{i}.png"
                filepath = os.path.join(save_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                saved_paths.append(filepath)
                logger.info(f"[Jimeng] 图片已保存: {filepath}")
                
            except Exception as e:
                logger.error(f"[Jimeng] 下载图片失败 {url}: {e}")
        
        return saved_paths
    
    def generate_text_to_video(self, prompt: str, model: str = "s2.0", 
                                ratio: str = "16:9", duration: int = 4) -> Dict:
        """
        文生视频 - 使用正确的API端点（与浏览器一致）
        
        Args:
            prompt: 提示词
            model: 视频模型 (s2.0, s2.0p, p2.0p)
            ratio: 视频比例 (16:9, 9:16, 1:1, 4:3, 3:4)
            duration: 视频时长（秒），默认4秒
            
        Returns:
            {
                "success": bool,
                "task_id": str,
                "url": str,  # 视频URL
                "error": str
            }
        """
        try:
            print(f"\n[1/3] 开始提交视频生成任务...")
            print(f"  - 提示词: {prompt}")
            print(f"  - 模型: {model}")
            print(f"  - 比例: {ratio}")
            print(f"  - 时长: {duration}秒")
            logger.info(f"[Jimeng] 开始文生视频 - 模型: {model}, 比例: {ratio}, 时长: {duration}秒")
            
            # 模型配置 - 使用正确的模型key
            model_map = {
                "s2.0": "dreamina_seedance_40_vision",
                "s2.0p": "dreamina_seedance_40_vision",
                "p2.0p": "dreamina_ailab_generate_video_model_v1.4"
            }
            model_req_key = model_map.get(model, "dreamina_seedance_40_vision")
            
            duration_ms = duration * 1000
            if duration_ms not in [4000, 5000]:
                duration_ms = 4000
            
            # 生成UUID
            submit_id = str(uuid.uuid4())
            draft_id = str(uuid.uuid4())
            component_id = str(uuid.uuid4())
            ability_id = str(uuid.uuid4())
            gen_video_id = str(uuid.uuid4())
            text_to_video_id = str(uuid.uuid4())
            video_gen_input_id = str(uuid.uuid4())
            
            # 使用与浏览器相同的API端点
            url = f"{self.base_url}/mweb/v1/aigc_draft/generate"
            
            babi_param = {
                "scenario": "image_video_generation",
                "feature_key": "aigc_to_video",
                "feature_entrance": "to_video",
                "feature_entrance_detail": "to_video-text_to_video"
            }
            
            # 构建draft_content（与浏览器一致的结构）
            draft_content = {
                "type": "draft",
                "id": draft_id,
                "min_version": "3.3.9",
                "min_features": ["AIGC_Video_UnifiedEdit"],
                "is_from_tsn": True,
                "version": "3.3.12",
                "main_component_id": component_id,
                "component_list": [{
                    "type": "video_base_component",
                    "id": component_id,
                    "min_version": "1.0.0",
                    "aigc_mode": "workbench",
                    "metadata": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "created_platform": 3,
                        "created_platform_version": "",
                        "created_time_in_ms": str(int(time.time() * 1000)),
                        "created_did": ""
                    },
                    "generate_type": "gen_video",
                    "abilities": {
                        "type": "",
                        "id": ability_id,
                        "gen_video": {
                            "type": "",
                            "id": gen_video_id,
                            "text_to_video_params": {
                                "type": "",
                                "id": text_to_video_id,
                                "video_gen_inputs": [{
                                    "type": "",
                                    "id": video_gen_input_id,
                                    "min_version": "3.3.9",
                                    "prompt": prompt,
                                    "video_mode": 2,
                                    "fps": 24,
                                    "duration_ms": duration_ms,
                                    "idip_meta_list": [],
                                    "unified_edit_input": {
                                        "type": "",
                                        "id": str(uuid.uuid4()),
                                        "material_list": [],
                                        "meta_list": [{
                                            "type": "",
                                            "id": str(uuid.uuid4()),
                                            "meta_type": "text",
                                            "text": prompt
                                        }]
                                    }
                                }],
                                "video_aspect_ratio": ratio,
                                "seed": random.randint(1000000000, 9999999999),
                                "model_req_key": model_req_key,
                                "priority": 0
                            },
                            "video_task_extra": json.dumps({
                                "isDefaultSeed": 1,
                                "originSubmitId": submit_id,
                                "isRegenerate": False
                            })
                        }
                    },
                    "process_type": 1
                }]
            }
            
            data = {
                "extend": {
                    "root_model": model_req_key,
                    "workspace_id": 0,  # 0表示默认工作空间
                    "m_video_commerce_info": {
                        "benefit_type": "seedance_20_fast_720p_output",
                        "resource_id": "generate_video",
                        "resource_id_type": "str",
                        "resource_sub_type": "aigc"
                    },
                    "m_video_commerce_info_list": [{
                        "benefit_type": "seedance_20_fast_720p_output",
                        "resource_id": "generate_video",
                        "resource_id_type": "str",
                        "resource_sub_type": "aigc"
                    }]
                },
                "submit_id": submit_id,
                "metrics_extra": json.dumps({
                    "promptSource": "custom",
                    "originSubmitId": submit_id,
                    "isDefaultSeed": 1,
                    "originTemplateId": "",
                    "imageNameMapping": {},
                    "isUseAiGenPrompt": False,
                    "batchNumber": 1,
                    "enterFrom": "click",
                    "position": "page_bottom_box",
                    "functionMode": "omni_reference"
                }),
                "draft_content": json.dumps(draft_content),
                "http_common_info": {"aid": self.aid}
            }
            
            token_info = self.token_manager.get_token('/mweb/v1/aigc_draft/generate')
            params = {
                "babi_param": json.dumps(babi_param),
                "aid": self.aid,
                "device_platform": "web",
                "region": "cn",
                "web_id": self.token_manager.web_id,
                "da_version": "3.3.12",
                "web_component_open_flag": "1",
                "commerce_with_input_video": "1",
                "web_version": "7.5.0",
                "aigc_features": "app_lip_sync"
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            headers, _ = self.token_manager.get_headers(
                '/mweb/v1/aigc_draft/generate',
                referer='https://jimeng.jianying.com/ai-tool/generate?type=video',
                token_info=token_info
            )
            
            # 打印调试信息
            print(f"\n[DEBUG] 请求URL: {url}")
            print(f"[DEBUG] 请求参数: {json.dumps(params, ensure_ascii=False)[:300]}...")
            print(f"[DEBUG] 使用API端点: /mweb/v1/aigc_draft/generate（与浏览器一致）")
            
            # 发送请求
            print(f"\n[2/3] 正在发送API请求...")
            response = self._send_request("POST", url, params=params, json=data, headers=headers)
            
            print(f"\n[DEBUG] API响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            
            if not response or str(response.get('ret')) != '0':
                print(f"\n[ERROR] 视频提交失败！")
                print(f"  - 返回状态: {response.get('ret')}")
                print(f"  - 错误信息: {response}")
                logger.error(f"[Jimeng] 文生视频失败: {response}")
                return {
                    "success": False,
                    "error": f"API返回错误: {response}"
                }
            
            # 获取history_id（从响应的aigc_data中）
            history_id = response.get('data', {}).get('aigc_data', {}).get('history_record_id')
            if not history_id:
                print(f"\n[ERROR] 未获取到history_id！")
                print(f"  - 响应数据: {json.dumps(response.get('data', {}), ensure_ascii=False, indent=2)[:500]}...")
                return {
                    "success": False,
                    "error": "未获取到history_id"
                }
            
            print(f"\n[SUCCESS] 视频任务提交成功！")
            print(f"  - history_id: {history_id}")
            logger.info(f"[Jimeng] 视频提交成功，history_id: {history_id}")
            
            # 轮询等待视频生成（使用history_id轮询，和文生图一样）
            return self._poll_video_result_by_history(history_id, max_wait_time=600, check_interval=10)
            
        except Exception as e:
            logger.error(f"[Jimeng] 文生视频异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_image_to_video(self, image_path: str, prompt: str,
                                 model: str = "s2.0", duration: int = 5) -> Dict:
        """
        图生视频
        
        Args:
            image_path: 参考图片路径
            prompt: 提示词
            model: 视频模型
            duration: 视频时长（秒）
            
        Returns:
            同generate_text_to_video
        """
        try:
            logger.info(f"[Jimeng] 开始图生视频 - 模型: {model}, 时长: {duration}秒")
            
            # 上传图片
            upload_token = self._get_upload_token()
            if not upload_token:
                return {"success": False, "error": "获取上传token失败"}
            
            image_uri = self._upload_image(image_path, upload_token)
            if not image_uri:
                return {"success": False, "error": "上传图片失败"}
            
            logger.info(f"[Jimeng] 图片上传成功，URI: {image_uri}")
            
            # 模型配置
            model_map = {
                "s2.0": {
                    "model_req_key": "dreamina_ic_generate_video_model_vgfm_lite",
                    "benefit_type": "basic_video_operation_vgfm_lite",
                    "fps": 24
                },
                "s2.0p": {
                    "model_req_key": "dreamina_ic_generate_video_model_vgfm1.0",
                    "benefit_type": "basic_video_operation_vgfm",
                    "fps": 24
                }
            }
            
            model_config = model_map.get(model, model_map["s2.0"])
            duration_ms = duration * 1000
            
            submit_id = str(uuid.uuid4())
            
            url = f"{self.base_url}/mweb/v1/generate_video"
            
            babi_param = {
                "scenario": "image_video_generation",
                "feature_key": "image_to_video",
                "feature_entrance": "to_video",
                "feature_entrance_detail": "to_video-image_to_video"
            }
            
            data = {
                "submit_id": submit_id,
                "task_extra": json.dumps({
                    "promptSource": "custom",
                    "originSubmitId": str(uuid.uuid4()),
                    "isDefaultSeed": 1
                }),
                "http_common_info": {"aid": self.aid},
                "input": {
                    "video_gen_inputs": [
                        {
                            "prompt": prompt,
                            "fps": model_config["fps"],
                            "duration_ms": duration_ms,
                            "video_mode": 1,  # 图生视频用1
                            "template_id": "",
                            "first_frame_image": {
                                "image_uri": image_uri,
                                "source_from": "upload"
                            }
                        }
                    ],
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
            
            token_info = self.token_manager.get_token('/mweb/v1/generate_video')
            params = {
                "babi_param": json.dumps(babi_param),
                "aid": self.aid,
                "device_platform": "web",
                "region": "CN",
                "web_id": self.token_manager.web_id,
            }
            
            if token_info.get("msToken"):
                params["msToken"] = token_info["msToken"]
            if token_info.get("a_bogus"):
                params["a_bogus"] = token_info["a_bogus"]
            
            headers, _ = self.token_manager.get_headers(
                '/mweb/v1/generate_video',
                referer='https://jimeng.jianying.com/ai-tool/video/generate'
            )
            
            response = self._send_request("POST", url, params=params, json=data, headers=headers)
            
            if not response or str(response.get('ret')) != '0':
                logger.error(f"[Jimeng] 图生视频失败: {response}")
                return {
                    "success": False,
                    "error": f"API返回错误: {response}"
                }
            
            task_id = response.get('data', {}).get('aigc_data', {}).get('task', {}).get('task_id')
            if not task_id:
                return {
                    "success": False,
                    "error": "未获取到task_id"
                }
            
            logger.info(f"[Jimeng] 图生视频提交成功，task_id: {task_id}")
            
            return self._poll_video_result(task_id)
            
        except Exception as e:
            logger.error(f"[Jimeng] 图生视频异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _poll_video_result_by_history(self, history_id: str, max_wait_time: int = 600, 
                                       check_interval: int = 10) -> Dict:
        """
        通过history_id轮询视频生成结果（与文生图使用相同的接口）
        
        Args:
            history_id: 历史记录ID
            max_wait_time: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            生成结果
        """
        print(f"\n[3/3] 开始轮询视频生成状态...")
        print(f"  - history_id: {history_id}")
        print(f"  - 最大等待时间: {max_wait_time}秒")
        print(f"  - 检查间隔: {check_interval}秒")
        logger.info(f"[Jimeng] 开始轮询视频生成，history_id: {history_id}")
        
        max_retries = max_wait_time // check_interval
        
        for attempt in range(max_retries):
            time.sleep(check_interval)
            
            print(f"\n[轮询 #{attempt+1}/{max_retries}] 正在查询任务状态...")
            
            try:
                # 使用get_history_by_ids接口（与文生图相同）
                url = f"{self.base_url}/mweb/v1/get_history_by_ids"
                
                token_info = self.token_manager.get_token('/mweb/v1/get_history_by_ids')
                params = {
                    "aid": self.aid,
                    "device_platform": "web",
                    "region": "cn",
                    "web_id": self.token_manager.web_id,
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
                
                result = self._send_request("POST", url, params=params, json=data)
                
                print(f"[轮询 #{attempt+1}] API返回: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
                
                if not result or result.get("ret") != "0":
                    print(f"[轮询 #{attempt+1}] API请求失败: ret={result.get('ret') if result else 'None'}")
                    continue
                
                history_data = result.get("data", {}).get(history_id, {})
                if not history_data:
                    print(f"[轮询 #{attempt+1}] 未找到history_id对应的数据")
                    print(f"  - data keys: {list(result.get('data', {}).keys())}")
                    continue
                
                status = history_data.get("status")
                fail_code = history_data.get("fail_code", "")
                
                print(f"\n[轮询 #{attempt+1}] 任务状态: {status}")
                if fail_code:
                    print(f"  - 错误代码: {fail_code}")
                
                # 状态30: 完成
                if status == 30:
                    # 如果有fail_code，说明失败了
                    if fail_code:
                        fail_msg = history_data.get("fail_starling_message", history_data.get("fail_msg", "未知错误"))
                        print(f"\n[ERROR] 视频生成失败！")
                        print(f"  - 错误代码: {fail_code}")
                        print(f"  - 错误信息: {fail_msg}")
                        logger.error(f"[Jimeng] 视频生成失败: fail_code={fail_code}, fail_msg={fail_msg}")
                        return {
                            "success": False,
                            "error": f"视频生成失败 (错误码: {fail_code}): {fail_msg}"
                        }
                    
                    # 尝试获取视频URL
                    video_url = None
                    
                    # 从resources提取
                    resources = history_data.get("resources", [])
                    for resource in resources:
                        if resource.get("type") == "video":
                            video_url = resource.get("video_info", {}).get("video_url")
                            if video_url:
                                break
                    
                    # 从item_list提取（备用）
                    if not video_url:
                        item_list = history_data.get("item_list", [])
                        for item in item_list:
                            video = item.get("video", {})
                            if video and video.get("video_url"):
                                video_url = video["video_url"]
                                break
                    
                    if video_url:
                        elapsed_time = (attempt + 1) * check_interval
                        print(f"\n[SUCCESS] 视频生成成功！耗时: {elapsed_time}秒")
                        print(f"  - 视频URL: {video_url}")
                        logger.info(f"[Jimeng] 视频生成成功！耗时: {elapsed_time}秒")
                        return {
                            "success": True,
                            "history_id": history_id,
                            "url": video_url
                        }
                    else:
                        print(f"\n[WARNING] 状态30但未找到视频URL")
                        print(f"  - 完整数据: {json.dumps(history_data, ensure_ascii=False, indent=2)[:1000]}...")
                        # 继续等待，可能还在处理
                        continue
                
                # 状态40: 失败
                elif status == 40:
                    fail_msg = history_data.get("fail_msg", "未知错误")
                    print(f"\n[ERROR] 视频生成失败 (status=40)！")
                    print(f"  - 错误信息: {fail_msg}")
                    logger.error(f"[Jimeng] 视频生成失败: {fail_msg}")
                    return {
                        "success": False,
                        "error": f"视频生成失败: {fail_msg}"
                    }
                
                # 其他状态: 处理中
                else:
                    print(f"  - 任务处理中... (status={status})")
                    if (attempt + 1) % 6 == 0:
                        elapsed_time = (attempt + 1) * check_interval
                        print(f"  - 已等待 {elapsed_time}秒/{max_wait_time}秒")
                        logger.info(f"[Jimeng] 视频生成中... 已等待 {elapsed_time}秒/{max_wait_time}秒")
                    
            except Exception as e:
                logger.error(f"[Jimeng] 轮询视频状态异常: {e}")
                print(f"[轮询 #{attempt+1}] 异常: {e}")
                continue
        
        logger.error(f"[Jimeng] 视频生成超时，已等待 {max_wait_time}秒")
        return {
            "success": False,
            "error": f"视频生成超时，已等待{max_wait_time}秒"
        }
    
    def _poll_video_result(self, task_id: str, max_wait_time: int = 600, 
                           check_interval: int = 10) -> Dict:
        """
        轮询等待视频生成完成
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒），默认10分钟
            check_interval: 检查间隔（秒）
            
        Returns:
            生成结果
        """
        print(f"\n[3/3] 开始轮询视频生成状态...")
        print(f"  - 最大等待时间: {max_wait_time}秒")
        print(f"  - 检查间隔: {check_interval}秒")
        logger.info(f"[Jimeng] 开始轮询视频生成，最大等待时间: {max_wait_time}秒")
        
        max_retries = max_wait_time // check_interval
        
        for attempt in range(max_retries):
            time.sleep(check_interval)
            
            print(f"\n[轮询 #{attempt+1}/{max_retries}] 正在查询任务状态...")
            
            try:
                url = f"{self.base_url}/mweb/v1/mget_generate_task"
                
                token_info = self.token_manager.get_token('/mweb/v1/mget_generate_task')
                params = {
                    "aid": self.aid,
                    "device_platform": "web",
                    "region": "CN",
                    "web_id": self.token_manager.web_id,
                }
                
                data = {
                    "task_id_list": [task_id],
                    "http_common_info": {"aid": self.aid}
                }
                
                result = self._send_request("POST", url, params=params, json=data)
                
                print(f"[轮询 #{attempt+1}] API返回: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
                
                if not result or result.get("ret") != "0":
                    print(f"[轮询 #{attempt+1}] API请求失败: ret={result.get('ret') if result else 'None'}")
                    continue
                
                # 修复：数据在 task_map 中
                task_data = result.get("data", {}).get("task_map", {}).get(task_id, {})
                if not task_data:
                    print(f"[轮询 #{attempt+1}] 未找到task_id对应的数据")
                    print(f"  - data keys: {list(result.get('data', {}).keys())}")
                    continue
                
                status = task_data.get("status")
                fail_code = task_data.get("fail_code", "")
                
                # 打印状态信息
                print(f"\n[轮询 #{attempt+1}] 任务状态: {status}")
                if fail_code:
                    print(f"  - 错误代码: {fail_code}")
                print(f"  - 完整响应: {json.dumps(task_data, ensure_ascii=False, indent=2)[:1000]}...")
                
                # 状态30: 完成
                if status == 30:
                    video_url = task_data.get("video_url") or task_data.get("result_url")
                    
                    # 如果有fail_code，说明虽然状态是30但实际失败了
                    if fail_code:
                        fail_msg = task_data.get("fail_starling_message", task_data.get("fail_msg", "未知错误"))
                        print(f"\n[ERROR] 视频生成失败（status=30但有错误码）！")
                        print(f"  - 错误代码: {fail_code}")
                        print(f"  - 错误信息: {fail_msg}")
                        print(f"  - 完整数据: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
                        logger.error(f"[Jimeng] 视频生成失败: fail_code={fail_code}, fail_msg={fail_msg}")
                        return {
                            "success": False,
                            "error": f"视频生成失败 (错误码: {fail_code}): {fail_msg}"
                        }
                    
                    if video_url:
                        elapsed_time = (attempt + 1) * check_interval
                        logger.info(f"[Jimeng] 视频生成成功！耗时: {elapsed_time}秒")
                        return {
                            "success": True,
                            "task_id": task_id,
                            "url": video_url
                        }
                    else:
                        logger.error(f"[Jimeng] 视频完成但未找到URL")
                        return {
                            "success": False,
                            "error": "视频完成但未找到下载URL"
                        }
                
                # 状态40: 失败
                elif status == 40:
                    fail_msg = task_data.get("fail_msg", "未知错误")
                    fail_code = task_data.get("fail_code", "unknown")
                    print(f"\n[ERROR] 视频生成失败！")
                    print(f"  - 错误代码: {fail_code}")
                    print(f"  - 错误信息: {fail_msg}")
                    print(f"  - 完整数据: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
                    logger.error(f"[Jimeng] 视频生成失败: {fail_msg}")
                    return {
                        "success": False,
                        "error": f"视频生成失败: {fail_msg}"
                    }
                
                # 其他状态: 处理中
                else:
                    print(f"  - 任务处理中，继续等待...")
                    if (attempt + 1) % 6 == 0:
                        elapsed_time = (attempt + 1) * check_interval
                        print(f"  - 已等待 {elapsed_time}秒/{max_wait_time}秒")
                        logger.info(f"[Jimeng] 视频生成中... 已等待 {elapsed_time}秒/{max_wait_time}秒")
                    
            except Exception as e:
                logger.error(f"[Jimeng] 轮询视频状态异常: {e}")
                continue
        
        logger.error(f"[Jimeng] 视频生成超时，已等待 {max_wait_time}秒")
        return {
            "success": False,
            "error": f"视频生成超时，已等待{max_wait_time}秒"
        }
    
    def download_video(self, url: str, save_dir: str = "output_video") -> str:
        """
        下载视频到本地
        
        Args:
            url: 视频URL
            save_dir: 保存目录
            
        Returns:
            本地文件路径
        """
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            filename = f"jimeng_video_{int(time.time())}.mp4"
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"[Jimeng] 视频已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"[Jimeng] 下载视频失败: {e}")
            return ""
