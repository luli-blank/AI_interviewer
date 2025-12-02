from pydantic import BaseModel
from typing import List, Optional

# 定义单个选项的结构
class SurveyOption(BaseModel):
    label: str
    value: str

# 定义单个题目的结构
class SurveyQuestion(BaseModel):
    id: str
    title: str
    required: bool = True
    options: List[SurveyOption]

# 定义接口返回的整体结构
class SurveyResponse(BaseModel):
    code: int
    msg: str
    data: List[SurveyQuestion]