"""
闲鱼 OAuth 登录服务
实现浏览器自动登录并获取 Cookie
"""
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import json
import os

class XianyuOAuthService:
    """闲鱼 OAuth 登录服务"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.login_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def init_browser(self, headless: bool = False):
        """初始化浏览器"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info("✅ 浏览器已初始化")
    
    async def create_login_session(self, session_id: str, headless: bool = False) -> str:
        """创建登录会话，返回登录 URL"""
        await self.init_browser(headless)
        
        # 创建新上下文和页面
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # 访问闲鱼登录页
        login_url = "https://goofish.com/"
        await page.goto(login_url, wait_until="networkidle", timeout=30000)
        
        # 保存会话
        self.login_sessions[session_id] = {
            "context": context,
            "page": page,
            "status": "waiting",
            "cookie": None,
            "user_info": None,
            "created_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"✅ 创建登录会话：{session_id}, URL: {login_url}")
        return login_url
    
    async def check_login_status(self, session_id: str) -> Dict[str, Any]:
        """检查登录状态 - 增强版"""
        if session_id not in self.login_sessions:
            return {"status": "not_found", "message": "会话不存在"}
        
        session = self.login_sessions[session_id]
        page = session["page"]
        
        try:
            # 检查是否已登录
            is_logged_in = await self._check_if_logged_in(page)
            
            if is_logged_in:
                # 等待一下确保页面完全加载
                await asyncio.sleep(1)
                
                # 获取所有 Cookie
                cookies = await page.context.cookies()
                
                if not cookies:
                    logger.warning("⚠️ 检测到登录但 Cookie 为空")
                    return {"status": "waiting", "message": "登录检测中..."}
                
                # 转换为字符串
                cookie_str = self._cookies_to_string(cookies)
                
                # 记录 Cookie 信息（不记录具体值）
                cookie_names = [c['name'] for c in cookies]
                logger.info(f"✅ 获取到 {len(cookies)} 个 Cookie: {', '.join(cookie_names[:5])}...")
                
                # 获取用户信息
                user_info = await self._get_user_info(page)
                
                # 更新会话
                session["status"] = "logged_in"
                session["cookie"] = cookie_str
                session["user_info"] = user_info
                
                logger.info(f"✅ 登录成功！用户：{user_info.get('nick', 'Unknown')}")
                logger.info(f"📝 Cookie 长度：{len(cookie_str)} 字符")
                
                return {
                    "status": "logged_in",
                    "cookie": cookie_str,
                    "user_info": user_info
                }
            else:
                # 显示当前 URL 便于调试
                current_url = page.url
                if "waiting" not in session.get("last_log", ""):
                    logger.debug(f"⏳ 等待扫码中... 当前 URL: {current_url}")
                    session["last_log"] = "waiting"
                return {"status": "waiting", "message": "等待扫码登录"}
                
        except Exception as e:
            logger.error(f"❌ 检查登录状态失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
    
    async def _check_if_logged_in(self, page: Page) -> bool:
        """检查是否已登录 - 严格模式"""
        try:
            # 必须找到用户信息相关元素才能判断为已登录
            # 这些元素只有在真正登录成功后才会显示
            selectors = [
                ".avatar-img",           # 用户头像
                ".user-avatar",          # 用户头像备选
                ".user-name",            # 用户名
                ".nickname",             # 昵称
                ".account-info",         # 账号信息
                "[data-testid='user-avatar']",  # 测试 ID
                ".user-center",          # 用户中心
                ".my-page",              # 我的页面
            ]
            
            found_selector = None
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=1500)
                    if element:
                        found_selector = selector
                        logger.info(f"✅ 找到登录标识元素：{selector}")
                        break
                except:
                    continue
            
            if not found_selector:
                # 没有找到用户元素，检查 URL 和页面内容
                current_url = page.url
                page_content = await page.content()
                
                # 只有当 URL 包含用户相关路径且有用户信息时才判断为登录
                if "login" not in current_url.lower():
                    # 检查页面是否包含"退出登录"或"个人中心"等字样
                    if "退出" in page_content or "个人中心" in page_content or "我的" in page_content:
                        logger.info(f"✅ 通过页面内容判断已登录：{current_url}")
                        return True
                
                logger.debug(f"❌ 未检测到登录状态，当前 URL: {current_url}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查登录状态错误：{e}")
            return False
    
    async def _get_user_info(self, page: Page) -> Dict[str, Any]:
        """获取用户信息"""
        try:
            # 从页面获取用户信息
            user_info = await page.evaluate("""() => {
                return {
                    nick: document.querySelector('.user-name')?.textContent || 
                          document.querySelector('.nickname')?.textContent || 
                          'Unknown',
                    avatar: document.querySelector('.avatar-img')?.src || 
                            document.querySelector('.user-avatar')?.src || '',
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
            if session.get("page"):
                await session["page"].close()
            if session.get("context"):
                await session["context"].close()
            del self.login_sessions[session_id]
            logger.info(f"✅ 关闭登录会话：{session_id}")
    
    async def close_all(self):
        """关闭所有会话和浏览器"""
        for session_id in list(self.login_sessions.keys()):
            await self.close_session(session_id)
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        logger.info("👋 浏览器已关闭")


# 全局服务实例
xianyu_oauth = XianyuOAuthService()
