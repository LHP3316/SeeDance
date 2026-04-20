#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
cols = inspector.get_columns('system_logs')

print("system_logs表结构:")
for c in cols:
    print(f"  {c['name']}: {c['type']}")
