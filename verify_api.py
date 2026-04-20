#!/usr/bin/env python3
"""验证所有API端点是否已注册"""
import sys
sys.path.insert(0, 'backend')

from main import app

print("=" * 80)
print("SeeDance API 端点清单")
print("=" * 80)

routes = []
for route in app.routes:
    if hasattr(route, 'methods'):
        for method in route.methods:
            if method not in ['HEAD', 'OPTIONS']:
                routes.append({
                    'method': method,
                    'path': route.path,
                    'name': getattr(route, 'name', '')
                })

# 按路径排序
routes.sort(key=lambda x: x['path'])

# 分组显示
current_prefix = ""
for route in routes:
    # 提取前缀
    parts = route['path'].split('/')
    if len(parts) > 2:
        prefix = '/' + parts[1] + '/' + parts[2] if len(parts) > 3 else '/' + parts[1]
    else:
        prefix = route['path']
    
    if prefix != current_prefix:
        current_prefix = prefix
        print(f"\n{'─' * 60}")
        print(f"{prefix}")
        print(f"{'─' * 60}")
    
    print(f"  {route['method']:6s} {route['path']}")

print(f"\n{'=' * 80}")
print(f"总计: {len(routes)} 个API端点")
print(f"{'=' * 80}")
