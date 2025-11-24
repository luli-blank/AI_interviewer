import asyncio
import redis.asyncio as redis

async def main():
    # 1. 连接配置 (localhost:6379)
    # 格式: redis://主机名:端口/数据库编号
    redis_url = "redis://localhost:6379/0"
    
    print(f"🔄 正在尝试连接 Redis: {redis_url} ...")
    
    try:
        # 2. 建立连接
        r = redis.from_url(redis_url)
        
        # 3. 写入测试数据
        await r.set("test_key", "Hello from AI Interviewer!")
        
        # 4. 读取测试数据
        value = await r.get("test_key")
        
        print("✅ Redis 连接成功！")
        print(f"📝 读取到的数据: {value.decode('utf-8')}")
        
        # 5. 关闭连接
        await r.close()
        
    except Exception as e:
        print("❌ Redis 连接失败！请检查 Docker 是否启动。")
        print(f"错误信息: {e}")

if __name__ == "__main__":
    asyncio.run(main())