import sys
sys.path.insert(0, '/mnt/d/Project/seedance/backend')

import requests

# 登录
r1 = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
print(f"登录状态: {r1.status_code}")
print(f"登录返回: {r1.json()}\n")

token = r1.json()["access_token"]

# 获取任务列表
r2 = requests.get("http://localhost:8000/api/tasks/", headers={
    "Authorization": f"Bearer {token}"
}, params={
    "page": 1,
    "page_size": 20
})
print(f"任务列表状态: {r2.status_code}")
print(f"任务列表返回: {r2.text[:1000]}")
