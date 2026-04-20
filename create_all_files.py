#!/usr/bin/env python3
"""批量生成项目文件内容"""
import os
from pathlib import Path

base_dir = Path(__file__).parent

# 定义所有需要创建的文件及其内容
files_to_create = {
    # 后端配置
    "backend/config.py": '''from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "seedance"
    DB_PASSWORD: str = "seedance123"
    DB_NAME: str = "seedance_db"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    SESSION_ID: Optional[str] = None
    MAX_FILE_SIZE: int = 52428800
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"

settings = Settings()
''',
    
    "backend/.env.example": '''# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=seedance
DB_PASSWORD=seedance123
DB_NAME=seedance_db

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Jimeng API
SESSION_ID=

# Upload
MAX_FILE_SIZE=52428800
''',

    "backend/init_db.sql": '''-- 创建数据库
CREATE DATABASE IF NOT EXISTS seedance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER IF NOT EXISTS 'seedance'@'localhost' IDENTIFIED BY 'seedance123';
GRANT ALL PRIVILEGES ON seedance_db.* TO 'seedance'@'localhost';
FLUSH PRIVILEGES;
''',

    "backend/check_deps.py": '''#!/usr/bin/env python3
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

print("\nAll dependencies OK!")
''',

    # 后端模型
    "backend/models/user.py": '''from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
''',

    "backend/models/log.py": '''from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class LogLevelEnum(str, enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(LogLevelEnum), nullable=False)
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
''',

    "backend/models/material.py": '''from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class MaterialTypeEnum(str, enum.Enum):
    image = "image"
    video = "video"


class MaterialSourceEnum(str, enum.Enum):
    manual = "manual"
    api = "api"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(MaterialTypeEnum), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    source = Column(Enum(MaterialSourceEnum), default=MaterialSourceEnum.manual)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
''',

    "backend/models/system_config.py": '''from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
''',

    "backend/models/task_execution.py": '''from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class ExecutionStatusEnum(str, enum.Enum):
    running = "running"
    success = "success"
    failed = "failed"


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.running)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    history_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
''',

    "backend/models/task_image.py": '''from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class TaskImage(Base):
    __tablename__ = "task_images"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    reference_name = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="images")
''',

    # 后端Schema
    "backend/schemas/user.py": '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "admin"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
''',

    "backend/schemas/log.py": '''from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LogResponse(BaseModel):
    id: int
    level: str
    module: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class LogCreate(BaseModel):
    level: str
    module: str
    message: str
''',

    "backend/schemas/material.py": '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MaterialCreate(BaseModel):
    name: str
    type: str
    task_id: Optional[int] = None


class MaterialResponse(BaseModel):
    id: int
    name: str
    type: str
    file_url: str
    file_path: str
    source: str
    task_id: Optional[int]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
''',

    # 后端服务
    "backend/services/jimeng_service.py": '''import requests
from typing import Dict, Any, Optional
from config import settings


class JimengService:
    """即梦API服务"""
    
    BASE_URL = "https://jimeng.jianying.com"
    
    def __init__(self):
        self.session_id = settings.SESSION_ID
        self.headers = {
            "Cookie": f"sessionid={self.session_id}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """生成图片"""
        # TODO: 实现图片生成逻辑
        pass
    
    def generate_video(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """生成视频"""
        # TODO: 实现视频生成逻辑
        pass
    
    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        # TODO: 实现任务状态查询
        pass


jimeng_service = JimengService()
''',

    "backend/services/scheduler.py": '''from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
from models.task import Task, TaskStatusEnum


scheduler = BackgroundScheduler()


def init_scheduler():
    """初始化调度器"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(
            Task.schedule_type == "cron",
            Task.is_deleted == False
        ).all()
        
        for task in tasks:
            if task.cron_expression:
                scheduler.add_job(
                    execute_task,
                    CronTrigger.from_crontab(task.cron_expression),
                    args=[task.id],
                    id=f"task_{task.id}"
                )
        
        scheduler.start()
    finally:
        db.close()


def execute_task(task_id: int):
    """执行任务"""
    # TODO: 实现任务执行逻辑
    pass


def add_task_job(task_id: int, cron_expression: str):
    """添加任务调度"""
    scheduler.add_job(
        execute_task,
        CronTrigger.from_crontab(cron_expression),
        args=[task_id],
        id=f"task_{task_id}"
    )


def remove_task_job(task_id: int):
    """移除任务调度"""
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
''',

    "backend/services/task_runner.py": '''from database import SessionLocal
from models.task import Task, TaskStatusEnum
from models.task_execution import TaskExecution, ExecutionStatusEnum
from services.jimeng_service import jimeng_service
from datetime import datetime


class TaskRunner:
    """任务执行器"""
    
    def run_task(self, task_id: int):
        """执行任务"""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            
            # 创建执行记录
            execution = TaskExecution(
                task_id=task_id,
                status=ExecutionStatusEnum.running
            )
            db.add(execution)
            db.commit()
            
            # 更新任务状态
            task.status = TaskStatusEnum.running
            task.run_count += 1
            db.commit()
            
            # TODO: 执行实际任务逻辑
            
            # 更新执行结果
            execution.status = ExecutionStatusEnum.success
            execution.finished_at = datetime.now()
            db.commit()
            
        except Exception as e:
            # 记录错误
            if 'execution' in locals():
                execution.status = ExecutionStatusEnum.failed
                execution.error_message = str(e)
                db.commit()
        finally:
            db.close()


task_runner = TaskRunner()
''',

    # 后端API
    "backend/api/auth.py": '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserLogin, Token, UserResponse
from core.security import create_access_token, verify_password, get_password_hash
from core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已禁用"
        )
    
    access_token = create_access_token(data={
        "sub": user.username,
        "role": user.role
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
''',

    "backend/api/generation.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.task import Task
from services.jimeng_service import jimeng_service

router = APIRouter(prefix="/generation", tags=["生成"])


@router.post("/image")
async def generate_image(
    task_id: int,
    db: Session = Depends(get_db)
):
    """生成图片"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # TODO: 调用即梦API生成图片
    return {"message": "图片生成任务已提交"}


@router.post("/video")
async def generate_video(
    task_id: int,
    db: Session = Depends(get_db)
):
    """生成视频"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # TODO: 调用即梦API生成视频
    return {"message": "视频生成任务已提交"}
''',

    # 文档
    "DEBUG_GUIDE.md": '''# 调试指南

## 后端调试
- 查看日志: `tail -f logs/backend.log`
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 前端调试
- 查看日志: `tail -f logs/frontend.log`
- 前端地址: http://localhost:5173

## 常见问题
- 端口占用: 执行 `./stop` 清理
- 依赖缺失: `pip install -r requirements.txt`
''',

    "DEBUG_LOGIN.md": '''# 登录调试

## 默认账号
- 用户名: admin
- 密码: admin123

## 登录流程
1. POST /api/auth/login
2. 获取JWT Token
3. Token存储在localStorage
''',

    "DEPLOY.md": '''# 部署指南

## 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

## 快速部署
```bash
pip install -r requirements.txt
cd frontend && npm install
./start
```
''',

    "QUICKSTART.md": '''# 快速开始

## 启动服务
```bash
./start
```

## 访问地址
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API文档: http://localhost:8000/docs

## 默认账号
admin / admin123
''',

    "SCRIPTS.md": '''# 脚本说明

- `./start` - 启动服务
- `./stop` - 停止服务
- `./restart` - 重启服务
- `./status` - 查看状态
''',

    # 测试和工具
    "check_log_table.py": '''#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
cols = inspector.get_columns('system_logs')

print("system_logs表结构:")
for c in cols:
    print(f"  {c['name']}: {c['type']}")
''',

    "check_tables.py": '''#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("数据库表:")
for table in tables:
    print(f"  - {table}")
''',

    "check_users.py": '''#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from database import SessionLocal
from models.user import User

db = SessionLocal()
users = db.query(User).all()

print("用户列表:")
for user in users:
    print(f"  {user.id} - {user.username} ({user.role})")
''',

    "init-frontend.ps1": '''# PowerShell 前端初始化脚本
Set-Location frontend
npm install
Write-Host "Frontend dependencies installed!"
''',

    "reset_admin_password.py": '''#!/usr/bin/env python3
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
''',

    "test_login_api.py": '''#!/usr/bin/env python3
import requests

response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
''',

    "frontend/README.md": '''# SeeDance Frontend

Vue 3 + Vite + Element Plus

## Setup
```bash
npm install
npm run dev
```
''',
}

# 创建所有文件
created_count = 0
for filepath, content in files_to_create.items():
    full_path = base_dir / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding='utf-8')
    created_count += 1
    print(f"✓ {filepath}")

print(f"\n✅ 共创建 {created_count} 个文件")
