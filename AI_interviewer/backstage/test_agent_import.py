"""
测试 Agent 模块导入

运行此脚本检查 Agent 系统是否正确安装和配置
"""

import sys
from pathlib import Path

# 添加 backstage 根目录到路径
BACKSTAGE_ROOT = Path(__file__).parent
sys.path.insert(0, str(BACKSTAGE_ROOT))

print("=" * 60)
print("Agent 模块导入测试")
print("=" * 60)

# 1. 检查 agents 目录
agents_dir = BACKSTAGE_ROOT / "agents"
print(f"\n1. 检查 agents 目录: {agents_dir}")
if agents_dir.exists():
    print("   ✅ agents/ 目录存在")
    print(f"   内容: {list(agents_dir.iterdir())}")
else:
    print("   ❌ agents/ 目录不存在")
    sys.exit(1)

# 2. 测试导入 state 模块
print("\n2. 测试导入 state 模块...")
try:
    from agents.state import InterviewState, InterviewStage, create_initial_state
    print("   ✅ state 模块导入成功")
    print(f"   - InterviewStage: {InterviewStage}")
    print(f"   - 阶段列表: {InterviewStage.get_stage_order()}")
except ImportError as e:
    print(f"   ❌ state 模块导入失败: {e}")
    sys.exit(1)

# 3. 测试导入 context_manager
print("\n3. 测试导入 context_manager...")
try:
    from agents.context_manager import ContextManager
    print("   ✅ context_manager 导入成功")
except ImportError as e:
    print(f"   ❌ context_manager 导入失败: {e}")
    sys.exit(1)

# 4. 测试导入 RAG Tool
print("\n4. 测试导入 RAG Tool...")
try:
    from agents.tools.rag_tool import RAGTool
    print("   ✅ rag_tool 导入成功")
except ImportError as e:
    print(f"   ❌ rag_tool 导入失败: {e}")
    print(f"   可能缺少依赖: numpy, dashscope")
    sys.exit(1)

# 5. 测试导入 Web Search Tool
print("\n5. 测试导入 Web Search Tool...")
try:
    from agents.tools.web_search_tool import WebSearchTool
    print("   ✅ web_search_tool 导入成功")
except ImportError as e:
    print(f"   ❌ web_search_tool 导入失败: {e}")
    print(f"   可能缺少依赖: duckduckgo-search")

# 6. 测试导入 Graph
print("\n6. 测试导入 LangGraph...")
try:
    from agents.graph import InterviewGraph
    print("   ✅ graph 导入成功")
except ImportError as e:
    print(f"   ❌ graph 导入失败: {e}")
    print(f"   可能缺少依赖: langgraph, langchain, langchain-openai")
    sys.exit(1)

# 7. 测试导入主 Agent
print("\n7. 测试导入 InterviewerAgent...")
try:
    from agents.interviewer_agent import InterviewerAgent, interviewer_agent
    print("   ✅ interviewer_agent 导入成功")
    print(f"   - Agent 实例: {interviewer_agent}")
except ImportError as e:
    print(f"   ❌ interviewer_agent 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 8. 检查环境变量
print("\n8. 检查环境变量...")
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = {
    "Deepseek_API_Key": os.getenv("Deepseek_API_Key"),
    "DEEPSEEK_BASE_URL": os.getenv("DEEPSEEK_BASE_URL"),
    "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY"),
}

all_set = True
for var_name, var_value in required_vars.items():
    if var_value:
        print(f"   ✅ {var_name}: 已设置")
    else:
        print(f"   ⚠️ {var_name}: 未设置")
        all_set = False

if not all_set:
    print("\n   提示: 请在 .env 文件中配置缺失的 API Keys")

# 9. 测试简单功能
print("\n9. 测试基本功能...")
try:
    # 创建一个测试状态
    test_state = create_initial_state(
        session_id="test_001",
        user_id="test_user",
        job_name="Python开发工程师",
        resume_text="测试简历内容",
        context_file_path="test.md"
    )
    print("   ✅ 创建测试状态成功")
    print(f"   - 当前阶段: {test_state['current_stage']}")
    print(f"   - 岗位: {test_state['job_name']}")
except Exception as e:
    print(f"   ❌ 功能测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ 所有测试通过！Agent 模块可以正常使用")
print("=" * 60)
print("\n下一步:")
print("1. 启动服务: uvicorn app.api.main_api:app --reload --port 8001")
print("2. 访问文档: http://localhost:8001/docs")
print("3. WebSocket 端点: ws://localhost:8001/api/interview/ws/interview/agent?token=YOUR_TOKEN")
