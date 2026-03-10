"""
商品管理 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/items", tags=["商品管理"])

class ItemResponse(BaseModel):
    id: str
    title: str
    price: float
    status: str
    images: List[str]

@router.get("", response_model=List[ItemResponse])
async def get_items(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取商品列表"""
    return []

@router.get("/{item_id}")
async def get_item(item_id: str):
    """获取商品详情"""
    return {"id": item_id, "title": "测试商品", "price": 99.0, "status": "onsale"}

@router.post("/{item_id}/price")
async def update_item_price(item_id: str, price: float):
    """修改商品价格"""
    return {"success": True, "item_id": item_id, "new_price": price}

@router.post("/{item_id}/toggle")
async def toggle_item(item_id: str, action: str):
    """上架/下架商品"""
    # action: onshelf/offshelf
    return {"success": True}

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """删除商品"""
    return {"success": True}
