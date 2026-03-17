"""
配置管理模块 - 使用 pydantic-settings 进行配置验证
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, HttpUrl
from typing import Optional, List
from enum import Enum
import os


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = Field(
        default="sqlite:///./data/xianyu_bot.db",
        description="数据库连接 URL"
    )
    pool_size: int = Field(default=5, ge=1, le=20, description="连接池大小")
    max_overflow: int = Field(default=10, ge=0, le=20, description="最大溢出连接数")
    echo: bool = Field(default=False, description="是否打印 SQL 语句")
    
    @field_validator('url')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("数据库 URL 不能为空")
        if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
            raise ValueError("不支持的数据库类型")
        return v


class SecurityConfig(BaseSettings):
    """安全配置"""
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expiration_minutes: int = Field(default=1440, ge=1, description="JWT 过期时间 (分钟)")
    password_min_length: int = Field(default=8, ge=6, description="密码最小长度")
    max_login_attempts: int = Field(default=5, ge=3, description="最大登录尝试次数")
    lockout_duration_minutes: int = Field(default=30, ge=5, description="锁定持续时间")
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT 密钥长度至少 32 位")
        return v


class NotificationConfig(BaseSettings):
    """通知配置"""
    feishu_webhook: Optional[str] = Field(default=None, description="飞书 Webhook URL")
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram Bot Token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram Chat ID")
    wechat_work_webhook: Optional[str] = Field(default=None, description="企业微信 Webhook")
    dingtalk_webhook: Optional[str] = Field(default=None, description="钉钉 Webhook")
    bark_url: Optional[str] = Field(default=None, description="Bark 推送 URL")
    
    @field_validator('feishu_webhook', 'telegram_bot_token', mode='before')
    @classmethod
    def validate_webhook(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Webhook URL 必须以 http://或 https://开头")
        return v


class AutomationConfig(BaseSettings):
    """自动化配置"""
    auto_delivery_enabled: bool = Field(default=True, description="自动发货开关")
    auto_price_update_enabled: bool = Field(default=False, description="自动改价开关")
    auto_reply_enabled: bool = Field(default=True, description="自动回复开关")
    check_order_interval_seconds: int = Field(default=300, ge=60, description="订单检查间隔 (秒)")
    max_concurrent_deliveries: int = Field(default=5, ge=1, le=20, description="最大并发发货数")
    delivery_retry_times: int = Field(default=3, ge=0, le=5, description="发货重试次数")
    delivery_retry_delay_seconds: int = Field(default=60, ge=10, description="发货重试延迟")


class RateLimitConfig(BaseSettings):
    """限流配置"""
    enabled: bool = Field(default=True, description="限流开关")
    requests_per_minute: int = Field(default=60, ge=10, description="每分钟请求数限制")
    requests_per_hour: int = Field(default=1000, ge=100, description="每小时请求数限制")
    burst_size: int = Field(default=10, ge=1, description="突发请求大小")


class LogConfig(BaseSettings):
    """日志配置"""
    level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    file: str = Field(default="data/bot.log", description="日志文件路径")
    rotation: str = Field(default="10 MB", description="日志轮转大小")
    retention: str = Field(default="7 days", description="日志保留时间")
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="日志格式"
    )


class AppConfig(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # 应用配置
    app_name: str = Field(default="闲鱼自动售货机器人", description="应用名称")
    version: str = Field(default="3.0.0", description="版本号")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务地址")
    port: int = Field(default=8080, ge=1, le=65535, description="服务端口")
    workers: int = Field(default=1, ge=1, le=8, description="工作进程数")
    
    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    automation: AutomationConfig = Field(default_factory=AutomationConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    
    # 闲鱼配置
    xianyu_cookie: Optional[str] = Field(default=None, description="闲鱼 Cookie")
    xianyu_device_id: Optional[str] = Field(default=None, description="闲鱼设备 ID")
    
    # AI 配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI 模型")
    
    # OCR 配置
    baidu_ocr_api_key: Optional[str] = Field(default=None, description="百度 OCR API Key")
    baidu_ocr_secret: Optional[str] = Field(default=None, description="百度 OCR Secret")
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        if v not in ['development', 'testing', 'production']:
            raise ValueError("环境必须是 development, testing 或 production")
        return v
    
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.environment == 'development'
    
    def is_testing(self) -> bool:
        """是否测试环境"""
        return self.environment == 'testing'


# 全局配置实例
def get_config() -> AppConfig:
    """获取配置实例"""
    return AppConfig()


# 快捷访问
config = get_config()
