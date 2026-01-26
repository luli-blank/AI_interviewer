"""
面试状态定义

定义 LangGraph 工作流的状态结构，包括：
- 面试阶段 (InterviewStage)
- 完整状态 (InterviewState)
"""

from enum import Enum
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
import operator


class InterviewStage(str, Enum):
    """
    面试阶段枚举
    
    定义完整的面试流程阶段：
    1. OPENING - 开场白
    2. SELF_INTRO - 自我介绍
    3. PROJECT_DEEP_DIVE - 项目深挖
    4. BASIC_KNOWLEDGE - 基础知识考核
    5. SCENARIO_ALGORITHM - 算法/场景题
    6. REVERSE_INTERVIEW - 反问环节
    7. CLOSING - 结束
    """
    OPENING = "opening"                      # 开场白
    SELF_INTRO = "self_intro"                # 自我介绍
    PROJECT_DEEP_DIVE = "project_deep_dive"  # 项目深挖
    BASIC_KNOWLEDGE = "basic_knowledge"      # 基础知识考核
    SCENARIO_ALGORITHM = "scenario_algorithm" # 算法/场景题
    REVERSE_INTERVIEW = "reverse_interview"  # 反问环节
    CLOSING = "closing"                      # 结束
    
    @classmethod
    def get_stage_order(cls) -> List["InterviewStage"]:
        """获取阶段顺序列表"""
        return [
            cls.OPENING,
            cls.SELF_INTRO,
            cls.PROJECT_DEEP_DIVE,
            cls.BASIC_KNOWLEDGE,
            cls.SCENARIO_ALGORITHM,
            cls.REVERSE_INTERVIEW,
            cls.CLOSING
        ]
    
    @classmethod
    def get_next_stage(cls, current: "InterviewStage") -> Optional["InterviewStage"]:
        """获取下一个阶段"""
        order = cls.get_stage_order()
        try:
            idx = order.index(current)
            if idx < len(order) - 1:
                return order[idx + 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def get_stage_config(cls, stage: "InterviewStage") -> Dict[str, Any]:
        """获取阶段配置信息"""
        configs = {
            cls.OPENING: {
                "name": "开场白",
                "description": "欢迎候选人，介绍面试流程",
                "min_questions": 0,
                "max_questions": 0,
                "duration_minutes": 1
            },
            cls.SELF_INTRO: {
                "name": "自我介绍",
                "description": "让候选人介绍自己的背景和经历",
                "min_questions": 1,
                "max_questions": 2,
                "duration_minutes": 3
            },
            cls.PROJECT_DEEP_DIVE: {
                "name": "项目深挖",
                "description": "深入了解候选人的项目经验",
                "min_questions": 2,
                "max_questions": 4,
                "duration_minutes": 10
            },
            cls.BASIC_KNOWLEDGE: {
                "name": "基础知识考核",
                "description": "考察专业基础知识",
                "min_questions": 2,
                "max_questions": 4,
                "duration_minutes": 8
            },
            cls.SCENARIO_ALGORITHM: {
                "name": "场景/算法题",
                "description": "考察问题解决能力",
                "min_questions": 1,
                "max_questions": 2,
                "duration_minutes": 5
            },
            cls.REVERSE_INTERVIEW: {
                "name": "反问环节",
                "description": "候选人提问时间",
                "min_questions": 1,
                "max_questions": 1,
                "duration_minutes": 3
            },
            cls.CLOSING: {
                "name": "结束",
                "description": "感谢候选人，说明后续流程",
                "min_questions": 0,
                "max_questions": 0,
                "duration_minutes": 1
            }
        }
        return configs.get(stage, {})


class QuestionRecord(TypedDict):
    """单个问答记录"""
    question: str                    # 问题内容
    answer: str                      # 候选人回答
    score: float                     # 评分 (1-10)
    feedback: str                    # 评价
    stage: str                       # 所属阶段
    is_follow_up: bool              # 是否是追问
    reference_answer: Optional[str]  # 参考答案
    source: Optional[str]            # 题目来源 (rag/web/generated)
    timestamp: str                   # 时间戳


class RAGResult(TypedDict):
    """RAG 检索结果"""
    question: str           # 检索到的问题
    reference_answer: str   # 参考答案
    category: str           # 分类
    difficulty: int         # 难度 (1-5)
    score: float           # 相似度分数


class InterviewState(TypedDict):
    """
    LangGraph 面试状态
    
    包含面试过程中的所有状态信息
    """
    # ===== 基础信息 =====
    session_id: str                      # 会话ID
    user_id: str                         # 用户ID
    job_name: str                        # 目标岗位
    resume_text: str                     # 简历文本
    
    # ===== 阶段管理 =====
    current_stage: InterviewStage        # 当前阶段
    stage_question_count: int            # 当前阶段已问问题数
    follow_up_count: int                 # 当前问题追问次数
    
    # ===== 问答历史 =====
    question_history: List[QuestionRecord]  # 完整问答历史
    current_question: Optional[str]         # 当前问题
    current_answer: Optional[str]           # 当前回答
    
    # ===== RAG & 搜索 =====
    rag_results: List[RAGResult]            # RAG 检索结果缓存
    web_search_results: List[Dict]          # Web 搜索结果缓存
    search_keywords: List[str]              # 生成的搜索关键词
    
    # ===== 预取缓存 =====
    prefetch_questions: List[Dict]          # 预取的问题缓存
    prefetch_stage: Optional[str]           # 预取针对的阶段
    
    # ===== 评估 =====
    total_score: float                      # 总分
    stage_scores: Dict[str, float]          # 各阶段得分
    
    # ===== Agent 决策 =====
    next_action: str                        # 下一步动作: ask_question, follow_up, next_stage, end
    thinking_message: Optional[str]         # 思考占位符消息 (用于 filler words)
    needs_web_search: bool                  # 是否需要网络搜索
    
    # ===== 上下文文件 =====
    context_file_path: Optional[str]        # 上下文 .md 文件路径
    
    # ===== 时间管理 =====
    start_time: str                         # 开始时间
    stage_start_time: str                   # 当前阶段开始时间
    
    # ===== 输出 =====
    output_question: Optional[str]          # 最终输出的问题
    output_reference: Optional[str]         # 参考答案（内部使用）


def create_initial_state(
    session_id: str,
    user_id: str,
    job_name: str,
    resume_text: str,
    context_file_path: str
) -> InterviewState:
    """
    创建初始面试状态
    
    Args:
        session_id: 会话ID
        user_id: 用户ID
        job_name: 目标岗位
        resume_text: 简历文本
        context_file_path: 上下文文件路径
        
    Returns:
        初始化的 InterviewState
    """
    now = datetime.now().isoformat()
    return InterviewState(
        session_id=session_id,
        user_id=user_id,
        job_name=job_name,
        resume_text=resume_text,
        current_stage=InterviewStage.OPENING,
        stage_question_count=0,
        follow_up_count=0,
        question_history=[],
        current_question=None,
        current_answer=None,
        rag_results=[],
        web_search_results=[],
        search_keywords=[],
        prefetch_questions=[],
        prefetch_stage=None,
        total_score=0.0,
        stage_scores={},
        next_action="ask_question",
        thinking_message=None,
        needs_web_search=False,
        context_file_path=context_file_path,
        start_time=now,
        stage_start_time=now,
        output_question=None,
        output_reference=None
    )
