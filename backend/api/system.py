from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.deps import require_admin, require_super_admin
from database import get_db
from models.log import SystemLog
from models.system_config import SystemConfig
from models.user import User
from schemas.log import SystemLogList
from schemas.user import UserCreate, UserList, UserResponse, UserUpdate

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    from models.material import Material
    from models.task import Task

    total_tasks = db.query(Task).filter(Task.is_deleted == False).count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    running_tasks = db.query(Task).filter(Task.status == "running").count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()
    failed_tasks = db.query(Task).filter(Task.status == "failed").count()

    total_images = db.query(Material).filter(Material.type == "image").count()
    total_videos = db.query(Material).filter(Material.type == "video").count()

    return {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "running_tasks": running_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "total_images": total_images,
        "total_videos": total_videos,
    }


@router.get("/users", response_model=UserList)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    query = db.query(User).filter(User.role != "super_admin")
    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": users}


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    if user_data.role == "super_admin":
        raise HTTPException(status_code=400, detail="Creating super admin is forbidden")

    from core.security import get_password_hash

    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "super_admin":
        raise HTTPException(status_code=400, detail="Updating super admin is forbidden")

    if user_data.password:
        from core.security import get_password_hash

        user.password_hash = get_password_hash(user_data.password)

    if user_data.role:
        if user_data.role == "super_admin":
            raise HTTPException(status_code=400, detail="Promoting to super admin is forbidden")
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "super_admin":
        raise HTTPException(status_code=400, detail="Deleting super admin is forbidden")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/config/sessionid")
async def get_sessionid(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    config = db.query(SystemConfig).filter(SystemConfig.key == "jimeng_sessionid").first()
    if not config:
        return {"sessionid": "", "configured": False}
    return {
        "sessionid": config.value,
        "configured": bool(config.value),
        "updated_at": config.updated_at,
    }


@router.put("/config/sessionid")
async def update_sessionid(
    sessionid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    config = db.query(SystemConfig).filter(SystemConfig.key == "jimeng_sessionid").first()
    if config:
        config.value = sessionid
        config.updated_by = current_user.id
    else:
        config = SystemConfig(
            key="jimeng_sessionid",
            value=sessionid,
            description="jimeng sessionid",
            updated_by=current_user.id,
        )
        db.add(config)

    db.commit()

    log = SystemLog(
        level="info",
        module="system",
        message=f"{current_user.username} updated sessionid",
        user_id=current_user.id,
    )
    db.add(log)
    db.commit()

    return {"message": "sessionid updated"}


@router.get("/logs", response_model=SystemLogList)
async def get_system_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(SystemLog)
    if level:
        query = query.filter(SystemLog.level == level)
    if module:
        query = query.filter(SystemLog.module == module)

    total = query.count()
    logs = (
        query.order_by(SystemLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": logs}
