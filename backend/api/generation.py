from fastapi import APIRouter, Depends, HTTPException
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
