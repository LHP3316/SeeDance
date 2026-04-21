#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("数据库表:")
for table in tables:
    print(f"  - {table}")
