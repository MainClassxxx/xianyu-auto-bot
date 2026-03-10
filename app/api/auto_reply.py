"""
自动回复 API
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/auto-reply", tags=["自动回复"])

@router.get("/rules")
async def get_reply_rules():
    """获取自动回复规则列表"""
    return []

@router.post("/rules")
async def create_reply_rule():
    """创建自动回复规则"""
    return {"success": True}

@router.delete("/rules/{rule_id}")
async def delete_reply_rule(rule_id: int):
    """删除自动回复规则"""
    return {"success": True}
