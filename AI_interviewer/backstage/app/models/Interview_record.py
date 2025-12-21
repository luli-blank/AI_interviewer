from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func 
from app.db.session import Base

class Interview_record(Base):
    __tablename__ = "interview_record"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    position_id = Column(Integer, ForeignKey("interview_position.id"))
    interviewer_id = Column(Integer, ForeignKey("interviewer.id"))
    time = Column(DateTime, server_default=func.now())
    

    # __init__ 方法是 Python 对象的逻辑，不会影响建表，这里保持原样即可
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)