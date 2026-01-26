"""
AI面试服务模块
提供TTS、ASR、LLM等AI能力的封装
"""

import json
import asyncio
from typing import AsyncGenerator, Optional, List, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings
from dotenv import load_dotenv
import os
import dashscope  # 引入 dashscope 原生 SDK
import base64     # 引入 base64
import numpy as np # 引入 numpy
import struct     # 引入 struct 用于构建 wav 头

load_dotenv()
# ==================== 配置 ====================
# DeepSeek Chat API 配置
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 阿里云百炼 API 配置 (用于 TTS 和 ASR)
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1" # OpenAI兼容接口地址
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 设置 dashscope 全局配置 (原生 SDK 需要)
dashscope.api_key = DASHSCOPE_API_KEY
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1' # 原生 SDK 接口地址

# ==================== 题库模板（临时，后续迁移到数据库）====================
INTERVIEW_QUESTION_BANK = {
    "通用问题": [
        {
            "question": "请先做一个简短的自我介绍。",
            "reference_answer": "观察候选人的表达能力、逻辑性、以及是否能突出自己的亮点。",
            "category": "开场",
            "difficulty": 1
        },
        {
            "question": "你为什么想要应聘这个岗位？",
            "reference_answer": "考察候选人对岗位的理解、职业规划、以及动机是否匹配。",
            "category": "动机",
            "difficulty": 1
        },
        {
            "question": "你觉得自己最大的优势是什么？",
            "reference_answer": "考察候选人的自我认知能力，优势是否与岗位要求匹配。",
            "category": "自我认知",
            "difficulty": 1
        },
        {
            "question": "你在团队合作中通常扮演什么角色？",
            "reference_answer": "考察团队协作能力、角色定位、以及沟通能力。",
            "category": "团队合作",
            "difficulty": 2
        },
        {
            "question": "请描述一个你遇到的最大挑战，以及你是如何解决的？",
            "reference_answer": "考察问题解决能力、抗压能力、以及复盘总结能力。",
            "category": "问题解决",
            "difficulty": 2
        }
    ],
    "技术岗位": [
        {
            "question": "请介绍一个你做过的技术项目，你在其中负责什么？",
            "reference_answer": "考察技术深度、项目经验、以及角色定位。",
            "category": "项目经验",
            "difficulty": 2
        },
        {
            "question": "你平时是如何学习新技术的？",
            "reference_answer": "考察学习能力、技术热情、以及成长潜力。",
            "category": "学习能力",
            "difficulty": 1
        }
    ],
    "产品岗位": [
        {
            "question": "你如何理解产品经理这个岗位？",
            "reference_answer": "考察对产品岗位的认知深度。",
            "category": "岗位认知",
            "difficulty": 1
        },
        {
            "question": "如果开发说你的需求无法实现，你会怎么处理？",
            "reference_answer": "考察沟通协调能力、需求优先级判断能力。",
            "category": "沟通协调",
            "difficulty": 2
        }
    ],
    "结束语": [
        {
            "question": "你还有什么想问我的吗？",
            "reference_answer": "面试结束的标准问题，观察候选人的思考深度。",
            "category": "结束",
            "difficulty": 1
        }
    ]
}


class AIInterviewService:
    """AI面试服务类"""
    
    def __init__(self):
        # DeepSeek 客户端 (用于智能决策)
        self.deepseek_client = AsyncOpenAI(
            api_key=os.getenv("Deepseek_API_Key"),
            base_url=DEEPSEEK_BASE_URL
        )
        
        # 阿里云百炼客户端 (用于 TTS 和 ASR)
        self.dashscope_client = AsyncOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=DASHSCOPE_BASE_URL
        )
    
    def _add_wav_header(self, pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, bit_depth: int = 16) -> bytes:
        """
        为 PCM 数据添加 WAV 头
        """
        header = bytearray()
        # RIFF chunk
        header.extend(b'RIFF')
        header.extend(struct.pack('<I', 36 + len(pcm_data)))
        header.extend(b'WAVE')
        # fmt chunk
        header.extend(b'fmt ')
        header.extend(struct.pack('<I', 16))  # chunk size
        header.extend(struct.pack('<H', 1))   # format tag (1=PCM)
        header.extend(struct.pack('<H', channels))
        header.extend(struct.pack('<I', sample_rate))
        header.extend(struct.pack('<I', sample_rate * channels * bit_depth // 8)) # byte rate
        header.extend(struct.pack('<H', channels * bit_depth // 8)) # block align
        header.extend(struct.pack('<H', bit_depth))
        # data chunk
        header.extend(b'data')
        header.extend(struct.pack('<I', len(pcm_data)))
        
        return bytes(header) + pcm_data

    # ==================== TTS 语音合成 ====================
    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        流式文字转语音 (使用 qwen-tts 原生 SDK)
        
        Args:
            text: 要转换的文本
            
        Yields:
            音频数据块 (bytes)
        """
        try:
            # 依照官方示例使用 DashScope SDK
            response = dashscope.MultiModalConversation.call(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                model="qwen3-tts-flash",
                text=text,
                voice="Cherry",
                language_type="Chinese",
                stream=True
            )
            
            for chunk in response:
                if chunk.output is not None and chunk.output.audio is not None:
                    audio = chunk.output.audio
                    if audio.data is not None:
                        # 官方示例返回的是 base64 编码的 WAV/PCM 数据
                        wav_bytes = base64.b64decode(audio.data)
                        yield wav_bytes
                        
        except Exception as e:
            print(f"TTS Stream Error: {e}")
            yield b""
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        非流式文字转语音 (使用 qwen3-tts-flash 原生 SDK)
        
        Args:
            text: 要转换的文本
            
        Returns:
            完整的音频数据 (bytes)
        """
        print(f"\n[AI Service] 🎤 Calling TTS (Text-to-Speech)...")
        print(f"[AI Service] Model: qwen3-tts-flash (DashScope SDK)")
        print(f"[AI Service] Input Text: {text[:50]}... (Length: {len(text)})")

        try:
            # 封装一个同步调用函数
            def _sync_call():
                # 根据官方示例，必须启用 stream=True 才能获取音频流
                # 即使我们要非流式结果，也需要把流读完拼起来
                responses = dashscope.MultiModalConversation.call(
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                    model="qwen3-tts-flash",
                    text=text,
                    voice="Cherry",
                    language_type="Chinese",
                    stream=True
                )
                
                full_audio = bytearray()
                for chunk in responses:
                    if chunk.output is not None and chunk.output.audio is not None:
                        audio = chunk.output.audio
                        if audio.data is not None:
                            wav_bytes = base64.b64decode(audio.data)
                            full_audio.extend(wav_bytes)
                return bytes(full_audio)

            # 在线程池中执行
            loop = asyncio.get_running_loop()
            pcm_content = await loop.run_in_executor(None, _sync_call)
            
            # 添加 WAV 头
            wav_content = self._add_wav_header(pcm_content)
            
            print(f"[AI Service] ✅ TTS Success. Output Audio Size: {len(wav_content)} bytes")
            return wav_content
            
        except Exception as e:
            print(f"[AI Service] ❌ TTS Error: {e}")
            return b""
    
    # ==================== ASR 语音识别 ====================
    async def speech_to_text_stream(
        self, 
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> AsyncGenerator[str, None]:
        """
        流式语音转文字 (使用原生DashScope SDK)
        """
        print(f"\n[AI Service] 👂 Calling ASR Stream...")
        print(f"[AI Service] Input Audio Size: {len(audio_data)} bytes")

        try:
            # 使用原生 DashScope SDK 调用 ASR
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 构建消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": f"data:audio/wav;base64,{audio_base64}"
                        }
                    ]
                }
            ]
            
            # 封装一个同步调用函数
            def _sync_asr_call():
                response = dashscope.MultiModalConversation.call(
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                    model="qwen3-asr-flash",
                    messages=messages,
                    result_format="message",
                    asr_options={
                        "enable_itn": False  # 不启用逆文本规范化
                    }
                )
                return response
            
            # 在线程池中执行同步调用
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, _sync_asr_call)
            
            # 解析响应
            if response.status_code == 200:
                result_text = response.output.choices[0].message.content
                print(f"[AI Service] ✅ ASR Success. Result: {result_text}")
                yield result_text
            else:
                print(f"[AI Service] ❌ ASR Error: {response}")
                yield ""
                    
        except Exception as e:
            print(f"[AI Service] ❌ ASR Error: {e}")
            yield ""
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        非流式语音转文字 (使用原生DashScope SDK)
        """
        print(f"\n[AI Service] 👂 Calling ASR (Speech-to-Text)...")
        print(f"[AI Service] Input Audio Size: {len(audio_data)} bytes")
        
        try:
            # 使用原生 DashScope SDK 调用 ASR
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 构建消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "audio": f"data:audio/wav;base64,{audio_base64}"
                        }
                    ]
                }
            ]
            
            # 封装一个同步调用函数
            def _sync_asr_call():
                response = dashscope.MultiModalConversation.call(
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                    model="qwen3-asr-flash",
                    messages=messages,
                    result_format="message",
                    asr_options={
                        "enable_itn": False  # 不启用逆文本规范化
                    }
                )
                return response
            
            # 在线程池中执行同步调用
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, _sync_asr_call)
            
            # 解析响应
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 处理返回结果：可能是字符串、列表或字典
                if isinstance(content, str):
                    # 尝试解析JSON字符串
                    try:
                        import json
                        parsed = json.loads(content)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            # 提取列表中第一个元素的text字段
                            if isinstance(parsed[0], dict) and 'text' in parsed[0]:
                                final_text = parsed[0]['text']
                            else:
                                final_text = str(parsed[0])
                        else:
                            final_text = content
                    except (json.JSONDecodeError, ValueError):
                        # 如果不是JSON，直接使用原字符串
                        final_text = content
                elif isinstance(content, list) and len(content) > 0:
                    # 如果已经是列表，提取text字段
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        final_text = content[0]['text']
                    else:
                        final_text = str(content[0])
                elif isinstance(content, dict) and 'text' in content:
                    final_text = content['text']
                else:
                    final_text = str(content)
                
                print(f"[AI Service] ✅ ASR Final Result: '{final_text}'")
                return final_text.strip() if isinstance(final_text, str) else str(final_text)
            else:
                print(f"[AI Service] ❌ ASR Error: {response}")
                return ""
                
        except Exception as e:
            print(f"[AI Service] ❌ ASR Error: {e}")
            return ""
    
    # ==================== LLM 智能决策 ====================
    async def generate_interview_questions(
        self,
        resume_text: str,
        job_name: str,
        num_questions: int = 8
    ) -> List[Dict[str, Any]]:
        """
        根据简历和岗位生成面试问题
        
        Args:
            resume_text: 简历文本
            job_name: 目标岗位名称
            num_questions: 需要生成的问题数量
            
        Returns:
            问题列表，每个问题包含 question, reference_answer, category
        """
        print(f"\n[AI Service] 🧠 Calling LLM (Generate Questions)...")
        print(f"[AI Service] Model: deepseek-chat")
        print(f"[AI Service] Job: {job_name}, Generating {num_questions} questions")

        all_questions = []
        all_questions.extend(INTERVIEW_QUESTION_BANK["通用问题"])
        
        # 根据岗位类型添加专业问题
        if "技术" in job_name or "开发" in job_name or "工程师" in job_name:
            all_questions.extend(INTERVIEW_QUESTION_BANK["技术岗位"])
        elif "产品" in job_name:
            all_questions.extend(INTERVIEW_QUESTION_BANK["产品岗位"])
        
        prompt = f"""你是一位资深的面试官，请根据候选人的简历和目标岗位，从以下题库中选择最合适的{num_questions}个问题，并可以根据简历内容对问题进行个性化调整。

## 候选人简历：
{resume_text[:3000]}  # 限制长度防止token溢出

## 目标岗位：{job_name}

## 可选题库：
{json.dumps(all_questions, ensure_ascii=False, indent=2)}

## 要求：
1. 选择与候选人背景和目标岗位最匹配的问题
2. 可以根据简历中的具体内容调整问题，使其更有针对性
3. 问题难度应该循序渐进，从简单到复杂
4. 最后一个问题应该是结束语

请以JSON数组格式返回，每个问题包含：
- question: 问题内容
- reference_answer: 参考评判标准
- category: 问题类别
- is_from_resume: 是否基于简历内容定制 (true/false)

只返回JSON数组，不要其他内容。
"""
        
        try:
            response = await self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的AI面试官助手，擅长根据简历定制面试问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            # 解析JSON
            questions = json.loads(result)
            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            
            final_questions = questions[:num_questions]
            print(f"[AI Service] ✅ Questions Generated: {len(final_questions)}")
            return final_questions
            
        except Exception as e:
            print(f"[AI Service] ❌ Question generation error: {e}")
            print(f"Question generation error: {e}")
            # 返回默认问题
            return INTERVIEW_QUESTION_BANK["通用问题"][:num_questions]
    
    async def analyze_answer_and_decide(
        self,
        current_question: str,
        reference_answer: str,
        user_answer: str,
        resume_text: str,
        question_history: List[Dict],
        remaining_questions: int
    ) -> Dict[str, Any]:
        """
        分析用户回答并决定下一步行动
        
        Args:
            current_question: 当前问题
            reference_answer: 参考答案/评判标准
            user_answer: 用户的回答
            resume_text: 简历文本
            question_history: 已完成的问答历史
            remaining_questions: 剩余问题数量
            
        Returns:
            决策结果，包含：
            - action: "follow_up" | "next_question" | "end_interview"
            - follow_up_question: 追问问题（如果action是follow_up）
            - score: 本题评分 (1-10)
            - feedback: 简短评价
            - reason: 决策理由
        """
        history_text = "\n".join([
            f"Q: {h['question']}\nA: {h['answer']}\n评分: {h.get('score', 'N/A')}"
            for h in question_history[-3:]  # 只取最近3轮
        ])
        
        prompt = f"""你是一位资深面试官，请分析候选人的回答并决定下一步行动。

## 当前问题：
{current_question}

## 参考评判标准：
{reference_answer}

## 候选人回答：
{user_answer}

## 候选人简历摘要：
{resume_text[:1500]}

## 最近问答历史：
{history_text if history_text else "（这是第一个问题）"}

## 剩余问题数：{remaining_questions}

## 请分析并决策：

1. 评估回答质量（1-10分）：
   - 完整性：是否正面回答了问题
   - 深度：是否有具体案例和数据
   - 逻辑性：表达是否清晰连贯
   - 真实性：与简历描述是否一致

2. 决定下一步行动：
   - "follow_up": 需要追问（回答不完整、有疑点、发现亮点需要深挖）
   - "next_question": 进入下一题（回答充分或追问已达2次）
   - "end_interview": 结束面试（所有核心问题已问完或时间超过25分钟）

请以JSON格式返回：
{{
    "score": 评分数字,
    "feedback": "简短评价，不超过50字",
    "action": "follow_up/next_question/end_interview",
    "follow_up_question": "追问问题（仅当action为follow_up时需要）",
    "reason": "决策理由，不超过30字"
}}

只返回JSON，不要其他内容。
"""
        
        try:
            print(f"\n[AI Service] ⚖️ Calling LLM (Analyze Answer)...")
            print(f"[AI Service] Model: deepseek-chat")
            
            response = await self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的AI面试官，擅长评估候选人的回答并做出合理决策。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"[AI Service] ✅ Analysis Result: Action={result.get('action')}, Score={result.get('score')}")
            return result
            
        except Exception as e:
            print(f"[AI Service] ❌ Answer analysis error: {e}")
            # 默认进入下一题
            return {
                "score": 5,
                "feedback": "系统处理中",
                "action": "next_question",
                "reason": "系统默认"
            }
    
    async def generate_interview_opening(self, candidate_name: str = "同学") -> str:
        """生成面试开场白"""
        return f"你好{candidate_name}，我是今天的AI面试官。在开始正式面试之前，请确认你的摄像头和麦克风已经准备就绪。准备好了吗？准备好就可以开始了。"
    
    async def generate_interview_closing(
        self,
        question_history: List[Dict],
        overall_score: float
    ) -> str:
        """生成面试结束语"""
        prompt = f"""请根据面试情况生成一段专业、温和的结束语。

## 面试问答历史：
{json.dumps(question_history[-5:], ensure_ascii=False)}

## 整体评分：{overall_score:.1f}/10

要求：
1. 感谢候选人的参与
2. 简要肯定表现亮点（如果有）
3. 说明后续流程
4. 语气专业友善
5. 控制在100字以内

只输出结束语内容，不要其他格式。
"""
        
        try:
            response = await self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Closing generation error: {e}")
            return "好的，今天的面试就到这里。感谢你的参与，后续结果我们会通过邮件通知你。祝你一切顺利！"
    
    async def stream_text_response(
        self,
        prompt: str,
        system_prompt: str = "你是一位专业的AI面试官。"
    ) -> AsyncGenerator[str, None]:
        """
        流式生成文本响应
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Yields:
            文本片段
        """
        try:
            response = await self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"Stream text error: {e}")
            yield "抱歉，系统处理中，请稍候..."


# 单例实例
ai_interview_service = AIInterviewService()
