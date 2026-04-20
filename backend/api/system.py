from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.system_config import SystemConfig
from models.user import User
from models.log import SystemLog
from schemas.user import UserCreate, UserResponse
from schemas.log import LogResponse
from core.security import get_password_hash
from core.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/system", tags=["系统管理"])


@router.get("/session")
async def get_session_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取SessionID配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == "jimeng_session_id").first()
    return {"sessionid": config.value if config else ""}


@router.put("/session")
async def update_session_id(
    sessionid: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新SessionID配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == "jimeng_session_id").first()
    
    if config:
        config.value = sessionid.get("sessionid", "")
    else:
        config = SystemConfig(
            key="jimeng_session_id",
            value=sessionid.get("sessionid", ""),
            description="即梦API SessionID"
        )
        db.add(config)
    
    db.commit()
    return {"message": "更新成功"}


@router.get("/users", response_model=dict)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": users
    }


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许删除超级管理员
    if user.role == "super_admin":
        raise HTTPException(status_code=400, detail="不能删除超级管理员")
    
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}


@router.get("/logs", response_model=dict)
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统日志"""
    query = db.query(SystemLog)
    
    if level:
        query = query.filter(SystemLog.level == level)
    
    total = query.count()
    logs = query.order_by(SystemLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": logs
    }
