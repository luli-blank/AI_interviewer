# 放在 backstage 根目录下运行： python init_db.py
from sqlalchemy import create_engine
from app.db.session import Base
# 确保所有需要创建表的模型都在这里被导入
from app.models.Character_answer import Character_answer 
from app.core.config import settings

def init_db():
    print("正在准备创建数据表...")
    
    # 1. 获取配置中的 URL
    db_url = settings.DATABASE_URL
    
    # 2. 强制转换为同步驱动 (如果你原配置是 aiomysql)
    if "aiomysql" in db_url:
        print("检测到异步驱动 aiomysql，正在临时切换为 pymysql 以执行同步建表...")
        db_url = db_url.replace("aiomysql", "pymysql")
        
    # 3. 创建引擎
    engine = create_engine(db_url, echo=True)
    
    # 4. 建表
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表 Character_answer (及其他已导入模型) 创建成功！")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        print("提示：请检查 MySQL 是否启动，以及数据库名称是否存在。")

if __name__ == "__main__":
    init_db()