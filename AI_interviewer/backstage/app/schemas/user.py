from pydantic import BaseModel

# 用于接收前端传来的注册信息
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 用于返回给前端的信息（不包含密码）
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True # 允许从 ORM 模型读取数据