"""
数据模型模块

包含所有数据库模型定义
"""

from .user import User
from .Resume_message import Resume_messages
from .Interview_position import Interview_position
from .Interview_record import Interview_record
from .Jobs import Jobs
from .Interviewer import Interviewer
from .Character_question import Character_question

# 导入所有模型以便 SQLAlchemy 自动创建表
__all__ = [
    "User",
    "Resume_messages",
    "Interview_position",
    "Interview_record",
    "Jobs",
    "Interviewer",
    "Character_question",
]

# 注意：Character_answer 和 Interview_question 模型如果需要，请确保文件存在
try:
    from .Character_answer import Character_answer
    __all__.append("Character_answer")
except ImportError:
    pass

try:
    from .Interview_question import InterviewQuestion, InterviewQuestionUsage
    __all__.extend(["InterviewQuestion", "InterviewQuestionUsage"])
except ImportError:
    pass
