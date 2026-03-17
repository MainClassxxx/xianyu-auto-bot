"""
闲鱼扫码登录服务 - 增强版
支持浏览器自动登录、二维码扫描、Cookie 持久化
"""
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import json
import os
from pathlib import Path
from datetime import datetime, timedelta


class XianyuLoginService:
    """闲鱼扫码登录服务 - 增强版"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.login_sessions: Dict[str, Dict[str, Any]] = {}
        self.cookie_dir = Path(".cookies")
        self.cookie_dir.mkdir(exist_ok=True)
    
    async def init_browser(self, headless: bool = False):
        """初始化浏览器"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            logger.info("✅ 浏览器已初始化")
    
    async def create_login_session(self, session_id: str, headless: bool = False) -> Dict[str, Any]:
        """创建登录会话"""
        await self.init_browser(headless)
        
        # 创建新上下文和页面
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )
        
        page = await context.new_page()
        
        # 访问闲鱼登录页
        login_url = "https://m.goofish.com/"
        logger.info(f"📱 访问登录页：{login_url}")
        await page.goto(login_url, wait_until="networkidle", timeout=30000)
        
        # 保存会话
        self.login_sessions[session_id] = {
            "context": context,
            "page": page,
            "status": "waiting",
            "cookie": None,
            "user_info": None,
            "created_at": datetime.now(),
            "last_check": datetime.now()
        }
        
        logger.info(f"✅ 创建登录会话：{session_id}")
        return {
            "session_id": session_id,
            "login_url": login_url,
            "status": "waiting",
            "message": "请在浏览器中打开链接并扫码登录"
        }
    
    async def check_login_status(self, session_id: str) -> Dict[str, Any]:
        """检查登录状态"""
        if session_id not in self.login_sessions:
            return {"status": "not_found", "message": "会话不存在"}
        
        session = self.login_sessions[session_id]
        page = session["page"]
        
        try:
            # 防止检查过于频繁
            now = datetime.now()
            if (now - session["last_check"]).total_seconds() < 2:
                return {"status": "checking", "message": "检查中..."}
            
            session["last_check"] = now
            
            # 检查是否已登录
            is_logged_in = await self._check_if_logged_in(page)
            
            if is_logged_in:
                # 等待页面稳定
                await asyncio.sleep(2)
                
                # 获取所有 Cookie
                cookies = await page.context.cookies()
                
                if not cookies:
                    return {"status": "waiting", "message": "登录检测中..."}
                
                # 筛选关键 Cookie
                important_cookies = self._filter_important_cookies(cookies)
                cookie_str = self._cookies_to_string(important_cookies)
                
                # 获取用户信息
                user_info = await self._get_user_info(page)
                
                # 保存 Cookie 到文件
                account_id = user_info.get('userId', session_id)
                await self._save_cookie(account_id, cookie_str, important_cookies)
                
                # 更新会话
                session["status"] = "logged_in"
                session["cookie"] = cookie_str
                session["user_info"] = user_info
                
                logger.info(f"✅ 登录成功！用户：{user_info.get('nick', 'Unknown')}")
                
                return {
                    "status": "logged_in",
                    "cookie": cookie_str,
                    "user_info": user_info,
                    "message": "登录成功，Cookie 已保存"
                }
            else:
                return {"status": "waiting", "message": "等待扫码登录"}
                
        except Exception as e:
            logger.error(f"❌ 检查登录状态失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
    
    async def _check_if_logged_in(self, page: Page) -> bool:
        """检查是否已登录"""
        try:
            current_url = page.url
            
            # 检查 URL
            if any(k in current_url.lower() for k in ["login", "signin", "auth"]):
                return False
            
            # 检查 Cookie
            cookies = await page.context.cookies()
            login_cookies = [
                c for c in cookies 
                if any(name in c.get('name', '').lower() for name in ['_tb_token_', 'cookie2', 'sgcookie', '_l_g_'])
            ]
            
            if login_cookies:
                logger.info(f"✅ 检测到 {len(login_cookies)} 个登录 Cookie")
                return True
            
            # 检查页面元素
            selectors = [
                ".avatar", ".user-name", ".nickname", 
                "[data-testid='user-avatar']", ".my-page"
            ]
            
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=1000)
                    if element:
                        logger.info(f"✅ 找到登录标识：{selector}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 检查登录状态错误：{e}")
            return False
    
    def _filter_important_cookies(self, cookies: list) -> list:
        """筛选重要的 Cookie"""
        important_names = [
            '_tb_token_', 'cookie2', 'sgcookie', '_l_g_',
            'cna', 'tracknick', 'lid', 'uc0', 'uc1',
            'existshop', 'cn3lite', 'thw', 'l', 't'
        ]
        
        return [c for c in cookies if any(name in c.get('name', '').lower() for name in important_names)]
    
    def _cookies_to_string(self, cookies: list) -> str:
        """将 Cookie 列表转换为字符串"""
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    
    async def _get_user_info(self, page: Page) -> Dict[str, Any]:
        """获取用户信息"""
        try:
            user_info = await page.evaluate("""() => {
                return {
                    nick: document.querySelector('.user-name')?.textContent || 
                          document.querySelector('.nickname')?.textContent || 
                          document.querySelector('.avatar')?.alt || 'Unknown',
                    userId: window.userId || window.user?.id || '',
                    avatar: document.querySelector('.avatar-img')?.src || 
                            document.querySelector('.avatar')?.src || ''
                };
            }""")
            return user_info
        except Exception as e:
            logger.error(f"获取用户信息失败：{e}")
            return {"nick": "Unknown", "userId": "", "avatar": ""}
    
    async def _save_cookie(self, account_id: str, cookie_str: str, cookies: list):
        """保存 Cookie 到文件"""
        try:
            cookie_file = self.cookie_dir / f"{account_id}.json"
            
            cookie_data = {
                "account_id": account_id,
                "cookie": cookie_str,
                "cookies": cookies,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cookie 已保存到：{cookie_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存 Cookie 失败：{e}")
    
    @classmethod
    def load_cookie(cls, account_id: str) -> Optional[Dict[str, Any]]:
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
                logger.warning(f"⚠️ Cookie 已过期：{account_id}")
                cookie_file.unlink()
                return None
            
            logger.info(f"✅ 加载 Cookie：{account_id}")
            return cookie_data
            
        except Exception as e:
            logger.error(f"❌ 加载 Cookie 失败：{e}")
            return None
    
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
xianyu_login_service = XianyuLoginService()
