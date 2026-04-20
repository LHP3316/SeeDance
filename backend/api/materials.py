from pathlib import Path
from typing import Optional
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models.material import Material, MaterialSourceEnum, MaterialTypeEnum
from schemas.material import MaterialListResponse, MaterialResponse

router = APIRouter(prefix="/materials", tags=["绱犳潗绠＄悊"])

BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads" / "materials"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=MaterialListResponse)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Material)

    if type:
        query = query.filter(Material.type == type)

    total = query.count()
    materials = query.order_by(Material.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": materials,
    }


@router.post("/upload", response_model=MaterialResponse)
async def upload_material(
    file: UploadFile = File(...),
    type: str = "image",
    task_id: Optional[int] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if type == "image" and not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="鍙兘涓婁紶鍥剧墖鏂囦欢")

    if type == "video" and not (file.content_type or "").startswith("video/"):
        raise HTTPException(status_code=400, detail="鍙兘涓婁紶瑙嗛鏂囦欢")

    original_name = (file.filename or "").replace("\\", "/").split("/")[-1].strip()
    ext = os.path.splitext(original_name)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    material = Material(
        name=unique_filename,  # 使用真实文件名（UUID格式）
        type=MaterialTypeEnum.image if type == "image" else MaterialTypeEnum.video,
        file_url=f"/uploads/materials/{unique_filename}",
        file_path=str(file_path),
        source=MaterialSourceEnum.manual,
        task_id=task_id,
        created_by=current_user.id,
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return material


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="绱犳潗涓嶅瓨鍦?)

    if os.path.exists(material.file_path):
        os.remove(material.file_path)

    db.delete(material)
    db.commit()

    return {"message": "鍒犻櫎鎴愬姛"}
