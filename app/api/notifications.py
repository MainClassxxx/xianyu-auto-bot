"""
通知管理 API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import NotificationChannel
from app.services.notification_service import NotificationService, FeishuNotificationService, init_feishu_webhook

router = APIRouter(prefix="/api/notifications", tags=["通知管理"])

class NotificationChannelCreate(BaseModel):
    name: str
    channel_type: str  # feishu, telegram, wechat, dingtalk
    webhook_url: Optional[str] = None
    token: Optional[str] = None

class NotificationChannelUpdate(BaseModel):
    name: Optional[str] = None
    webhook_url: Optional[str] = None
    token: Optional[str] = None
    enabled: Optional[bool] = None

class TestNotification(BaseModel):
    channel_id: int
    message: str = "测试消息"

@router.get("/channels", response_model=List[dict])
async def get_notification_channels(db: Session = Depends(get_db)):
    """获取通知渠道列表"""
    channels = db.query(NotificationChannel).all()
    return channels

@router.post("/channels", response_model=dict)
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    db: Session = Depends(get_db)
):
    """创建通知渠道"""
    channel = NotificationChannel(**channel_data.dict())
    db.add(channel)
    db.commit()
    db.refresh(channel)
    
    return {"success": True, "channel_id": channel.id}

@router.put("/channels/{channel_id}")
async def update_notification_channel(
    channel_id: int,
    channel_update: NotificationChannelUpdate,
    db: Session = Depends(get_db)
):
    """更新通知渠道"""
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    
    for key, value in channel_update.dict(exclude_unset=True).items():
        setattr(channel, key, value)
    
    db.commit()
    db.refresh(channel)
    
    return {"success": True}

@router.delete("/channels/{channel_id}")
async def delete_notification_channel(channel_id: int, db: Session = Depends(get_db)):
    """删除通知渠道"""
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    
    db.delete(channel)
    db.commit()
    
    return {"success": True}

@router.post("/channels/{channel_id}/toggle")
async def toggle_notification_channel(channel_id: int, db: Session = Depends(get_db)):
    """启用/禁用通知渠道"""
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    
    channel.enabled = not channel.enabled
    db.commit()
    
    return {"success": True, "enabled": channel.enabled}

@router.post("/test")
async def test_notification(
    test_data: TestNotification,
    db: Session = Depends(get_db)
):
    """测试通知"""
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == test_data.channel_id
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    
    if not channel.enabled:
        raise HTTPException(status_code=400, detail="渠道已禁用")
    
    if channel.channel_type == "feishu" and channel.webhook_url:
        service = FeishuNotificationService(channel.webhook_url)
        success = service.send_text(f"🧪 {test_data.message}")
        
        if success:
            return {"success": True, "message": "测试消息发送成功"}
        else:
            raise HTTPException(status_code=500, detail="发送失败")
    
    return {"success": True, "message": "测试完成"}

@router.post("/feishu/setup")
async def setup_feishu_webhook(
    webhook_url: str,
    db: Session = Depends(get_db)
):
    """快速配置飞书 Webhook"""
    channel = init_feishu_webhook(db, webhook_url)
    return {"success": True, "channel_id": channel.id}

@router.get("/history")
async def get_notification_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取通知历史"""
    # TODO: 实现通知历史记录
    return {"records": []}
