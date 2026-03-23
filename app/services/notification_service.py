"""
飞书通知服务 - 增强版（带重试机制和日志记录）
"""
import requests
import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.models import NotificationChannel, SystemLog

class FeishuNotificationService:
    """飞书通知服务（增强版）"""
    
    def __init__(self, webhook_url: str, max_retries: int = 3, retry_delay: int = 2):
        self.webhook_url = webhook_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def send_text(self, content: str, at_all: bool = False) -> bool:
        """发送文本消息"""
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        if at_all:
            payload["content"]["text"] = f"<at user_id=\"all\">所有人</at>\n{content}"
        
        return self._send_with_retry(payload, "text")
    
    def send_post(self, title: str, content: List[List[Dict[str, Any]]]) -> bool:
        """发送富文本消息"""
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content
                    }
                }
            }
        }
        return self._send_with_retry(payload, "post")
    
    def send_card(self, card: Dict[str, Any]) -> bool:
        """发送交互式卡片"""
        payload = {
            "msg_type": "interactive",
            "card": card
        }
        return self._send_with_retry(payload, "card")
    
    def _send(self, payload: Dict[str, Any]) -> bool:
        """发送消息（基础方法）"""
        response = requests.post(
            self.webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("StatusCode") == 0 or result.get("code") == 0:
                return True
            else:
                logger.error(f"❌ 飞书消息发送失败：{result}")
                return False
        else:
            logger.error(f"❌ 飞书消息发送失败：HTTP {response.status_code}")
            return False
    
    def _send_with_retry(self, payload: Dict[str, Any], msg_type: str) -> bool:
        """发送消息（带重试机制）"""
        attempt = 0
        
        while attempt < self.max_retries:
            try:
                if self._send(payload):
                    logger.info(f"✅ 飞书{msg_type}消息发送成功（尝试 {attempt + 1}/{self.max_retries}）")
                    return True
                
                attempt += 1
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt  # 指数退避
                    logger.warning(f"⚠️ 飞书消息发送失败，{wait_time}秒后重试（{attempt + 1}/{self.max_retries}）")
                    time.sleep(wait_time)
                    
            except requests.exceptions.Timeout:
                attempt += 1
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ 请求超时，{self.retry_delay}秒后重试（{attempt + 1}/{self.max_retries}）")
                    time.sleep(self.retry_delay)
            except requests.exceptions.ConnectionError:
                attempt += 1
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ 连接错误，{self.retry_delay}秒后重试（{attempt + 1}/{self.max_retries}）")
                    time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"❌ 发送消息异常：{e}")
                break
        
        logger.error(f"❌ 飞书消息发送失败，已达最大重试次数 {self.max_retries}")
        return False
    
    def log_notification(self, db: Session, notification_type: str, status: str, 
                        error_message: Optional[str] = None, data: Optional[Dict] = None):
        """记录通知日志"""
        log = SystemLog(
            level="INFO" if status == "success" else "ERROR",
            module="notification",
            message=f"飞书通知{notification_type} - {status}",
            data={
                "type": notification_type,
                "status": status,
                "error": error_message,
                "webhook_url": self.webhook_url[:20] + "..." if self.webhook_url else None,
                **data if data else {}
            }
        )
        db.add(log)
        db.commit()


class NotificationService:
    """统一通知服务（增强版）"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_enabled_channels(self) -> List[NotificationChannel]:
        """获取所有启用的通知渠道"""
        return self.db.query(NotificationChannel).filter(
            NotificationChannel.enabled == True
        ).all()
    
    def send_order_notification(self, order_info: Dict[str, Any]) -> bool:
        """发送订单通知"""
        channels = self.get_enabled_channels()
        if not channels:
            logger.warning("⚠️ 没有启用的通知渠道")
            return False
        
        success = False
        for channel in channels:
            if channel.channel_type == "feishu":
                service = FeishuNotificationService(channel.webhook_url)
                
                content = f"""📦 新订单通知

订单号：{order_info.get('order_id', 'N/A')}
商品：{order_info.get('item_title', 'N/A')}
金额：¥{order_info.get('price', 0)}
买家：{order_info.get('buyer_name', 'N/A')}
时间：{order_info.get('created_at', 'N/A')}

请及时处理！"""
                
                result = service.send_text(content)
                if result:
                    success = True
                    service.log_notification(
                        self.db, 
                        "order_notification", 
                        "success",
                        data={"order_id": order_info.get('order_id')}
                    )
                else:
                    service.log_notification(
                        self.db,
                        "order_notification",
                        "failed",
                        error_message="发送失败",
                        data={"order_id": order_info.get('order_id')}
                    )
        
        return success
    
    def send_delivery_notification(self, delivery_info: Dict[str, Any]) -> bool:
        """发送发货通知"""
        channels = self.get_enabled_channels()
        if not channels:
            return False
        
        success = False
        for channel in channels:
            if channel.channel_type == "feishu":
                service = FeishuNotificationService(channel.webhook_url)
                
                content = f"""✅ 自动发货完成

订单号：{delivery_info.get('order_id', 'N/A')}
商品：{delivery_info.get('item_title', 'N/A')}
发货时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

发货内容：{delivery_info.get('content', 'N/A')}"""
                
                result = service.send_text(content)
                if result:
                    success = True
                    service.log_notification(
                        self.db,
                        "delivery_notification",
                        "success",
                        data={"order_id": delivery_info.get('order_id')}
                    )
                else:
                    service.log_notification(
                        self.db,
                        "delivery_notification",
                        "failed",
                        error_message="发送失败",
                        data={"order_id": delivery_info.get('order_id')}
                    )
        
        return success
    
    def send_alert(self, title: str, message: str, level: str = "info") -> bool:
        """发送告警通知"""
        channels = self.get_enabled_channels()
        if not channels:
            return False
        
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        emoji = emojis.get(level, "ℹ️")
        
        success = False
        for channel in channels:
            if channel.channel_type == "feishu":
                service = FeishuNotificationService(channel.webhook_url)
                
                content = f"""{emoji} {title}

{message}

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                result = service.send_text(content, at_all=(level == "error"))
                if result:
                    success = True
                    service.log_notification(
                        self.db,
                        "alert",
                        "success",
                        data={"title": title, "level": level}
                    )
                else:
                    service.log_notification(
                        self.db,
                        "alert",
                        "failed",
                        error_message="发送失败",
                        data={"title": title, "level": level}
                    )
        
        return success
    
    def send_hourly_report(self, report_data: Dict[str, Any]) -> bool:
        """发送每小时进度报告"""
        channels = self.get_enabled_channels()
        if not channels:
            return False
        
        success = False
        for channel in channels:
            if channel.channel_type == "feishu":
                service = FeishuNotificationService(channel.webhook_url)
                
                # 构建富文本内容
                content = [
                    [{"tag": "text", "text": f"📊 闲鱼机器人进度报告\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"}],
                    [{"tag": "text", "text": "总体进度："}],
                    [{"tag": "text", "text": f"{report_data.get('progress', 0)}%", "tag_style": "bold"}],
                    [{"tag": "text", "text": f"\n\n今日收入：¥{report_data.get('revenue', 0)}"}],
                    [{"tag": "text", "text": f"\n待发货订单：{report_data.get('pending_orders', 0)}"}],
                    [{"tag": "text", "text": f"\n在线账号：{report_data.get('active_accounts', 0)}"}],
                ]
                
                result = service.send_post("📊 闲鱼机器人进度报告", content)
                if result:
                    success = True
                    service.log_notification(
                        self.db,
                        "hourly_report",
                        "success",
                        data=report_data
                    )
                else:
                    service.log_notification(
                        self.db,
                        "hourly_report",
                        "failed",
                        error_message="发送失败",
                        data=report_data
                    )
        
        return success


def init_feishu_webhook(db: Session, webhook_url: str) -> NotificationChannel:
    """初始化飞书 Webhook"""
    # 检查是否已存在
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.channel_type == "feishu"
    ).first()
    
    if channel:
        channel.webhook_url = webhook_url
        channel.enabled = True
        db.commit()
        logger.info("✅ 更新飞书 Webhook")
    else:
        channel = NotificationChannel(
            name="飞书通知",
            channel_type="feishu",
            webhook_url=webhook_url,
            enabled=True
        )
        db.add(channel)
        db.commit()
        logger.info("✅ 创建飞书 Webhook")
    
    return channel
