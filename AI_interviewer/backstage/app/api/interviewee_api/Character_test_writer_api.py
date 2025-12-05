from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func  # 引入 select 用于查询, func 用于数据库函数

# 引入你的 Pydantic 模型 (schemas)
from app.schemas.Character_test_writer_problem import SurveyQuestion, SurveyResponse
# 引入你的 ORM 模型 (models)
from app.models.Character_question import Character_question
# 引入数据库会话依赖
from app.db.session import get_db
from app.schemas.Character_test_writer_problem import SurveySubmissionSchema
from app.core.get_user import get_current_user_id 
from app.models.Character_answer import Character_answer  # 导入你的模型

router = APIRouter()

# ===================================================================
# 2. 通过变量设置题目数量
# ===================================================================
# 你可以在这里修改，来控制最终问卷的题目总数
TOTAL_QUESTIONS_TO_FETCH = 5


@router.get("/questions", response_model=SurveyResponse)
async def get_survey_questions(db: AsyncSession = Depends(get_db)):
    """
    从数据库中随机获取指定数量的问卷题目列表
    """
    
    # ===================================================================
    # 3. 从数据表中随机抽取题目
    # ===================================================================
    # 构建查询语句：
    # - select(Character_question): 选择要查询的表
    # - order_by(func.random()): 按随机顺序排序。
    #   注意: func.random() 适用于 PostgreSQL 和 SQLite。
    #   如果你的数据库是 MySQL，请使用 func.rand()
    # - limit(TOTAL_QUESTIONS_TO_FETCH): 限制返回的记录数量
    
    # 假设你使用的是 PostgreSQL 或 SQLite
    stmt = select(Character_question).order_by(func.random()).limit(TOTAL_QUESTIONS_TO_FETCH)
    
    # 如果你用的是 MySQL，请使用下面这行代替
    # stmt = select(Character_question).order_by(func.rand()).limit(TOTAL_QUESTIONS_TO_FETCH)

    # 执行查询
    result = await db.execute(stmt)
    # 获取所有查询到的 ORM 对象实例
    db_questions = result.scalars().all()

    # ===================================================================
    # 1. 将数据库数据格式化为接口需要的格式
    # ===================================================================
    # 将从数据库取出的 ORM 对象列表，转换为 Pydantic 模型列表
    questions_data = []
    for db_question in db_questions:
        # 数据库里的 answers 字段是 JSON，SQLAlchemy 会自动将其解析为 Python 的 list of dicts,
        # Pydantic 可以直接用它来填充 options
        question = SurveyQuestion(
            id=str(db_question.id),          # 将数据库的 int 类型 id 转为 str
            title=db_question.questions,
            required=True,                   # 根据需要可以设为 True 或 False
            options=db_question.answers
        )
        questions_data.append(question)

    # 返回符合 SurveyResponse 模型的最终结果
    return SurveyResponse(code=200, msg="success", data=questions_data)


@router.post("/submit_survey")
async def submit_survey_data(
    payload: SurveySubmissionSchema,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    接收前端提交的完整问答对
    """
    print(f"用户 ID: {current_user_id}")
    print(f"收到提交: {payload.submission_time}")
    
    qa_data_list = []
    for item in payload.answers:
        qa_data_list.append({
            "question": item.question_text,
            "answer": item.answer_text
        })

    new_record = Character_answer(
            userId=current_user_id,
            question_and_answer=qa_data_list,  # 直接存入列表，底层会自动转 JSON
            submissionTime=payload.submission_time
        )
    db.add(new_record)

    try:
        await db.commit()
        # 如果是新增记录，可以 refresh 一下获取生成的主键ID（可选）
    except Exception as e:
        await db.rollback() # 出错回滚
        print(f"数据库保存失败: {e}")
        return {"code": 500, "msg": "服务器内部错误，保存失败", "data": None}

    return {"code": 200, "msg": "提交成功", "data": {"user_id": current_user_id}}