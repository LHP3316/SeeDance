from pydantic import BaseModel
from typing import Optional, List
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


class MaterialListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[MaterialResponse]
