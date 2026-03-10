"""
电影票截图检测服务
"""
import base64
from typing import Optional, Dict, Any
from loguru import logger
from PIL import Image
import io

class TicketDetectionService:
    """电影票截图检测服务"""
    
    def __init__(self):
        self.detection_history = []
    
    async def detect_from_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """从图片检测电影票信息"""
        try:
            # 1. OCR 识别文字
            text = await self._ocr_image(image_data)
            
            # 2. 提取电影票信息
            ticket_info = self._extract_ticket_info(text)
            
            if ticket_info:
                self.detection_history.append({
                    "time": "2024-03-10 14:00:00",
                    "ticket_info": ticket_info
                })
                logger.info(f"🎬 检测到电影票：{ticket_info.get('movie_name')}")
            
            return ticket_info
            
        except Exception as e:
            logger.error(f"电影票检测失败：{e}")
            return None
    
    async def _ocr_image(self, image_data: bytes) -> str:
        """OCR 识别图片文字"""
        # 这里可以集成百度 OCR、腾讯 OCR 或 Tesseract
        # 目前是模拟实现
        return """
        流浪地球 2
        万达影城 (CBD 店)
        2024-03-10 19:30
        8 号厅激光 IMAX
        8 排 9 座
        票价：¥45.0
        """
    
    def _extract_ticket_info(self, text: str) -> Optional[Dict[str, Any]]:
        """从 OCR 结果提取电影票信息"""
        lines = text.strip().split('\n')
        
        if len(lines) < 4:
            return None
        
        # 简单解析（实际项目需要更智能的解析）
        return {
            "movie_name": lines[0].strip() if len(lines) > 0 else "",
            "cinema_name": lines[1].strip() if len(lines) > 1 else "",
            "show_time": lines[2].strip() if len(lines) > 2 else "",
            "seat_info": lines[4].strip() if len(lines) > 4 else "",
            "price": self._extract_price(lines)
        }
    
    def _extract_price(self, lines: list) -> float:
        """提取票价"""
        for line in lines:
            if "票价" in line or "¥" in line:
                try:
                    # 提取数字
                    price_str = ''.join(c for c in line if c.isdigit() or c == '.')
                    return float(price_str) if price_str else 0.0
                except:
                    pass
        return 0.0
    
    def get_history(self, limit: int = 50) -> list:
        """获取检测历史"""
        return self.detection_history[-limit:]
