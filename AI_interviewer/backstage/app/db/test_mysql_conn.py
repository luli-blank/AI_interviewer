import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    # 1. 数据库配置
    # 对应 docker-compose 里的配置: user:password@localhost:3306/ai_interviewer
    # 驱动使用 mysql+aiomysql
    DATABASE_URL = "mysql+aiomysql://user:password@localhost:3306/ai_interviewer"
    
    print(f"🔄 正在尝试连接 MySQL ...")

    try:
        # 2. 创建引擎
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        # 3. 尝试连接并执行简单查询
        async with engine.connect() as conn:
            # 执行 SELECT 1，这是数据库界的 "Ping" 命令
            result = await conn.execute(text("SELECT 'MySQL Connection Success!'"))
            message = result.scalar()
            
            print("✅ MySQL 连接成功！")
            print(f"📝 数据库回应: {message}")
            
        # 4. 销毁引擎
        await engine.dispose()
        
    except Exception as e:
        print("❌ MySQL 连接失败！")
        print(f"错误信息: {e}")
        print("提示：请检查 docker-compose.yml 里的密码是否为 'password'")

if __name__ == "__main__":
    asyncio.run(main())