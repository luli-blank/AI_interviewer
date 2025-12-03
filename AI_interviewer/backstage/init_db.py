import sys
import os
import asyncio

# 1. 路径设置
sys.path.append(os.getcwd())

# 2. 引入基础组件
from app.db.session import engine, Base

# ==========================================
# 关键步骤：必须在这里导入模型
# ==========================================
try:
    from app.models.Character_question import Character_question
    print(f"✅ 成功导入模型类: {Character_question}")
except ImportError as e:
    print(f"❌ 导入失败，请检查路径或文件名: {e}")
    exit(1)

async def init_db():
    print("正在连接数据库 (Async模式)...")
    
    # --- 调试代码：打印当前 Base 知道的所有表名 ---
    print(f"当前注册的表: {list(Base.metadata.tables.keys())}")
    
    if "character_questions" not in Base.metadata.tables:
        print("❌ 错误: 'character_questions' 未在 metadata 中找到！")
        print("   原因可能是：模型类定义中缺少 __tablename__ 或者没有继承 Base")
        return

    async with engine.begin() as conn:
        # 执行建表
        print("正在执行 create_all...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 脚本执行完毕！请检查数据库是否出现新表。")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())