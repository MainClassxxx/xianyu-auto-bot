"""
账号管理 API - 真实实现
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Account
from app.services.xianyu_api import xianyu_manager, XianyuClient
from loguru import logger

router = APIRouter(prefix="/api/accounts", tags=["账号管理"])

class AccountCreate(BaseModel):
    name: str
    cookie: str
    device_id: Optional[str] = None

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    cookie: Optional[str] = None
    status: Optional[str] = None

class AccountResponse(BaseModel):
    id: int
    name: str
    device_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[AccountResponse])
async def get_accounts(status: Optional[str] = None, db: Session = Depends(get_db)):
    """获取账号列表"""
    query = db.query(Account)
    if status:
        query = query.filter(Account.status == status)
    return query.all()

@router.post("", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """添加账号"""
    # 1. 创建账号记录
    db_account = Account(
        name=account.name,
        cookie=account.cookie,
        device_id=account.device_id or f"device_{datetime.now().timestamp()}",
        status="active"  # 默认设为 active，让用户自己测试
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # 2. 尝试测试连接（但不阻止添加）
    try:
        client = XianyuClient(account.cookie, db_account.device_id)
        is_valid = await client.test_connection()
        
        if not is_valid:
            # 标记为 inactive 但不阻止添加
            db_account.status = "inactive"
            db.commit()
            logger.warning(f"⚠️ 账号 {account.name} Cookie 可能无效，已标记为 inactive")
        else:
            # 添加到管理器
            xianyu_manager.add_client(str(db_account.id), account.cookie, db_account.device_id)
            logger.info(f"✅ 添加账号：{account.name}")
    except Exception as e:
        logger.warning(f"⚠️ 测试连接失败：{e}，账号已保存但状态为 inactive")
        db_account.status = "inactive"
        db.commit()
    
    return db_account

@router.get("/{account_id}")
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """获取账号详情"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    return account

@router.put("/{account_id}")
async def update_account(account_id: int, account_update: AccountUpdate, db: Session = Depends(get_db)):
    """更新账号"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    if account_update.name:
        account.name = account_update.name
    if account_update.cookie:
        account.cookie = account_update.cookie
    if account_update.status:
        account.status = account_update.status
    
    db.commit()
    db.refresh(account)
    
    # 如果更新了 cookie，重新创建客户端
    if account_update.cookie:
        client = XianyuClient(account_update.cookie, account.device_id)
        is_valid = await client.test_connection()
        if is_valid:
            xianyu_manager.add_client(str(account.id), account_update.cookie, account.device_id)
    
    return account

@router.delete("/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """删除账号"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    db.delete(account)
    db.commit()
    
    # 从管理器移除
    xianyu_manager.remove_client(str(account_id))
    
    return {"success": True}

@router.post("/{account_id}/refresh")
async def refresh_account(account_id: int, db: Session = Depends(get_db)):
    """刷新账号状态"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    # 测试连接
    client = XianyuClient(account.cookie, account.device_id)
    is_valid = await client.test_connection()
    
    account.status = "active" if is_valid else "inactive"
    db.commit()
    
    if is_valid:
        xianyu_manager.add_client(str(account.id), account.cookie, account.device_id)
    
    return {
        "success": True,
        "status": account.status,
        "account_info": client.account_info
    }

@router.post("/{account_id}/restart")
async def restart_account(account_id: int, db: Session = Depends(get_db)):
    """重启账号连接"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    # 移除旧客户端
    xianyu_manager.remove_client(str(account_id))
    
    # 创建新客户端
    client = xianyu_manager.XianyuClient(account.cookie, account.device_id)
    is_valid = await client.test_connection()
    
    if is_valid:
        xianyu_manager.add_client(str(account.id), account.cookie, account.device_id)
    
    return {"success": is_valid}
