"""
闲鱼登录 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.services.xianyu_oauth import xianyu_oauth

router = APIRouter(prefix="/api/auth", tags=["认证登录"])

class LoginSessionCreate(BaseModel):
    headless: bool = False

class LoginSessionResponse(BaseModel):
    session_id: str
    login_url: str
    status: str

@router.post("/xianyu", response_model=LoginSessionResponse)
async def create_xianyu_login(login_data: LoginSessionCreate = None):
    """创建闲鱼登录会话"""
    session_id = str(uuid.uuid4())
    
    try:
        login_url = await xianyu_oauth.create_login_session(session_id)
        
        return {
            "session_id": session_id,
            "login_url": login_url,
            "status": "waiting"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建登录会话失败：{str(e)}")

@router.get("/xianyu/{session_id}")
async def check_login_status(session_id: str):
    """检查登录状态"""
    result = await xianyu_oauth.check_login_status(session_id)
    
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@router.delete("/xianyu/{session_id}")
async def close_login_session(session_id: str):
    """关闭登录会话"""
    await xianyu_oauth.close_session(session_id)
    return {"success": True}
