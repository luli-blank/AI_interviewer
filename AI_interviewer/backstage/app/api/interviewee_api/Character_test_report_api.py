# Character_test_report_api.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import OpenAI

# 引入你的 Pydantic 模型 (schemas)
from app.schemas.Character_test_report import ReportSchema
# 引入数据库会话依赖
from app.db.session import get_db
from app.core.get_user import get_current_user_id 
from app.models.Character_answer import Character_answer
from dotenv import load_dotenv  # <--- 加上这一行
import os

load_dotenv()  # 这样这行代码才会被识别
router = APIRouter()

def _default_radar(personality_type: str) -> list[dict]:
    """
    为缺失雷达字段的历史报告提供一个可用的默认值（0-100）。
    ESFJ：按你的需求维度做更贴合的默认分。
    其他类型：基于字母做一个简单启发式（不追求严格心理学，只保证可用与稳定）。
    """
    pt = (personality_type or "").upper().strip()

    # 你的指定：ESFJ
    if pt == "ESFJ":
        return [
            {"name": "理解与交流能力", "score": 88},
            {"name": "团队协作能力", "score": 92},
            {"name": "服务意识", "score": 95},
            {"name": "执行与责任感", "score": 85},
            {"name": "抗压与适应能力", "score": 65},
        ]

    # 通用启发式
    e = 10 if "E" in pt else 0
    f = 10 if "F" in pt else 0
    j = 10 if "J" in pt else 0
    n = 5 if "N" in pt else 0
    s = 5 if "S" in pt else 0
    t = 10 if "T" in pt else 0
    i = 10 if "I" in pt else 0
    p = 10 if "P" in pt else 0

    def clamp(x: int) -> int:
        return max(0, min(100, x))

    communication = clamp(60 + e + n - i)
    teamwork = clamp(60 + e + f - i)
    service = clamp(55 + f + s - t)
    execution = clamp(55 + j + s - p)
    stress = clamp(55 + t + p - f)  # F 偏向关系，冲突压力可能更高 => 分稍低

    return [
        {"name": "理解与交流能力", "score": communication},
        {"name": "团队协作能力", "score": teamwork},
        {"name": "服务意识", "score": service},
        {"name": "执行与责任感", "score": execution},
        {"name": "抗压与适应能力", "score": stress},
    ]


def _default_motivation(personality_type: str) -> dict:
    pt = (personality_type or "").upper().strip()
    if pt == "ESFJ":
        return {
            "maslow_focus": ["社交需求（归属感）", "尊重需求（社会认同）"],
            "motivation_summary": "你通常更容易被团队归属感、被认可的成就感以及对他人产生正向影响所驱动。",
            "ideal_environment": [
                "团队氛围和谐、协作清晰",
                "有明确晋升/成长通道与阶段性目标",
                "即时的正面反馈与可见的工作成果",
                "能与人频繁互动、帮助他人的岗位场景",
            ],
            "risk_warnings": [
                "若岗位长期高强度竞争、负反馈密集，可能更易产生压力与情绪消耗",
                "若工作环境缺乏人际互动（如长期封闭式分析/纯研发），绩效潜力可能受阻",
            ],
        }
    return {
        "maslow_focus": ["成长需求", "成就与认可"],
        "motivation_summary": "你的长期动力通常来自成长、掌控感与阶段性成就反馈。",
        "ideal_environment": ["目标清晰", "反馈及时", "能持续学习与承担责任"],
        "risk_warnings": ["长期缺乏反馈或目标不清晰，可能导致动力下降"],
    }


def _ensure_extended_fields(report: dict) -> dict:
    """为旧缓存/旧模型返回补齐新字段，避免前端升级后缺字段报错。"""
    if not isinstance(report, dict):
        return report

    pt = report.get("personality_type", "") if isinstance(report.get("personality_type", ""), str) else ""

    if "competency_radar" not in report or not report.get("competency_radar"):
        report["competency_radar"] = _default_radar(pt)

    if "motivation_values" not in report or not isinstance(report.get("motivation_values"), dict):
        report["motivation_values"] = _default_motivation(pt)
    else:
        mv = report["motivation_values"]
        mv.setdefault("maslow_focus", [])
        mv.setdefault("motivation_summary", "")
        mv.setdefault("ideal_environment", [])
        mv.setdefault("risk_warnings", [])
        report["motivation_values"] = mv

    return report
def _force_clean_llm_lists(report: dict) -> dict:
    """
    强制清洗 AI 返回的数据。
    如果 motivation_values 中的字段是字符串（如 'A、B, C'），强制切割为列表 ['A', 'B', 'C']。
    解决 Pydantic 报错：Input should be a valid list
    """
    if not isinstance(report, dict):
        return report

    mv = report.get("motivation_values")
    # 如果 motivation_values 存在且是字典，才进行清洗
    if isinstance(mv, dict):
        # 需要强制转列表的字段名
        target_fields = ["maslow_focus", "ideal_environment", "risk_warnings"]
        
        for field in target_fields:
            val = mv.get(field)
            # 核心逻辑：如果是字符串，就手动切割
            if isinstance(val, str):
                # 1. 替换中文顿号、中文逗号为英文逗号
                # 2. 按逗号切割
                # 3. 去除首尾空格，并过滤掉空项
                cleaned_list = [
                    item.strip() 
                    for item in val.replace("、", ",").replace("，", ",").split(",") 
                    if item.strip()
                ]
                mv[field] = cleaned_list # 回写清洗后的列表
        
        report["motivation_values"] = mv # 更新回主字典
        
    return report

@router.get("/generate_report", response_model=ReportSchema)
async def generate_report(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    根据数据库中的问答对生成测试报告。
    逻辑：优先读取数据库已有的分析结果；如果没有，则调用 AI 生成并保存。
    """
    # 1. 取该用户最新一条记录
    result = await db.execute(
        select(Character_answer)
        .where(Character_answer.userId == current_user_id)
        .order_by(Character_answer.submissionTime.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if not record:
        # 无记录时，返回一个完整的空结构（包含新增字段），避免前端渲染报错
        empty_report = {
            "total": 0,
            "personality_type": "",
            "career_preferences": [],
            "strengths": [],
            "weaknesses": [],
            "summary": "尚未提交任何问卷数据，无法生成测试报告。",
        }
        empty_report = _ensure_extended_fields(empty_report)
        return ReportSchema(**empty_report)

    # =================================================================
    # NEW: 检查数据库中是否已经有分析结果 (缓存机制)
    # =================================================================
    # 假设数据库模型中的字段名为 analysis_report (请确保 models/Character_answer.py 中有此字段)
    if record.analysis_report:
        print("✅ 命中缓存：直接从数据库返回分析报告，无需调用 AI。")
        # 直接将数据库存储的 JSON (字典) 转为 Schema 返回
        # 如果数据库存的是字符串，这里需要 json.loads(record.analysis_report)
        cached = record.analysis_report
        cached = _ensure_extended_fields(cached)
        # 可选：补齐后回写一次，保证后续直接命中完整字段
        try:
            record.analysis_report = cached
            await db.commit()
            await db.refresh(record)
        except Exception:
            await db.rollback()
        return ReportSchema(**cached)

    # =================================================================
    # 如果数据库中 analysis_report 为 NULL，则执行 AI 分析流程
    # =================================================================
    print("⏳ 未找到缓存报告，正在调用 AI 进行分析...")

    qa_list = record.question_and_answer  # 这是 JSON 列表

    # -----------------------------
    # 生成 Prompt
    # -----------------------------
    qa_text = "\n".join([
        f"Q{idx}: {qa['question']}\nA{idx}: {qa['answer']}\n"
        for idx, qa in enumerate(qa_list, 1)
    ])

    prompt = f"""
你是一名资深职业性格与职业规划分析专家。
以下是用户提交的 MBTI 风格的问卷问答对，请你根据内容生成一份结构化的职业性格分析报告。

要求：
1. 必须返回 JSON 格式（纯 JSON，不要 markdown，不要多余文本）。
2. 字段包括（字段名必须完全一致）：
   - total：问答对数量（整数）
   - personality_type：根据问答推测的 MBTI 类型（字符串，例如 INFP、ESTJ 等）
   - career_preferences：根据用户性格偏好推荐的职业方向（字符串列表）
   - strengths：用户在职场上的主要优势（字符串列表）
   - weaknesses：用户在职场上的潜在劣势或注意点（字符串列表）
   - summary：对用户职业性格与发展建议的总体总结（字符串）
   - competency_radar：职业竞争力雷达图（列表，长度5；每项为对象：{{"name":"维度名", "score":"0-100整数"}})
       维度必须包含且顺序建议如下：
       1) 理解与交流能力
       2) 团队协作能力
       3) 服务意识
       4) 执行与责任感
       5) 抗压与适应能力
   - motivation_values：职业动机与价值观适配（对象）
     必须基于候选人的真实回答，字段要求如下：
{{
    "maslow_focus": ["维度1", "维度2"], 
    "motivation_summary": "概括候选人的核心驱动力",
    "ideal_environment": ["环境特点1", "环境特点2"],
    "risk_warnings": ["风险点1", "风险点2"]
}}

注意：
1. maslow_focus 必须从以下维度中选择 1-2 个放入列表：生理需求-薪资、安全需求-稳定、社交需求-归属、尊重需求-认可、自我实现 。
2. ideal_environment 和 risk_warnings 必须返回字符串列表（List of strings），严禁返回单个字符串 [cite: 12]。

以下为问答内容：
{qa_text}

请输出纯 JSON，严禁使用 markdown 代码块包裹。
"""

    # -----------------------------
    # 调用 LLM 生成报告
    # -----------------------------
    raw_text = ""
    try:
        # 建议加上 timeout 防止请求卡死
        client = OpenAI(
            api_key=os.getenv("Deepseek_API_Key"),
            base_url="https://api.deepseek.com",
            timeout=60.0 # 设置 60秒超时
        )

        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一名资深职业性格与职业规划分析专家，精通 MBTI 理论及其在职业发展中的应用。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        raw_text = completion.choices[0].message.content.strip()
        print(raw_text)
    except Exception as e:
        print("❌ LLM API 调用失败：", e)
        # 这里可以选择抛出异常，或者返回一个空的报告结构
        raise HTTPException(500, f"大模型接口调用失败: {str(e)}")

    # -----------------------------
    # 解析 JSON
    # -----------------------------
    report_json = {}
    
    # 简单的清洗逻辑，防止 AI 返回 ```json 包裹
    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "")
    elif raw_text.startswith("```"):
         raw_text = raw_text.replace("```", "")

    try:
        report_json = json.loads(raw_text)
    except json.JSONDecodeError:
        print("❌ LLM 返回格式不规范：", raw_text)
        raise HTTPException(500, "大模型返回了非 JSON 内容")
    # ==========================================
    # 【新增代码】在此处调用清洗函数，修复格式错误
    # ==========================================
    report_json = _force_clean_llm_lists(report_json) 
    # ==========================================

    # 原有的补齐字段逻辑保持不变
    report_json = _ensure_extended_fields(report_json)

    # =================================================================
    # NEW: 将生成的报告回写到数据库 (更新操作)
    # =================================================================
    try:
        print("💾 正在将新生成的报告保存到数据库...")
        record.analysis_report = report_json # 更新字段
        await db.commit()       # 提交事务
        await db.refresh(record) # 刷新数据
        print("✅ 数据库更新成功！")
    except Exception as e:
        print(f"⚠️ 报告已生成但保存数据库失败: {e}")
        # 这里即使保存失败，为了用户体验，也可以先把结果返回给前端
        # 但通常建议 rollback 防止事务锁死
        await db.rollback()

    return ReportSchema(**report_json)
