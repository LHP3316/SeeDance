from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, Boolean, BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class TaskTypeEnum(str, enum.Enum):
    image = "image"
    video = "video"


class TaskStatusEnum(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ScheduleTypeEnum(str, enum.Enum):
    manual = "manual"
    cron = "cron"
    once = "once"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum(TaskTypeEnum), nullable=False)
    prompt = Column(Text, nullable=False)
    model = Column(String(50), nullable=False)
    ratio = Column(String(20), nullable=False)
    duration = Column(String(20), nullable=True)  # 视频时长(如 "4s", "5s")
    resolution = Column(String(20), nullable=True)  # 分辨率 2k/4k
    image_size = Column(String(20), nullable=True)  # 图片尺寸
    params = Column(String(1000), nullable=True)  # 扩展参数JSON
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.pending, nullable=False)
    schedule_type = Column(Enum(ScheduleTypeEnum), default=ScheduleTypeEnum.manual, nullable=False)
    cron_expression = Column(String(100), nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    next_run_time = Column(DateTime, nullable=True)
    last_run_time = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    image_material_id = Column(Integer, nullable=True)
    video_material_id = Column(Integer, nullable=True)
    history_record_id = Column(String(100), nullable=True)  # 即梦平台历史记录ID
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    images = relationship("TaskImage", back_populates="task", cascade="all, delete-orphan")
    executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")
