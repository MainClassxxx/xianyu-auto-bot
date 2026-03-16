"""
会员购买和支付服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger
from app.models.user import User, MembershipLevel
from app.services.membership_service import MembershipService

# 会员套餐配置
MEMBERSHIP_PLANS = {
    "vip": {
        "1_month": {"days": 30, "price": 9.9, "name": "VIP 会员 - 1 个月"},
        "2_months": {"days": 60, "price": 17.9, "name": "VIP 会员 - 2 个月"},
        "3_months": {"days": 90, "price": 24.9, "name": "VIP 会员 - 3 个月"},
        "6_months": {"days": 180, "price": 45.9, "name": "VIP 会员 - 6 个月"},
        "12_months": {"days": 365, "price": 79.9, "name": "VIP 会员 - 12 个月"},
    },
    "svip": {
        "1_month": {"days": 30, "price": 19.9, "name": "SVIP 会员 - 1 个月"},
        "2_months": {"days": 60, "price": 35.9, "name": "SVIP 会员 - 2 个月"},
        "3_months": {"days": 90, "price": 49.9, "name": "SVIP 会员 - 3 个月"},
        "6_months": {"days": 180, "price": 89.9, "name": "SVIP 会员 - 6 个月"},
        "12_months": {"days": 365, "price": 159.9, "name": "SVIP 会员 - 12 个月"},
    }
}

class MembershipOrderService:
    """会员订单服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.membership_service = MembershipService(db)
    
    def get_membership_plans(self) -> Dict:
        """获取所有会员套餐"""
        return MEMBERSHIP_PLANS
    
    def create_order(
        self, 
        user: User, 
        level: str, 
        plan: str,
        payment_method: str = "alipay"  # alipay, wechat
    ) -> Dict:
        """创建会员购买订单"""
        from app.models.membership import MembershipOrder
        
        # 验证套餐
        if level not in MEMBERSHIP_PLANS:
            raise ValueError("无效的会员等级")
        
        if plan not in MEMBERSHIP_PLANS[level]:
            raise ValueError("无效的套餐")
        
        plan_info = MEMBERSHIP_PLANS[level][plan]
        
        # 生成订单号
        order_no = f"VIP{datetime.now().strftime('%Y%m%d%H%M%S')}{user.id}"
        
        # 创建订单
        order = MembershipOrder(
            order_no=order_no,
            user_id=user.id,
            username=user.username,
            level=level,
            plan=plan,
            days=plan_info["days"],
            price=plan_info["price"],
            payment_method=payment_method,
            status="pending"  # pending, paid, cancelled, expired
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        logger.info(f"📝 创建会员订单：{order_no}, 用户：{user.username}, 金额：{plan_info['price']}")
        
        return {
            "order_no": order_no,
            "level": level,
            "plan": plan,
            "plan_name": plan_info["name"],
            "days": plan_info["days"],
            "price": plan_info["price"],
            "payment_method": payment_method,
            "payment_url": f"/api/membership/pay/{order_no}",  # 支付链接（后续实现）
            "expire_at": order.expire_at
        }
    
    def pay_order(self, order_no: str, transaction_id: str = None, use_balance: bool = False) -> Dict:
        """支付订单并开通会员"""
        from app.models.membership import MembershipOrder
        from app.services.referral_service import BalanceService
        
        order = self.db.query(MembershipOrder).filter(
            MembershipOrder.order_no == order_no
        ).first()
        
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != "pending":
            raise ValueError(f"订单状态不正确：{order.status}")
        
        user = self.db.query(User).filter(User.id == order.user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        # 根据支付方式处理
        if order.payment_method == "balance" or use_balance:
            # 使用余额支付
            balance_service = BalanceService(self.db)
            
            if not balance_service.use_balance(
                user_id=user.id,
                amount=order.price,
                order_no=order_no,
                description=f"购买{order.level}会员-{order.plan}"
            ):
                raise ValueError("余额不足")
            
            order.transaction_id = f"BAL{datetime.now().timestamp()}"
        else:
            # 第三方支付
            order.transaction_id = transaction_id or f"TXN{datetime.now().timestamp()}"
        
        # 更新订单状态
        order.status = "paid"
        order.paid_at = datetime.now()
        
        # 开通会员
        self.membership_service.upgrade_membership(user, order.level, order.days)
        logger.info(f"✅ 用户 {user.username} 已开通 {order.level} 会员，{order.days}天")
        
        # 追踪推广购买（如果有）
        self.track_referral_purchase(user, order_no, order.price)
        
        self.db.commit()
        
        logger.info(f"💰 订单支付成功：{order_no}, 交易 ID: {order.transaction_id}")
        
        return {
            "success": True,
            "order_no": order_no,
            "level": order.level,
            "days": order.days,
            "paid_at": order.paid_at
        }
    
    def track_referral_purchase(self, user: User, order_no: str, order_amount: float, order_type: str = "membership"):
        """追踪推广购买/充值"""
        try:
            from app.services.referral_service import ReferralService
            referral_service = ReferralService(self.db)
            referral_service.track_purchase(user, order_no, order_amount, order_type)
            logger.info(f"🔗 已追踪推广{order_type}：{order_no}")
        except Exception as e:
            logger.error(f"追踪推广失败：{e}")
    
    def get_user_orders(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict:
        """获取用户订单列表"""
        from app.models.membership import MembershipOrder
        
        query = self.db.query(MembershipOrder).filter(
            MembershipOrder.user_id == user_id
        ).order_by(desc(MembershipOrder.created_at))
        
        total = query.count()
        orders = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "orders": orders
        }
    
    def cancel_order(self, order_no: str, user_id: int) -> bool:
        """取消订单"""
        from app.models.membership import MembershipOrder
        
        order = self.db.query(MembershipOrder).filter(
            MembershipOrder.order_no == order_no,
            MembershipOrder.user_id == user_id
        ).first()
        
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != "pending":
            raise ValueError("只能取消待支付订单")
        
        order.status = "cancelled"
        self.db.commit()
        
        logger.info(f"❌ 订单已取消：{order_no}")
        return True
    
    def get_order_detail(self, order_no: str) -> Optional[Dict]:
        """获取订单详情"""
        from app.models.membership import MembershipOrder
        
        order = self.db.query(MembershipOrder).filter(
            MembershipOrder.order_no == order_no
        ).first()
        
        if not order:
            return None
        
        return {
            "order_no": order.order_no,
            "user_id": order.user_id,
            "username": order.username,
            "level": order.level,
            "plan": order.plan,
            "days": order.days,
            "price": order.price,
            "payment_method": order.payment_method,
            "status": order.status,
            "created_at": order.created_at,
            "paid_at": order.paid_at,
            "transaction_id": order.transaction_id,
            "expire_at": order.expire_at
        }


class AdminMembershipService:
    """管理员会员服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.membership_service = MembershipService(db)
    
    def grant_membership(
        self, 
        admin: User, 
        target_user_id: int, 
        level: str, 
        days: int,
        reason: str = None
    ) -> Dict:
        """管理员手动开通会员"""
        from app.models.membership import MembershipGrantLog
        from app.services.membership_service import AdminService
        
        # 检查管理员权限
        admin_service = AdminService(self.db)
        if not admin_service.is_admin(admin):
            raise PermissionError("需要管理员权限")
        
        # 获取目标用户
        target_user = self.db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise ValueError("用户不存在")
        
        # 验证等级
        if level not in [MembershipLevel.VIP.value, MembershipLevel.SVIP.value]:
            raise ValueError("只能开通 VIP 或 SVIP 会员")
        
        # 开通会员
        self.membership_service.upgrade_membership(target_user, level, days)
        
        # 记录日志
        log = MembershipGrantLog(
            admin_id=admin.id,
            admin_username=admin.username,
            user_id=target_user_id,
            username=target_user.username,
            level=level,
            days=days,
            reason=reason or "管理员手动开通"
        )
        self.db.add(log)
        self.db.commit()
        
        logger.info(f"🎁 管理员 {admin.username} 为用户 {target_user.username} 开通 {level} 会员 {days}天")
        
        return {
            "success": True,
            "user_id": target_user_id,
            "username": target_user.username,
            "level": level,
            "days": days,
            "expire_at": target_user.membership_expire_at
        }
    
    def get_grant_logs(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取会员开通日志"""
        from app.models.membership import MembershipGrantLog
        
        query = self.db.query(MembershipGrantLog).order_by(
            desc(MembershipGrantLog.created_at)
        )
        
        total = query.count()
        logs = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "logs": logs
        }
