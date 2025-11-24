from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. 创建异步引擎 (Engine)
#这是连接数据库的入口。echo=True 会在控制台打印 SQL 语句，开发时非常有用，上线后建议改为 False
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, 
    pool_pre_ping=True,  # 每次从连接池拿连接前都会 ping 一下，防止连接断开报错
    pool_size=10,        # 连接池大小
    max_overflow=20      # 超过连接池大小时，允许额外创建的连接数
)

# 2. 创建会话工厂 (Session Factory)
# 只要调用它，就会产生一个新的数据库会话
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False  # 关键配置！防止异步操作提交后属性失效
)

# 3. 创建 ORM 基类 (Base)
# 所有的模型（如 User）都要继承它
Base = declarative_base()

# 4. 获取数据库会话的依赖函数 (Dependency)
# 这是一个生成器，FastAPI 会用它来注入 db 参数
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 请求结束，FastAPI 会自动执行这里的代码（如果有的话）
        except Exception as e:
            # 如果发生异常，回滚事务
            await session.rollback()
            raise e
        finally:
            # 关闭会话，归还连接给连接池
            await session.close()