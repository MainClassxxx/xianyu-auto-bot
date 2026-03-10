"""
自动回复 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/auto-reply", tags=["自动回复"])

class ReplyRule(BaseModel):
    name: str
    keyword: str
    match_type: str = "contains"  # exact/contains/regex/ai
    reply_content: str
    reply_type: str = "text"  # text/image
    enabled: bool = True
    priority: int = 0

class ReplyRuleResponse(ReplyRule):
    id: int

@router.get("/rules", response_model=List[ReplyRuleResponse])
async def get_reply_rules(account_id: Optional[int] = None):
    """获取自动回复规则列表"""
    return []

@router.post("/rules", response_model=ReplyRuleResponse)
async def create_reply_rule(rule: ReplyRule):
    """创建自动回复规则"""
    return {"id": 1, **rule.dict()}

@router.put("/rules/{rule_id}")
async def update_reply_rule(rule_id: int, rule: ReplyRule):
    """更新自动回复规则"""
    return {"success": True}

@router.delete("/rules/{rule_id}")
async def delete_reply_rule(rule_id: int):
    """删除自动回复规则"""
    return {"success": True}

@router.post("/rules/{rule_id}/toggle")
async def toggle_reply_rule(rule_id: int):
    """启用/禁用规则"""
    return {"success": True}
