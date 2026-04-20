#!/usr/bin/env python3
"""Check if all dependencies are installed"""
import sys

required = ['fastapi', 'sqlalchemy', 'uvicorn', 'pydantic', 'pymysql']

for pkg in required:
    try:
        __import__(pkg.replace('-', '_'))
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg} - pip install {pkg}")
        sys.exit(1)

print("
All dependencies OK!")
