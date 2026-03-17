"""
基础测试 - 验证测试框架正常工作
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db, init_db
from app.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """数据库会话 fixture"""
    # 创建表
    from app.models import ModelBase
    ModelBase.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理测试数据
        from app.models import ModelBase
        ModelBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端 fixture"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestHealthCheck:
    """健康检查测试"""
    
    def test_root(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "闲鱼自动售货机器人"
        assert "version" in data
    
    def test_health(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestUser:
    """用户相关测试"""
    
    def test_create_user(self, db_session):
        """测试创建用户"""
        from app.models.user import User
        from datetime import datetime
        
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.created_at is not None


class TestAccount:
    """账号管理测试"""
    
    def test_create_account(self, db_session):
        """测试创建闲鱼账号"""
        from app.models import Account
        
        account = Account(
            name="测试账号",
            cookie="test_cookie=value",
            device_id="device_test_001",
            status="active"
        )
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        
        assert account.id is not None
        assert account.name == "测试账号"
        assert account.device_id == "device_test_001"
        assert account.status == "active"


class TestDeliveryRule:
    """自动发货规则测试"""
    
    def test_create_delivery_rule(self, db_session):
        """测试创建发货规则"""
        from app.models.auto_delivery import DeliveryRule
        
        rule = DeliveryRule(
            account_id=1,
            name="测试规则",
            keyword="测试商品",
            delivery_content="自动发货内容",
            delivery_type="text",
            stock=-1,
            enabled=True,
            priority=0
        )
        
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        
        assert rule.id is not None
        assert rule.name == "测试规则"
        assert rule.keyword == "测试商品"
        assert rule.stock == -1  # 无限库存
        assert rule.enabled is True


class TestNotificationChannel:
    """通知渠道测试"""
    
    def test_create_feishu_channel(self, db_session):
        """测试创建飞书通知渠道"""
        from app.models import NotificationChannel
        
        channel = NotificationChannel(
            name="飞书测试",
            channel_type="feishu",
            webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/test",
            enabled=True
        )
        
        db_session.add(channel)
        db_session.commit()
        db_session.refresh(channel)
        
        assert channel.id is not None
        assert channel.channel_type == "feishu"
        assert channel.enabled is True


# 异步测试示例
@pytest.mark.asyncio
async def test_async_example():
    """异步测试示例"""
    import asyncio
    await asyncio.sleep(0.1)
    assert True


# 参数化测试示例
@pytest.mark.parametrize("test_input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(test_input, expected):
    """参数化测试示例"""
    assert test_input ** 2 == expected


# 标记测试
@pytest.mark.slow
def test_slow_operation():
    """慢速测试标记"""
    import time
    time.sleep(0.5)
    assert True


@pytest.mark.api
def test_api_marker(client):
    """API 测试标记"""
    response = client.get("/health")
    assert response.status_code == 200
