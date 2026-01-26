# 🤖 切换到 Agent 面试系统指南

## ✅ 已完成的配置

1. **Agent 模块已创建**：`backstage/agents/` 
   - LangGraph 工作流
   - RAG 题库检索  
   - Web 搜索增强
   - 多阶段面试管理

2. **后端 API 已集成**：`backstage/app/api/interviewee_api/Interview_session_agent_api.py`
   - WebSocket 端点：`/api/interview/ws/interview/agent`
   - 自动加载检测（如果依赖未安装会回退到旧版）

3. **前端已切换**：`client/src/views/Interview.vue`
   - 现在连接到新的 Agent 端点

---

## 🚀 启动步骤

### 1️⃣ 确保已安装 Agent 依赖

```powershell
cd D:\Github\AI_interviewer\AI_interviewer\backstage
pip install -r requirements_agent.txt
```

> **requirements_agent.txt** 包含：
> - langgraph
> - langchain-openai
> - numpy
> - duckduckgo-search
> - aiohttp

### 2️⃣ 验证 Agent 模块可用

```powershell
python test_agent_import.py
```

应该看到：
```
✅ 所有测试通过！Agent 模块可以正常使用
```

### 3️⃣ 启动后端

```powershell
cd D:\Github\AI_interviewer\AI_interviewer\backstage
uvicorn app.api.main_api:app --reload --port 8001
```

检查启动日志，应该包含：
```
[Main API] ✅ Agent API loaded successfully
[Main API] ✅ Agent routes registered at /api/interview/ws/interview/agent
```

### 4️⃣ 启动前端

```powershell
cd D:\Github\AI_interviewer\AI_interviewer\client
npm run dev
```

---

## 🔍 验证 Agent 是否生效

### 方法1：查看后端日志

启动后端时，如果看到：
```
[Main API] ✅ Agent API loaded successfully
```
说明 Agent 模块已加载

如果看到：
```
[Main API] ⚠️ Agent API not available: No module named 'langgraph'
```
说明缺少依赖，需要执行步骤 1

### 方法2：测试 WebSocket 连接

打开浏览器控制台，在面试页面查看网络请求：

- **旧版**：`ws://localhost:8001/api/interview/ws/interview`
- **新版**：`ws://localhost:8001/api/interview/ws/interview/agent` ✅

### 方法3：观察面试行为

**旧版特征**（硬编码）：
- 固定的 8 个问题
- 问题顺序不变
- 不会根据简历和回答调整

**新版特征**（Agent）：
- 动态生成问题（基于简历和回答）
- 有 7 个面试阶段（开场→自我介绍→项目深挖→基础知识→场景算法→反问→结束）
- 每个阶段有最少和最多问题限制
- 会根据回答质量动态调整问题数量

---

## 🔄 如果需要切换回旧版

修改 `client/src/views/Interview.vue` 第 205 行：

```typescript
// 切换回旧版
const wsUrl = `${urlObj.origin}${basePath}/api/interview/ws/interview?token=${token}`;

// 使用新版 Agent
// const wsUrl = `${urlObj.origin}${basePath}/api/interview/ws/interview/agent?token=${token}`;
```

---

## 📊 Agent 系统架构

```
面试流程：
┌─────────────────────────────────────────────────────────┐
│ 1. 开场寒暄 (OPENING) - 1-2题                           │
│    - "请简单介绍一下自己"                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 自我介绍深挖 (SELF_INTRO) - 1-3题                    │
│    - 基于简历内容提问                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 项目经验深挖 (PROJECT_DEEP_DIVE) - 2-5题             │
│    - RAG 检索相关技术问题                               │
│    - Web 搜索最新技术动态                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 基础知识考察 (BASIC_KNOWLEDGE) - 2-4题               │
│    - 编程语言、框架、数据库等                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 场景与算法 (SCENARIO_ALGORITHM) - 1-3题              │
│    - 场景设计题                                          │
│    - 算法思维题                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 反问环节 (REVERSE_INTERVIEW) - 1-2题                 │
│    - "你有什么想问我的吗？"                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 7. 结束语 (CLOSING) - 1题                               │
│    - 感谢并告知后续流程                                  │
└─────────────────────────────────────────────────────────┘
```

### Agent 核心功能

- **RAG 检索**：从 30+ 题库中搜索相关问题（使用 text-embedding-v3）
- **Web 搜索**：实时搜索技术动态（DuckDuckGo/Tavily/Serper）
- **上下文管理**：将面试记录保存为 Markdown（`data/interview_contexts/`）
- **异步预取**：提前生成下一个问题，减少等待时间
- **思考占位**：生成 "让我想想..." 等自然的停顿语句

---

## 🛠️ 故障排查

### 问题：启动时看到 "Agent API not available"

**原因**：缺少依赖包

**解决**：
```powershell
cd backstage
pip install -r requirements_agent.txt
```

### 问题：面试时还是旧的固定问题

**原因**：前端可能没有重启，或者浏览器缓存

**解决**：
1. 确保前端已重启（`npm run dev`）
2. 清除浏览器缓存（Ctrl+Shift+R 强制刷新）
3. 检查浏览器控制台的 WebSocket URL

### 问题：Agent 生成问题很慢

**原因**：
- 首次调用 DeepSeek API 需要初始化
- 网络搜索需要时间

**优化**：
- Agent 已实现异步预取，第二个问题开始会很快
- 可以在 `agents/prompts.py` 中调整 prompt 长度

---

## 📝 配置文件说明

### `.env` 必需的环境变量

```bash
# DeepSeek API（用于 LLM 生成）
Deepseek_API_Key=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# DashScope API（用于文本嵌入和 TTS/ASR）
DASHSCOPE_API_KEY=sk-xxxxx

# Web 搜索（可选，至少需要一个）
TAVILY_API_KEY=tvly-xxxxx        # Tavily（推荐）
SERPER_API_KEY=xxxxx             # Serper
# DuckDuckGo 不需要 API Key
```

---

## 📚 相关文档

- **Agent 模块说明**：`AGENT_README.md`
- **测试脚本**：`test_agent_import.py`
- **依赖清单**：`requirements_agent.txt`

---

## ✨ 新旧版本对比

| 功能 | 旧版（硬编码） | 新版（Agent） |
|------|---------------|--------------|
| 题库来源 | 固定 8 个问题 | RAG 检索 + Web 搜索 |
| 问题适应性 | 所有人一样 | 根据简历和回答动态调整 |
| 面试阶段 | 无分阶段 | 7 个明确阶段 |
| 技术深度 | 固定深度 | 根据回答质量调整 |
| 上下文记忆 | 无持久化 | Markdown 文件保存 |
| 响应速度 | 快 | 有预取优化 |
| 可扩展性 | 难扩展 | 易添加新工具和阶段 |

---

## 🎯 下一步优化建议

1. **添加评分机制**：在每个阶段结束时生成评分
2. **多轮追问**：对不清楚的回答自动追问
3. **多模态分析**：结合视频表情和语气分析
4. **个性化题库**：根据岗位类型加载不同题库
5. **实时反馈**：面试过程中给出即时提示

---

有任何问题可以查看日志：
- 后端日志：终端输出
- 前端日志：浏览器控制台（F12）
- Agent 日志：`backstage/` 目录下的 uvicorn 输出
