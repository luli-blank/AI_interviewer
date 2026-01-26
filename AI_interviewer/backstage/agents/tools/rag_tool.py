"""
RAG 检索工具

基于向量嵌入的题库检索工具，支持：
- 题库加载和嵌入
- 语义相似度检索
- 多分类题目召回
"""

import os
import json
import pickle
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# 嵌入文件存储目录
EMBEDDING_DIR = Path(__file__).parent.parent.parent / "data" / "embedding"

# 题库文件
QUESTION_BANK_FILE = EMBEDDING_DIR / "question_bank.json"
EMBEDDING_FILE = EMBEDDING_DIR / "question_embeddings.pkl"


class RAGTool:
    """
    RAG 检索工具
    
    使用向量嵌入进行语义检索，从题库中召回相关问题
    """
    
    def __init__(self):
        """初始化 RAG 工具"""
        self.question_bank: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embedding_model = None
        self._initialized = False
        self._ensure_directory()
    
    def _ensure_directory(self):
        """确保嵌入目录存在"""
        EMBEDDING_DIR.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """
        初始化 RAG 工具
        
        加载题库和嵌入，如果嵌入不存在则创建
        """
        if self._initialized:
            return
        
        # 加载题库
        await self._load_question_bank()
        
        # 加载或创建嵌入
        if EMBEDDING_FILE.exists():
            await self._load_embeddings()
        else:
            await self._create_embeddings()
        
        self._initialized = True
        print(f"[RAG Tool] ✅ Initialized with {len(self.question_bank)} questions")
    
    async def _load_question_bank(self):
        """加载题库"""
        if QUESTION_BANK_FILE.exists():
            loop = asyncio.get_running_loop()
            self.question_bank = await loop.run_in_executor(
                None, self._sync_load_json, QUESTION_BANK_FILE
            )
        else:
            # 创建默认题库
            await self._create_default_question_bank()
    
    def _sync_load_json(self, file_path: Path) -> List[Dict]:
        """同步加载 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _create_default_question_bank(self):
        """创建默认题库"""
        self.question_bank = self._get_default_questions()
        
        # 保存到文件
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self._sync_save_json, QUESTION_BANK_FILE, self.question_bank
        )
        print(f"[RAG Tool] 📝 Created default question bank with {len(self.question_bank)} questions")
    
    def _sync_save_json(self, file_path: Path, data: Any):
        """同步保存 JSON 文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def _load_embeddings(self):
        """加载嵌入向量"""
        loop = asyncio.get_running_loop()
        self.embeddings = await loop.run_in_executor(
            None, self._sync_load_pickle, EMBEDDING_FILE
        )
        print(f"[RAG Tool] 📥 Loaded embeddings: {self.embeddings.shape}")
    
    def _sync_load_pickle(self, file_path: Path) -> np.ndarray:
        """同步加载 Pickle 文件"""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    
    async def _create_embeddings(self):
        """
        创建题库嵌入
        
        使用 DashScope 的文本嵌入模型
        """
        import dashscope
        from dashscope import TextEmbedding
        
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        print(f"[RAG Tool] 🔄 Creating embeddings for {len(self.question_bank)} questions...")
        
        # 准备文本
        texts = [
            f"{q['category']}: {q['question']}"
            for q in self.question_bank
        ]
        
        # 批量获取嵌入
        embeddings_list = []
        batch_size = 25  # DashScope 每次最多 25 条
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: TextEmbedding.call(
                        model=TextEmbedding.Models.text_embedding_v3,
                        input=batch,
                        dimension=1024
                    )
                )
                
                if response.status_code == 200:
                    for embedding in response.output['embeddings']:
                        embeddings_list.append(embedding['embedding'])
                else:
                    print(f"[RAG Tool] ❌ Embedding error: {response}")
                    # 使用随机向量作为后备
                    for _ in batch:
                        embeddings_list.append(np.random.randn(1024).tolist())
                        
            except Exception as e:
                print(f"[RAG Tool] ❌ Embedding batch error: {e}")
                # 使用随机向量作为后备
                for _ in batch:
                    embeddings_list.append(np.random.randn(1024).tolist())
        
        self.embeddings = np.array(embeddings_list)
        
        # 保存嵌入
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, self._sync_save_pickle, EMBEDDING_FILE, self.embeddings
        )
        print(f"[RAG Tool] ✅ Created and saved embeddings: {self.embeddings.shape}")
    
    def _sync_save_pickle(self, file_path: Path, data: np.ndarray):
        """同步保存 Pickle 文件"""
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        difficulty_range: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        语义检索题目
        
        Args:
            query: 检索查询（关键词或问题描述）
            top_k: 返回结果数量
            category_filter: 分类过滤
            difficulty_range: 难度范围 (min, max)
            
        Returns:
            检索到的题目列表，包含相似度分数
        """
        if not self._initialized:
            await self.initialize()
        
        # 获取查询的嵌入
        query_embedding = await self._get_embedding(query)
        
        if query_embedding is None:
            print(f"[RAG Tool] ⚠️ Failed to get query embedding, using fallback")
            return self._fallback_search(query, top_k, category_filter)
        
        # 计算相似度
        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        
        # 获取排序后的索引
        sorted_indices = np.argsort(similarities)[::-1]
        
        # 过滤和收集结果
        results = []
        for idx in sorted_indices:
            if len(results) >= top_k:
                break
            
            question = self.question_bank[idx]
            
            # 分类过滤
            if category_filter and question.get('category') != category_filter:
                continue
            
            # 难度过滤
            if difficulty_range:
                difficulty = question.get('difficulty', 3)
                if not (difficulty_range[0] <= difficulty <= difficulty_range[1]):
                    continue
            
            results.append({
                "question": question['question'],
                "reference_answer": question.get('reference_answer', ''),
                "category": question.get('category', ''),
                "difficulty": question.get('difficulty', 3),
                "tags": question.get('tags', []),
                "score": float(similarities[idx])
            })
        
        print(f"[RAG Tool] 🔍 Search '{query[:30]}...' returned {len(results)} results")
        return results
    
    async def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """获取文本的嵌入向量"""
        import dashscope
        from dashscope import TextEmbedding
        
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: TextEmbedding.call(
                    model=TextEmbedding.Models.text_embedding_v3,
                    input=text,
                    dimension=1024
                )
            )
            
            if response.status_code == 200:
                return np.array(response.output['embeddings'][0]['embedding'])
            else:
                print(f"[RAG Tool] ❌ Embedding error: {response}")
                return None
                
        except Exception as e:
            print(f"[RAG Tool] ❌ Embedding error: {e}")
            return None
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """计算余弦相似度"""
        # 归一化
        a_norm = a / (np.linalg.norm(a) + 1e-8)
        b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
        
        # 点积
        return np.dot(b_norm, a_norm)
    
    def _fallback_search(
        self,
        query: str,
        top_k: int,
        category_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        后备的关键词搜索
        
        当嵌入服务不可用时使用
        """
        query_lower = query.lower()
        results = []
        
        for question in self.question_bank:
            if category_filter and question.get('category') != category_filter:
                continue
            
            # 简单的关键词匹配
            question_text = question['question'].lower()
            category = question.get('category', '').lower()
            tags = ' '.join(question.get('tags', [])).lower()
            
            combined = f"{question_text} {category} {tags}"
            
            # 计算匹配分数
            score = sum(1 for word in query_lower.split() if word in combined)
            
            if score > 0:
                results.append({
                    "question": question['question'],
                    "reference_answer": question.get('reference_answer', ''),
                    "category": question.get('category', ''),
                    "difficulty": question.get('difficulty', 3),
                    "tags": question.get('tags', []),
                    "score": score / len(query_lower.split())
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    async def search_by_keywords(
        self,
        keywords: List[str],
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        基于关键词列表检索
        
        Args:
            keywords: 关键词列表
            top_k: 返回结果数量
            category_filter: 分类过滤
            
        Returns:
            检索到的题目列表
        """
        # 将关键词组合成查询
        query = " ".join(keywords)
        return await self.search(query, top_k, category_filter)
    
    async def get_questions_by_stage(
        self,
        stage: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        根据面试阶段获取推荐题目
        
        Args:
            stage: 面试阶段
            top_k: 返回数量
            
        Returns:
            推荐的题目列表
        """
        stage_category_map = {
            "self_intro": "自我介绍",
            "project_deep_dive": "项目经验",
            "basic_knowledge": "基础知识",
            "scenario_algorithm": "场景算法",
            "reverse_interview": "反问环节"
        }
        
        category = stage_category_map.get(stage, "通用")
        
        # 直接按分类获取
        results = [
            {
                "question": q['question'],
                "reference_answer": q.get('reference_answer', ''),
                "category": q.get('category', ''),
                "difficulty": q.get('difficulty', 3),
                "tags": q.get('tags', []),
                "score": 1.0
            }
            for q in self.question_bank
            if q.get('category', '').startswith(category) or category in q.get('tags', [])
        ][:top_k]
        
        return results
    
    def _get_default_questions(self) -> List[Dict]:
        """获取默认题库"""
        return [
            # ===== 自我介绍 =====
            {
                "question": "请用1-2分钟简单介绍一下你自己。",
                "reference_answer": "考察表达能力、逻辑性、是否能突出亮点。好的回答应包含：教育背景、核心技能、相关经验、求职动机。",
                "category": "自我介绍",
                "difficulty": 1,
                "tags": ["开场", "表达能力"]
            },
            {
                "question": "你为什么对这个岗位感兴趣？",
                "reference_answer": "考察求职动机和岗位匹配度。期望听到对岗位的理解、与自身技能的匹配、职业规划。",
                "category": "自我介绍",
                "difficulty": 1,
                "tags": ["动机", "职业规划"]
            },
            
            # ===== 项目经验 =====
            {
                "question": "请介绍一个你最有成就感的项目，你在其中负责什么？",
                "reference_answer": "考察项目经验深度、角色定位。使用STAR法则评估：情境、任务、行动、结果。",
                "category": "项目经验",
                "difficulty": 2,
                "tags": ["项目", "成就"]
            },
            {
                "question": "在这个项目中，你遇到的最大挑战是什么？你是如何解决的？",
                "reference_answer": "考察问题解决能力、抗压能力。期望听到具体的挑战、思考过程、解决方案、结果。",
                "category": "项目经验",
                "difficulty": 3,
                "tags": ["挑战", "问题解决"]
            },
            {
                "question": "这个项目的技术选型是怎么考虑的？有没有更好的方案？",
                "reference_answer": "考察技术视野和决策能力。期望听到技术对比、权衡考虑、对替代方案的了解。",
                "category": "项目经验",
                "difficulty": 3,
                "tags": ["技术选型", "架构"]
            },
            {
                "question": "你在团队中是如何与其他成员协作的？",
                "reference_answer": "考察团队协作能力。期望听到沟通方式、冲突处理、协作工具使用。",
                "category": "项目经验",
                "difficulty": 2,
                "tags": ["团队", "协作"]
            },
            
            # ===== 基础知识 - 通用 =====
            {
                "question": "请解释一下什么是RESTful API？",
                "reference_answer": "REST是一种架构风格，核心概念：资源、URI、HTTP方法、无状态、统一接口。",
                "category": "基础知识-通用",
                "difficulty": 2,
                "tags": ["API", "REST", "后端"]
            },
            {
                "question": "HTTP和HTTPS有什么区别？HTTPS是如何保证安全的？",
                "reference_answer": "HTTPS = HTTP + TLS/SSL。安全保证：加密传输、身份验证、数据完整性。握手过程。",
                "category": "基础知识-通用",
                "difficulty": 2,
                "tags": ["网络", "安全", "HTTP"]
            },
            {
                "question": "数据库事务的ACID特性是什么？",
                "reference_answer": "原子性、一致性、隔离性、持久性。每个特性的含义和实现方式。",
                "category": "基础知识-通用",
                "difficulty": 3,
                "tags": ["数据库", "事务", "ACID"]
            },
            
            # ===== 基础知识 - Python =====
            {
                "question": "Python中的GIL是什么？它有什么影响？",
                "reference_answer": "全局解释器锁，确保同一时刻只有一个线程执行Python字节码。影响多线程性能，解决方案：多进程、异步IO。",
                "category": "基础知识-Python",
                "difficulty": 3,
                "tags": ["Python", "GIL", "多线程"]
            },
            {
                "question": "Python中的装饰器是什么？请举例说明。",
                "reference_answer": "装饰器是修改函数行为的语法糖，本质是高阶函数。常见应用：日志、权限、缓存。",
                "category": "基础知识-Python",
                "difficulty": 2,
                "tags": ["Python", "装饰器"]
            },
            {
                "question": "解释Python中的生成器和迭代器的区别。",
                "reference_answer": "迭代器是实现了__iter__和__next__的对象。生成器是特殊的迭代器，使用yield。优点：内存效率。",
                "category": "基础知识-Python",
                "difficulty": 2,
                "tags": ["Python", "生成器", "迭代器"]
            },
            
            # ===== 基础知识 - JavaScript =====
            {
                "question": "请解释JavaScript中的事件循环(Event Loop)机制。",
                "reference_answer": "单线程执行，异步通过事件循环实现。调用栈、任务队列、微任务队列。宏任务和微任务的执行顺序。",
                "category": "基础知识-JavaScript",
                "difficulty": 3,
                "tags": ["JavaScript", "事件循环", "异步"]
            },
            {
                "question": "var、let、const有什么区别？",
                "reference_answer": "作用域：var函数级，let/const块级。提升行为不同。const不可重新赋值。",
                "category": "基础知识-JavaScript",
                "difficulty": 1,
                "tags": ["JavaScript", "变量"]
            },
            {
                "question": "什么是闭包？请举例说明它的应用场景。",
                "reference_answer": "函数访问其词法作用域外的变量。应用：数据私有化、柯里化、模块模式。",
                "category": "基础知识-JavaScript",
                "difficulty": 2,
                "tags": ["JavaScript", "闭包"]
            },
            
            # ===== 基础知识 - Java =====
            {
                "question": "请解释Java中的垃圾回收机制。",
                "reference_answer": "自动内存管理。标记-清除、复制、标记-整理算法。分代收集：年轻代、老年代。常见GC：G1、ZGC。",
                "category": "基础知识-Java",
                "difficulty": 3,
                "tags": ["Java", "GC", "内存"]
            },
            {
                "question": "HashMap的实现原理是什么？",
                "reference_answer": "数组+链表+红黑树。哈希函数、扩容机制、线程安全问题。Java 8优化。",
                "category": "基础知识-Java",
                "difficulty": 3,
                "tags": ["Java", "HashMap", "数据结构"]
            },
            {
                "question": "什么是Spring的IoC和AOP？",
                "reference_answer": "IoC控制反转，DI依赖注入。AOP面向切面编程，横切关注点。应用：事务、日志、权限。",
                "category": "基础知识-Java",
                "difficulty": 2,
                "tags": ["Java", "Spring", "IoC", "AOP"]
            },
            
            # ===== 场景/算法 =====
            {
                "question": "如果让你设计一个短链接服务，你会怎么设计？",
                "reference_answer": "核心：URL映射、唯一ID生成、重定向。考虑：进制转换、分布式ID、缓存、过期策略。",
                "category": "场景算法",
                "difficulty": 4,
                "tags": ["系统设计", "短链接"]
            },
            {
                "question": "如何设计一个高并发的秒杀系统？",
                "reference_answer": "核心问题：超卖、性能、公平性。方案：限流、缓存、消息队列、乐观锁/分布式锁、预扣减。",
                "category": "场景算法",
                "difficulty": 5,
                "tags": ["系统设计", "高并发", "秒杀"]
            },
            {
                "question": "请描述一下你对微服务架构的理解。",
                "reference_answer": "服务拆分、独立部署、API网关、服务发现、配置中心、链路追踪。优缺点对比。",
                "category": "场景算法",
                "difficulty": 3,
                "tags": ["架构", "微服务"]
            },
            {
                "question": "给定一个整数数组，找出两数之和等于目标值的索引。",
                "reference_answer": "方法：暴力O(n²)、哈希表O(n)。代码实现、边界条件、复杂度分析。",
                "category": "场景算法",
                "difficulty": 2,
                "tags": ["算法", "数组", "哈希表"]
            },
            
            # ===== 反问环节 =====
            {
                "question": "你还有什么想问我的吗？",
                "reference_answer": "标准结束问题。好的问题：团队情况、技术栈、成长路径、项目规划。避免只问薪资福利。",
                "category": "反问环节",
                "difficulty": 1,
                "tags": ["结束", "反问"]
            }
        ]
    
    async def add_question(self, question: Dict) -> bool:
        """
        添加新题目到题库
        
        Args:
            question: 题目信息
            
        Returns:
            是否添加成功
        """
        try:
            # 验证必要字段
            if 'question' not in question:
                return False
            
            # 添加默认字段
            question.setdefault('reference_answer', '')
            question.setdefault('category', '通用')
            question.setdefault('difficulty', 3)
            question.setdefault('tags', [])
            
            self.question_bank.append(question)
            
            # 重新创建嵌入
            await self._create_embeddings()
            
            # 保存题库
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, self._sync_save_json, QUESTION_BANK_FILE, self.question_bank
            )
            
            return True
            
        except Exception as e:
            print(f"[RAG Tool] ❌ Add question error: {e}")
            return False


# 单例实例
rag_tool = RAGTool()
