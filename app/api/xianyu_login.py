"""
闲鱼账号登录 API
提供扫码登录、Cookie 管理等功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models import Account
from app.api.auth import get_current_user
from app.services.xianyu_login_service import xianyu_login_service
from app.services.xianyu_client_enhanced import xianyu_manager
import uuid

router = APIRouter(prefix="/api/auth", tags=["账号登录"])


class CreateLoginSessionRequest(BaseModel):
    """创建登录会话请求"""
    headless: bool = False


class LoginSessionResponse(BaseModel):
    """登录会话响应"""
    session_id: str
    login_url: str
    status: str
    message: str


class CheckLoginStatusResponse(BaseModel):
    """检查登录状态响应"""
    status: str
    message: str
    cookie: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


@router.post("/login/create", response_model=LoginSessionResponse)
async def create_login_session(
    request: CreateLoginSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """创建扫码登录会话"""
    session_id = str(uuid.uuid4())
    
    result = await xianyu_login_service.create_login_session(
        session_id=session_id,
        headless=request.headless
    )
    
    return LoginSessionResponse(**result)


@router.get("/login/check/{session_id}", response_model=CheckLoginStatusResponse)
async def check_login_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """检查登录状态"""
    result = await xianyu_login_service.check_login_status(session_id)
    
    return CheckLoginStatusResponse(**result)


@router.post("/login/save")
async def save_login_session(
    session_id: str,
    account_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存登录会话到数据库"""
    # 从会话中获取 Cookie
    if session_id not in xianyu_login_service.login_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = xianyu_login_service.login_sessions[session_id]
    
    if session["status"] != "logged_in":
        raise HTTPException(status_code=400, detail="尚未登录")
    
    cookie = session["cookie"]
    user_info = session["user_info"]
    device_id = xianyu_login_service._generate_device_id() if hasattr(xianyu_login_service, '_generate_device_id') else f"device_{uuid.uuid4().hex[:16]}"
    
    # 创建账号记录
    account = Account(
        name=account_name,
        cookie=cookie,
        device_id=device_id,
        status="active"
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # 关闭会话
    await xianyu_login_service.close_session(session_id)
    
    return {
        "success": True,
        "account_id": account.id,
        "account_name": account.name,
        "user_info": user_info
    }


@router.get("/cookies")
async def list_cookies(
    current_user: User = Depends(get_current_user)
):
    """列出所有保存的 Cookie"""
    from pathlib import Path
    import json
    
    cookie_dir = Path(".cookies")
    cookies = []
    
    if cookie_dir.exists():
        for cookie_file in cookie_dir.glob("*.json"):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                cookies.append({
                    "account_id": cookie_data.get("account_id"),
                    "saved_at": cookie_data.get("saved_at"),
                    "expires_at": cookie_data.get("expires_at"),
                    "nick": cookie_data.get("nick", "Unknown")
                })
            except Exception as e:
                continue
    
    return {"cookies": cookies}


@router.delete("/cookies/{account_id}")
async def delete_cookie(
    account_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除指定账号的 Cookie"""
    from pathlib import Path
    
    cookie_file = Path(f".cookies/{account_id}.json")
    
    if cookie_file.exists():
        cookie_file.unlink()
        return {"success": True, "message": f"已删除 Cookie: {account_id}"}
    else:
        raise HTTPException(status_code=404, detail="Cookie 不存在")


@router.post("/accounts/load-from-cookie")
async def load_accounts_from_cookie(
    current_user: User = Depends(get_current_user)
):
    """从 Cookie 文件加载账号"""
    from pathlib import Path
    import json
    
    cookie_dir = Path(".cookies")
    loaded = []
    
    if cookie_dir.exists():
        for cookie_file in cookie_dir.glob("*.json"):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                account_id = cookie_data.get("account_id")
                cookie = cookie_data.get("cookie")
                
                if account_id and cookie:
                    xianyu_manager.add_client(
                        account_id=account_id,
                        cookie=cookie
                    )
                    loaded.append(account_id)
            except Exception as e:
                continue
    
    return {
        "success": True,
        "loaded_accounts": loaded,
        "total": len(loaded)
    }
