# backstage/app/api/interviewee_api/Character_test_video_api.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
import os
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()

# 确保上传目录存在
UPLOAD_DIR = "data/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ⚠️ 修改点 1: 路由路径中去掉了 /{user_id}
@router.websocket("/ws/video_stream")
async def websocket_video_stream(
    websocket: WebSocket, 
    # ⚠️ 修改点 2: 函数参数中不再接收 user_id，只接收 token
    token: str = Query(...) 
):
    """
    WebSocket 视频流接口
    URL 格式: ws://domain/api/ws/video_stream?token=ey...
    """
    
    current_user_id = None

    # --- 🔒 身份验证与 ID 解析 ---
    try:
        # 1. 解码 Token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 2. 从 Token 中提取 user_id (通常在 'sub' 字段)
        # 如果你的 token 里存 ID 的字段叫 'id' 或 'user_id'，请这里相应修改
        current_user_id = payload.get("sub")

        if current_user_id is None:
            print("Token invalid: No user ID found in token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    except JWTError as e:
        print(f"Token validation failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    except Exception as e:
        print(f"Auth error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    # --- ✅ 验证通过，建立连接 ---
    await websocket.accept()
    
    # 使用从 Token 解析出来的 ID 命名文件
    file_path = os.path.join(UPLOAD_DIR, f"{current_user_id}_interview.webm")
    print(f"User {current_user_id} connected. Saving to {file_path}")
    
    try:
        # 使用 'ab' (append binary) 模式打开文件
        with open(file_path, "ab") as video_file:
            while True:
                data = await websocket.receive_bytes()
                video_file.write(data)
                
    except WebSocketDisconnect:
        print(f"User {current_user_id} disconnected")
    except Exception as e:
        print(f"Error processing video stream: {e}")