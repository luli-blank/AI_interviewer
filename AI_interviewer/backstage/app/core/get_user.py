from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

# 引入你的配置，获取 SECRET_KEY 和 ALGORITHM
from app.core.config import settings 
# 如果你还没有 settings，暂时可以用硬编码 (不推荐)：
# settings = type('Settings', (), {'SECRET_KEY': 'YOUR_SECRET_KEY', 'ALGORITHM': 'HS256'})

# 1. 定义 OAuth2 模式
# tokenUrl 指向你的登录接口路由，这样 Swagger UI (http://localhost:8000/docs) 里的 "Authorize" 按钮才能工作
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/login" 
)

# 2. 核心函数：解析 Token 获取 User ID
def get_current_user_id(
    token: str = Depends(reusable_oauth2)
) -> str:
    """
    依赖项：
    1. 自动从 Header 提取 Authorization: Bearer <token>
    2. 验证 Token 签名和有效期
    3. 返回 Token 中包含的 User ID (sub)
    """
    # 定义验证失败时的 401 错误
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # --- 解密核心逻辑 ---
        # 使用配置中的密钥解密
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 获取 Token 中的 'sub' 字段 (通常存放 User ID)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        return user_id

    except (JWTError, ValidationError):
        # 如果 Token 过期、伪造或格式错误，抛出 401
        raise credentials_exception

def get_current_user_int_id(
    token: str = Depends(reusable_oauth2)
) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("id")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except (JWTError, ValidationError, ValueError):
        raise credentials_exception