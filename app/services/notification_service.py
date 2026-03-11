"""
飞书通知服务
"""
import requests
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.models import NotificationChannel

class FeishuNotificationService:
    """飞书通知服务"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
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
        
        return self._send(payload)
    
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
        return self._send(payload)
    
    def send_card(self, card: Dict[str, Any]) -> bool:
        """发送交互式卡片"""
        payload = {
            "msg_type": "interactive",
            "card": card
        }
        return self._send(payload)
    
    def _send(self, payload: Dict[str, Any]) -> bool:
        """发送消息"""
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("StatusCode") == 0 or result.get("code") == 0:
                    logger.info("✅ 飞书消息发送成功")
                    return True
                else:
                    logger.error(f"❌ 飞书消息发送失败：{result}")
                    return False
            else:
                logger.error(f"❌ 飞书消息发送失败：{response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 飞书消息发送异常：{e}")
            return False


class NotificationService:
    """统一通知服务"""
    
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
                
                if service.send_text(content):
                    success = True
        
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
                
                if service.send_text(content):
                    success = True
        
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
                
                if service.send_text(content, at_all=(level == "error")):
                    success = True
        
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
                
                if service.send_post("📊 闲鱼机器人进度报告", content):
                    success = True
        
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
