from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# # ==========================================
# # 关键步骤：解决跨域问题 (CORS)
# # ==========================================
# origins = [
#     "http://localhost:5173",  # 允许 Vite 开发服务器访问
#     "http://127.0.0.1:5173",
#     "app://."                 # 允许 Electron 打包后的应用访问
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[origins],      # 允许的源
    allow_origins=["*"],      # 允许的源
    allow_credentials=True,
    allow_methods=["*"],        # 允许所有方法 (GET, POST, etc.)
    allow_headers=["*"],        # 允许所有 Header                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
)

# --- 定义数据模型 ---
class LoginRequest(BaseModel):
    username: str
    password: str

# --- 定义接口 ---
@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.post("/login")
def login(data: LoginRequest):
    # 模拟登录逻辑
    if data.username == "admin" and data.password == "123456":
        return {"code": 200, "message": "登录成功", "token": "fake-jwt-token"}
    else:
        return {"code": 401, "message": "用户名或密码错误"}

# 启动命令（在终端运行）：
# uvicorn main:app --reload --port 8000