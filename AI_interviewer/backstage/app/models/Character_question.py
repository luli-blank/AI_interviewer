# 修改前：from sqlalchemy import Column, Integer, String
# 修改后：引入 JSON
from sqlalchemy import Column, Integer, String, JSON 
from app.db.session import Base

class Character_question(Base):
    __tablename__ = "character_questions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), index=True) # 建议去掉 unique=True，除非每种类型只有一道题
    questions = Column(String(100), unique=True)
    answers = Column(JSON, nullable=False)

    # __init__ 方法是 Python 对象的逻辑，不会影响建表，这里保持原样即可
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.answers is not None:
            if not isinstance(self.answers, list) or len(self.answers) != 4:
                raise ValueError("answers must be a list with 4 elements")