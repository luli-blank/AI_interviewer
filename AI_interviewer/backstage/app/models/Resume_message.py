from sqlalchemy import Column, String, Text, DateTime, func
from app.db.session import Base
import uuid

class Resume_messages(Base):
    __tablename__ = "interview_resume_messages"

    # === 1. 基础信息 ===
    # 使用 String(36) 存储 UUID，作为主键
    session_id = Column(String(36), primary_key=True, index=True)
    # 用户ID，不可为空
    user_id = Column(String(36), nullable=False, index=True)

    # === 2. 核心业务字段 ===
    job_name = Column(String(255), nullable=False)
    job_desc = Column(Text, nullable=True)          # 职位描述通常较长，使用 Text
    
    # 修改后的公司字段
    company_intended = Column(String(255), nullable=True)
    company_intended_type = Column(Text, nullable=True)
    
    # 简历信息
    resume_text = Column(Text, nullable=True)       # 简历文本
    resume_file_path = Column(String(512), nullable=True) # 文件存储路径
    resume_file_text = Column(Text, nullable=True) 
    # === 3. 时间戳 ===
    created_at = Column(DateTime, server_default=func.now())

    # === 初始化逻辑 ===
    def __init__(self, *args, **kwargs):
        # 逻辑1：如果创建时没传 Session ID，自动生成 UUID
        if "session_id" not in kwargs or not kwargs["session_id"]:
            kwargs["session_id"] = str(uuid.uuid4())
        
        # (已删除 status 的默认值设置，因为字段已被移除)

        super().__init__(*args, **kwargs)

        # 逻辑2：必填字段校验
        if not self.job_name:
            raise ValueError("Job Name is required for an interview session.")
        
        # 新增逻辑：既然数据库定义 user_id 不可为空，这里最好也校验一下
        if not self.user_id:
             raise ValueError("User ID is required.")

        