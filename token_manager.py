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
        timestamp = int(time.time())
        expire_time = timestamp + 60 * 24 * 60 * 60  # 60天后
        expire_date = time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", time.gmtime(expire_time))
        
        cookie_parts = [
            f"sessionid={self.sessionid}",
            f"sessionid_ss={self.sessionid}",
            f"_tea_web_id={self.web_id}",
            f"web_id={self.web_id}",
            f"_v2_spipe_web_id={self.web_id}",
            f"uid_tt={self.user_id}",
            f"uid_tt_ss={self.user_id}",
            f"sid_tt={self.sessionid}",
            f"sid_guard={self.sessionid}%7C{timestamp}%7C5184000%7C{expire_date}",
            f"ssid_ucp_v1=1.0.0-{hashlib.md5((self.sessionid + str(timestamp)).encode()).hexdigest()}",
            f"sid_ucp_v1=1.0.0-{hashlib.md5((self.sessionid + str(timestamp)).encode()).hexdigest()}",
            "store-region=cn-gd",
            "store-region-src=uid",
            "is_staff_user=false"
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
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sign': token_info["sign"],
            'sign-ver': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
        
        # 非生成接口保留 msToken 和 a-bogus
        if api_path != '/mweb/v1/aigc_draft/generate':
            headers['msToken'] = token_info["msToken"]
            headers['a-bogus'] = token_info["a_bogus"]
        
        return headers, token_info
