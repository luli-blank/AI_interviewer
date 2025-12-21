from pydantic import BaseModel
from typing import Optional, List

class Position(BaseModel):
    id: int
    position_name: str
    description: Optional[str] = None  # ✅ 允许 None

    class Config:
        orm_mode = True  # ✅ 启用 ORM 模式

class InterviewerInfo(BaseModel):
    id: int
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        orm_mode = True

class PositionWithInterviewers(BaseModel):
    id: int
    position_name: str
    description: Optional[str] = None
    interviewers: List[InterviewerInfo] = []

    class Config:
        orm_mode = True
