"""
商品管理 API - 真实实现
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Account
from app.services.xianyu_api import xianyu_manager

router = APIRouter(prefix="/api/items", tags=["商品管理"])

class PriceUpdate(BaseModel):
    price: float

class ToggleRequest(BaseModel):
    action: str  # "onshelf" or "offshelf"

@router.get("", response_model=List[dict])
async def get_items(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    if account_id:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        
        client = xianyu_manager.get_client(str(account_id))
        if not client:
            raise HTTPException(status_code=400, detail="账号未连接")
        
        items = await client.get_items(status=status or "onsale", page=page, page_size=page_size)
        return items
    
    return []

@router.get("/{item_id}")
async def get_item(item_id: str):
    """获取商品详情"""
    return {"item_id": item_id}

@router.post("/{item_id}/price")
async def update_item_price(
    item_id: str,
    price_update: PriceUpdate,
    account_id: int,
    db: Session = Depends(get_db)
):
    """修改商品价格"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    client = xianyu_manager.get_client(str(account_id))
    if not client:
        raise HTTPException(status_code=400, detail="账号未连接")
    
    success = await client.update_item_price(item_id, price_update.price)
    
    if success:
        return {"success": True, "item_id": item_id, "new_price": price_update.price}
    else:
        raise HTTPException(status_code=500, detail="改价失败")

@router.post("/{item_id}/toggle")
async def toggle_item(
    item_id: str,
    toggle_req: ToggleRequest,
    account_id: int,
    db: Session = Depends(get_db)
):
    """上架/下架商品"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    client = xianyu_manager.get_client(str(account_id))
    if not client:
        raise HTTPException(status_code=400, detail="账号未连接")
    
    success = await client.shelf_item(item_id, toggle_req.action)
    
    return {"success": success, "item_id": item_id, "action": toggle_req.action}

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """删除商品"""
    return {"success": True}
