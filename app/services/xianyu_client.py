"""
闲鱼 API 客户端
"""
import httpx
from typing import Optional, Dict, Any
from loguru import logger

class XianyuClient:
    """闲鱼 API 客户端"""
    
    def __init__(self, cookie: str, device_id: str = "device_001"):
        self.cookie = cookie
        self.device_id = device_id
        self.base_url = "https://goofish.com"
        self.client = httpx.AsyncClient(
            headers={
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30.0
        )
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """获取账号信息"""
        try:
            response = await self.client.get(f"{self.base_url}/api/account/info")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"获取账号信息失败：{e}")
        return None
    
    async def get_messages(self, limit: int = 20) -> list:
        """获取消息列表"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/messages",
                params={"limit": limit}
            )
            if response.status_code == 200:
                return response.json().get("messages", [])
        except Exception as e:
            logger.error(f"获取消息失败：{e}")
        return []
    
    async def send_message(self, user_id: str, content: str) -> bool:
        """发送消息"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/messages/send",
                json={"user_id": user_id, "content": content}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"发送消息失败：{e}")
        return False
    
    async def get_orders(self, status: str = "pending") -> list:
        """获取订单列表"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/orders",
                params={"status": status}
            )
            if response.status_code == 200:
                return response.json().get("orders", [])
        except Exception as e:
            logger.error(f"获取订单失败：{e}")
        return []
    
    async def deliver_order(self, order_id: str, content: str) -> bool:
        """发货"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/orders/deliver",
                json={"order_id": order_id, "content": content}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"发货失败：{e}")
        return False
    
    async def update_price(self, item_id: str, price: float) -> bool:
        """改价"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/items/update_price",
                json={"item_id": item_id, "price": price}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"改价失败：{e}")
        return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
