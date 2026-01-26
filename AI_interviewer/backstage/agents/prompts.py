"""
提示词模板

定义 Agent 使用的各种 Prompt 模板
"""

# ==================== 系统提示词 ====================

INTERVIEWER_SYSTEM_PROMPT = """你是一位资深的AI面试官，具备以下特点：
1. 专业、友善、有耐心
2. 善于引导候选人展现真实能力
3. 能够根据回答进行有深度的追问
4. 严格按照面试流程推进

## 面试阶段说明
- opening: 开场白，欢迎候选人
- self_intro: 自我介绍，了解候选人背景
- project_deep_dive: 项目深挖，深入了解技术能力
- basic_knowledge: 基础知识考核，考察专业基础
- scenario_algorithm: 场景/算法题，考察问题解决能力
- reverse_interview: 反问环节，让候选人提问
- closing: 结束，感谢并说明后续流程

## 你的任务
1. 根据当前阶段和上下文，生成合适的面试问题
2. 评估候选人的回答质量
3. 决定是否追问或进入下一阶段
4. 确保面试流程完整且专业
"""

# ==================== 关键词生成 ====================

KEYWORD_GENERATION_PROMPT = """根据以下信息，生成用于检索面试题目的关键词。

## 候选人简历摘要
{resume_summary}

## 目标岗位
{job_name}

## 当前面试阶段
{current_stage}

## 最近对话
{recent_context}

## 要求
1. 生成 3-5 个与当前阶段相关的关键词
2. 关键词应该能够检索到有针对性的面试题
3. 考虑候选人的技术栈和经验

请以 JSON 数组格式返回关键词，例如：["Python", "后端开发", "数据库"]
"""

# ==================== 问题生成 ====================

QUESTION_GENERATION_PROMPT = """作为面试官，请根据以下信息生成一个面试问题。

## 当前阶段
{current_stage}（{stage_description}）

## 候选人简历摘要
{resume_summary}

## 目标岗位
{job_name}

## 已问问题（避免重复）
{asked_questions}

## RAG 检索到的候选题目
{rag_results}

## 网络搜索补充信息（如有）
{web_results}

## 最近对话上下文
{recent_context}

## 要求
1. 问题应该与当前阶段主题匹配
2. 如果有合适的 RAG 候选题目，可以直接使用或微调
3. 结合简历内容使问题更有针对性
4. 问题要清晰、具体、可回答
5. 难度适中，循序渐进

请返回 JSON 格式：
{{
    "question": "你的问题",
    "reference_answer": "参考评判标准",
    "source": "rag/web/generated",
    "difficulty": 1-5
}}
"""

# ==================== 回答分析 ====================

ANSWER_ANALYSIS_PROMPT = """分析候选人的回答并决定下一步行动。

## 当前问题
{current_question}

## 参考评判标准
{reference_answer}

## 候选人回答
{user_answer}

## 当前阶段
{current_stage}

## 阶段已问题数
{stage_question_count}

## 当前问题追问次数
{follow_up_count}

## 简历摘要
{resume_summary}

## 要求
评估回答质量（1-10分）：
- 完整性：是否正面回答了问题
- 深度：是否有具体案例和细节
- 逻辑性：表达是否清晰连贯
- 专业性：术语使用是否准确

决定下一步（严格按顺序，绝不允许跳回前面的阶段）：
- "follow_up": 需要追问（回答不够深入、有亮点值得挖掘、有疑点需要澄清）
- "next_question": 继续当前阶段的下一个问题
- "next_stage": 进入下一个面试阶段（严格按 opening→self_intro→project_deep_dive→basic_knowledge→scenario_algorithm→reverse_interview→closing 顺序）
- "end_interview": 结束面试（仅在 closing 阶段或特殊情况使用）

重要约束：
1. 绝对不要跳回到已经完成的阶段（例如从 project_deep_dive 跳回 self_intro）
2. 阶段只能向前推进，不能后退
3. 当前阶段完成后，必须进入下一个阶段，而不是前一个

请返回 JSON 格式：
{{
    "score": 评分数字,
    "feedback": "简短评价，不超过 50 字",
    "action": "follow_up/next_question/next_stage/end_interview",
    "follow_up_question": "追问问题（仅当 action 为 follow_up 时需要）",
    "reason": "决策理由，不超过 30 字",
    "should_advance_stage": true/false
}}
"""

# ==================== 追问生成 ====================

FOLLOW_UP_PROMPT = """根据候选人的回答生成一个追问问题。

## 原问题
{original_question}

## 候选人回答
{user_answer}

## 追问原因
{follow_up_reason}

## 简历相关信息
{resume_context}

## 要求
1. 追问应该深挖候选人回答中的细节
2. 可以要求举具体例子
3. 可以询问技术实现细节
4. 可以探讨遇到的挑战和解决方案
5. 追问要自然流畅，不要像审问

请直接返回追问问题文本。
"""

# ==================== 阶段转换 ====================

STAGE_TRANSITION_PROMPT = """根据面试进展决定是否转换阶段。

## 当前阶段
{current_stage}

## 阶段配置
- 最少问题数: {min_questions}
- 最多问题数: {max_questions}
- 已问问题数: {asked_count}

## 最近回答质量
{recent_scores}

## 面试已用时间
{elapsed_minutes} 分钟

## 要求
决定是否应该进入下一阶段：
1. 如果已达到最多问题数，应该转换
2. 如果回答质量稳定且达到最少问题数，可以转换
3. 考虑整体面试时间控制

请返回 JSON 格式：
{{
    "should_advance": true/false,
    "reason": "决策理由"
}}
"""

# ==================== 开场白 ====================

OPENING_PROMPT = """生成面试开场白。

## 候选人姓名
{candidate_name}

## 目标岗位
{job_name}

## 要求
1. 友好、专业
2. 介绍自己是 AI 面试官
3. 简要说明面试流程
4. 确认设备准备
5. 控制在 100 字以内

请直接返回开场白文本。
"""

# ==================== 结束语 ====================

CLOSING_PROMPT = """生成面试结束语。

## 问答历史摘要
{qa_summary}

## 整体评分
{overall_score}/10

## 面试时长
{duration_minutes} 分钟

## 要求
1. 感谢候选人参与
2. 简要肯定亮点（如果有）
3. 说明后续流程
4. 专业友善
5. 控制在 100 字以内

请直接返回结束语文本。
"""

# ==================== 思考占位符（Filler Words）====================

FILLER_MESSAGES = {
    "searching": [
        "让我想想如何更好地考察这个方向...",
        "这个问题涉及的内容比较广，让我整理一下...",
        "根据你的回答，我想深入了解一些细节...",
    ],
    "web_search": [
        "这个技术点我需要确认一下最新的信息...",
        "让我查证一下相关的技术细节...",
        "稍等，我核实一下这个领域的最新动态...",
    ],
    "thinking": [
        "好的，让我根据你的回答想一个更有针对性的问题...",
        "我在整理一下思路...",
        "基于你的经历，我想从另一个角度考察...",
    ],
    "transitioning": [
        "好的，我们换一个方向...",
        "接下来我们进入下一个环节...",
        "这部分考察得差不多了，让我们继续...",
    ]
}

# ==================== 预取提示 ====================

PREFETCH_PROMPT = """根据面试进展预测下一个可能的问题方向。

## 当前阶段
{current_stage}

## 简历摘要
{resume_summary}

## 已问问题
{asked_questions}

## 最近回答
{recent_answer}

## 要求
预测接下来最可能需要的问题类型和关键词，用于提前检索。

请返回 JSON 格式：
{{
    "predicted_topics": ["话题1", "话题2"],
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "likely_next_stage": "可能的下一阶段"
}}
"""
