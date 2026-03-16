"""
管理员 API - 用户管理和权限控制
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, MembershipLevel
from app.services.membership_service import AdminService, MembershipService
from app.api.auth import get_current_user, oauth2_scheme

router = APIRouter(prefix="/api/admin", tags=["管理员"])

class UserUpgradeRequest(BaseModel):
    """升级用户会员请求"""
    user_id: int
    level: str  # normal, vip, svip
    days: int

class UserBanRequest(BaseModel):
    """封禁用户请求"""
    user_id: int
    reason: str

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    role: str
    membership_level: str
    membership_expire_at: Optional[datetime]
    status: str
    created_at: datetime
    last_login_at: Optional[datetime]
    total_api_calls: int
    today_api_calls: int

class AdminUserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    users: List[UserResponse]

@router.get("/users", response_model=AdminUserListResponse)
async def get_all_users(
    page: int = 1,
    page_size: int = 20,
    role: Optional[str] = None,
    membership_level: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有用户列表（仅管理员）"""
    admin_service = AdminService(db)
    
    # 检查管理员权限
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 构建查询
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if membership_level:
        query = query.filter(User.membership_level == membership_level)
    if status:
        query = query.filter(User.status == status)
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    # 分页
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "users": users
    }

@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户详情（仅管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    membership_service = MembershipService(db)
    user_features = membership_service.get_user_features(user)
    
    return {
        "user": user,
        "features": user_features
    }

@router.post("/users/upgrade")
async def upgrade_user_membership(
    request: UserUpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """升级用户会员等级（仅管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取目标用户
    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证等级
    if request.level not in [MembershipLevel.NORMAL.value, MembershipLevel.VIP.value, MembershipLevel.SVIP.value]:
        raise HTTPException(status_code=400, detail="无效的会员等级")
    
    # 升级会员
    admin_service.upgrade_user(current_user, target_user, request.level, request.days)
    
    return {
        "success": True,
        "message": f"已将用户 {target_user.username} 升级为 {request.level}，有效期 {request.days} 天"
    }

@router.post("/users/ban")
async def ban_user(
    request: UserBanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """封禁用户（仅管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if target_user.role in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="不能封禁管理员")
    
    admin_service.ban_user(current_user, target_user, request.reason)
    
    return {
        "success": True,
        "message": f"已封禁用户 {target_user.username}"
    }

@router.post("/users/unban/{user_id}")
async def unban_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解封用户（仅管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    admin_service.unban_user(current_user, target_user)
    
    return {
        "success": True,
        "message": f"已解封用户 {target_user.username}"
    }

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统统计信息（仅管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_admin(current_user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 统计用户数量
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == "active").count()
    vip_users = db.query(User).filter(User.membership_level == MembershipLevel.VIP.value).count()
    svip_users = db.query(User).filter(User.membership_level == MembershipLevel.SVIP.value).count()
    
    # 统计今日 API 调用
    from sqlalchemy import func
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_api_calls = db.query(func.sum(User.today_api_calls)).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "banned": total_users - active_users,
            "vip": vip_users,
            "svip": svip_users,
            "normal": total_users - vip_users - svip_users
        },
        "api_calls": {
            "today": today_api_calls
        }
    }

@router.get("/logs")
async def get_admin_logs(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取管理员操作日志（仅超级管理员）"""
    admin_service = AdminService(db)
    
    if not admin_service.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    
    from app.models.user import AdminOperationLog
    
    query = db.query(AdminOperationLog).order_by(AdminOperationLog.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "logs": logs
    }
