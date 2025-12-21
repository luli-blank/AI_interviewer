from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InterviewRecordBase(BaseModel):
    position_id: int
    interviewer_id: int

class InterviewRecordCreate(InterviewRecordBase):
    pass

class InterviewRecord(InterviewRecordBase):
    id: int
    user_id: int
    time: datetime
    
    # 为了方便前端展示，可以包含关联的名称信息
    position_name: Optional[str] = None
    interviewer_name: Optional[str] = None

    class Config:
        orm_mode = True
