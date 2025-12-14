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

router = APIRouter()

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
        return ReportSchema(
            total=0,
            quality_score=0, # 注意：ReportSchema 定义里是否有这个字段，请根据实际情况调整
            issues=["尚未提交任何问卷数据"],
            summary="无可生成的测试报告"
        )

    # =================================================================
    # NEW: 检查数据库中是否已经有分析结果 (缓存机制)
    # =================================================================
    # 假设数据库模型中的字段名为 analysis_report (请确保 models/Character_answer.py 中有此字段)
    if record.analysis_report:
        print("✅ 命中缓存：直接从数据库返回分析报告，无需调用 AI。")
        # 直接将数据库存储的 JSON (字典) 转为 Schema 返回
        # 如果数据库存的是字符串，这里需要 json.loads(record.analysis_report)
        return ReportSchema(**record.analysis_report)

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
1. 必须返回 JSON 格式。
2. 字段包括：
   - total：问答对数量（整数）
   - personality_type：根据问答推测的 MBTI 类型（字符串，例如 INFP、ESTJ 等）
   - career_preferences：根据用户性格偏好推荐的职业方向（字符串列表）
   - strengths：用户在职场上的主要优势（字符串列表）
   - weaknesses：用户在职场上的潜在劣势或注意点（字符串列表）
   - summary：对用户职业性格与发展建议的总体总结（字符串）

以下为问答内容：
{qa_text}

请输出符合 JSON 结构的职业性格分析报告,不使用markdown格式返回。
"""

    # -----------------------------
    # 调用 LLM 生成报告
    # -----------------------------
    raw_text = ""
    try:
        # 建议加上 timeout 防止请求卡死
        client = OpenAI(
            api_key="sk-328183fb945949288a55c7712c2cc706", 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=60.0 # 设置 60秒超时
        )

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一名资深职业性格与职业规划分析专家，精通 MBTI 理论及其在职业发展中的应用。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        raw_text = completion.choices[0].message.content.strip()

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