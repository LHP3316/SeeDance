from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from schemas.log import LogResponse


class TaskImageRef(BaseModel):
    image_id: int
    reference_name: Optional[str] = None
    sort_order: int = 0


class TaskCreate(BaseModel):
    name: str = Field(..., max_length=200)
    type: str  # image or video
    prompt: str
    model: str
    ratio: str
    duration: int = 4  # 视频时长（秒），默认4秒
    resolution: Optional[str] = None
    image_size: Optional[str] = None
    schedule_type: str = "manual"
    cron_expression: Optional[str] = None
    scheduled_time: datetime  # 执行时间（必填）
    images: List[TaskImageRef] = []
    # 支持直接传图片URL数组（用于快速创建）
    image_urls: Optional[List[str]] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    prompt: Optional[str] = None
    model: Optional[str] = None
    ratio: Optional[str] = None
    duration: Optional[int] = None
    resolution: Optional[str] = None
    image_size: Optional[str] = None
    schedule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    images: Optional[List[TaskImageRef]] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    type: str
    prompt: str
    model: str
    ratio: str
    duration: Optional[int] = None
    resolution: Optional[str] = None
    image_size: Optional[str] = None
    params: Optional[str] = None
    status: str
    schedule_type: str
    cron_expression: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    run_count: int = 0
    is_deleted: bool = False
    error_message: Optional[str] = None
    image_material_id: Optional[int] = None
    video_material_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    id: int
    task_id: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    history_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskList(BaseModel):
    """任务列表响应"""
    total: int
    page: int
    page_size: int
    items: List[TaskResponse]


class TaskLogList(BaseModel):
    """任务日志列表响应"""
    total: int
    page: int
    page_size: int
    items: List[LogResponse]
