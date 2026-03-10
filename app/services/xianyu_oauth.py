"""
闲鱼 OAuth 登录服务
实现浏览器自动登录并获取 Cookie
"""
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page
import json
import os

class XianyuOAuthService:
    """闲鱼 OAuth 登录服务"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.login_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def init_browser(self, headless: bool = False):
        """初始化浏览器"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=headless)
            logger.info("✅ 浏览器已初始化")
    
    async def create_login_session(self, session_id: str) -> str:
        """创建登录会话，返回登录 URL"""
        await self.init_browser()
        
        # 创建新页面
        page = await self.browser.new_page()
        
        # 访问闲鱼登录页
        await page.goto("https://goofish.com/", wait_until="networkidle")
        
        # 保存会话
        self.login_sessions[session_id] = {
            "page": page,
            "status": "waiting",
            "cookie": None,
            "created_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"✅ 创建登录会话：{session_id}")
        return f"https://goofish.com/"
    
    async def check_login_status(self, session_id: str) -> Dict[str, Any]:
        """检查登录状态"""
        if session_id not in self.login_sessions:
            return {"status": "not_found", "message": "会话不存在"}
        
        session = self.login_sessions[session_id]
        page = session["page"]
        
        try:
            # 检查是否已登录（检查页面元素）
            is_logged_in = await self._check_if_logged_in(page)
            
            if is_logged_in:
                # 获取 Cookie
                cookies = await page.context.cookies()
                cookie_str = self._cookies_to_string(cookies)
                
                # 获取用户信息
                user_info = await self._get_user_info(page)
                
                # 更新会话
                session["status"] = "logged_in"
                session["cookie"] = cookie_str
                session["user_info"] = user_info
                
                logger.info(f"✅ 登录成功：{user_info.get('nick', 'Unknown')}")
                
                return {
                    "status": "logged_in",
                    "cookie": cookie_str,
                    "user_info": user_info
                }
            else:
                return {"status": "waiting", "message": "等待用户登录"}
                
        except Exception as e:
            logger.error(f"❌ 检查登录状态失败：{e}")
            return {"status": "error", "message": str(e)}
    
    async def _check_if_logged_in(self, page: Page) -> bool:
        """检查是否已登录"""
        try:
            # 检查是否存在用户头像或用户名元素
            # 这里需要根据闲鱼实际页面结构调整
            selectors = [
                ".user-avatar",
                ".user-name",
                ".nickname",
                "[data-testid='user-avatar']",
            ]
            
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        return True
                except:
                    continue
            
            # 或者检查 URL 是否变化
            current_url = page.url
            if "login" not in current_url.lower():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查登录状态错误：{e}")
            return False
    
    async def _get_user_info(self, page: Page) -> Dict[str, Any]:
        """获取用户信息"""
        try:
            # 从页面获取用户信息
            user_info = await page.evaluate("""() => {
                return {
                    nick: document.querySelector('.user-name')?.textContent || 'Unknown',
                    avatar: document.querySelector('.user-avatar')?.src || '',
                    userId: window.userId || ''
                };
            }""")
            
            return user_info
        except Exception as e:
            logger.error(f"获取用户信息失败：{e}")
            return {"nick": "Unknown", "avatar": "", "userId": ""}
    
    def _cookies_to_string(self, cookies: list) -> str:
        """将 Cookie 列表转换为字符串"""
        cookie_parts = []
        for cookie in cookies:
            cookie_parts.append(f"{cookie['name']}={cookie['value']}")
        return "; ".join(cookie_parts)
    
    async def close_session(self, session_id: str):
        """关闭登录会话"""
        if session_id in self.login_sessions:
            session = self.login_sessions[session_id]
            if session["page"]:
                await session["page"].close()
            del self.login_sessions[session_id]
            logger.info(f"✅ 关闭登录会话：{session_id}")
    
    async def close_all(self):
        """关闭所有会话和浏览器"""
        for session_id in list(self.login_sessions.keys()):
            await self.close_session(session_id)
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        logger.info("👋 浏览器已关闭")


# 全局服务实例
xianyu_oauth = XianyuOAuthService()
