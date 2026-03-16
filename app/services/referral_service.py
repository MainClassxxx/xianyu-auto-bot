"""
推广返利服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger
import random
import string
from app.models.user import User
from app.models.referral import ReferralLink, ReferralRecord, UserBalance, BalanceTransaction, RechargeOrder, ReferralStatus

# 返利配置
COMMISSION_CONFIG = {
    "rate": 0.3,  # 30% 返利
    "min_order_amount": 0.01,  # 最小订单金额
}

# 充值套餐
RECHARGE_PACKAGES = [
    {"amount": 10, "bonus": 0, "name": "10 元"},
    {"amount": 30, "bonus": 2, "name": "30 元"},
    {"amount": 50, "bonus": 5, "name": "50 元"},
    {"amount": 100, "bonus": 15, "name": "100 元"},
    {"amount": 200, "bonus": 40, "name": "200 元"},
    {"amount": 500, "bonus": 120, "name": "500 元"},
]

class ReferralService:
    """推广服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_referral_code(self) -> str:
        """生成唯一推广码"""
        while True:
            # 生成 8 位随机码（字母 + 数字）
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # 检查是否已存在
            existing = self.db.query(ReferralLink).filter(
                ReferralLink.referral_code == code
            ).first()
            
            if not existing:
                return code
    
    def create_referral_link(self, user: User) -> Dict:
        """创建推广链接"""
        # 检查是否已有推广链接
        existing = self.db.query(ReferralLink).filter(
            ReferralLink.user_id == user.id
        ).first()
        
        if existing:
            return self.get_referral_link(user.id)
        
        # 生成推广码
        referral_code = self.generate_referral_code()
        
        # 创建推广链接
        referral_url = f"https://yourdomain.com/register?ref={referral_code}"
        
        link = ReferralLink(
            user_id=user.id,
            username=user.username,
            referral_code=referral_code,
            referral_url=referral_url
        )
        
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        
        logger.info(f"🔗 用户 {user.username} 创建推广链接：{referral_code}")
        
        return {
            "id": link.id,
            "referral_code": link.referral_code,
            "referral_url": link.referral_url,
            "total_clicks": link.total_clicks,
            "total_registrations": link.total_registrations,
            "total_purchases": link.total_purchases,
            "total_earnings": link.total_earnings,
            "is_active": link.is_active
        }
    
    def get_referral_link(self, user_id: int) -> Optional[Dict]:
        """获取用户推广链接"""
        link = self.db.query(ReferralLink).filter(
            ReferralLink.user_id == user_id
        ).first()
        
        if not link:
            return None
        
        return {
            "id": link.id,
            "referral_code": link.referral_code,
            "referral_url": link.referral_url,
            "total_clicks": link.total_clicks,
            "total_registrations": link.total_registrations,
            "total_purchases": link.total_purchases,
            "total_earnings": round(link.total_earnings, 2),
            "is_active": link.is_active,
            "created_at": link.created_at
        }
    
    def track_registration(self, referral_code: str, new_user: User) -> Optional[ReferralRecord]:
        """追踪用户注册"""
        # 查找推广链接
        link = self.db.query(ReferralLink).filter(
            ReferralLink.referral_code == referral_code
        ).first()
        
        if not link or not link.is_active:
            return None
        
        # 检查是否已有记录
        existing = self.db.query(ReferralRecord).filter(
            ReferralRecord.referral_link_id == link.id,
            ReferralRecord.referred_user_id == new_user.id
        ).first()
        
        if existing:
            return None
        
        # 创建推广记录
        record = ReferralRecord(
            referral_link_id=link.id,
            referrer_id=link.user_id,
            referrer_username=link.username,
            referred_user_id=new_user.id,
            referred_username=new_user.username,
            commission_rate=COMMISSION_CONFIG["rate"],
            status=ReferralStatus.PENDING.value,
            registered_at=datetime.now()
        )
        
        self.db.add(record)
        
        # 更新统计
        link.total_registrations += 1
        self.db.commit()
        
        logger.info(f"📝 推广注册：{link.username} → {new_user.username}")
        
        return record
    
    def track_purchase(self, user: User, order_no: str, order_amount: float) -> Optional[ReferralRecord]:
        """追踪用户购买并返利"""
        if order_amount < COMMISSION_CONFIG["min_order_amount"]:
            return None
        
        # 查找用户的推广记录（待生效）
        record = self.db.query(ReferralRecord).filter(
            ReferralRecord.referred_user_id == user.id,
            ReferralRecord.status == ReferralStatus.PENDING.value,
            ReferralRecord.order_no.is_(None)
        ).order_by(desc(ReferralRecord.created_at)).first()
        
        if not record:
            return None
        
        # 计算返利
        commission = order_amount * record.commission_rate
        
        # 更新记录
        record.order_no = order_no
        record.order_amount = order_amount
        record.commission_amount = commission
        record.status = ReferralStatus.ACTIVE.value
        record.purchased_at = datetime.now()
        
        # 给推广人返利
        self.add_commission(record.referrer_id, commission, order_no, record.id)
        
        # 更新推广链接统计
        link = self.db.query(ReferralLink).filter(
            ReferralLink.id == record.referral_link_id
        ).first()
        
        if link:
            link.total_purchases += 1
            link.total_earnings += commission
        
        self.db.commit()
        
        logger.info(f"💰 推广购买返利：{record.referrer_username} 获得 ¥{commission} 返利")
        
        return record
    
    def add_commission(self, user_id: int, amount: float, order_no: str, referral_id: int):
        """添加返利到用户余额"""
        # 获取或创建用户余额账户
        balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user_id
        ).first()
        
        if not balance:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                balance = UserBalance(
                    user_id=user_id,
                    username=user.username,
                    balance=0.0
                )
                self.db.add(balance)
                self.db.commit()
                self.db.refresh(balance)
        
        # 更新余额
        balance_before = balance.balance
        balance.balance += amount
        balance.total_commission += amount
        
        # 创建交易记录
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="commission",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance.balance,
            related_order_no=order_no,
            related_referral_id=referral_id,
            description=f"推广返利 - 订单 {order_no}",
            remark=f"返利比例：{COMMISSION_CONFIG['rate']*100}%"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"💵 返利入账：用户 {balance.username} 余额 +¥{amount}")


class BalanceService:
    """余额服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_balance(self, user_id: int) -> Optional[Dict]:
        """获取用户余额"""
        balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user_id
        ).first()
        
        if not balance:
            return None
        
        return {
            "user_id": balance.user_id,
            "username": balance.username,
            "balance": round(balance.balance, 2),
            "frozen_balance": round(balance.frozen_balance, 2),
            "total_recharge": round(balance.total_recharge, 2),
            "total_consumption": round(balance.total_consumption, 2),
            "total_commission": round(balance.total_commission, 2),
            "updated_at": balance.updated_at
        }
    
    def get_or_create_balance(self, user: User) -> UserBalance:
        """获取或创建用户余额账户"""
        balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user.id
        ).first()
        
        if not balance:
            balance = UserBalance(
                user_id=user.id,
                username=user.username,
                balance=0.0
            )
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def recharge(self, user: User, amount: float, order_no: str, payment_method: str = "alipay") -> Dict:
        """充值"""
        # 创建充值订单
        order = RechargeOrder(
            order_no=order_no,
            user_id=user.id,
            username=user.username,
            amount=amount,
            payment_method=payment_method,
            status="pending"
        )
        
        self.db.add(order)
        self.db.commit()
        
        logger.info(f"💳 创建充值订单：{order_no}, 金额：¥{amount}")
        
        return {
            "order_no": order_no,
            "amount": amount,
            "payment_method": payment_method,
            "status": "pending",
            "expire_at": order.expire_at
        }
    
    def confirm_recharge(self, order_no: str, transaction_id: str = None) -> Dict:
        """确认充值并追踪推广返利"""
        order = self.db.query(RechargeOrder).filter(
            RechargeOrder.order_no == order_no
        ).first()
        
        if not order:
            raise ValueError("订单不存在")
        
        if order.status != "pending":
            raise ValueError(f"订单状态不正确：{order.status}")
        
        # 更新订单状态
        order.status = "paid"
        order.paid_at = datetime.now()
        order.transaction_id = transaction_id or f"TXN{datetime.now().timestamp()}"
        
        # 更新用户余额
        balance = self.get_or_create_balance_by_id(order.user_id)
        balance_before = balance.balance
        
        # 计算赠送金额
        bonus = self.calculate_recharge_bonus(order.amount)
        total_amount = order.amount + bonus
        
        balance.balance += total_amount
        balance.total_recharge += order.amount
        
        # 创建交易记录
        transaction = BalanceTransaction(
            user_id=order.user_id,
            transaction_type="recharge",
            amount=total_amount,
            balance_before=balance_before,
            balance_after=balance.balance,
            related_order_no=order_no,
            description=f"充值 ¥{order.amount}" + (f" + 赠送 ¥{bonus}" if bonus > 0 else ""),
            remark=f"支付方式：{order.payment_method}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"✅ 充值成功：{order.username} 充值 ¥{order.amount}, 实际入账 ¥{total_amount}")
        
        # 追踪推广充值返利（30%）
        self.track_referral_recharge(order, order.amount)
        
        return {
            "success": True,
            "order_no": order_no,
            "amount": order.amount,
            "bonus": bonus,
            "total_amount": total_amount,
            "paid_at": order.paid_at
        }
    
    def track_referral_recharge(self, order, amount: float):
        """追踪推广充值返利"""
        try:
            from app.models.user import User
            user = self.db.query(User).filter(User.id == order.user_id).first()
            if user:
                from app.services.referral_service import ReferralService
                referral_service = ReferralService(self.db)
                referral_service.track_purchase(
                    user=user,
                    order_no=order.order_no,
                    order_amount=amount,
                    order_type="recharge"
                )
                logger.info(f"🔗 已追踪推广充值返利：{order.order_no}")
        except Exception as e:
            logger.error(f"追踪推广充值返利失败：{e}")
    
    def get_or_create_balance_by_id(self, user_id: int) -> UserBalance:
        """通过用户 ID 获取或创建余额账户"""
        balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user_id
        ).first()
        
        if not balance:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                balance = UserBalance(
                    user_id=user_id,
                    username=user.username,
                    balance=0.0
                )
                self.db.add(balance)
                self.db.commit()
                self.db.refresh(balance)
        
        return balance
    
    def calculate_recharge_bonus(self, amount: float) -> float:
        """计算充值赠送金额"""
        for package in RECHARGE_PACKAGES:
            if abs(package["amount"] - amount) < 0.01:
                return package["bonus"]
        return 0.0
    
    def use_balance(self, user_id: int, amount: float, order_no: str, description: str = "") -> bool:
        """使用余额"""
        balance = self.db.query(UserBalance).filter(
            UserBalance.user_id == user_id
        ).first()
        
        if not balance or balance.balance < amount:
            return False
        
        balance_before = balance.balance
        balance.balance -= amount
        balance.total_consumption += amount
        
        # 创建交易记录
        transaction = BalanceTransaction(
            user_id=user_id,
            transaction_type="consumption",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance.balance,
            related_order_no=order_no,
            description=description,
            remark="余额支付"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"💸 余额消费：用户余额 -¥{amount}")
        
        return True
    
    def get_transactions(self, user_id: int, page: int = 1, page_size: int = 20) -> Dict:
        """获取用户交易记录"""
        query = self.db.query(BalanceTransaction).filter(
            BalanceTransaction.user_id == user_id
        ).order_by(desc(BalanceTransaction.created_at))
        
        total = query.count()
        transactions = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "total": total,
            "transactions": transactions
        }
    
    def get_recharge_packages(self) -> List[Dict]:
        """获取充值套餐"""
        return RECHARGE_PACKAGES
