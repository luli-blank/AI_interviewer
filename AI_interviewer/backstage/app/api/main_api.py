from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.interviewee_api import Resume_upload_api
from .interviewee_api import Interview_video_api
from app.api.interviewee_api import Login_api   
from app.db.session import engine, Base
from app.core.get_user import get_current_user_id
from fastapi import Depends
from app.api.interviewee_api import Character_test_writer_api,Character_test_report_api, Interview_position_api, Interview_record_api
from app.api.interviewee_api import Interview_session_api  # 面试会话API (旧版)

# 尝试导入 Agent API（如果依赖未安装则跳过）
try:
    from app.api.interviewee_api import Interview_session_agent_api
    AGENT_API_AVAILABLE = True
    print("[Main API] ✅ Agent API loaded successfully")
except ImportError as e:
    AGENT_API_AVAILABLE = False
    Interview_session_agent_api = None
    print(f"[Main API] ⚠️ Agent API not available: {e}")
    print("[Main API] Agent features will be disabled. To enable, install: pip install -r requirements_agent.txt")

# 导入所有模型以便自动创建表
from app.models.Interview_question import InterviewQuestion, InterviewQuestionUsage

app = FastAPI()

# 添加日志中间件，用于调试请求是否到达
@app.middleware("http")
async def log_request_start(request: Request, call_next):
    print(f"👉 [Middleware] Start request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        print(f"✅ [Middleware] End request: {request.method} {request.url} - Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ [Middleware] Request failed: {request.method} {request.url} - Error: {str(e)}")
        raise e

# # ==========================================
# # 关键步骤：解决跨域问题 (CORS)
# # ==========================================
# origins = [
#     "http://localhost:5173",  # 允许 Vite 开发服务器访问
#     "http://127.0.0.1:5173",
#     "app://."                 # 允许 Electron 打包后的应用访问
# ]

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        # 这一步会在数据库里自动创建 users 表
        await conn.run_sync(Base.metadata.create_all)
@app.get("/")
async def root():
    return {"message": "AI Interviewer Backend Running"}

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[origins],      # 允许的源
    allow_origins=["*"],      # 允许的源
    allow_credentials=False,
    allow_methods=["*"],        # 允许所有方法 (GET, POST, etc.)
    allow_headers=["*"],        # 允许所有 Header                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
)

app.include_router(Login_api.router, prefix="/api/interviewee", tags=["interviewee"])
app.include_router(Character_test_writer_api.router, prefix="/api/interviewee", tags=["Interviewee Survey"],dependencies=[Depends(get_current_user_id)])
app.include_router(Character_test_report_api.router, prefix="/api/interviewee", tags=["Interviewee Survey"],dependencies=[Depends(get_current_user_id)])
app.include_router(Interview_video_api.router, tags=["video_stream"])
app.include_router(Interview_position_api.router, prefix="/api/interviewee", tags=["Interview Position"], dependencies=[Depends(get_current_user_id)])
app.include_router(Interview_record_api.router, prefix="/api/interviewee", tags=["Interview Record"], dependencies=[Depends(get_current_user_id)])
app.include_router(Resume_upload_api.router, prefix="/api/interview", tags=["Interview Create"], dependencies=[Depends(get_current_user_id)])
app.include_router(Interview_session_api.router, prefix="/api/interview", tags=["Interview Session"])  # 面试会话路由 (旧版)

# 只在 Agent API 可用时注册路由
if AGENT_API_AVAILABLE and Interview_session_agent_api is not None:
    app.include_router(Interview_session_agent_api.router, prefix="/api/interview", tags=["Interview Session Agent"])
    print("[Main API] ✅ Agent routes registered at /api/interview/ws/interview/agent")
else:
    print("[Main API] ⚠️ Agent routes not registered (dependencies missing)")

# 启动命令（在终端运行）：终端路径需要抵达backstage
# uvicorn app.api.main_api:app --reload --port 8000