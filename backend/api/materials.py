from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime
from database import get_db
from models.material import Material, MaterialTypeEnum, MaterialSourceEnum
from schemas.material import MaterialCreate, MaterialResponse
from core.deps import get_current_user
from config import settings

router = APIRouter(prefix="/materials", tags=["素材管理"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=dict)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取素材列表"""
    query = db.query(Material)
    
    if type:
        query = query.filter(Material.type == type)
    
    total = query.count()
    materials = query.order_by(Material.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": materials
    }


@router.post("/upload", response_model=MaterialResponse)
async def upload_material(
    file: UploadFile = File(...),
    type: str = "image",
    task_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传素材"""
    # 验证文件类型
    if type == "image" and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    if type == "video" and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="只能上传视频文件")
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 创建素材记录
    material = Material(
        name=file.filename,
        type=MaterialTypeEnum.image if type == "image" else MaterialTypeEnum.video,
        file_url=f"/uploads/{unique_filename}",
        file_path=file_path,
        source=MaterialSourceEnum.manual,
        task_id=task_id,
        created_by=current_user.id
    )
    
    db.add(material)
    db.commit()
    db.refresh(material)
    
    return material


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除素材"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    # 删除物理文件
    if os.path.exists(material.file_path):
        os.remove(material.file_path)
    
    db.delete(material)
    db.commit()
    
    return {"message": "删除成功"}
