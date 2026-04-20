#!/bin/bash
cd /mnt/d/Project/seedance
source ~/miniconda3/etc/profile.d/conda.sh
conda activate seedance

cd backend
python << 'EOF'
import sys
sys.path.insert(0, '.')
from main import app

print("=" * 80)
print("SeeDance API 端点清单")
print("=" * 80)

routes = []
for route in app.routes:
    if hasattr(route, 'methods'):
        for method in route.methods:
            if method not in ['HEAD', 'OPTIONS']:
                routes.append((method, route.path))

routes.sort(key=lambda x: x[1])

current_prefix = ""
for method, path in routes:
    parts = path.split('/')
    prefix = '/' + '/'.join(parts[1:3]) if len(parts) > 2 else path
    
    if prefix != current_prefix:
        current_prefix = prefix
        print(f"\n{'─' * 60}")
        print(f"{prefix}")
        print(f"{'─' * 60}")
    
    print(f"  {method:6s} {path}")

print(f"\n{'=' * 80}")
print(f"总计: {len(routes)} 个API端点")
print(f"{'=' * 80}")
EOF
