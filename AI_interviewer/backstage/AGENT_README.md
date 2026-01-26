# Agent 系统使用指南

## 🔧 修复说明

已修复以下问题：
1. ✅ 创建了 `app/models/__init__.py` - Python 包初始化文件
2. ✅ 创建了 `app/models/Character_answer.py` - 性格测试答案模型
3. ✅ 创建了 `app/models/Interview_question.py` - 面试题目模型

## 📦 安装依赖

```bash
cd backstage
pip install -r requirements_agent.txt
```

## 🚀 启动服务

```bash
cd backstage
uvicorn app.api.main_api:app --reload --port 8001
```

## 🔗 API 端点

### 旧版面试 API
- WebSocket: `ws://localhost:8001/api/interview/ws/interview?token=YOUR_JWT_TOKEN`

### 新版 Agent 面试 API
- WebSocket: `ws://localhost:8001/api/interview/ws/interview/agent?token=YOUR_JWT_TOKEN`
- 阶段信息: `GET /api/interview/agent/stages`
- 会话状态: `GET /api/interview/agent/session/{session_id}`

## 📁 生成的文件位置

### 题库数据
- 题库文件: `backstage/data/embedding/question_bank.json`
- 向量文件: `backstage/data/embedding/question_embeddings.pkl`

### 面试记录
- 上下文文件: `backstage/data/interview_contexts/*.md`
- CSV 记录: `backstage/data/interview_records/*.csv`

## ⚙️ 环境变量（可选）

在 `.env` 文件中添加：

```env
# DeepSeek LLM (必需)
Deepseek_API_Key=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# DashScope (必需，用于 TTS/ASR/Embedding)
DASHSCOPE_API_KEY=your_dashscope_key

# Web 搜索 (可选，选一个即可)
TAVILY_API_KEY=your_tavily_key
SERPER_API_KEY=your_serper_key
# 如果都不配置，会自动使用免费的 DuckDuckGo
```

## 🔍 测试步骤

1. **启动服务**
   ```bash
   uvicorn app.api.main_api:app --reload --port 8001
   ```

2. **检查是否正常**
   - 访问 `http://localhost:8001` 应该看到 `{"message": "AI Interviewer Backend Running"}`
   - 访问 `http://localhost:8001/docs` 查看 API 文档

3. **测试新 Agent API**
   - 使用前端连接到 `/api/interview/ws/interview/agent`
   - 或使用 WebSocket 测试工具

## ⚠️ 首次运行注意事项

首次启动时，系统会自动：
1. 创建默认题库 (约 30 道题)
2. 计算向量嵌入 (可能需要 10-30 秒)

如果看到以下日志，说明正常：
```
[RAG Tool] 📝 Created default question bank with XX questions
[RAG Tool] 🔄 Creating embeddings for XX questions...
[RAG Tool] ✅ Created and saved embeddings: (XX, 1024)
```

## 🐛 常见问题

### 问题 1: ModuleNotFoundError
- **原因**: 缺少 `__init__.py` 或模型文件
- **解决**: 已通过本次修复解决

### 问题 2: 题库文件不存在
- **原因**: 首次运行自动创建
- **解决**: 等待自动创建完成，或手动创建 `data/embedding/` 目录

### 问题 3: Embedding 创建失败
- **原因**: DASHSCOPE_API_KEY 未配置或无效
- **解决**: 检查 `.env` 文件中的 API Key

## 📊 性能优化

- **异步预取**: 在用户回答时后台准备下一个问题
- **向量缓存**: 题库向量化后保存，避免重复计算
- **Filler Words**: 长时间处理时发送思考消息

## 🔄 从旧版迁移

前端只需修改 WebSocket URL：
```javascript
// 旧版
const ws = new WebSocket('ws://localhost:8001/api/interview/ws/interview?token=...')

// 新版 Agent
const ws = new WebSocket('ws://localhost:8001/api/interview/ws/interview/agent?token=...')
```

新版 Agent 消息格式完全兼容旧版，额外增加：
- `stage_change`: 阶段转换通知
- `thinking`: 思考占位符消息
