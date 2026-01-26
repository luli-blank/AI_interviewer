"""
面试题目模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class QuestionDifficulty(str, enum.Enum):
    """题目难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionCategory(str, enum.Enum):
    """题目分类枚举"""
    SELF_INTRO = "self_intro"
    PROJECT = "project"
    BASIC_KNOWLEDGE = "basic_knowledge"
    ALGORITHM = "algorithm"
    SCENARIO = "scenario"
    REVERSE = "reverse"


class InterviewQuestion(Base):
    """面试题目表"""
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_text = Column(Text, nullable=False, comment="问题文本")
    reference_answer = Column(Text, nullable=True, comment="参考答案/评判标准")
    category = Column(String(50), nullable=False, default="basic_knowledge", comment="问题分类")
    difficulty = Column(String(20), nullable=False, default="medium", comment="难度等级")
    tags = Column(String(500), nullable=True, comment="标签，逗号分隔")
    job_type = Column(String(100), nullable=True, comment="适用岗位类型")
    
    # 元数据
    is_active = Column(Boolean, default=True, comment="是否启用")
    usage_count = Column(Integer, default=0, comment="使用次数")
    avg_score = Column(Integer, nullable=True, comment="平均得分")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<InterviewQuestion(id={self.id}, category={self.category}, difficulty={self.difficulty})>"


class InterviewQuestionUsage(Base):
    """面试题目使用记录表"""
    __tablename__ = "interview_question_usage"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(Integer, nullable=False, index=True, comment="题目ID")
    session_id = Column(String(100), nullable=False, index=True, comment="会话ID")
    user_id = Column(String(100), nullable=False, index=True, comment="用户ID")
    user_answer = Column(Text, nullable=True, comment="用户回答")
    score = Column(Integer, nullable=True, comment="得分")
    feedback = Column(Text, nullable=True, comment="评价反馈")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<InterviewQuestionUsage(id={self.id}, question_id={self.question_id}, session_id={self.session_id})>"
