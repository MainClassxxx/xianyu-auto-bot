"""
通知管理 API
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/notifications", tags=["通知管理"])

@router.get("/channels")
async def get_channels():
    """获取通知渠道列表"""
    return []

@router.post("/channels")
async def create_channel():
    """创建通知渠道"""
    return {"success": True}

@router.delete("/channels/{channel_id}")
async def delete_channel(channel_id: int):
    """删除通知渠道"""
    return {"success": True}
