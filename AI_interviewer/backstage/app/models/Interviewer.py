from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

class Interviewer(Base):
    __tablename__ = "interviewer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(50))
    description = Column(String(100))
    avatar = Column(String(255), default="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png")


    # __init__ 方法是 Python 对象的逻辑，不会影响建表，这里保持原样即可
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)