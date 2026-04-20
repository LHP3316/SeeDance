from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class LogLevelEnum(str, enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(LogLevelEnum), nullable=False)
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
