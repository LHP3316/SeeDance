#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import SessionLocal
from models.user import User
from core.security import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    user.password_hash = get_password_hash("admin123")
    db.commit()
    print("Admin password reset to: admin123")
else:
    print("Admin user not found")
