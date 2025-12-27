from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- 1. 定义你需要哪些配置 ---
    # 变量名必须和 .env 文件里的一模一样（不区分大小写）
    
    # 数据库连接串
    DATABASE_URL: str
    
    # Redis 连接串
    REDIS_URL: str
    
    # 项目名称 (可选，方便以后扩展)
    PROJECT_NAME: str = "AI Interviewer"

    SECRET_KEY: str 
    ALGORITHM: str

    Silicon_OCR_API_Key: str
    # --- 2. 告诉 Pydantic 去哪里找配置 ---
    class Config:
        # 指定读取根目录下的 .env 文件
        env_file = ".env"
        # 如果 .env 文件没有编码，默认使用 utf-8
        env_file_encoding = "utf-8"
        # 如果 .env 里有多余的变量，忽略它，不要报错
        extra = "ignore"

# --- 3. 实例化 ---
# 这一步执行时，Pydantic 会自动去读取 .env，并校验数据
settings = Settings()