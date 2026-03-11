"""
权限中间件 - JWT 认证和权限验证
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

class PermissionDenied(Exception):
    """权限不足异常"""
    pass

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已过期或无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="账号未激活")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

def require_permission(permission: str):
    """权限装饰器"""
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # 管理员拥有所有权限
        if current_user.role == "admin":
            return current_user
        
        # TODO: 实现基于角色的权限检查
        # 目前简单实现：只有管理员有权限
        raise PermissionDenied(f"权限不足：需要 {permission}")
    
    return permission_checker

def check_data_ownership(db: Session, model, item_id: int, user: User) -> bool:
    """检查数据归属权"""
    # 管理员可以访问所有数据
    if user.role == "admin":
        return True
    
    # 普通用户只能访问自己的数据
    item = db.query(model).filter(model.id == item_id).first()
    if not item:
        return False
    
    # TODO: 添加 user_id 字段到模型，检查归属
    return True
