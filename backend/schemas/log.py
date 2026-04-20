from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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


class LogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[LogResponse]
