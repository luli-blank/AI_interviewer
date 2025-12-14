from pydantic import BaseModel

# 报告返回结构
class ReportSchema(BaseModel):
    total: int
    personality_type: str
    career_preferences: list[str]
    strengths: list[str]
    weaknesses: list[str]
    summary:str