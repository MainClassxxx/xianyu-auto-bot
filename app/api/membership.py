"""
会员购买 API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.services.membership_order_service import MembershipOrderService, AdminMembershipService, MEMBERSHIP_PLANS
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/membership", tags=["会员购买"])

class MembershipPlanResponse(BaseModel):
    """会员套餐响应"""
    level: str
    plans: List[dict]

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    level: str  # vip, svip
    plan: str  # 1_month, 2_months, etc.
    payment_method: str = "alipay"  # alipay, wechat

class OrderResponse(BaseModel):
    """订单响应"""
    order_no: str
    level: str
    plan: str
    plan_name: str
    days: int
    price: float
    payment_method: str
    status: str
    created_at: datetime
    expire_at: datetime

@router.get("/plans")
async def get_membership_plans(db: Session = Depends(get_db)):
    """获取所有会员套餐"""
    return {
        "plans": MEMBERSHIP_PLANS
    }

@router.post("/order/create", response_model=dict)
async def create_membership_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建会员购买订单"""
    service = MembershipOrderService(db)
    
    try:
        order = service.create_order(
            user=current_user,
            level=request.level,
            plan=request.plan,
            payment_method=request.payment_method
        )
        
        return {
            "success": True,
            "data": order
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/order/{order_no}")
async def get_order_detail(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    service = MembershipOrderService(db)
    
    order = service.get_order_detail(order_no)
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查权限：只能查看自己的订单，管理员可以查看所有订单
    if order["user_id"] != current_user.id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="无权查看此订单")
    
    return {
        "success": True,
        "data": order
    }

@router.get("/orders")
async def get_user_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户订单列表"""
    service = MembershipOrderService(db)
    
    orders = service.get_user_orders(current_user.id, page, page_size)
    
    return {
        "success": True,
        "data": orders
    }

@router.post("/order/{order_no}/cancel")
async def cancel_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消订单"""
    service = MembershipOrderService(db)
    
    try:
        success = service.cancel_order(order_no, current_user.id)
        return {"success": True, "message": "订单已取消"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/order/{order_no}/pay")
async def pay_order(
    order_no: str,
    transaction_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """支付订单（模拟支付，后续接入真实支付）"""
    service = MembershipOrderService(db)
    
    try:
        result = service.pay_order(order_no, transaction_id)
        return {
            "success": True,
            "message": "支付成功，会员已开通",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========== 管理员接口 ==========

@router.post("/admin/grant")
async def admin_grant_membership(
    user_id: int,
    level: str,
    days: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员手动开通会员"""
    service = AdminMembershipService(db)
    
    try:
        result = service.grant_membership(
            admin=current_user,
            target_user_id=user_id,
            level=level,
            days=days,
            reason=reason
        )
        return {
            "success": True,
            "message": f"已为用户开通 {level} 会员 {days}天",
            "data": result
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/grant-logs")
async def get_grant_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会员开通日志（仅管理员）"""
    service = AdminMembershipService(db)
    
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    logs = service.get_grant_logs(page, page_size)
    
    return {
        "success": True,
        "data": logs
    }
