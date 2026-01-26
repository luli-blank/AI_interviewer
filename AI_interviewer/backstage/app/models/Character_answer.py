"""
性格测试答案模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class Character_answer(Base):
    """性格测试答案表（匹配实际数据库结构）"""
    __tablename__ = "character_answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(String(50), nullable=True, index=True, comment="用户ID")  # 数据库中是驼峰命名
    question_and_answer = Column(JSON, nullable=True, comment="问题和答案的JSON数据")
    submissionTime = Column(DateTime, server_default=func.now(), comment="提交时间")
    analysis_report = Column(JSON, nullable=True, comment="分析报告JSON")
    
    def __repr__(self):
        return f"<Character_answer(id={self.id}, userId={self.userId})>"
