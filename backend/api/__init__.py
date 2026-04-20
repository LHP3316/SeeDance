"""
API路由统一入口
所有API路由统一添加 /api 前缀
"""
from fastapi import APIRouter

from . import auth, tasks, materials, system, generation

# 创建带 /api 前缀的主路由
api_router = APIRouter(prefix="/api")

# 注册所有子路由（子路由不需要再加 /api 前缀）
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(materials.router)
api_router.include_router(system.router)
api_router.include_router(generation.router)
