from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

class Interview_position(Base):
    __tablename__ = "interview_position"

    id = Column(Integer, primary_key=True, index=True)
    position_name = Column(String(50))
    description = Column(String(100))

    # __init__ 方法是 Python 对象的逻辑，不会影响建表，这里保持原样即可
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)