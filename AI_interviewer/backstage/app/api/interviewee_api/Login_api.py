from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# 启动命令（在终端运行）：
# uvicorn main:app --reload --port 8000