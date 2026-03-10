"""
对话消息 API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/conversations", tags=["对话消息"])

class MessageResponse(BaseModel):
    id: str
    sender: str
    content: str
    msg_type: str
    created_at: str

class SendMessageRequest(BaseModel):
    conversation_id: str
    content: str
    msg_type: str = "text"

@router.get("", response_model=List[dict])
async def get_conversations(account_id: Optional[int] = None):
    """获取会话列表"""
    return []

@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: str, page: int = 1, page_size: int = 50):
    """获取消息列表"""
    return []

@router.post("/{conversation_id}/messages")
async def send_message(conversation_id: str, message: SendMessageRequest):
    """发送消息"""
    return {"success": True, "message_id": "msg_123"}

@router.post("/{conversation_id}/messages/image")
async def send_image(conversation_id: str, image: UploadFile = File(...)):
    """发送图片"""
    return {"success": True, "image_url": "https://example.com/image.jpg"}

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除会话"""
    return {"success": True}
