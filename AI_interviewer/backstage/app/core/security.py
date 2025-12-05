# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
# 1. 配置参数 (生产环境建议放在 .env 文件中)
# 这是一个随机生成的密钥，用于给 Token 签名，绝对不能泄露
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token 有效期 30 分钟

# 2. 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 功能A: 密码处理 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码和数据库里的哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """将明文密码转换为哈希值"""
    return pwd_context.hash(password)

# --- 功能B: Token 生成 ---

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """生成 JWT Token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 默认过期时间
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 将过期时间加入 payload
    to_encode.update({"exp": expire})
    
    # 生成加密的 Token 字符串
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt