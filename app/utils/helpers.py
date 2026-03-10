"""
工具函数
"""
import os
from pathlib import Path
from loguru import logger

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent

def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    logger.debug(f"确保目录存在：{path}")

def load_env():
    """加载环境变量"""
    from dotenv import load_dotenv
    env_file = get_project_root() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"已加载环境变量：{env_file}")
    else:
        logger.warning(f"环境变量文件不存在：{env_file}")
