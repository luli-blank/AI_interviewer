backstage/
├── .env                  # 环境变量（数据库密码、Redis地址、API Key等）
├── .gitignore            # Git忽略文件
├── requirements.txt      # 依赖包列表
├── alembic.ini           # Alembic 数据库迁移配置
├── alembic/              # 数据库迁移脚本目录 (由 alembic init 生成)
├── main.py               # 项目入口文件 (启动 FastAPI)
└── app/                  # 核心代码目录
    ├── __init__.py
    ├── api/              # 接口层 (Routers)
    │   ├── __init__.py
    │   └── v1/           # API 版本控制
    │       ├── __init__.py
    │       ├── api.py    # 汇总所有路由
    │       └── endpoints/
    │           ├── __init__.py
    │           ├── auth.py       # 登录注册接口
    │           ├── interviews.py # 面试相关接口
    │           └── users.py      # 用户管理接口
    ├── core/             # 核心配置 (Config, Security)
    │   ├── __init__.py
    │   ├── config.py     # 读取 .env 配置
    │   └── security.py   # JWT Token 生成与校验
    ├── db/               # 数据库连接
    │   ├── __init__.py
    │   ├── session.py    # MySQL 数据库 Session 会话
    │   ├── base.py       # 导入所有 Model 供 Alembic 识别
    │   └── redis.py      # Redis 连接池管理
    ├── models/           # 数据库模型 (MySQL Tables - ORM)
    │   ├── __init__.py
    │   ├── user.py       # 用户表定义
    │   └── interview.py  # 面试记录表定义
    ├── schemas/          # 数据验证模式 (Pydantic Models)
    │   ├── __init__.py
    │   ├── user.py       # 用户请求/响应结构
    │   └── interview.py  # 面试请求/响应结构
    ├── crud/             # 数据库增删改查逻辑 (CRUD)
    │   ├── __init__.py
    │   ├── crud_user.py
    │   └── crud_interview.py
    └── services/         # 复杂业务逻辑 (AI调用, Redis缓存)
        ├── __init__.py
        ├── ai_engine.py  # 调用 OpenAI/LLM 的逻辑
        └── cache_service.py # 封装 Redis 操作