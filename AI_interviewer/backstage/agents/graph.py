"""
LangGraph 面试工作流

定义面试官 Agent 的工作流程，包括：
- 状态管理
- 节点定义
- 边缘条件
- 工作流编排
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from dotenv import load_dotenv

# LangGraph 相关导入
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 本地模块导入
from .state import InterviewState, InterviewStage, QuestionRecord, create_initial_state
from .tools.rag_tool import rag_tool
from .tools.web_search_tool import web_search_tool
from .context_manager import ContextManager
from .prompts import (
    INTERVIEWER_SYSTEM_PROMPT,
    KEYWORD_GENERATION_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_ANALYSIS_PROMPT,
    FOLLOW_UP_PROMPT,
    STAGE_TRANSITION_PROMPT,
    OPENING_PROMPT,
    CLOSING_PROMPT,
    PREFETCH_PROMPT,
    FILLER_MESSAGES
)

load_dotenv()


class InterviewGraph:
    """
    面试工作流图
    
    使用 LangGraph 实现面试官的决策流程
    """
    
    def __init__(self):
        """初始化面试工作流"""
        # 初始化 LLM（使用 DeepSeek）
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
            temperature=0.3  # 更低温度用于精确任务
        )
        
        # 构建工作流图
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
        
    def _build_graph(self) -> StateGraph:
        """
        构建 LangGraph 工作流
        
        节点：
        1. generate_keywords - 生成搜索关键词
        2. rag_search - RAG 题库检索
        3. decide_web_search - 决定是否需要网络搜索
        4. web_search - 网络搜索（可选）
        5. generate_question - 生成问题
        6. output_question - 输出问题（最终节点）
        
        Returns:
            StateGraph 实例
        """
        # 创建状态图
        graph = StateGraph(InterviewState)
        
        # 添加节点
        graph.add_node("generate_keywords", self._node_generate_keywords)
        graph.add_node("rag_search", self._node_rag_search)
        graph.add_node("decide_web_search", self._node_decide_web_search)
        graph.add_node("web_search", self._node_web_search)
        graph.add_node("generate_question", self._node_generate_question)
        graph.add_node("output_question", self._node_output_question)
        
        # 设置入口点
        graph.set_entry_point("generate_keywords")
        
        # 添加边
        graph.add_edge("generate_keywords", "rag_search")
        graph.add_edge("rag_search", "decide_web_search")
        
        # 条件边：决定是否进行网络搜索
        graph.add_conditional_edges(
            "decide_web_search",
            self._should_web_search,
            {
                "search": "web_search",
                "skip": "generate_question"
            }
        )
        
        graph.add_edge("web_search", "generate_question")
        graph.add_edge("generate_question", "output_question")
        graph.add_edge("output_question", END)
        
        return graph
    
    # ==================== 节点实现 ====================
    
    async def _node_generate_keywords(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：生成搜索关键词
        
        根据简历、岗位、阶段和上下文生成检索关键词
        """
        print(f"[Graph Node] 🔑 Generating keywords for stage: {state['current_stage']}")
        
        # 构建 Prompt
        prompt = KEYWORD_GENERATION_PROMPT.format(
            resume_summary=state['resume_text'][:1500],
            job_name=state['job_name'],
            current_stage=state['current_stage'],
            recent_context=self._format_recent_qa(state['question_history'][-3:])
        )
        
        try:
            response = await self.llm_precise.ainvoke([
                SystemMessage(content="你是一个关键词生成助手，只输出 JSON 数组。"),
                HumanMessage(content=prompt)
            ])
            
            # 解析关键词
            content = response.content.strip()
            # 尝试提取 JSON 数组
            if '[' in content and ']' in content:
                start = content.index('[')
                end = content.rindex(']') + 1
                keywords = json.loads(content[start:end])
            else:
                keywords = content.split(',')
            
            keywords = [k.strip().strip('"\'') for k in keywords if k.strip()]
            print(f"[Graph Node] ✅ Generated keywords: {keywords}")
            
            return {"search_keywords": keywords}
            
        except Exception as e:
            print(f"[Graph Node] ❌ Keyword generation error: {e}")
            # 后备关键词
            fallback_keywords = [state['job_name'], state['current_stage']]
            return {"search_keywords": fallback_keywords}
    
    async def _node_rag_search(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：RAG 题库检索
        
        使用生成的关键词从题库中检索相关题目
        """
        print(f"[Graph Node] 📚 RAG searching with keywords: {state['search_keywords']}")
        
        # 确保 RAG 工具已初始化
        await rag_tool.initialize()
        
        # 执行检索
        results = await rag_tool.search_by_keywords(
            keywords=state['search_keywords'],
            top_k=5
        )
        
        # 过滤已问过的题目
        asked_questions = {q['question'] for q in state['question_history']}
        filtered_results = [
            r for r in results 
            if r['question'] not in asked_questions
        ]
        
        print(f"[Graph Node] ✅ RAG returned {len(filtered_results)} unique results")
        
        return {"rag_results": filtered_results}
    
    async def _node_decide_web_search(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：决定是否需要网络搜索
        
        根据 RAG 结果质量和阶段需求决定
        """
        rag_results = state.get('rag_results', [])
        current_stage = state['current_stage']
        
        # 决策逻辑：
        # 1. 如果 RAG 结果为空或分数过低，考虑网络搜索
        # 2. 如果是项目深挖阶段且简历提到特定技术，可能需要搜索
        # 3. 如果是场景题阶段，可能需要最新案例
        
        needs_search = False
        thinking_message = None
        
        if not rag_results:
            needs_search = True
            thinking_message = FILLER_MESSAGES["searching"][0]
        elif all(r.get('score', 0) < 0.5 for r in rag_results):
            needs_search = True
            thinking_message = FILLER_MESSAGES["web_search"][0]
        elif current_stage == InterviewStage.PROJECT_DEEP_DIVE:
            # 检查简历中是否有需要验证的技术
            resume_lower = state['resume_text'].lower()
            tech_keywords = ['kubernetes', 'kafka', 'elasticsearch', 'tensorflow', 'pytorch']
            if any(tech in resume_lower for tech in tech_keywords):
                needs_search = True
                thinking_message = FILLER_MESSAGES["web_search"][1]
        
        print(f"[Graph Node] 🤔 Web search decision: {needs_search}")
        
        return {
            "needs_web_search": needs_search,
            "thinking_message": thinking_message
        }
    
    def _should_web_search(self, state: InterviewState) -> Literal["search", "skip"]:
        """条件函数：判断是否执行网络搜索"""
        if state.get('needs_web_search', False):
            return "search"
        return "skip"
    
    async def _node_web_search(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：网络搜索
        
        执行网络搜索获取补充信息
        """
        print(f"[Graph Node] 🌐 Performing web search...")
        
        # 构建搜索查询
        keywords = state.get('search_keywords', [])
        job_name = state['job_name']
        query = f"{job_name} {' '.join(keywords)} 面试题"
        
        try:
            results = await web_search_tool.search(query, max_results=3)
            print(f"[Graph Node] ✅ Web search returned {len(results)} results")
            return {"web_search_results": results}
        except Exception as e:
            print(f"[Graph Node] ❌ Web search error: {e}")
            return {"web_search_results": []}
    
    async def _node_generate_question(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：生成面试问题
        
        综合所有信息生成最终的面试问题
        """
        current_stage = state['current_stage']
        print(f"[Graph Node] 💬 Generating question for stage: {current_stage}")
        
        # 获取阶段配置
        stage_config = InterviewStage.get_stage_config(current_stage)
        
        # 获取阶段顺序和当前位置
        stage_order = InterviewStage.get_stage_order()
        current_stage_idx = stage_order.index(current_stage) if current_stage in stage_order else 0
        stage_progress = f"({current_stage_idx + 1}/{len(stage_order)})"
        
        # 格式化 RAG 结果
        rag_formatted = self._format_rag_results(state.get('rag_results', []))
        
        # 格式化 Web 结果
        web_formatted = web_search_tool.format_results_for_prompt(
            state.get('web_search_results', [])
        ) if state.get('web_search_results') else "无"
        
        # 构建 Prompt - 强调当前阶段约束
        prompt = QUESTION_GENERATION_PROMPT.format(
            current_stage=f"{current_stage} {stage_progress}",
            stage_description=stage_config.get('description', ''),
            resume_summary=state['resume_text'][:1500],
            job_name=state['job_name'],
            asked_questions=self._format_asked_questions(state['question_history']),
            rag_results=rag_formatted,
            web_results=web_formatted,
            recent_context=self._format_recent_qa(state['question_history'][-3:])
        )
        
        # 添加阶段约束提示
        stage_constraint = f"""

重要约束：
1. 当前阶段是 [{current_stage}]，必须生成与此阶段匹配的问题
2. 绝对禁止生成“请做一个自我介绍”或开场白类问题（除非当前阶段是 self_intro）
3. 如果当前是 project_deep_dive 阶段，应询问项目技术细节
4. 如果当前是 basic_knowledge 阶段，应询问专业基础知识
5. 如果当前是 scenario_algorithm 阶段，应询问场景或算法题
6. 问题必须与已问问题不重复
"""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=INTERVIEWER_SYSTEM_PROMPT),
                HumanMessage(content=prompt + stage_constraint)
            ])
            
            # 解析 JSON 响应
            content = response.content.strip()
            # 提取 JSON
            if '{' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                result = json.loads(content[start:end])
            else:
                result = {
                    "question": content,
                    "reference_answer": "",
                    "source": "generated",
                    "difficulty": 3
                }
            
            print(f"[Graph Node] ✅ Generated question: {result.get('question', '')[:50]}...")
            
            return {
                "output_question": result.get('question', ''),
                "output_reference": result.get('reference_answer', '')
            }
            
        except Exception as e:
            print(f"[Graph Node] ❌ Question generation error: {e}")
            # 使用 RAG 结果作为后备
            if state.get('rag_results'):
                fallback = state['rag_results'][0]
                return {
                    "output_question": fallback['question'],
                    "output_reference": fallback.get('reference_answer', '')
                }
            return {
                "output_question": "请介绍一下你最近参与的一个项目。",
                "output_reference": ""
            }
    
    async def _node_output_question(self, state: InterviewState) -> Dict[str, Any]:
        """
        节点：输出问题（最终节点）
        
        准备最终输出
        """
        print(f"[Graph Node] 📤 Outputting question: {state.get('output_question', '')[:50]}...")
        return {}  # 状态已经包含输出
    
    # ==================== 辅助方法 ====================
    
    def _format_recent_qa(self, qa_list: List[Dict]) -> str:
        """格式化最近的问答记录"""
        if not qa_list:
            return "（这是第一个问题）"
        
        formatted = ""
        for i, qa in enumerate(qa_list, 1):
            formatted += f"\nQ{i}: {qa.get('question', '')}\n"
            formatted += f"A{i}: {qa.get('answer', '')}\n"
            formatted += f"评分: {qa.get('score', 'N/A')}/10\n"
        return formatted
    
    def _format_rag_results(self, results: List[Dict]) -> str:
        """格式化 RAG 检索结果"""
        if not results:
            return "无相关题目"
        
        formatted = ""
        for i, r in enumerate(results, 1):
            formatted += f"\n{i}. [{r.get('category', 'N/A')}] {r['question']}\n"
            formatted += f"   参考: {r.get('reference_answer', 'N/A')[:100]}...\n"
            formatted += f"   难度: {r.get('difficulty', 3)}/5, 相似度: {r.get('score', 0):.2f}\n"
        return formatted
    
    def _format_asked_questions(self, history: List[Dict]) -> str:
        """格式化已问过的问题列表"""
        if not history:
            return "（暂无）"
        return "\n".join([f"- {q.get('question', '')}" for q in history])
    
    # ==================== 公开接口 ====================
    
    async def generate_question(self, state: InterviewState) -> Dict[str, Any]:
        """
        生成面试问题（主入口）
        
        Args:
            state: 当前面试状态
            
        Returns:
            包含问题和参考答案的字典
        """
        # 运行工作流
        result = await self.compiled_graph.ainvoke(state)
        
        return {
            "question": result.get('output_question', ''),
            "reference_answer": result.get('output_reference', ''),
            "thinking_message": result.get('thinking_message')
        }


# 单例实例
interview_graph = InterviewGraph()
