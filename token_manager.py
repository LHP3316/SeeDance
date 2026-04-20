"""
即梦AI Token管理器
负责生成签名、Cookie、msToken等认证参数
"""

import random
import hashlib
import time
from typing import Dict, Any, Optional
import logging
import os
import json

logger = logging.getLogger(__name__)


class TokenManager:
    """Token管理器，负责生成认证参数"""
    
    def __init__(self, sessionid: str):
        """
        初始化Token管理器
        
        Args:
            sessionid: 从Cookie中获取的sessionid
        """
        self.sessionid = sessionid
        self.version_code = "5.8.0"
        self.platform_code = "7"
        self.aid = "513695"
        
        # 生成随机ID
        self.web_id = self._generate_web_id()
        self.user_id = self._generate_web_id()
        self.device_id = self._generate_web_id()
        
        logger.info(f"[TokenManager] 初始化成功，web_id: {self.web_id}")
    
    def _generate_web_id(self) -> str:
        """生成19位随机web_id"""
        return ''.join([str(random.randint(0, 9)) for _ in range(19)])
    
    def _generate_ms_token(self) -> str:
        """生成107位随机msToken"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(107))
    
    def _generate_sign(self, api_path: str, timestamp: str) -> str:
        """
        生成sign签名
        
        Args:
            api_path: API路径
            timestamp: 时间戳
            
        Returns:
            MD5签名
        """
        sign_str = f"9e2c|{api_path[-7:]}|{self.platform_code}|{self.version_code}|{timestamp}||11ac"
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def _generate_a_bogus(self) -> str:
        """生成32位随机a_bogus"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(32))
    
    def _generate_cookie(self) -> str:
        """
        生成完整的Cookie字符串
        
        Returns:
            Cookie字符串
        """
        # 使用网页版Cookie中的原始时间戳，避免触发风控
        # 更新时间戳为当前时间，避免过期
        timestamp = int(time.time())  # 使用当前时间戳
        expire_time = timestamp + 31536000  # 1年
        from datetime import datetime, timezone, timedelta
        expire_date_obj = datetime.fromtimestamp(expire_time, tz=timezone.utc)
        expire_date = expire_date_obj.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        
        cookie_parts = [
            f"sessionid={self.sessionid}",
            f"sessionid_ss={self.sessionid}",
            f"_tea_web_id={self.web_id}",
            f"web_id={self.web_id}",
            f"_v2_spipe_web_id={self.web_id}",
            f"uid_tt={self.user_id}",
            f"uid_tt_ss={self.user_id}",
            f"sid_tt={self.sessionid}",
            f"sid_guard={self.sessionid}%7C{timestamp}%7C31536000%7CSat%2C+17-Apr-2027+02%3A54%3A29+GMT",
            f"ssid_ucp_v1=1.0.0-{hashlib.md5((self.sessionid + str(timestamp)).encode()).hexdigest()}",
            f"sid_ucp_v1=1.0.0-{hashlib.md5((self.sessionid + str(timestamp)).encode()).hexdigest()}",
            "store-region=cn-gd",
            "store-region-src=uid",
            "is_staff_user=false",
            "ttwid=1|LlHqsZ2vBHo1qc2ym36T62tRmZ6EgOVqMS-DeTVBE5g|1776667543|dffd461eed29cde363f8545cdc1c53d69babf027ef04facdffeec136b09c329f",  # 添加 ttwid
            "odin_tt=304cd0c3f05aeeab872dc95c8a06892da4c736dd67bfc6adb34994b1f0fb5de540f98077a641aa37d0537d3565f9caf0f38ed5c15e8078d962260e049f77451e",  # 添加 odin_tt
            "s_v_web_id=verify_mo1bb0pe_c9oFbrqI_C3K6_4Fa3_9ROP_uesVHlSzvgqW"  # 添加 s_v_web_id
        ]
        
        return "; ".join(cookie_parts)
    
    def get_token(self, api_path: str = "/") -> Dict[str, str]:
        """
        获取完整的token信息
        
        Args:
            api_path: API路径，用于生成签名
            
        Returns:
            包含cookie、msToken、sign等信息的字典
        """
        timestamp = str(int(time.time()))
        
        return {
            "cookie": self._generate_cookie(),
            "msToken": self._generate_ms_token(),
            "sign": self._generate_sign(api_path, timestamp),
            "a_bogus": self._generate_a_bogus(),
            "device_time": timestamp,
            "web_id": self.web_id
        }
    
    def get_headers(self, api_path: str = "/", referer: str = "https://jimeng.jianying.com/ai-tool/image/generate", token_info: Dict = None) -> Dict[str, str]:
        """
        获取完整的请求头
        
        Args:
            api_path: API路径
            referer: Referer头
            token_info: 可选，外部传入的token_info，避免重复生成
            
        Returns:
            请求头字典
        """
        # 如果没有传入token_info，则生成新的
        if token_info is None:
            token_info = self.get_token(api_path)
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'app-sdk-version': self.version_code,
            'appid': self.aid,
            'appvr': self.version_code,
            'content-type': 'application/json',
            'cookie': token_info["cookie"],
            'device-time': token_info["device_time"],
            'lan': 'zh-Hans',
            'loc': 'cn',
            'origin': 'https://jimeng.jianying.com',
            'pf': self.platform_code,
            'priority': 'u=1, i',
            'referer': referer,
            'sec-ch-ua': '"Chromium";v="131", "Not=A?Brand";v="24", "Google Chrome";v="131"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sign': token_info["sign"],
            'sign-ver': '1',
            'tdid': '',  # 设备ID，留空即可
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        
        # msToken 和 a_bogus 放在 URL 参数中，不再放在 headers 中
        # 这样所有接口都可以使用
        # 不需要特殊处理
        
        return headers, token_info
