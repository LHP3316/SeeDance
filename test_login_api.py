#!/usr/bin/env python3
import requests

response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
