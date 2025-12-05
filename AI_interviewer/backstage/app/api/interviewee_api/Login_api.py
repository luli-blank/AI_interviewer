from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import json

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

from app.core.security import verify_password, get_password_hash, create_access_token
router = APIRouter()


# --- 定义数据模型 ---
class LoginRequest(BaseModel):
    username: str
    password: str

# --- 定义接口 ---
@router.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

# @router.post("/login")
# def login(data: LoginRequest):
#     # 模拟登录逻辑
#     if data.username == "admin" and data.password == "123456":
#         return {"code": 200, "message": "登录成功", "token": "fake-jwt-token"}
#     else:
#         return {"code": 401, "message": "用户名或密码错误"}

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. 构造查询语句，根据用户名查找用户
    query = select(User).where(User.username == data.username)
    
    # 2. 执行查询
    result = await db.execute(query)
    user = result.scalar_one_or_none()  # 获取唯一结果，如果不存在则为 None

    # 3. 验证账户和密码
    # 【修改点 3】: 使用 verify_password 验证密文是否匹配
    # (data.password 是前端传来的 "123456"，user.password 是数据库里的哈希值)
    if user and verify_password(data.password, user.password):
        
        # 【修改点 4】: 验证成功，生成真正的 JWT Token
        # 我们可以把用户名或用户ID放入 Token 载荷中
        access_token = create_access_token(
            data={"sub": user.username, "id": user.id}
        )

        return {
            "code": 200, 
            "message": "登录成功", 
            "token": access_token  # 返回真正的加密 Token
        }
    else:
        return {
            "code": 401, 
            "message": "用户名或密码错误"
        }

# --- 场景1: 注册用户 (写操作) ---
# 策略: 写入 MySQL -> 删除可能的缓存
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    # 【修改点 1】: 获取密码的哈希值（加密）
    # 不再直接存储 user_in.password，而是存储 hashed_password
    hashed_password = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        # 【修改点 2】: 存入数据库的是加密后的乱码，而不是明文
        password=hashed_password
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