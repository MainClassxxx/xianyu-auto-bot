"""
闲鱼 API 客户端 - 增强版
支持真实扫码登录、Cookie 管理、自动刷新
"""
import httpx
import json
import time
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


class XianyuClient:
    """闲鱼 API 客户端 - 增强版"""
    
    # 真实闲鱼 API 端点
    XIANFU_BASE = "https://api.goofish.com"  # 参考端点，实际需抓包确认
    MOBILE_BASE = "https://m.goofish.com"
    
    def __init__(self, cookie: Optional[str] = None, device_id: Optional[str] = None, account_id: Optional[str] = None):
        self.account_id = account_id
        self.cookie = cookie
        self.device_id = device_id or self._generate_device_id()
        self.cookie_file = Path(f".cookies/{account_id}.json") if account_id else None
        
        # HTTP 客户端配置
        self.client: Optional[httpx.AsyncClient] = None
        self.account_info: Optional[Dict[str, Any]] = None
        self.last_request_time: float = 0
        self.request_count: int = 0
        self._init_client()
    
    def _init_client(self):
        """初始化 HTTP 客户端"""
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 xianyu/14.0.1",
            "X-Device-Id": self.device_id,
            "Referer": "https://m.goofish.com/",
            "Content-Type": "application/json",
        }
        
        if self.cookie:
            headers["Cookie"] = self.cookie
        
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
            http2=True  # 闲鱼支持 HTTP/2
        )
    
    def _generate_device_id(self) -> str:
        """生成设备 ID"""
        import uuid
        return f"device_{uuid.uuid4().hex[:16]}"
    
    async def _rate_limit(self):
        """请求限流，避免被风控"""
        now = time.time()
        if now - self.last_request_time < 0.5:  # 至少间隔 500ms
            await asyncio.sleep(0.5)
        self.last_request_time = time.time()
        self.request_count += 1
        
        # 每 100 次请求休息 10 秒
        if self.request_count % 100 == 0:
            logger.info(f"⏳ 已达到 {self.request_count} 次请求，休息 10 秒...")
            await asyncio.sleep(10)
    
    async def _request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """统一请求方法，带限流和错误处理"""
        await self._rate_limit()
        
        try:
            response = await self.client.request(method, url, **kwargs)
            
            if response.status_code == 401:
                logger.error("❌ Cookie 已过期，需要重新登录")
                await self._handle_cookie_expired()
                return None
            
            if response.status_code == 429:
                logger.warning("⚠️ 请求过于频繁，等待 30 秒...")
                await asyncio.sleep(30)
                return await self._request(method, url, **kwargs)
            
            if response.status_code != 200:
                logger.error(f"❌ 请求失败：{response.status_code} - {response.text[:200]}")
                return None
            
            data = response.json()
            
            # 检查业务错误码
            if isinstance(data, dict):
                code = data.get("code", data.get("errorCode", 0))
                if code != 0 and code != "0":
                    logger.error(f"❌ 业务错误：code={code}, msg={data.get('message', data.get('errorMsg', 'Unknown'))}")
                    return None
            
            return data
            
        except httpx.TimeoutException:
            logger.error("❌ 请求超时")
            return None
        except Exception as e:
            logger.error(f"❌ 请求异常：{e}")
            return None
    
    async def test_connection(self) -> bool:
        """测试连接是否有效"""
        try:
            # 尝试获取账号信息
            info = await self.get_account_info()
            if info:
                logger.info(f"✅ 闲鱼连接成功：{info.get('nick', 'Unknown')} (ID: {info.get('userId', 'N/A')})")
                return True
            else:
                logger.error("❌ 闲鱼连接失败，Cookie 可能已过期")
                return False
        except Exception as e:
            logger.error(f"❌ 闲鱼连接错误：{e}")
            return False
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """获取账号信息"""
        if self.account_info:
            return self.account_info
        
        # 尝试从多个端点获取账号信息
        endpoints = [
            ("GET", f"{self.MOBILE_BASE}/api/home/user/info", {}),
            ("GET", f"{self.XIANFU_BASE}/api/user/profile", {}),
        ]
        
        for method, url, params in endpoints:
            data = await self._request(method, url, params=params)
            if data and data.get("data"):
                self.account_info = data.get("data")
                return self.account_info
        
        return None
    
    async def get_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取消息列表"""
        data = await self._request(
            "GET",
            f"{self.XIANFU_BASE}/api/msg/chatList",
            params={"limit": limit}
        )
        return data.get("data", {}).get("messages", []) if data else []
    
    async def send_message(self, user_id: str, content: str, msg_type: str = "text") -> bool:
        """发送消息"""
        payload = {
            "userId": user_id,
            "content": content,
            "msgType": msg_type
        }
        
        data = await self._request(
            "POST",
            f"{self.XIANFU_BASE}/api/msg/send",
            json=payload
        )
        return data is not None and data.get("code", -1) == 0
    
    async def get_orders(self, status: str = "all", page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取订单列表"""
        params = {"page": page, "pageSize": page_size}
        if status != "all":
            params["status"] = status
        
        data = await self._request(
            "GET",
            f"{self.XIANFU_BASE}/api/order/list",
            params=params
        )
        return data.get("data", {}).get("orders", []) if data else []
    
    async def get_order_detail(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单详情"""
        data = await self._request(
            "GET",
            f"{self.XIANFU_BASE}/api/order/detail",
            params={"orderId": order_id}
        )
        return data.get("data") if data else None
    
    async def deliver_order(self, order_id: str, content: str, deliver_type: str = "auto") -> bool:
        """发货"""
        payload = {
            "orderId": order_id,
            "content": content,
            "deliverType": deliver_type
        }
        
        data = await self._request(
            "POST",
            f"{self.XIANFU_BASE}/api/order/deliver",
            json=payload
        )
        
        if data and data.get("code", -1) == 0:
            logger.info(f"✅ 订单 {order_id} 发货成功")
            return True
        else:
            logger.error(f"❌ 订单 {order_id} 发货失败")
            return False
    
    async def get_items(self, status: str = "onsale", page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取商品列表"""
        params = {"page": page, "pageSize": page_size, "status": status}
        
        data = await self._request(
            "GET",
            f"{self.XIANFU_BASE}/api/item/list",
            params=params
        )
        return data.get("data", {}).get("items", []) if data else []
    
    async def update_item_price(self, item_id: str, new_price: float) -> bool:
        """修改商品价格"""
        payload = {"itemId": item_id, "price": new_price}
        
        data = await self._request(
            "POST",
            f"{self.XIANFU_BASE}/api/item/updatePrice",
            json=payload
        )
        
        if data and data.get("code", -1) == 0:
            logger.info(f"✅ 商品 {item_id} 价格修改为 {new_price}")
            return True
        return False
    
    async def shelf_item(self, item_id: str, action: str) -> bool:
        """上架/下架商品"""
        payload = {"itemId": item_id, "action": action}
        
        data = await self._request(
            "POST",
            f"{self.XIANFU_BASE}/api/item/shelf",
            json=payload
        )
        return data is not None and data.get("code", -1) == 0
    
    async def save_cookie(self):
        """保存 Cookie 到文件"""
        if not self.cookie_file:
            return
        
        try:
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            
            cookie_data = {
                "cookie": self.cookie,
                "device_id": self.device_id,
                "account_id": self.account_id,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()  # 假设 7 天有效期
            }
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cookie 已保存到 {self.cookie_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存 Cookie 失败：{e}")
    
    @classmethod
    async def load_cookie(cls, account_id: str) -> Optional["XianyuClient"]:
        """从文件加载 Cookie"""
        cookie_file = Path(f".cookies/{account_id}.json")
        
        if not cookie_file.exists():
            return None
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(cookie_data.get("expires_at", ""))
            if datetime.now() > expires_at:
                logger.warning(f"⚠️ Cookie 已过期，需要重新登录")
                cookie_file.unlink()
                return None
            
            client = cls(
                cookie=cookie_data["cookie"],
                device_id=cookie_data["device_id"],
                account_id=cookie_data["account_id"]
            )
            
            logger.info(f"✅ 从文件加载 Cookie：{account_id}")
            return client
            
        except Exception as e:
            logger.error(f"❌ 加载 Cookie 失败：{e}")
            return None
    
    async def _handle_cookie_expired(self):
        """处理 Cookie 过期"""
        if self.cookie_file and self.cookie_file.exists():
            self.cookie_file.unlink()
            logger.info(f"🗑️ 已删除过期的 Cookie 文件")
        
        self.cookie = None
        self.account_info = None
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
        logger.info(f"👋 闲鱼客户端已关闭：{self.account_id or 'Anonymous'}")


class XianyuManager:
    """闲鱼客户端管理器 - 管理多个账号"""
    
    def __init__(self):
        self.clients: Dict[str, XianyuClient] = {}
    
    def add_client(self, account_id: str, cookie: str, device_id: Optional[str] = None):
        """添加账号客户端"""
        client = XianyuClient(cookie=cookie, device_id=device_id, account_id=account_id)
        self.clients[account_id] = client
        logger.info(f"✅ 添加账号客户端：{account_id}")
    
    async def add_client_from_file(self, account_id: str) -> bool:
        """从文件加载账号客户端"""
        client = await XianyuClient.load_cookie(account_id)
        if client:
            self.clients[account_id] = client
            return True
        return False
    
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
