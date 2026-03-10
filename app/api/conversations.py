"""
对话消息 API
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/conversations", tags=["对话消息"])

@router.get("")
async def get_conversations():
    """获取会话列表"""
    return []

@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    """获取消息列表"""
    return []

@router.post("/{conversation_id}/messages")
async def send_message(conversation_id: str):
    """发送消息"""
    return {"success": True}

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除会话"""
    return {"success": True}
