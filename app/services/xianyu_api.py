"""
闲鱼 API 客户端 - 真实实现
基于 Cookie 的 HTTP 请求
"""
import httpx
import json
import time
from typing import Optional, Dict, Any, List
from loguru import logger
from datetime import datetime

class XianyuClient:
    """闲鱼 API 客户端"""
    
    def __init__(self, cookie: str, device_id: str = "device_001"):
        self.cookie = cookie
        self.device_id = device_id
        self.base_url = "https://goofish.com"
        
        # HTTP 客户端配置
        self.client = httpx.AsyncClient(
            headers={
                "Cookie": cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://goofish.com/",
                "Content-Type": "application/json"
            },
            timeout=30.0,
            follow_redirects=True
        )
        
        self.account_info = None
    
    async def test_connection(self) -> bool:
        """测试连接是否有效"""
        try:
            response = await self.client.get(f"{self.base_url}/api/home/user/info")
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.account_info = data.get("data", {})
                    logger.info(f"✅ 闲鱼连接成功：{self.account_info.get('nick', 'Unknown')}")
                    return True
            logger.error("❌ 闲鱼连接失败，Cookie 可能已过期")
            return False
        except Exception as e:
            logger.error(f"❌ 闲鱼连接错误：{e}")
            return False
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """获取账号信息"""
        if not self.account_info:
            await self.test_connection()
        return self.account_info
    
    async def get_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取消息列表"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/msg/chatList",
                params={"limit": limit}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("messages", [])
        except Exception as e:
            logger.error(f"获取消息失败：{e}")
        return []
    
    async def send_message(self, user_id: str, content: str) -> bool:
        """发送消息"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/msg/send",
                json={
                    "userId": user_id,
                    "content": content,
                    "msgType": "text"
                }
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"发送消息失败：{e}")
        return False
    
    async def get_orders(self, status: str = "all", page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取订单列表"""
        try:
            params = {
                "page": page,
                "pageSize": page_size
            }
            if status != "all":
                params["status"] = status
            
            response = await self.client.get(
                f"{self.base_url}/api/order/list",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("orders", [])
        except Exception as e:
            logger.error(f"获取订单失败：{e}")
        return []
    
    async def get_order_detail(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单详情"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/order/detail",
                params={"orderId": order_id}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data")
        except Exception as e:
            logger.error(f"获取订单详情失败：{e}")
        return None
    
    async def deliver_order(self, order_id: str, content: str) -> bool:
        """发货"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/order/deliver",
                json={
                    "orderId": order_id,
                    "content": content,
                    "deliverType": "auto"
                }
            )
            if response.status_code == 200:
                logger.info(f"✅ 订单 {order_id} 发货成功")
                return True
            else:
                logger.error(f"❌ 订单 {order_id} 发货失败：{response.text}")
                return False
        except Exception as e:
            logger.error(f"发货失败：{e}")
        return False
    
    async def get_items(self, status: str = "onsale", page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取商品列表"""
        try:
            params = {
                "page": page,
                "pageSize": page_size,
                "status": status
            }
            
            response = await self.client.get(
                f"{self.base_url}/api/item/list",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("items", [])
        except Exception as e:
            logger.error(f"获取商品列表失败：{e}")
        return []
    
    async def update_item_price(self, item_id: str, new_price: float) -> bool:
        """修改商品价格"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/item/updatePrice",
                json={
                    "itemId": item_id,
                    "price": new_price
                }
            )
            if response.status_code == 200:
                logger.info(f"✅ 商品 {item_id} 价格修改为 {new_price}")
                return True
            else:
                logger.error(f"❌ 商品 {item_id} 改价失败：{response.text}")
                return False
        except Exception as e:
            logger.error(f"改价失败：{e}")
        return False
    
    async def shelf_item(self, item_id: str, action: str) -> bool:
        """上架/下架商品"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/item/shelf",
                json={
                    "itemId": item_id,
                    "action": action  # "onshelf" or "offshelf"
                }
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"商品上下架失败：{e}")
        return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
        logger.info("👋 闲鱼客户端已关闭")


class XianyuManager:
    """闲鱼客户端管理器 - 管理多个账号"""
    
    def __init__(self):
        self.clients: Dict[str, XianyuClient] = {}
    
    def add_client(self, account_id: str, cookie: str, device_id: str):
        """添加账号客户端"""
        self.clients[account_id] = XianyuClient(cookie, device_id)
        logger.info(f"✅ 添加账号客户端：{account_id}")
    
    def remove_client(self, account_id: str):
        """移除账号客户端"""
        if account_id in self.clients:
            del self.clients[account_id]
            logger.info(f"✅ 移除账号客户端：{account_id}")
    
    def get_client(self, account_id: str) -> Optional[XianyuClient]:
        """获取账号客户端"""
        return self.clients.get(account_id)
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """测试所有账号连接"""
        results = {}
        for account_id, client in self.clients.items():
            results[account_id] = await client.test_connection()
        return results
    
    async def close_all(self):
        """关闭所有客户端"""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()


# 全局管理器实例
xianyu_manager = XianyuManager()
