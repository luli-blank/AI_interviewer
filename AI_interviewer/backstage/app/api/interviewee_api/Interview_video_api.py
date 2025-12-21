from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
import os
from datetime import datetime
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()

# 确保上传目录存在
UPLOAD_DIR = "data/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.websocket("/ws/video_stream")
async def websocket_video_stream(
    websocket: WebSocket, 
    token: str = Query(...) 
):
    """
    WebSocket 视频流接口
    URL 格式: ws://domain/api/ws/video_stream?token=ey...
    """
    
    current_user_id = None

    # --- 🔒 身份验证与 ID 解析 ---
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
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
    
    # --- 修改点：在文件名后加时间戳 ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{current_user_id}_interview_{timestamp}.webm")
    print(f"User {current_user_id} connected. Saving to {file_path}")
    
    try:
        with open(file_path, "ab") as video_file:
            while True:
                data = await websocket.receive_bytes()
                video_file.write(data)
                
    except WebSocketDisconnect:
        print(f"User {current_user_id} disconnected")
    except Exception as e:
        print(f"Error processing video stream: {e}")
