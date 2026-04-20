#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import SessionLocal
from models.user import User

db = SessionLocal()
users = db.query(User).all()

print("用户列表:")
for user in users:
    print(f"  {user.id} - {user.username} ({user.role})")
