from pydantic import BaseModel, Field


class CompetencyRadarItem(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)


class MotivationValues(BaseModel):
    # 马斯洛需求侧重点（例如：归属感、社会认同）
    maslow_focus: list[str] = []
    # 动机总结
    motivation_summary: str = ""
    # 理想工作环境建议
    ideal_environment: list[str] = []
    # 风险预警
    risk_warnings: list[str] = []


# 报告返回结构
class ReportSchema(BaseModel):
    total: int
    personality_type: str
    career_preferences: list[str]
    strengths: list[str]
    weaknesses: list[str]
    summary: str

    # 新增：职业竞争力雷达图（核心能力量化）
    competency_radar: list[CompetencyRadarItem] = []

    # 新增：职业动机与价值观适配（深度分析）
    motivation_values: MotivationValues = MotivationValues()