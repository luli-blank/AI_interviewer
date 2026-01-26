"""
初始化面试题库数据
运行方式: python -m app.data.init_question_bank
"""
import asyncio
import json
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.Interview_question import InterviewQuestion

# 初始题库数据
INITIAL_QUESTIONS = [
    # ==================== 开场问题 ====================
    {
        "question": "请先做一个简短的自我介绍。",
        "reference_answer": "观察候选人的表达能力、逻辑性、以及是否能突出自己的亮点。重点关注：1)是否有清晰的结构 2)是否突出与岗位相关的经验 3)时间控制是否合理(1-2分钟)",
        "category": "opening",
        "difficulty": 1,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "你刚才提到的XX经历，能详细说说吗？",
            "你认为自己最突出的能力是什么？",
            "为什么选择在这个时间点寻找新机会？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["表达清晰度", "内容结构", "亮点突出", "时间把控"], ensure_ascii=False)
    },
    
    # ==================== 动机类问题 ====================
    {
        "question": "你为什么想要应聘这个岗位？",
        "reference_answer": "考察候选人对岗位的理解、职业规划、以及动机是否与公司匹配。好的回答应该体现：1)对岗位的深入了解 2)个人能力与岗位的匹配 3)真诚的动机",
        "category": "motivation",
        "difficulty": 1,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "你对这个岗位的日常工作内容了解多少？",
            "你觉得自己哪些能力最适合这个岗位？",
            "如果入职后发现工作内容与预期不符，你会怎么办？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["岗位理解", "动机真诚度", "职业规划", "匹配度"], ensure_ascii=False)
    },
    {
        "question": "你的职业规划是什么？未来3-5年有什么目标？",
        "reference_answer": "考察候选人的职业目标是否清晰，以及是否与公司发展方向匹配。",
        "category": "motivation",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "为了实现这个目标，你目前在做哪些准备？",
            "如果这个目标无法实现，你会怎么调整？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["目标清晰度", "可行性", "与岗位匹配度"], ensure_ascii=False)
    },
    
    # ==================== 自我认知类 ====================
    {
        "question": "你觉得自己最大的优势是什么？",
        "reference_answer": "考察候选人的自我认知能力，优势是否与岗位要求匹配，以及是否有具体事例支撑。",
        "category": "self_awareness",
        "difficulty": 1,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "能举一个具体的例子说明这个优势吗？",
            "这个优势是如何培养起来的？",
            "在工作中这个优势给你带来了什么帮助？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["自我认知", "案例支撑", "与岗位匹配"], ensure_ascii=False)
    },
    {
        "question": "你认为自己有哪些需要改进的地方？",
        "reference_answer": "考察候选人的自我反思能力和成长意识。好的回答应该：1)真诚承认不足 2)说明正在采取的改进措施 3)不要说致命缺点",
        "category": "self_awareness",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "你具体在怎么改进这个问题？",
            "这个不足对你的工作产生过什么影响？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["自我反思", "改进意识", "回答技巧"], ensure_ascii=False)
    },
    
    # ==================== 团队协作类 ====================
    {
        "question": "你在团队合作中通常扮演什么角色？",
        "reference_answer": "考察团队协作能力、角色定位、以及沟通能力。",
        "category": "teamwork",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "能举一个具体的团队合作案例吗？",
            "如果团队中有人不配合，你会怎么处理？",
            "你最喜欢和什么样的人合作？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["角色认知", "协作能力", "沟通能力"], ensure_ascii=False)
    },
    {
        "question": "描述一次你和同事产生分歧的经历，你是如何处理的？",
        "reference_answer": "考察冲突处理能力、沟通技巧、以及情商。好的回答应该展示：1)冷静客观的态度 2)寻求共识的努力 3)最终的解决方案",
        "category": "teamwork",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "如果对方坚持己见不愿妥协呢？",
            "这次经历让你学到了什么？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["冲突处理", "沟通技巧", "情商", "结果导向"], ensure_ascii=False)
    },
    
    # ==================== 问题解决类 ====================
    {
        "question": "请描述一个你遇到的最大挑战，以及你是如何解决的？",
        "reference_answer": "考察问题解决能力、抗压能力、以及复盘总结能力。使用STAR法则评估：Situation情境、Task任务、Action行动、Result结果",
        "category": "problem_solving",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "在这个过程中你遇到的最大困难是什么？",
            "如果重来一次，你会有什么不同的做法？",
            "这次经历对你后来的工作有什么影响？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["问题分析", "解决方案", "执行力", "复盘能力"], ensure_ascii=False)
    },
    {
        "question": "当你面对一个完全陌生的任务时，你通常会怎么开始？",
        "reference_answer": "考察学习能力、问题分解能力、以及主动性。",
        "category": "problem_solving",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "能举一个具体的例子吗？",
            "如果资源有限，你会如何取舍？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["学习能力", "问题分解", "主动性", "方法论"], ensure_ascii=False)
    },
    
    # ==================== 项目经验类 ====================
    {
        "question": "请介绍一个你做过的最有成就感的项目，你在其中负责什么？",
        "reference_answer": "考察项目经验、角色定位、以及成果产出。重点关注：1)项目背景和目标 2)个人贡献 3)量化成果",
        "category": "project",
        "difficulty": 2,
        "job_types": "通用",
        "follow_up_directions": json.dumps([
            "这个项目最大的难点是什么？你是如何解决的？",
            "如果重新做这个项目，你会有什么改进？",
            "项目中你学到了什么？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["项目理解", "个人贡献", "成果量化", "反思能力"], ensure_ascii=False)
    },
    
    # ==================== 技术类问题 ====================
    {
        "question": "你平时是如何学习新技术的？",
        "reference_answer": "考察学习能力、技术热情、以及成长潜力。好的回答应该展示：1)有系统的学习方法 2)持续学习的习惯 3)学以致用的能力",
        "category": "technical",
        "difficulty": 1,
        "job_types": "技术,开发,工程师",
        "follow_up_directions": json.dumps([
            "最近在学什么新技术？",
            "能分享一个你学习后应用的案例吗？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["学习方法", "学习习惯", "实践能力"], ensure_ascii=False)
    },
    {
        "question": "你如何保证代码质量？",
        "reference_answer": "考察编码习惯、质量意识、以及工程化思维。",
        "category": "technical",
        "difficulty": 2,
        "job_types": "技术,开发,工程师",
        "follow_up_directions": json.dumps([
            "你用过哪些代码质量工具？",
            "代码Review时你会关注哪些方面？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["质量意识", "工程化思维", "工具使用"], ensure_ascii=False)
    },
    
    # ==================== 产品类问题 ====================
    {
        "question": "你如何理解产品经理这个岗位？",
        "reference_answer": "考察对产品岗位的认知深度，以及是否有清晰的职责边界认识。",
        "category": "product",
        "difficulty": 1,
        "job_types": "产品,产品经理,PM",
        "follow_up_directions": json.dumps([
            "产品经理最重要的能力是什么？",
            "产品经理和项目经理有什么区别？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["岗位理解", "职责认知", "行业认知"], ensure_ascii=False)
    },
    {
        "question": "如果开发说你的需求无法实现，你会怎么处理？",
        "reference_answer": "考察沟通协调能力、需求优先级判断能力、以及灵活性。",
        "category": "product",
        "difficulty": 2,
        "job_types": "产品,产品经理,PM",
        "follow_up_directions": json.dumps([
            "如何判断需求的优先级？",
            "有没有遇到过必须坚持的需求？最后怎么解决的？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["沟通能力", "优先级判断", "灵活性", "结果导向"], ensure_ascii=False)
    },
    {
        "question": "你觉得什么样的产品才算是一个好产品？",
        "reference_answer": "考察产品思维、用户视角、以及商业意识。",
        "category": "product",
        "difficulty": 2,
        "job_types": "产品,产品经理,PM",
        "follow_up_directions": json.dumps([
            "能举一个你认为好的产品的例子吗？",
            "如何衡量一个产品是否成功？"
        ], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["产品思维", "用户视角", "商业意识"], ensure_ascii=False)
    },
    
    # ==================== 结束问题 ====================
    {
        "question": "你还有什么想问我的吗？",
        "reference_answer": "面试结束的标准问题，观察候选人的思考深度和对机会的重视程度。好的问题应该体现对岗位/公司/团队的深入了解意愿。",
        "category": "closing",
        "difficulty": 1,
        "job_types": "通用",
        "follow_up_directions": json.dumps([], ensure_ascii=False),
        "scoring_dimensions": json.dumps(["问题质量", "思考深度", "重视程度"], ensure_ascii=False)
    },
]


async def init_question_bank():
    """初始化题库数据"""
    async with AsyncSessionLocal() as db:
        # 检查是否已有数据
        result = await db.execute(select(InterviewQuestion).limit(1))
        existing = result.scalar_one_or_none()
        
        if existing:
            print("题库中已有数据，跳过初始化")
            return
        
        # 插入数据
        for q_data in INITIAL_QUESTIONS:
            question = InterviewQuestion(**q_data)
            db.add(question)
        
        await db.commit()
        print(f"成功初始化 {len(INITIAL_QUESTIONS)} 道面试题")


if __name__ == "__main__":
    asyncio.run(init_question_bank())
