"""
面试官智能体

对外提供的统一接口，封装所有面试官 Agent 功能
后端只需要调用这个模块的方法，无需关心内部实现
"""

import os
import json
import asyncio
import random
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import (
    InterviewState, 
    InterviewStage, 
    QuestionRecord,
    create_initial_state
)
from .graph import interview_graph
from .context_manager import ContextManager
from .tools.rag_tool import rag_tool
from .tools.web_search_tool import web_search_tool
from .prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    ANSWER_ANALYSIS_PROMPT,
    FOLLOW_UP_PROMPT,
    STAGE_TRANSITION_PROMPT,
    OPENING_PROMPT,
    CLOSING_PROMPT,
    PREFETCH_PROMPT,
    FILLER_MESSAGES
)

load_dotenv()


class InterviewerAgent:
    """
    面试官智能体
    
    提供完整的面试官功能，包括：
    - 面试初始化
    - 问题生成（带异步预取）
    - 回答分析
    - 阶段管理
    - 上下文持久化
    
    使用示例:
    ```python
    agent = InterviewerAgent()
    
    # 1. 初始化面试
    state, opening = await agent.initialize_interview(
        session_id="xxx",
        user_id="user123",
        job_name="Python开发工程师",
        resume_text="..."
    )
    
    # 2. 获取问题
    result = await agent.get_next_question(state)
    question = result["question"]
    thinking_msg = result.get("thinking_message")  # 如果需要等待，先播放这个
    
    # 3. 处理回答
    analysis = await agent.process_answer(state, user_answer)
    
    # 4. 结束面试
    closing = await agent.end_interview(state)
    ```
    """
    
    def __init__(self):
        """初始化面试官 Agent"""
        # LLM 客户端
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=os.getenv("Deepseek_API_Key"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            temperature=0.7
        )
        
        self.llm_precise = ChatOpenAI(
            model="deepseek-chat",
            api_key=os.getenv("Deepseek_API_Key"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            temperature=0.3
        )
        
        # 预取任务缓存
        self._prefetch_cache: Dict[str, asyncio.Task] = {}
        
        # 上下文管理器缓存
        self._context_managers: Dict[str, ContextManager] = {}
        
    # ==================== 初始化 ====================
    
    async def initialize_interview(
        self,
        session_id: str,
        user_id: str,
        job_name: str,
        resume_text: str
    ) -> Tuple[InterviewState, str]:
        """
        初始化面试
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            job_name: 目标岗位
            resume_text: 简历文本
            
        Returns:
            (初始状态, 开场白文本)
        """
        print(f"[Interviewer Agent] 🚀 Initializing interview for {user_id}")
        
        # 1. 创建上下文管理器
        context_manager = ContextManager(session_id, user_id, job_name)
        context_file = await context_manager.initialize(resume_text)
        self._context_managers[session_id] = context_manager
        
        # 2. 初始化 RAG 工具（预加载题库）
        await rag_tool.initialize()
        
        # 3. 创建初始状态
        state = create_initial_state(
            session_id=session_id,
            user_id=user_id,
            job_name=job_name,
            resume_text=resume_text,
            context_file_path=context_file
        )
        
        # 4. 生成开场白
        opening = await self._generate_opening(job_name)
        
        # 5. 启动预取任务（为第一个问题预热）
        self._start_prefetch(state)
        
        print(f"[Interviewer Agent] ✅ Interview initialized. Context file: {context_file}")
        
        return state, opening
    
    async def _generate_opening(self, job_name: str, candidate_name: str = "同学") -> str:
        """生成开场白"""
        prompt = OPENING_PROMPT.format(
            candidate_name=candidate_name,
            job_name=job_name
        )
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一位专业的 AI 面试官。"),
                HumanMessage(content=prompt)
            ])
            return response.content.strip()
        except Exception as e:
            print(f"[Interviewer Agent] ❌ Opening generation error: {e}")
            return f"你好{candidate_name}，我是今天的 AI 面试官。欢迎参加{job_name}岗位的面试。请确认你的设备准备就绪，准备好了就可以开始。"
    
    # ==================== 问题生成 ====================
    
    async def get_next_question(
        self,
        state: InterviewState,
        on_thinking: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        获取下一个面试问题
        
        Args:
            state: 当前面试状态
            on_thinking: 思考消息回调（用于发送 filler words）
            
        Returns:
            {
                "question": str,
                "reference_answer": str,
                "thinking_message": Optional[str],  # 如果有延迟需要播放
                "stage": str,
                "is_stage_changed": bool
            }
        """
        session_id = state['session_id']
        current_stage = state['current_stage']
        
        # 清除旧的预取缓存（禁用预取以避免阶段错乱）
        if session_id in self._prefetch_cache:
            old_task = self._prefetch_cache[session_id]
            if not old_task.done():
                old_task.cancel()
            del self._prefetch_cache[session_id]
        
        print(f"[Interviewer Agent] 🎯 Generating question for stage: {current_stage}")
        
        # 发送思考消息（如果有回调）
        thinking_msg = random.choice(FILLER_MESSAGES["thinking"])
        if on_thinking:
            on_thinking(thinking_msg)
        
        # 使用 LangGraph 生成问题
        result = await interview_graph.generate_question(state)
        
        # 更新状态
        state['current_question'] = result['question']
        state['stage_question_count'] += 1
        
        # 记录到上下文文件
        context_manager = self._context_managers.get(session_id)
        if context_manager:
            await context_manager.append_question(
                question=result['question'],
                stage=state['current_stage'],
                question_index=len(state['question_history']) + 1,
                source=result.get('source', 'generated')
            )
        
        print(f"[Interviewer Agent] ✅ Question generated for {current_stage}: {result['question'][:50]}...")
        
        return {
            "question": result['question'],
            "reference_answer": result.get('reference_answer', ''),
            "thinking_message": result.get('thinking_message'),
            "stage": state['current_stage'],
            "is_stage_changed": False
        }
    
    def _start_prefetch(self, state: InterviewState):
        """[DISABLED] 预取功能已禁用以避免阶段错乱"""
        # 禁用预取，因为它会导致阶段不同步
        pass
    
    # ==================== 回答处理 ====================
    
    async def process_answer(
        self,
        state: InterviewState,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        处理用户回答
        
        Args:
            state: 当前面试状态
            user_answer: 用户的回答
            
        Returns:
            {
                "score": float,
                "feedback": str,
                "action": str,  # "follow_up", "next_question", "next_stage", "end_interview"
                "follow_up_question": Optional[str],
                "should_advance_stage": bool,
                "next_stage": Optional[str]
            }
        """
        print(f"[Interviewer Agent] 📝 Processing answer: {user_answer[:50]}...")
        
        session_id = state['session_id']
        current_question = state.get('current_question', '')
        
        # 1. 分析回答
        analysis = await self._analyze_answer(state, user_answer)
        
        # 2. 记录到历史
        record = QuestionRecord(
            question=current_question,
            answer=user_answer,
            score=analysis.get('score', 5),
            feedback=analysis.get('feedback', ''),
            stage=state['current_stage'],
            is_follow_up=state['follow_up_count'] > 0,
            reference_answer=state.get('output_reference'),
            source='agent',
            timestamp=datetime.now().isoformat()
        )
        state['question_history'].append(record)
        
        # 3. 更新分数
        state['total_score'] += analysis.get('score', 5)
        
        # 更新阶段分数
        stage_key = state['current_stage']
        if stage_key not in state['stage_scores']:
            state['stage_scores'][stage_key] = 0
        state['stage_scores'][stage_key] += analysis.get('score', 5)
        
        # 4. 记录到上下文文件
        context_manager = self._context_managers.get(session_id)
        if context_manager:
            await context_manager.append_answer(
                answer=user_answer,
                score=analysis.get('score'),
                feedback=analysis.get('feedback')
            )
        
        # 5. 根据分析结果决定下一步
        action = analysis.get('action', 'next_question')
        should_advance = analysis.get('should_advance_stage', False)
        
        # 检查是否需要进入下一阶段
        if should_advance or action == 'next_stage':
            next_stage = InterviewStage.get_next_stage(state['current_stage'])
            
            # 关键校验：确保只能向前推进，不能跳回
            if next_stage:
                stage_order = InterviewStage.get_stage_order()
                current_idx = stage_order.index(state['current_stage'])
                next_idx = stage_order.index(next_stage)
                
                # 只允许向前进入下一个阶段
                if next_idx == current_idx + 1:
                    # 记录阶段转换
                    if context_manager:
                        await context_manager.append_stage_transition(
                            from_stage=state['current_stage'],
                            to_stage=next_stage
                        )
                    
                    print(f"[Interviewer Agent] 🚦 Stage transition: {state['current_stage']} -> {next_stage}")
                    state['current_stage'] = next_stage
                    state['stage_question_count'] = 0
                    state['follow_up_count'] = 0
                    state['stage_start_time'] = datetime.now().isoformat()
                    
                    analysis['next_stage'] = next_stage
                    analysis['action'] = 'next_stage'
                else:
                    # 防止跳跃或后退
                    print(f"[Interviewer Agent] ⚠️ Prevented invalid stage jump: {state['current_stage']} -> {next_stage}")
                    analysis['should_advance_stage'] = False
                    analysis['action'] = 'next_question'
            else:
                # 没有下一阶段，结束面试
                analysis['action'] = 'end_interview'
        
        # 处理追问
        if action == 'follow_up':
            state['follow_up_count'] += 1
            
            # 如果追问超过限制，改为下一题
            if state['follow_up_count'] >= 2:
                analysis['action'] = 'next_question'
                state['follow_up_count'] = 0
        else:
            state['follow_up_count'] = 0
        
        # 检查是否到达结束阶段
        if state['current_stage'] == InterviewStage.CLOSING:
            analysis['action'] = 'end_interview'
        
        return analysis
    
    async def _analyze_answer(
        self,
        state: InterviewState,
        user_answer: str
    ) -> Dict[str, Any]:
        """分析用户回答"""
        stage_config = InterviewStage.get_stage_config(state['current_stage'])
        
        # 获取阶段顺序信息
        stage_order = InterviewStage.get_stage_order()
        current_idx = stage_order.index(state['current_stage'])
        next_stage = stage_order[current_idx + 1] if current_idx < len(stage_order) - 1 else "END"
        
        # 构建 prompt，包含阶段顺序约束
        prompt = ANSWER_ANALYSIS_PROMPT.format(
            current_question=state.get('current_question', ''),
            reference_answer=state.get('output_reference', '无'),
            user_answer=user_answer,
            current_stage=state['current_stage'],
            stage_question_count=state['stage_question_count'],
            follow_up_count=state['follow_up_count'],
            resume_summary=state['resume_text'][:1000]
        )
        
        # 添加额外的阶段约束
        stage_constraint = f"""

注意：当前阶段是 [{state['current_stage']}]，下一个阶段只能是 [{next_stage}]。
阶段顺序：opening → self_intro → project_deep_dive → basic_knowledge → scenario_algorithm → reverse_interview → closing
绝对禁止跳回已完成的阶段！"""
        
        try:
            response = await self.llm_precise.ainvoke([
                SystemMessage(content=INTERVIEWER_SYSTEM_PROMPT),
                HumanMessage(content=prompt + stage_constraint)
            ])
            
            content = response.content.strip()
            
            # 提取 JSON
            if '{' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                result = json.loads(content[start:end])
            else:
                result = {
                    "score": 5,
                    "feedback": "回答已记录",
                    "action": "next_question",
                    "should_advance_stage": False
                }
            
            # 检查是否应该进入下一阶段
            min_questions = stage_config.get('min_questions', 1)
            max_questions = stage_config.get('max_questions', 3)
            
            if state['stage_question_count'] >= max_questions:
                result['should_advance_stage'] = True
            elif state['stage_question_count'] >= min_questions:
                # 如果回答质量稳定，可以提前进入下一阶段
                if result.get('score', 5) >= 7:
                    result['should_advance_stage'] = True
            
            print(f"[Interviewer Agent] ✅ Analysis: score={result.get('score')}, action={result.get('action')}")
            return result
            
        except Exception as e:
            print(f"[Interviewer Agent] ❌ Analysis error: {e}")
            return {
                "score": 5,
                "feedback": "系统处理中",
                "action": "next_question",
                "should_advance_stage": False
            }
    
    # ==================== 阶段管理 ====================
    
    async def get_stage_info(self, state: InterviewState) -> Dict[str, Any]:
        """
        获取当前阶段信息
        
        Args:
            state: 当前面试状态
            
        Returns:
            阶段配置信息
        """
        stage_config = InterviewStage.get_stage_config(state['current_stage'])
        return {
            "current_stage": state['current_stage'],
            "stage_name": stage_config.get('name', ''),
            "stage_description": stage_config.get('description', ''),
            "questions_asked": state['stage_question_count'],
            "min_questions": stage_config.get('min_questions', 1),
            "max_questions": stage_config.get('max_questions', 3),
            "all_stages": [s.value for s in InterviewStage.get_stage_order()]
        }
    
    async def force_next_stage(self, state: InterviewState) -> Optional[InterviewStage]:
        """
        强制进入下一阶段
        
        Args:
            state: 当前面试状态
            
        Returns:
            新的阶段，如果已是最后阶段则返回 None
        """
        next_stage = InterviewStage.get_next_stage(state['current_stage'])
        
        if next_stage:
            context_manager = self._context_managers.get(state['session_id'])
            if context_manager:
                await context_manager.append_stage_transition(
                    from_stage=state['current_stage'],
                    to_stage=next_stage
                )
            
            state['current_stage'] = next_stage
            state['stage_question_count'] = 0
            state['follow_up_count'] = 0
            state['stage_start_time'] = datetime.now().isoformat()
            
            print(f"[Interviewer Agent] ➡️ Forced stage transition to: {next_stage}")
        
        return next_stage
    
    # ==================== 结束面试 ====================
    
    async def end_interview(self, state: InterviewState) -> Dict[str, Any]:
        """
        结束面试
        
        Args:
            state: 当前面试状态
            
        Returns:
            {
                "closing_text": str,
                "summary": {
                    "total_questions": int,
                    "average_score": float,
                    "duration_minutes": int,
                    "stage_scores": dict
                }
            }
        """
        session_id = state['session_id']
        print(f"[Interviewer Agent] 🏁 Ending interview: {session_id}")
        
        # 1. 计算统计信息
        total_questions = len(state['question_history'])
        average_score = state['total_score'] / max(total_questions, 1)
        
        start_time = datetime.fromisoformat(state['start_time'])
        duration_minutes = (datetime.now() - start_time).seconds // 60
        
        # 2. 生成结束语
        closing_text = await self._generate_closing(
            state['question_history'],
            average_score,
            duration_minutes
        )
        
        # 3. 记录总结到上下文文件
        context_manager = self._context_managers.get(session_id)
        if context_manager:
            await context_manager.append_summary(
                total_questions=total_questions,
                total_score=state['total_score'],
                stage_scores=state['stage_scores'],
                duration_minutes=duration_minutes
            )
        
        # 4. 清理资源
        await self._cleanup(session_id)
        
        return {
            "closing_text": closing_text,
            "summary": {
                "total_questions": total_questions,
                "average_score": round(average_score, 1),
                "duration_minutes": duration_minutes,
                "stage_scores": state['stage_scores']
            }
        }
    
    async def _generate_closing(
        self,
        question_history: List[Dict],
        overall_score: float,
        duration_minutes: int
    ) -> str:
        """生成结束语"""
        # 简化问答历史
        qa_summary = "\n".join([
            f"Q: {q.get('question', '')[:50]}... A: 评分{q.get('score', 'N/A')}"
            for q in question_history[-5:]
        ])
        
        prompt = CLOSING_PROMPT.format(
            qa_summary=qa_summary,
            overall_score=overall_score,
            duration_minutes=duration_minutes
        )
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一位专业的 AI 面试官。"),
                HumanMessage(content=prompt)
            ])
            return response.content.strip()
        except Exception as e:
            print(f"[Interviewer Agent] ❌ Closing generation error: {e}")
            return "好的，今天的面试就到这里。感谢你的参与，后续结果我们会通过邮件通知你。祝你一切顺利！"
    
    async def _cleanup(self, session_id: str):
        """清理会话资源"""
        # 取消预取任务
        if session_id in self._prefetch_cache:
            task = self._prefetch_cache[session_id]
            if not task.done():
                task.cancel()
            del self._prefetch_cache[session_id]
        
        # 清理上下文管理器引用（保留文件）
        if session_id in self._context_managers:
            del self._context_managers[session_id]
        
        print(f"[Interviewer Agent] 🧹 Cleaned up session: {session_id}")
    
    # ==================== 工具方法 ====================
    
    async def get_filler_message(self, message_type: str = "thinking") -> str:
        """
        获取思考占位符消息
        
        Args:
            message_type: 消息类型 (searching, web_search, thinking, transitioning)
            
        Returns:
            随机选择的占位符消息
        """
        messages = FILLER_MESSAGES.get(message_type, FILLER_MESSAGES["thinking"])
        return random.choice(messages)
    
    async def search_question_bank(
        self,
        keywords: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        直接搜索题库（调试用）
        
        Args:
            keywords: 关键词列表
            top_k: 返回数量
            
        Returns:
            检索到的题目列表
        """
        await rag_tool.initialize()
        return await rag_tool.search_by_keywords(keywords, top_k)


# 单例实例
interviewer_agent = InterviewerAgent()
