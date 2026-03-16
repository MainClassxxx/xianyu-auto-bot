"""
推广返利和余额 API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.services.referral_service import ReferralService, BalanceService, RECHARGE_PACKAGES
from app.api.auth import get_current_user
import uuid

router = APIRouter(prefix="/api/referral", tags=["推广返利"])

class ReferralLinkResponse(BaseModel):
    """推广链接响应"""
    id: int
    referral_code: str
    referral_url: str
    total_clicks: int
    total_registrations: int
    total_purchases: int
    total_earnings: float
    is_active: bool

class BalanceResponse(BaseModel):
    """余额响应"""
    user_id: int
    username: str
    balance: float
    frozen_balance: float
    total_recharge: float
    total_commission: float

class CreateRechargeOrderRequest(BaseModel):
    """创建充值订单请求"""
    amount: float
    payment_method: str = "alipay"

class UseBalanceRequest(BaseModel):
    """使用余额请求"""
    amount: float
    order_no: str
    description: str = ""

# ========== 推广链接管理 ==========

@router.get("/link", response_model=ReferralLinkResponse)
async def get_referral_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的推广链接"""
    service = ReferralService(db)
    link = service.get_referral_link(current_user.id)
    
    if not link:
        # 自动创建
        link = service.create_referral_link(current_user)
    
    return link

@router.post("/link/create", response_model=ReferralLinkResponse)
async def create_referral_link(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建推广链接"""
    service = ReferralService(db)
    link = service.create_referral_link(current_user)
    return link

@router.get("/stats")
async def get_referral_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取推广统计"""
    service = ReferralService(db)
    link = service.get_referral_link(current_user.id)
    
    if not link:
        return {
            "total_registrations": 0,
            "total_purchases": 0,
            "total_earnings": 0.0,
            "recent_records": []
        }
    
    # 获取最近的推广记录
    from app.models.referral import ReferralRecord
    records = db.query(ReferralRecord).filter(
        ReferralRecord.referrer_id == current_user.id
    ).order_by(ReferralRecord.created_at.desc()).limit(10).all()
    
    return {
        "total_registrations": link["total_registrations"],
        "total_purchases": link["total_purchases"],
        "total_earnings": link["total_earnings"],
        "recent_records": records
    }

# ========== 余额管理 ==========

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户余额"""
    service = BalanceService(db)
    balance = service.get_balance(current_user.id)
    
    if not balance:
        # 返回空余额
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "balance": 0.0,
            "frozen_balance": 0.0,
            "total_recharge": 0.0,
            "total_commission": 0.0
        }
    
    return balance

@router.get("/balance/packages")
async def get_recharge_packages(db: Session = Depends(get_db)):
    """获取充值套餐"""
    service = BalanceService(db)
    return {
        "packages": service.get_recharge_packages()
    }

@router.post("/recharge/create")
async def create_recharge_order(
    request: CreateRechargeOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建充值订单"""
    service = BalanceService(db)
    
    # 生成订单号
    order_no = f"RC{datetime.now().strftime('%Y%m%d%H%M%S')}{current_user.id}"
    
    order = service.recharge(
        user=current_user,
        amount=request.amount,
        order_no=order_no,
        payment_method=request.payment_method
    )
    
    return {
        "success": True,
        "data": order
    }

@router.post("/recharge/{order_no}/pay")
async def pay_recharge_order(
    order_no: str,
    transaction_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """支付充值订单"""
    service = BalanceService(db)
    
    try:
        result = service.confirm_recharge(order_no, transaction_id)
        return {
            "success": True,
            "message": "充值成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/balance/transactions")
async def get_balance_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取余额交易记录"""
    service = BalanceService(db)
    transactions = service.get_transactions(current_user.id, page, page_size)
    
    return {
        "success": True,
        "data": transactions
    }

@router.post("/balance/use")
async def use_balance(
    request: UseBalanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """使用余额支付"""
    service = BalanceService(db)
    
    success = service.use_balance(
        user_id=current_user.id,
        amount=request.amount,
        order_no=request.order_no,
        description=request.description
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="余额不足")
    
    return {
        "success": True,
        "message": "余额支付成功"
    }

# ========== 推广注册处理 ==========

@router.post("/register/track")
async def track_referral_registration(
    referral_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """追踪推广注册（用户注册后调用）"""
    service = ReferralService(db)
    
    # 检查是否已有推广链接（推广人不能注册自己的链接）
    existing_link = service.get_referral_link(current_user.id)
    if existing_link and existing_link.get("referral_code") == referral_code:
        return {"success": False, "message": "不能通过自己的推广链接注册"}
    
    # 追踪注册
    record = service.track_registration(referral_code, current_user)
    
    if record:
        return {
            "success": True,
            "message": "推广注册已记录",
            "referrer": record.referrer_username
        }
    else:
        return {
            "success": False,
            "message": "无效的推广码"
        }
