from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from interviewee_api import Login_api   
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

app.include_router(Login_api.router, prefix="/api/interviewee",tags=["interviewee"])

 
# 启动命令（在终端运行）：
# uvicorn main_api:app --reload --port 8000