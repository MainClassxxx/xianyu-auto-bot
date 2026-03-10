"""
数据统计 API
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/stats", tags=["数据统计"])

@router.get("/overview")
async def get_overview():
    """获取概览统计"""
    return {
        "total_items": 0,
        "total_orders": 0,
        "total_revenue": 0.0,
        "pending_orders": 0
    }

@router.get("/orders")
async def get_order_stats():
    """获取订单统计"""
    return {"total": 0}

@router.get("/revenue")
async def get_revenue_stats():
    """获取收入统计"""
    return {"total": 0.0}
