from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum


class ExecutionStatusEnum(str, enum.Enum):
    running = "running"
    success = "success"
    failed = "failed"


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(Enum(ExecutionStatusEnum), default=ExecutionStatusEnum.running)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)  # 使用数据库中已有的字段名
    duration_seconds = Column(Integer, nullable=True)
    history_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    output_files = Column(Text, nullable=True)  # 生成的文件路径列表（JSON格式）
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="executions")
