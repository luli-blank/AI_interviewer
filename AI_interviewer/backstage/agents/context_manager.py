"""
面试上下文管理器

负责将面试对话持久化到 .md 文件，支持：
- 创建上下文文件
- 追加对话记录
- 读取完整上下文
- 格式化输出
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# 上下文文件存储目录
CONTEXT_DIR = Path(__file__).parent.parent / "data" / "interview_contexts"


class ContextManager:
    """
    面试上下文管理器
    
    将面试对话以 Markdown 格式持久化存储
    """
    
    def __init__(self, session_id: str, user_id: str, job_name: str):
        """
        初始化上下文管理器
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            job_name: 目标岗位
        """
        self.session_id = session_id
        self.user_id = user_id
        self.job_name = job_name
        self.file_path = self._create_file_path()
        self._ensure_directory()
        
    def _create_file_path(self) -> Path:
        """生成上下文文件路径"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.user_id}_{timestamp}_context.md"
        return CONTEXT_DIR / filename
    
    def _ensure_directory(self):
        """确保目录存在"""
        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self) -> str:
        """获取文件路径字符串"""
        return str(self.file_path)
    
    async def initialize(self, resume_text: str) -> str:
        """
        初始化上下文文件
        
        Args:
            resume_text: 简历文本
            
        Returns:
            文件路径
        """
        header = f"""# 面试上下文记录

## 基本信息
- **会话ID**: {self.session_id}
- **用户ID**: {self.user_id}
- **目标岗位**: {self.job_name}
- **开始时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 简历摘要

```
{resume_text[:2000]}{"..." if len(resume_text) > 2000 else ""}
```

---

## 面试对话记录

"""
        await self._write_file(header, mode='w')
        return self.get_file_path()
    
    async def append_question(
        self, 
        question: str, 
        stage: str,
        question_index: int,
        is_follow_up: bool = False,
        source: Optional[str] = None
    ):
        """
        追加问题记录
        
        Args:
            question: 问题内容
            stage: 当前阶段
            question_index: 问题序号
            is_follow_up: 是否是追问
            source: 题目来源 (rag/web/generated)
        """
        follow_up_mark = " (追问)" if is_follow_up else ""
        source_mark = f" [来源: {source}]" if source else ""
        
        content = f"""
### Q{question_index}{follow_up_mark}{source_mark}
**阶段**: {stage}  
**时间**: {datetime.now().strftime("%H:%M:%S")}

> **面试官**: {question}

"""
        await self._write_file(content)
    
    async def append_answer(
        self,
        answer: str,
        score: Optional[float] = None,
        feedback: Optional[str] = None
    ):
        """
        追加回答记录
        
        Args:
            answer: 候选人回答
            score: 评分
            feedback: 评价
        """
        content = f"""**候选人**: {answer}

"""
        if score is not None:
            content += f"**评分**: {score}/10\n"
        if feedback:
            content += f"**评价**: {feedback}\n"
        content += "\n---\n"
        
        await self._write_file(content)
    
    async def append_stage_transition(self, from_stage: str, to_stage: str):
        """
        追加阶段转换记录
        
        Args:
            from_stage: 原阶段
            to_stage: 新阶段
        """
        content = f"""
## 🔄 阶段转换: {from_stage} → {to_stage}
**时间**: {datetime.now().strftime("%H:%M:%S")}

---

"""
        await self._write_file(content)
    
    async def append_summary(
        self,
        total_questions: int,
        total_score: float,
        stage_scores: Dict[str, float],
        duration_minutes: int
    ):
        """
        追加面试总结
        
        Args:
            total_questions: 总问题数
            total_score: 总分
            stage_scores: 各阶段得分
            duration_minutes: 面试时长
        """
        avg_score = total_score / max(total_questions, 1)
        
        content = f"""
---

## 📊 面试总结

- **总问题数**: {total_questions}
- **平均得分**: {avg_score:.1f}/10
- **面试时长**: {duration_minutes} 分钟

### 各阶段得分

| 阶段 | 得分 |
|------|------|
"""
        for stage, score in stage_scores.items():
            content += f"| {stage} | {score:.1f} |\n"
        
        content += f"""
---

*记录结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        await self._write_file(content)
    
    async def read_full_context(self) -> str:
        """
        读取完整上下文
        
        Returns:
            完整的上下文文本
        """
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self._sync_read_file)
        except FileNotFoundError:
            return ""
    
    def _sync_read_file(self) -> str:
        """同步读取文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def read_recent_context(self, num_exchanges: int = 5) -> str:
        """
        读取最近几轮对话
        
        Args:
            num_exchanges: 要读取的对话轮数
            
        Returns:
            最近的上下文文本
        """
        full_context = await self.read_full_context()
        
        # 按 "---" 分割获取最近的对话
        sections = full_context.split("---")
        
        # 保留头部信息和最近的对话
        if len(sections) <= num_exchanges + 2:
            return full_context
        
        # 头部（基本信息+简历）+ 最近对话
        header_sections = sections[:3]  # 基本信息、简历摘要、对话记录标题
        recent_sections = sections[-(num_exchanges):]
        
        return "---".join(header_sections + recent_sections)
    
    async def _write_file(self, content: str, mode: str = 'a'):
        """
        异步写入文件
        
        Args:
            content: 要写入的内容
            mode: 写入模式 ('w' 或 'a')
        """
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sync_write_file, content, mode)
    
    def _sync_write_file(self, content: str, mode: str = 'a'):
        """同步写入文件"""
        with open(self.file_path, mode, encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def format_context_for_prompt(
        resume_text: str,
        question_history: List[Dict],
        current_stage: str,
        job_name: str
    ) -> str:
        """
        格式化上下文用于 Prompt
        
        Args:
            resume_text: 简历文本
            question_history: 问答历史
            current_stage: 当前阶段
            job_name: 目标岗位
            
        Returns:
            格式化的上下文字符串
        """
        context = f"""## 面试上下文

### 基本信息
- 目标岗位: {job_name}
- 当前阶段: {current_stage}

### 简历摘要
{resume_text[:1500]}

### 已完成的问答 ({len(question_history)} 轮)
"""
        
        for i, record in enumerate(question_history[-5:], 1):  # 只取最近5轮
            context += f"""
**Q{i}** [{record.get('stage', 'N/A')}]: {record.get('question', '')}
**A{i}**: {record.get('answer', '')}
**评分**: {record.get('score', 'N/A')}/10
"""
        
        return context
    
    async def cleanup(self, keep_file: bool = True):
        """
        清理资源
        
        Args:
            keep_file: 是否保留文件
        """
        if not keep_file and self.file_path.exists():
            os.remove(self.file_path)
