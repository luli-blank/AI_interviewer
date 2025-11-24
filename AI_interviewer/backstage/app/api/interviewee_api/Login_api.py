from fastapi import APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import json

from app.db.session import get_db
from app.db.redis_tool import get_redis
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
import redis.asyncio as redis

router = APIRouter()


# --- 定义数据模型 ---
class LoginRequest(BaseModel):
    username: str
    password: str

# --- 定义接口 ---
@router.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@router.post("/login")
def login(data: LoginRequest):
    # 模拟登录逻辑
    if data.username == "admin" and data.password == "123456":
        return {"code": 200, "message": "登录成功", "token": "fake-jwt-token"}
    else:
        return {"code": 401, "message": "用户名或密码错误"}


# --- 场景1: 注册用户 (写操作) ---
# 策略: 写入 MySQL -> 删除可能的缓存
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")



# 启动命令（在终端运行）：
# uvicorn main:app --reload --port 8000