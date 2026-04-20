#!/usr/bin/env python3
from __future__ import annotations

import importlib
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure SQLAlchemy model registry is complete before handling requests.
import models  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seedance-backend")

app = FastAPI(
    title="SeeDance Backend",
    version="1.0.0",
    description="Backend service for SeeDance",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "SeeDance backend is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _try_include_router(module_name: str) -> None:
    try:
        module = importlib.import_module(module_name)
        router = getattr(module, "router", None) or getattr(module, "api_router", None)
        if router is not None:
            app.include_router(router)
            logger.info("Loaded router: %s", module_name)
        else:
            logger.warning("Router missing in module: %s", module_name)
    except Exception as exc:
        logger.warning("Skip router %s: %s", module_name, exc)


# 加载API路由（统一通过 api.__init__.py 入口）
_try_include_router("api")
