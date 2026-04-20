#!/usr/bin/env python3
import requests

# 先登录获取token
login_resp = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
print("登录响应:", login_resp.status_code)
print("登录返回:", login_resp.json())

token = login_resp.json().get("access_token")
print("\nToken:", token[:50] + "...")

# 测试任务列表
headers = {"Authorization": f"Bearer {token}"}
tasks_resp = requests.get(
    "http://localhost:8000/api/tasks/",
    headers=headers,
    params={"page": 1, "page_size": 20}
)
print("\n任务列表响应:", tasks_resp.status_code)
print("任务列表返回:", tasks_resp.text[:500])
