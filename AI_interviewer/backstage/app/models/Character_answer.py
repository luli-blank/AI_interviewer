from sqlalchemy import Column, Integer, String, JSON, DateTime  # 1. 引入 DateTime
from sqlalchemy.sql import func # 可选：用于设置数据库层面的默认时间
from app.db.session import Base

class Character_answer(Base):
    __tablename__ = "character_answers" # 修正：对应你init_db.py里检查的表名，注意这里通常用复数
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(String(50), unique=False, index=True)
    question_and_answer = Column(JSON)
    submissionTime = Column(DateTime, server_default=func.now())