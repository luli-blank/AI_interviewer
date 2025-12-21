from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

class Jobs(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("interview_position.id"))
    interviewer_id = Column(Integer, ForeignKey("interviewer.id"))

    # __init__ 方法是 Python 对象的逻辑，不会影响建表，这里保持原样即可
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)