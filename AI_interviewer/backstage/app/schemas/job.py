from pydantic import BaseModel
from typing import Optional, List

class Job(BaseModel):
    position_id: int
    position_name: str
    interviewer_name: str
    description: Optional[str] = None  # ✅ 允许 None

    class Config:
        orm_mode = False  # ✅ 启用 ORM 模式