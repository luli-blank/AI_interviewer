"""
同步 ORM → MySQL 表结构（只增不删）
用法：
    python sync_db.py
"""

from sqlalchemy import create_engine, inspect, text
from app.core.config import settings
from app.db.session import Base


from app.models.Interviewer import Interviewer 
from app.models.user import User
from app.models.Interview_record import Interview_record
from app.models.Interview_position import Interview_position
from app.models.Jobs import Jobs

def get_sync_engine():
    db_url = settings.DATABASE_URL
    if "aiomysql" in db_url:
        db_url = db_url.replace("aiomysql", "pymysql")
    return create_engine(db_url, echo=True)


def sync_table(engine, table):
    inspector = inspect(engine)
    table_name = table.name

    print(f"\n🔍 同步表：{table_name}")

    # 数据库中已有字段
    db_columns = {
        col["name"]: col
        for col in inspector.get_columns(table_name)
    }

    with engine.begin() as conn:
        for column in table.columns:
            if column.name in db_columns:
                continue

            col_type = column.type.compile(engine.dialect)
            nullable = "NULL" if column.nullable else "NOT NULL"

            sql = f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column.name} {col_type} {nullable}
            """

            print(f"➕ 新增字段：{column.name}")
            print(sql.strip())
            conn.execute(text(sql))


def main():
    engine = get_sync_engine()
    inspector = inspect(engine)

    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            print(f"\n🆕 表不存在，直接创建：{table_name}")
            table.create(bind=engine)
        else:
            sync_table(engine, table)

    print("\n✅ 表结构同步完成")


if __name__ == "__main__":
    main()
