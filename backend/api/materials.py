from datetime import datetime
import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import BASE_DIR, PROJECT_ROOT, UPLOAD_DIR
from core.deps import require_admin
from database import get_db
from models.material import Material
from models.task import Task
from models.task_execution import TaskExecution
from models.user import User
from schemas.material import MaterialList, MaterialResponse

router = APIRouter(prefix="/materials", tags=["素材管理"])


def _try_fix_mojibake(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _resolve_material_file_path(material: Material) -> Optional[Path]:
    raw_path = material.file_path or ""
    candidates: list[Path] = []

    if raw_path:
        p = Path(raw_path)
        candidates.append(p)
        if not p.is_absolute():
            candidates.append(PROJECT_ROOT / raw_path)
            candidates.append(BASE_DIR / raw_path)
            if raw_path.startswith("uploads/"):
                candidates.append(UPLOAD_DIR / raw_path[len("uploads/"):])

        fixed_raw = _try_fix_mojibake(raw_path)
        if fixed_raw != raw_path:
            fp = Path(fixed_raw)
            candidates.append(fp)
            if not fp.is_absolute():
                candidates.append(PROJECT_ROOT / fixed_raw)
                candidates.append(BASE_DIR / fixed_raw)
                if fixed_raw.startswith("uploads/"):
                    candidates.append(UPLOAD_DIR / fixed_raw[len("uploads/"):])

    file_url = material.file_url or ""
    if file_url.startswith("/uploads/"):
        rel = file_url[len("/uploads/"):]
        candidates.append(UPLOAD_DIR / rel)

        fixed_url = _try_fix_mojibake(file_url)
        if fixed_url.startswith("/uploads/"):
            candidates.append(UPLOAD_DIR / fixed_url[len("/uploads/"):])

    checked = set()
    for c in candidates:
        r = c.resolve(strict=False)
        key = str(r)
        if key in checked:
            continue
        checked.add(key)
        if r.exists():
            return r
    return None


@router.get("/", response_model=MaterialList)
async def get_materials(
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Material)
    if type:
        query = query.filter(Material.type == type)

    total = query.count()
    materials = (
        query.order_by(Material.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": materials}


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.post("/upload")
async def upload_material(
    file: UploadFile = File(...),
    task_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    upload_dir = UPLOAD_DIR / "materials"
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    safe_name = f"{timestamp}_{abs(hash((file.filename or '') + timestamp)) % 100000000}{ext}"
    file_path = str(upload_dir / safe_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_ext = ext.lower()
    material_type = "video" if file_ext in [".mp4", ".avi", ".mov", ".mkv"] else "image"

    material = Material(
        name=file.filename or safe_name,
        type=material_type,
        file_url=f"/uploads/materials/{safe_name}",
        file_path=file_path,
        source="manual",
        task_id=task_id,
        created_by=current_user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {"id": material.id, "file_url": material.file_url, "message": "Upload success"}


@router.post("/task/{task_id}/save")
async def save_task_result(
    task_id: int,
    file_url: str,
    file_path: str,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    execution = (
        db.query(TaskExecution)
        .filter(TaskExecution.task_id == task_id)
        .order_by(TaskExecution.started_at.desc())
        .first()
    )

    material = Material(
        name=f"{task.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        type=task.type,
        file_url=file_url,
        file_path=file_path,
        source="generated",
        task_id=task_id,
        execution_id=execution.id if execution else None,
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {"id": material.id, "message": "Saved"}


@router.get("/download/{material_id}")
async def download_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    real_path = _resolve_material_file_path(material)
    if not real_path:
        raise HTTPException(status_code=404, detail="Material file not found")

    real_path_str = str(real_path)
    if material.file_path != real_path_str:
        material.file_path = real_path_str
        try:
            rel = real_path.relative_to(UPLOAD_DIR).as_posix()
            material.file_url = f"/uploads/{rel}"
        except ValueError:
            pass
        db.commit()

    media_type = "video/mp4" if str(material.type) == "video" else "image/png"
    filename = material.name or real_path.name
    return FileResponse(path=real_path_str, filename=filename, media_type=media_type)
