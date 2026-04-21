from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class MaterialTypeEnum(str, enum.Enum):
    image = "image"
    video = "video"


class MaterialSourceEnum(str, enum.Enum):
    manual = "manual"
    api = "api"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 真实文件名（UUID格式）
    type = Column(Enum(MaterialTypeEnum), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    source = Column(Enum(MaterialSourceEnum), default=MaterialSourceEnum.manual)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
