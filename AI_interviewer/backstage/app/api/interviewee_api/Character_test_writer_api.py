from fastapi import APIRouter
from app.schemas.Character_test_writer_problem import SurveyQuestion, SurveyOption, SurveyResponse

router = APIRouter()

@router.get("/questions", response_model=SurveyResponse)
async def get_survey_questions():
    """
    获取问卷题目列表
    """
    # 模拟从数据库取出的数据
    questions_data = [
        SurveyQuestion(
            id="q1", 
            title="您最擅长的编程语言是？", 
            required=True,
            options=[
                SurveyOption(label="Python", value="python"),
                SurveyOption(label="JavaScript / TypeScript", value="js"),
                SurveyOption(label="Java", value="java"),
                SurveyOption(label="C++", value="cpp")
            ]
        ),
        SurveyQuestion(
            id="q2", 
            title="您对目前薪资的期望范围？", 
            required=True,
            options=[
                SurveyOption(label="10k - 15k", value="low"),
                SurveyOption(label="15k - 25k", value="mid"),
                SurveyOption(label="25k +", value="high")
            ]
        ),
        SurveyQuestion(
            id="q1", 
            title="您最擅长的编程语言是？", 
            required=True,
            options=[
                SurveyOption(label="Python", value="python"),
                SurveyOption(label="JavaScript / TypeScript", value="js"),
                SurveyOption(label="Java", value="java"),
                SurveyOption(label="C++", value="cpp")
            ]
        ),
        SurveyQuestion(
            id="q2", 
            title="您对目前薪资的期望范围？", 
            required=True,
            options=[
                SurveyOption(label="10k - 15k", value="low"),
                SurveyOption(label="15k - 25k", value="mid"),
                SurveyOption(label="25k +", value="high")
            ]
        ),
        SurveyQuestion(
            id="q1", 
            title="您最擅长的编程语言是？", 
            required=True,
            options=[
                SurveyOption(label="Python", value="python"),
                SurveyOption(label="JavaScript / TypeScript", value="js"),
                SurveyOption(label="Java", value="java"),
                SurveyOption(label="C++", value="cpp")
            ]
        ),
        SurveyQuestion(
            id="q2", 
            title="您对目前薪资的期望范围？", 
            required=True,
            options=[
                SurveyOption(label="10k - 15k", value="low"),
                SurveyOption(label="15k - 25k", value="mid"),
                SurveyOption(label="25k +", value="high")
            ]
        )
    ]

    return SurveyResponse(code=200, msg="success", data=questions_data)