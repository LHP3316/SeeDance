from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class TaskImage(Base):
    __tablename__ = "task_images"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    image_url = Column(String(500), nullable=True)  # 图片URL
    reference_name = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="images")
