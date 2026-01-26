"""
面试会话管理API
处理面试的完整流程：初始化、问答交互、结束
"""
import os
import csv
import json
import asyncio
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import get_db, AsyncSessionLocal
from app.models.Resume_message import Resume_messages
from app.utils.ai_interview_service import ai_interview_service

router = APIRouter()

# ==================== 数据模型 ====================
class InterviewSession:
    """面试会话状态管理"""
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.resume_text: str = ""
        self.job_name: str = ""
        self.questions: List[Dict] = []
        self.current_question_index: int = 0
        self.question_history: List[Dict] = []  # 问答记录
        self.follow_up_count: int = 0  # 当前问题追问次数
        self.start_time: datetime = datetime.now()
        self.status: str = "initialized"  # initialized, waiting_ready, in_progress, ended
        self.total_score: float = 0
        
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "job_name": self.job_name,
            "current_question_index": self.current_question_index,
            "total_questions": len(self.questions),
            "status": self.status,
            "duration_seconds": (datetime.now() - self.start_time).seconds
        }

# 全局会话存储 (生产环境应使用 Redis)
active_sessions: Dict[str, InterviewSession] = {}

# ==================== 辅助函数 ====================
async def get_user_id_from_token(token: str) -> Optional[str]:
    """从JWT token中提取用户ID"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None

async def get_latest_resume(user_id: str, db: AsyncSession) -> Optional[Resume_messages]:
    """获取用户最新的简历信息"""
    result = await db.execute(
        select(Resume_messages)
        .where(Resume_messages.user_id == user_id)
        .order_by(desc(Resume_messages.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()

def save_interview_to_csv(session: InterviewSession, output_dir: str = "data/interview_records"):
    """将面试记录保存为CSV文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session.user_id}_interview_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow([
            '序号', '问题', '候选人回答', '评分', '评价', 
            '是否追问', '追问问题', '追问回答', '追问评分'
        ])
        
        # 写入数据
        for i, record in enumerate(session.question_history, 1):
            writer.writerow([
                i,
                record.get('question', ''),
                record.get('answer', ''),
                record.get('score', ''),
                record.get('feedback', ''),
                '是' if record.get('follow_up_question') else '否',
                record.get('follow_up_question', ''),
                record.get('follow_up_answer', ''),
                record.get('follow_up_score', '')
            ])
        
        # 写入汇总信息
        writer.writerow([])
        writer.writerow(['面试汇总'])
        writer.writerow(['目标岗位', session.job_name])
        writer.writerow(['总题数', len(session.question_history)])
        writer.writerow(['平均得分', f"{session.total_score / max(len(session.question_history), 1):.1f}"])
        writer.writerow(['面试时长', f"{(datetime.now() - session.start_time).seconds // 60} 分钟"])
    
    return filepath

# ==================== WebSocket 面试主接口 ====================
@router.websocket("/ws/interview")
async def websocket_interview(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket 面试主接口
    
    消息格式（JSON）：
    
    客户端发送：
    - {"type": "init"} - 初始化面试
    - {"type": "ready"} - 用户准备好开始
    - {"type": "audio", "data": "base64音频数据"} - 音频数据
    - {"type": "text", "data": "文本回答"} - 文本回答（调试用）
    - {"type": "end"} - 结束面试
    
    服务端发送：
    - {"type": "status", "data": {...}} - 状态更新
    - {"type": "question", "text": "问题文本", "index": 1, "total": 10}
    - {"type": "subtitle", "text": "字幕文本", "is_final": false}
    - {"type": "audio", "data": "base64音频数据"}
    - {"type": "transcription", "text": "识别文本", "is_final": false}
    - {"type": "analysis", "score": 8, "feedback": "..."}
    - {"type": "end", "reason": "completed", "csv_path": "..."}
    - {"type": "error", "message": "错误信息"}
    """
    
    # 1. 验证Token
    user_id = await get_user_id_from_token(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # 2. 接受连接
    await websocket.accept()
    print(f"[Interview WS] User {user_id} connected")
    
    # 3. 创建会话
    session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    session = InterviewSession(user_id, session_id)
    active_sessions[session_id] = session
    
    try:
        while True:
            # 接收消息
            raw_message = await websocket.receive_text()
            
            try:
                message = json.loads(raw_message)
                msg_type = message.get("type", "")
                
                # ========== 初始化面试 ==========
                if msg_type == "init":
                    await handle_init(websocket, session, user_id)
                
                # ========== 用户准备好 ==========
                elif msg_type == "ready":
                    await handle_ready(websocket, session)
                
                # ========== 接收音频数据 ==========
                elif msg_type == "audio":
                    audio_data = base64.b64decode(message.get("data", ""))
                    await handle_audio(websocket, session, audio_data)
                
                # ========== 接收文本回答（调试用）==========
                elif msg_type == "text":
                    text_answer = message.get("data", "")
                    await handle_text_answer(websocket, session, text_answer)
                
                # ========== 结束面试 ==========
                elif msg_type == "end":
                    await handle_end(websocket, session)
                    break
                
                else:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}"
                        })
                    except (RuntimeError, WebSocketDisconnect):
                        pass
                    
            except json.JSONDecodeError:
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                except (RuntimeError, WebSocketDisconnect):
                    pass
                
    except WebSocketDisconnect:
        print(f"[Interview WS] User {user_id} disconnected")
    except Exception as e:
        print(f"[Interview WS] Error: {e}")
        # 只在连接未关闭时才发送错误消息
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except RuntimeError:
            # 连接已关闭，忽略
            pass
    finally:
        # 清理会话
        if session_id in active_sessions:
            # 保存记录
            if session.question_history:
                save_interview_to_csv(session)
            del active_sessions[session_id]


async def handle_init(websocket: WebSocket, session: InterviewSession, user_id: str):
    """处理面试初始化"""
    try:
        # 1. 获取简历信息
        async with AsyncSessionLocal() as db:
            resume = await get_latest_resume(user_id, db)
            
            if not resume or not resume.resume_file_text:
                await websocket.send_json({
                    "type": "error",
                    "message": "未找到简历信息，请先上传简历"
                })
                return
            
            session.resume_text = resume.resume_file_text
            session.job_name = resume.job_name or "通用岗位"
        
        # 2. 发送状态更新
        await websocket.send_json({
            "type": "status",
            "data": {
                "stage": "loading_resume",
                "message": "正在加载简历信息..."
            }
        })
        
        # 3. 生成面试问题
        await websocket.send_json({
            "type": "status",
            "data": {
                "stage": "generating_questions",
                "message": "正在根据简历生成面试问题..."
            }
        })
        
        session.questions = await ai_interview_service.generate_interview_questions(
            resume_text=session.resume_text,
            job_name=session.job_name,
            num_questions=8
        )
        
        # 4. 生成开场白
        await websocket.send_json({
            "type": "status",
            "data": {
                "stage": "ready",
                "message": "准备就绪，等待开始...",
                "job_name": session.job_name,
                "total_questions": len(session.questions)
            }
        })
        
        # 5. 发送开场白文本（流式）
        opening = await ai_interview_service.generate_interview_opening()
        
        # 流式发送字幕
        for i in range(0, len(opening), 5):  # 每5个字符发送一次
            await websocket.send_json({
                "type": "subtitle",
                "text": opening[:i+5],
                "is_final": i + 5 >= len(opening)
            })
            await asyncio.sleep(0.05)
        
        # 6. 流式生成并发送开场白语音
        try:
            print(f"[WebSocket] 🎵 Starting streaming TTS for opening...")
            chunk_index = 0
            async for audio_chunk in ai_interview_service.text_to_speech_stream(opening):
                if audio_chunk:
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": base64.b64encode(audio_chunk).decode('utf-8'),
                        "format": "wav",
                        "chunk_index": chunk_index,
                        "is_final": False
                    })
                    chunk_index += 1
                    await asyncio.sleep(0.01)
            
            # 发送结束标记
            await websocket.send_json({
                "type": "audio_chunk",
                "data": "",
                "format": "wav",
                "chunk_index": chunk_index,
                "is_final": True
            })
            print(f"[WebSocket] ✅ Opening TTS streaming complete. Total chunks: {chunk_index}")
        except Exception as e:
            print(f"[WebSocket] ❌ TTS Error: {e}")
            # TTS失败不影响流程
        
        session.status = "waiting_ready"
        
    except Exception as e:
        print(f"Init error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"初始化失败: {str(e)}"
        })


async def handle_ready(websocket: WebSocket, session: InterviewSession):
    """处理用户准备就绪"""
    if session.status != "waiting_ready":
        await websocket.send_json({
            "type": "error",
            "message": "请先初始化面试"
        })
        return
    
    session.status = "in_progress"
    session.current_question_index = 0
    session.follow_up_count = 0
    
    # 发送第一个问题
    await send_question(websocket, session)


async def send_question(websocket: WebSocket, session: InterviewSession):
    """发送当前问题"""
    if session.current_question_index >= len(session.questions):
        # 所有问题已问完，结束面试
        await handle_end(websocket, session, reason="completed")
        return
    
    question = session.questions[session.current_question_index]
    question_text = question.get("question", "")
    
    # 1. 发送问题信息
    await websocket.send_json({
        "type": "question",
        "text": question_text,
        "index": session.current_question_index + 1,
        "total": len(session.questions),
        "category": question.get("category", "")
    })
    
    # 2. 流式发送字幕
    for i in range(0, len(question_text), 3):
        await websocket.send_json({
            "type": "subtitle",
            "text": question_text[:i+3],
            "is_final": i + 3 >= len(question_text)
        })
        await asyncio.sleep(0.03)
    
    # 3. 流式生成并发送语音
    try:
        print(f"[WebSocket] 🎵 Starting streaming TTS...")
        chunk_index = 0
        async for audio_chunk in ai_interview_service.text_to_speech_stream(question_text):
            if audio_chunk:
                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": base64.b64encode(audio_chunk).decode('utf-8'),
                    "format": "wav",
                    "chunk_index": chunk_index,
                    "is_final": False
                })
                chunk_index += 1
                await asyncio.sleep(0.01)  # 小延迟避免阻塞
        
        # 发送结束标记
        await websocket.send_json({
            "type": "audio_chunk",
            "data": "",
            "format": "wav",
            "chunk_index": chunk_index,
            "is_final": True
        })
        print(f"[WebSocket] ✅ TTS streaming complete. Total chunks: {chunk_index}")
    except Exception as e:
        print(f"[WebSocket] ❌ TTS Error: {e}")


async def handle_audio(websocket: WebSocket, session: InterviewSession, audio_data: bytes):
    """处理音频数据"""
    if session.status != "in_progress":
        return
    
    print(f"\n[WebSocket] 📥 Received Audio Message. Data Length: {len(audio_data)} bytes")

    # 1. 语音转文字
    try:
        transcription = await ai_interview_service.speech_to_text(audio_data)
        
        # 发送转录结果
        await websocket.send_json({
            "type": "transcription",
            "text": transcription,
            "is_final": True
        })
        
        # 2. 处理回答
        if transcription.strip():
            print(f"[WebSocket] 👤 User Answer: {transcription}")
            await process_answer(websocket, session, transcription)
        else:
            print(f"[WebSocket] ⚠️ Empty transcription, ignoring.")
            
    except WebSocketDisconnect:
        print(f"[WebSocket] ⚠️ Client disconnected during audio processing")
        # 不再尝试发送消息
    except Exception as e:
        print(f"[WebSocket] ❌ ASR Processing Error: {e}")
        # 只在连接未关闭时才发送错误消息
        try:
            await websocket.send_json({
                "type": "error",
                "message": "语音识别失败，请重试"
            })
        except (RuntimeError, WebSocketDisconnect):
            # 连接已关闭，忽略
            pass


async def handle_text_answer(websocket: WebSocket, session: InterviewSession, text: str):
    """处理文本回答（调试用）"""
    if session.status != "in_progress":
        return
    
    if text.strip():
        await process_answer(websocket, session, text)


async def process_answer(websocket: WebSocket, session: InterviewSession, answer: str):
    """处理用户回答并决定下一步"""
    current_question = session.questions[session.current_question_index]
    
    # 1. 分析回答
    await websocket.send_json({
        "type": "status",
        "data": {
            "stage": "analyzing",
            "message": "正在分析回答..."
        }
    })
    
    analysis = await ai_interview_service.analyze_answer_and_decide(
        current_question=current_question.get("question", ""),
        reference_answer=current_question.get("reference_answer", ""),
        user_answer=answer,
        resume_text=session.resume_text[:1500],
        question_history=session.question_history,
        remaining_questions=len(session.questions) - session.current_question_index - 1
    )
    
    # 2. 发送分析结果
    await websocket.send_json({
        "type": "analysis",
        "score": analysis.get("score", 5),
        "feedback": analysis.get("feedback", ""),
        "action": analysis.get("action", "next_question")
    })
    
    # 3. 记录问答
    record = {
        "question": current_question.get("question", ""),
        "answer": answer,
        "score": analysis.get("score", 5),
        "feedback": analysis.get("feedback", ""),
        "category": current_question.get("category", "")
    }
    
    action = analysis.get("action", "next_question")
    
    # 4. 根据决策执行动作
    if action == "follow_up" and session.follow_up_count < 2:
        # 追问
        session.follow_up_count += 1
        follow_up_question = analysis.get("follow_up_question", "能再详细说说吗？")
        
        record["follow_up_question"] = follow_up_question
        session.question_history.append(record)
        session.total_score += analysis.get("score", 5)
        
        # 发送追问
        await websocket.send_json({
            "type": "question",
            "text": follow_up_question,
            "index": session.current_question_index + 1,
            "total": len(session.questions),
            "is_follow_up": True
        })
        
        # 发送字幕和语音
        for i in range(0, len(follow_up_question), 3):
            await websocket.send_json({
                "type": "subtitle",
                "text": follow_up_question[:i+3],
                "is_final": i + 3 >= len(follow_up_question)
            })
            await asyncio.sleep(0.03)
        
        try:
            print(f"[WebSocket] 🎵 Starting streaming TTS for follow-up...")
            chunk_index = 0
            async for audio_chunk in ai_interview_service.text_to_speech_stream(follow_up_question):
                if audio_chunk:
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": base64.b64encode(audio_chunk).decode('utf-8'),
                        "format": "wav",
                        "chunk_index": chunk_index,
                        "is_final": False
                    })
                    chunk_index += 1
                    await asyncio.sleep(0.01)
            
            # 发送结束标记
            await websocket.send_json({
                "type": "audio_chunk",
                "data": "",
                "format": "wav",
                "chunk_index": chunk_index,
                "is_final": True
            })
            print(f"[WebSocket] ✅ Follow-up TTS streaming complete. Total chunks: {chunk_index}")
        except Exception as e:
            print(f"[WebSocket] ❌ TTS Error: {e}")
            
    elif action == "end_interview":
        # 结束面试
        session.question_history.append(record)
        session.total_score += analysis.get("score", 5)
        await handle_end(websocket, session, reason="ai_decision")
        
    else:
        # 下一题
        session.question_history.append(record)
        session.total_score += analysis.get("score", 5)
        session.current_question_index += 1
        session.follow_up_count = 0
        
        # 短暂停顿后发送下一题
        await asyncio.sleep(1)
        await send_question(websocket, session)


async def handle_end(websocket: WebSocket, session: InterviewSession, reason: str = "user_request"):
    """处理面试结束"""
    session.status = "ended"
    
    # 1. 计算平均分
    avg_score = session.total_score / max(len(session.question_history), 1)
    
    # 2. 生成结束语
    closing = await ai_interview_service.generate_interview_closing(
        question_history=session.question_history,
        overall_score=avg_score
    )
    
    # 3. 发送结束语字幕
    for i in range(0, len(closing), 5):
        await websocket.send_json({
            "type": "subtitle",
            "text": closing[:i+5],
            "is_final": i + 5 >= len(closing)
        })
        await asyncio.sleep(0.05)
    
    # 4. 流式生成结束语语音
    try:
        print(f"[WebSocket] 🎵 Starting streaming TTS for closing...")
        chunk_index = 0
        async for audio_chunk in ai_interview_service.text_to_speech_stream(closing):
            if audio_chunk:
                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": base64.b64encode(audio_chunk).decode('utf-8'),
                    "format": "wav",
                    "chunk_index": chunk_index,
                    "is_final": False
                })
                chunk_index += 1
                await asyncio.sleep(0.01)
        
        # 发送结束标记
        await websocket.send_json({
            "type": "audio_chunk",
            "data": "",
            "format": "wav",
            "chunk_index": chunk_index,
            "is_final": True
        })
        print(f"[WebSocket] ✅ Closing TTS streaming complete. Total chunks: {chunk_index}")
    except Exception as e:
        print(f"[WebSocket] ❌ TTS Error: {e}")
    
    # 5. 保存CSV
    csv_path = save_interview_to_csv(session)
    
    # 6. 发送结束消息（检查连接状态）
    try:
        await websocket.send_json({
            "type": "end",
            "reason": reason,
            "csv_path": csv_path,
            "summary": {
                "total_questions": len(session.question_history),
                "average_score": round(avg_score, 1),
                "duration_minutes": (datetime.now() - session.start_time).seconds // 60,
                "job_name": session.job_name
            }
        })
        
        # 7. 等待10秒后发送跳转信号
        await asyncio.sleep(10)
        await websocket.send_json({
            "type": "redirect",
            "target": "home"
        })
    except (RuntimeError, WebSocketDisconnect):
        print(f"[WebSocket] ⚠️ Client disconnected before end messages could be sent")
        # 连接已关闭，跳过后续消息发送


# ==================== HTTP 辅助接口 ====================
@router.get("/interview/session/{session_id}")
async def get_session_status(session_id: str):
    """获取会话状态"""
    if session_id in active_sessions:
        return active_sessions[session_id].to_dict()
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/interview/history/{user_id}")
async def get_interview_history(user_id: str):
    """获取用户的面试历史记录文件列表"""
    records_dir = "data/interview_records"
    if not os.path.exists(records_dir):
        return {"files": []}
    
    files = [
        f for f in os.listdir(records_dir)
        if f.startswith(user_id) and f.endswith('.csv')
    ]
    files.sort(reverse=True)
    return {"files": files}


@router.get("/interview/download/{filename}")
async def download_interview_record(filename: str):
    """下载面试记录CSV文件"""
    filepath = os.path.join("data/interview_records", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    def iterfile():
        with open(filepath, 'rb') as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
