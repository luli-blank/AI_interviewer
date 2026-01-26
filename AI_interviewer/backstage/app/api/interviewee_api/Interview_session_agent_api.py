"""
基于 Agent 的面试会话 API

使用 LangGraph Agent 实现智能面试官功能
这是新版本的面试 API，支持：
- 多阶段面试流程
- RAG 题库检索
- Web 搜索增强
- 异步预取优化
- 思考占位符（Filler Words）
"""

import os
import csv
import json
import asyncio
import base64
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jose import jwt, JWTError

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.Resume_message import Resume_messages
from app.utils.ai_interview_service import ai_interview_service
from sqlalchemy import select, desc

# 导入 Agent 模块
# 添加 agents 模块路径到 sys.path
import sys
from pathlib import Path

# 获取 backstage 根目录
BACKSTAGE_ROOT = Path(__file__).parent.parent.parent.parent
if str(BACKSTAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKSTAGE_ROOT))

try:
    from agents.interviewer_agent import interviewer_agent
    from agents.state import InterviewState, InterviewStage
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"[Agent API] ⚠️ Warning: Agent module not available: {e}")
    print(f"[Agent API] Agent features will be disabled. Please ensure agents/ directory exists in {BACKSTAGE_ROOT}")
    AGENT_AVAILABLE = False
    interviewer_agent = None
    InterviewState = dict
    InterviewStage = None

router = APIRouter()

# 活跃会话存储（存储 Agent 状态）
agent_sessions: Dict[str, Any] = {}


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


async def get_latest_resume(user_id: str) -> Optional[Resume_messages]:
    """获取用户最新的简历信息"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Resume_messages)
            .where(Resume_messages.user_id == user_id)
            .order_by(desc(Resume_messages.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()


def save_interview_to_csv(state: InterviewState, output_dir: str = "data/interview_records") -> str:
    """将面试记录保存为CSV文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{state['user_id']}_agent_interview_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            '序号', '阶段', '问题', '候选人回答', '评分', '评价', '是否追问'
        ])
        
        for i, record in enumerate(state['question_history'], 1):
            writer.writerow([
                i,
                record.get('stage', ''),
                record.get('question', ''),
                record.get('answer', ''),
                record.get('score', ''),
                record.get('feedback', ''),
                '是' if record.get('is_follow_up') else '否'
            ])
        
        # 汇总
        writer.writerow([])
        writer.writerow(['面试汇总 (Agent版)'])
        writer.writerow(['目标岗位', state['job_name']])
        writer.writerow(['总题数', len(state['question_history'])])
        avg_score = state['total_score'] / max(len(state['question_history']), 1)
        writer.writerow(['平均得分', f"{avg_score:.1f}"])
        
        start_time = datetime.fromisoformat(state['start_time'])
        duration = (datetime.now() - start_time).seconds // 60
        writer.writerow(['面试时长', f"{duration} 分钟"])
        
        # 阶段得分
        writer.writerow([])
        writer.writerow(['各阶段得分'])
        for stage, score in state.get('stage_scores', {}).items():
            writer.writerow([stage, f"{score:.1f}"])
    
    return filepath


async def send_text_with_tts(
    websocket: WebSocket,
    text: str,
    msg_type: str = "question",
    extra_data: Dict = None
):
    """
    发送文本并生成 TTS 语音
    
    改进：字幕和音频同时发送，避免字幕超前问题
    
    Args:
        websocket: WebSocket 连接
        text: 要发送的文本
        msg_type: 消息类型
        extra_data: 额外数据
    """
    # 1. 发送文本消息（告诉前端有新内容）
    msg = {"type": msg_type, "text": text}
    if extra_data:
        msg.update(extra_data)
    
    try:
        await websocket.send_json(msg)
    except (RuntimeError, WebSocketDisconnect):
        return
    
    # 2. 先生成完整的音频，然后再同时发送字幕和音频
    try:
        # 收集所有音频块
        audio_chunks = []
        async for audio_chunk in ai_interview_service.text_to_speech_stream(text):
            if audio_chunk:
                audio_chunks.append(audio_chunk)
        
        # 发送完整字幕（一次性，不再流式）
        await websocket.send_json({
            "type": "subtitle",
            "text": text,
            "is_final": True
        })
        
        # 流式发送音频块
        for chunk_index, audio_chunk in enumerate(audio_chunks):
            await websocket.send_json({
                "type": "audio_chunk",
                "data": base64.b64encode(audio_chunk).decode('utf-8'),
                "format": "wav",
                "chunk_index": chunk_index,
                "is_final": False
            })
            await asyncio.sleep(0.01)
        
        # 发送音频结束标记
        await websocket.send_json({
            "type": "audio_chunk",
            "data": "",
            "format": "wav",
            "chunk_index": len(audio_chunks),
            "is_final": True
        })
        
        # 不再在后端等待，由前端控制播放完毕后的状态
        
    except (RuntimeError, WebSocketDisconnect):
        pass
    except Exception as e:
        print(f"[Agent WS] ❌ TTS Error: {e}")


@router.websocket("/ws/interview/agent")
async def websocket_interview_agent(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    基于 Agent 的面试 WebSocket 接口
    
    消息格式（JSON）：
    
    客户端发送：
    - {"type": "init"} - 初始化面试
    - {"type": "ready"} - 用户准备好开始
    - {"type": "audio", "data": "base64音频数据"} - 音频数据
    - {"type": "text", "data": "文本回答"} - 文本回答
    - {"type": "end"} - 结束面试
    - {"type": "skip_stage"} - 跳过当前阶段
    
    服务端发送：
    - {"type": "status", "data": {...}} - 状态更新
    - {"type": "question", "text": "...", "stage": "...", "stage_info": {...}}
    - {"type": "thinking", "text": "思考中..."} - 思考占位符
    - {"type": "subtitle", "text": "...", "is_final": bool}
    - {"type": "audio_chunk", "data": "...", "is_final": bool}
    - {"type": "transcription", "text": "...", "is_final": bool}
    - {"type": "analysis", "score": 8, "feedback": "...", "action": "..."}
    - {"type": "stage_change", "from": "...", "to": "..."}
    - {"type": "end", "reason": "...", "summary": {...}}
    - {"type": "error", "message": "..."}
    """
    
    # 检查 Agent 是否可用
    if not AGENT_AVAILABLE or interviewer_agent is None:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Agent module not available")
        print("[Agent WS] ❌ Rejected connection: Agent module not loaded")
        return
    
    # 1. 验证 Token
    user_id = await get_user_id_from_token(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # 2. 接受连接
    await websocket.accept()
    print(f"[Agent WS] 🚀 User {user_id} connected (Agent Mode)")
    
    session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    state: Optional[InterviewState] = None
    
    try:
        while True:
            raw_message = await websocket.receive_text()
            
            try:
                message = json.loads(raw_message)
                msg_type = message.get("type", "")
                
                # ========== 初始化面试 ==========
                if msg_type == "init":
                    state = await handle_agent_init(websocket, session_id, user_id)
                    if state:
                        agent_sessions[session_id] = state
                
                # ========== 用户准备好 ==========
                elif msg_type == "ready":
                    if state:
                        await handle_agent_ready(websocket, state)
                
                # ========== 接收音频数据 ==========
                elif msg_type == "audio":
                    if state:
                        audio_data = base64.b64decode(message.get("data", ""))
                        await handle_agent_audio(websocket, state, audio_data)
                
                # ========== 接收文本回答 ==========
                elif msg_type == "text":
                    if state:
                        text_answer = message.get("data", "")
                        await handle_agent_text(websocket, state, text_answer)
                
                # ========== 跳过当前阶段 ==========
                elif msg_type == "skip_stage":
                    if state:
                        await handle_skip_stage(websocket, state)
                
                # ========== 结束面试 ==========
                elif msg_type == "end":
                    if state:
                        await handle_agent_end(websocket, state)
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
        print(f"[Agent WS] 👋 User {user_id} disconnected")
    except Exception as e:
        print(f"[Agent WS] ❌ Error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except RuntimeError:
            pass
    finally:
        # 清理会话
        if session_id in agent_sessions:
            if state and state.get('question_history'):
                save_interview_to_csv(state)
            del agent_sessions[session_id]
        print(f"[Agent WS] 🧹 Session {session_id} cleaned up")


async def handle_agent_init(
    websocket: WebSocket,
    session_id: str,
    user_id: str
) -> Optional[InterviewState]:
    """处理 Agent 模式的面试初始化"""
    try:
        # 1. 发送状态
        await websocket.send_json({
            "type": "status",
            "data": {"stage": "loading_resume", "message": "正在加载简历信息..."}
        })
        
        # 2. 获取简历
        resume = await get_latest_resume(user_id)
        if not resume or not resume.resume_file_text:
            await websocket.send_json({
                "type": "error",
                "message": "未找到简历信息，请先上传简历"
            })
            return None
        
        resume_text = resume.resume_file_text
        job_name = resume.job_name or "通用岗位"
        
        # 3. 发送状态
        await websocket.send_json({
            "type": "status",
            "data": {"stage": "initializing_agent", "message": "正在初始化 AI 面试官..."}
        })
        
        # 4. 初始化 Agent
        state, opening = await interviewer_agent.initialize_interview(
            session_id=session_id,
            user_id=user_id,
            job_name=job_name,
            resume_text=resume_text
        )
        
        # 5. 发送就绪状态
        stage_info = await interviewer_agent.get_stage_info(state)
        await websocket.send_json({
            "type": "status",
            "data": {
                "stage": "ready",
                "message": "准备就绪，等待开始...",
                "job_name": job_name,
                "interview_stages": stage_info['all_stages'],
                "current_stage": stage_info['current_stage']
            }
        })
        
        # 6. 发送开场白
        await send_text_with_tts(websocket, opening, "opening")
        
        # 7. 自动进入自我介绍阶段并发送第一个问题
        # 开场白不需要用户回答，直接开始正式面试
        state['current_stage'] = InterviewStage.SELF_INTRO
        state['stage_start_time'] = datetime.now().isoformat()
        
        await websocket.send_json({
            "type": "stage_change",
            "from": InterviewStage.OPENING.value,
            "to": InterviewStage.SELF_INTRO.value
        })
        
        # 发送第一个问题
        await send_next_question(websocket, state)
        
        print(f"[Agent WS] ✅ Interview initialized for {user_id}")
        return state
        
    except Exception as e:
        print(f"[Agent WS] ❌ Init error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"初始化失败: {str(e)}"
        })
        return None


async def handle_agent_ready(websocket: WebSocket, state: InterviewState):
    """
    处理用户准备就绪（已废弃 - 现在自动进入面试）
    
    开场白后会自动进入自我介绍阶段，这个函数保留用于向后兼容。
    如果用户发送 ready 消息，只是确认收到，不做其他处理。
    """
    print(f"[Agent WS] 📨 Received ready signal (already in {state['current_stage']} stage)")
    
    # 如果还在 OPENING 阶段（异常情况），手动推进
    if state['current_stage'] == InterviewStage.OPENING:
        state['current_stage'] = InterviewStage.SELF_INTRO
        state['stage_start_time'] = datetime.now().isoformat()
        
        await websocket.send_json({
            "type": "stage_change",
            "from": InterviewStage.OPENING.value,
            "to": InterviewStage.SELF_INTRO.value
        })
        
        await send_next_question(websocket, state)


async def send_next_question(websocket: WebSocket, state: InterviewState):
    """发送下一个问题"""
    
    # 定义思考消息回调
    async def on_thinking(msg: str):
        try:
            await websocket.send_json({
                "type": "thinking",
                "text": msg
            })
            # 也发送语音
            await send_text_with_tts(websocket, msg, "thinking")
        except (RuntimeError, WebSocketDisconnect):
            pass
    
    # 获取问题
    result = await interviewer_agent.get_next_question(state)
    
    # 如果有思考消息且之前没发过，发送它
    if result.get('thinking_message'):
        await on_thinking(result['thinking_message'])
    
    question = result['question']
    stage_info = await interviewer_agent.get_stage_info(state)
    
    # 发送问题
    await send_text_with_tts(
        websocket, 
        question, 
        "question",
        {
            "stage": state['current_stage'],
            "stage_info": stage_info,
            "question_index": len(state['question_history']) + 1
        }
    )


async def handle_agent_audio(
    websocket: WebSocket,
    state: InterviewState,
    audio_data: bytes
):
    """处理音频数据"""
    print(f"[Agent WS] 📥 Received audio: {len(audio_data)} bytes")
    
    try:
        # 1. 语音转文字
        transcription = await ai_interview_service.speech_to_text(audio_data)
        
        # 发送转录结果
        await websocket.send_json({
            "type": "transcription",
            "text": transcription,
            "is_final": True
        })
        
        # 2. 处理回答
        if transcription.strip():
            await process_agent_answer(websocket, state, transcription)
        else:
            print(f"[Agent WS] ⚠️ Empty transcription")
            
    except WebSocketDisconnect:
        print(f"[Agent WS] ⚠️ Client disconnected during audio processing")
    except Exception as e:
        print(f"[Agent WS] ❌ ASR Error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "语音识别失败，请重试"
            })
        except (RuntimeError, WebSocketDisconnect):
            pass


async def handle_agent_text(
    websocket: WebSocket,
    state: InterviewState,
    text: str
):
    """处理文本回答"""
    if text.strip():
        await process_agent_answer(websocket, state, text)


async def process_agent_answer(
    websocket: WebSocket,
    state: InterviewState,
    answer: str
):
    """处理用户回答"""
    print(f"[Agent WS] 👤 Processing answer: {answer}...")
    
    # 1. 发送分析状态
    await websocket.send_json({
        "type": "status",
        "data": {"stage": "analyzing", "message": "正在分析回答..."}
    })
    
    # 2. 使用 Agent 处理回答
    analysis = await interviewer_agent.process_answer(state, answer)
    
    # 3. 发送分析结果
    await websocket.send_json({
        "type": "analysis",
        "score": analysis.get("score", 5),
        "feedback": analysis.get("feedback", ""),
        "action": analysis.get("action", "next_question")
    })
    
    action = analysis.get("action", "next_question")
    
    # 4. 根据决策执行动作
    if action == "follow_up":
        # 追问
        follow_up = analysis.get("follow_up_question", "能再详细说说吗？")
        await send_text_with_tts(
            websocket,
            follow_up,
            "question",
            {
                "is_follow_up": True,
                "stage": state['current_stage']
            }
        )
        state['current_question'] = follow_up
        
    elif action == "next_stage":
        # 阶段转换
        new_stage = analysis.get("next_stage")
        if new_stage:
            await websocket.send_json({
                "type": "stage_change",
                "from": state['current_stage'],
                "to": new_stage
            })
        
        if state['current_stage'] == InterviewStage.CLOSING:
            await handle_agent_end(websocket, state)
        else:
            await asyncio.sleep(1)
            await send_next_question(websocket, state)
        
    elif action == "end_interview":
        await handle_agent_end(websocket, state)
        
    else:
        # 下一个问题
        await asyncio.sleep(1)
        await send_next_question(websocket, state)


async def handle_skip_stage(websocket: WebSocket, state: InterviewState):
    """处理跳过阶段请求"""
    old_stage = state['current_stage']
    new_stage = await interviewer_agent.force_next_stage(state)
    
    if new_stage:
        await websocket.send_json({
            "type": "stage_change",
            "from": old_stage,
            "to": new_stage
        })
        
        if new_stage == InterviewStage.CLOSING:
            await handle_agent_end(websocket, state)
        else:
            await send_next_question(websocket, state)
    else:
        await handle_agent_end(websocket, state)


async def handle_agent_end(
    websocket: WebSocket,
    state: InterviewState,
    reason: str = "completed"
):
    """处理面试结束"""
    print(f"[Agent WS] 🏁 Ending interview: {state['session_id']}")
    
    try:
        # 1. 使用 Agent 结束面试
        result = await interviewer_agent.end_interview(state)
        
        # 2. 保存 CSV（先保存，防止连接断开）
        csv_path = save_interview_to_csv(state)
        
        # 3. 先发送结束语（字幕 + TTS 音频）
        # 这样前端会播放结束语音频
        try:
            await websocket.send_json({
                "type": "closing",
                "text": result['closing_text']
            })
            
            # 使用 send_text_with_tts 发送字幕和音频
            await send_text_with_tts(websocket, result['closing_text'], "closing_speech")
            
        except (RuntimeError, WebSocketDisconnect):
            pass
        
        # 4. 发送结束消息（在结束语发送之后）
        # 前端收到这个消息后会设置 waitingForClosingRemarks = true
        # 等待音频队列播放完毕后才显示弹窗
        await websocket.send_json({
            "type": "end",
            "reason": reason,
            "csv_path": csv_path,
            "summary": result['summary']
        })
        
        print(f"[Agent WS] ✅ End message sent, waiting for client to finish playing closing speech")
        
    except (RuntimeError, WebSocketDisconnect):
        print(f"[Agent WS] ⚠️ Client disconnected during end handling")
    except Exception as e:
        print(f"[Agent WS] ❌ Error during end handling: {e}")


# ==================== HTTP 辅助接口 ====================

@router.get("/interview/agent/stages")
async def get_interview_stages():
    """获取所有面试阶段信息"""
    stages = []
    for stage in InterviewStage.get_stage_order():
        config = InterviewStage.get_stage_config(stage)
        stages.append({
            "stage": stage.value,
            **config
        })
    return {"stages": stages}


@router.get("/interview/agent/session/{session_id}")
async def get_agent_session_status(session_id: str):
    """获取 Agent 会话状态"""
    if session_id in agent_sessions:
        state = agent_sessions[session_id]
        stage_info = await interviewer_agent.get_stage_info(state)
        return {
            "session_id": session_id,
            "user_id": state['user_id'],
            "job_name": state['job_name'],
            "current_stage": state['current_stage'],
            "stage_info": stage_info,
            "questions_count": len(state['question_history']),
            "total_score": state['total_score'],
            "start_time": state['start_time']
        }
    return {"error": "Session not found"}
