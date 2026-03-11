"""
数据统计 API - 真实实现
"""
from fastapi import APIRouter, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models import Account, Item, Order, SystemLog

router = APIRouter(prefix="/api/stats", tags=["数据统计"])

@router.get("/overview")
async def get_overview(db: Session = Depends(get_db)):
    """获取概览统计"""
    # 账号统计
    total_accounts = db.query(Account).count()
    active_accounts = db.query(Account).filter(Account.status == "active").count()
    
    # 商品统计
    total_items = db.query(Item).count()
    onsale_items = db.query(Item).filter(Item.status == "onsale").count()
    
    # 订单统计
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    paid_orders = db.query(Order).filter(Order.status == "paid").count()
    
    # 收入统计 (今日)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = db.query(func.sum(Order.price)).filter(
        Order.status.in_(["paid", "shipped", "completed"]),
        Order.created_at >= today_start
    ).scalar() or 0.0
    
    return {
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "total_items": total_items,
        "onsale_items": onsale_items,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
        "total_revenue": today_revenue,
        "formatted_revenue": f"¥{today_revenue:.2f}"
    }

@router.get("/orders")
async def get_order_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取订单统计"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 按状态统计
    stats = db.query(
        Order.status,
        func.count(Order.id).label("count")
    ).filter(
        Order.created_at >= start_date
    ).group_by(Order.status).all()
    
    result = {stat.status: stat.count for stat in stats}
    result["total"] = sum(result.values())
    
    return result

@router.get("/revenue")
async def get_revenue_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取收入统计"""
    start_date = datetime.now() - timedelta(days=days)
    
    # 总收入
    total = db.query(func.sum(Order.price)).filter(
        Order.status.in_(["paid", "shipped", "completed"]),
        Order.created_at >= start_date
    ).scalar() or 0.0
    
    # 按日统计
    daily_stats = db.query(
        func.date(Order.created_at).label("date"),
        func.sum(Order.price).label("revenue")
    ).filter(
        Order.status.in_(["paid", "shipped", "completed"]),
        Order.created_at >= start_date
    ).group_by(func.date(Order.created_at)).all()
    
    return {
        "total": total,
        "formatted_total": f"¥{total:.2f}",
        "daily": [{"date": str(s.date), "revenue": float(s.revenue)} for s in daily_stats]
    }

@router.get("/accounts")
async def get_account_stats(db: Session = Depends(get_db)):
    """获取账号统计"""
    total = db.query(Account).count()
    active = db.query(Account).filter(Account.status == "active").count()
    inactive = total - active
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "active_rate": f"{(active/total*100) if total > 0 else 0:.1f}%"
    }

@router.get("/items")
async def get_item_stats(db: Session = Depends(get_db)):
    """获取商品统计"""
    total = db.query(Item).count()
    onsale = db.query(Item).filter(Item.status == "onsale").count()
    sold = db.query(Item).filter(Item.status == "sold").count()
    out = db.query(Item).filter(Item.status == "out").count()
    
    return {
        "total": total,
        "onsale": onsale,
        "sold": sold,
        "out": out
    }
