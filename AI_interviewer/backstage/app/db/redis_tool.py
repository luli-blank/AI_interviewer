import redis.asyncio as redis
from app.core.config import settings

# 1. 创建全局连接池 (Connection Pool)
# 这一步非常重要！我们不能每次请求都创建一个新的连接池，
# 而是要在程序启动时创建一个全局的池子，所有请求共用。
pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,  # 🔥 关键配置！下面会详细解释
    max_connections=10      # 最大连接数，防止 Redis 被撑爆
)

# 2. 获取 Redis 客户端的依赖函数
async def get_redis():
    # 从连接池里拿一个连接创建一个客户端对象
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        # 请求结束，关闭客户端（实际上是把连接归还给连接池）
        await client.close()