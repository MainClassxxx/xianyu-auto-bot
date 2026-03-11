"""
集成测试脚本
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ 健康检查通过")

def test_root():
    """测试根路径"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "闲鱼自动售货机器人"
    print("✅ 根路径通过")

def test_auth_captcha():
    """测试验证码"""
    response = requests.post(f"{BASE_URL}/api/auth/captcha")
    assert response.status_code == 200
    data = response.json()
    assert "captcha_id" in data
    print("✅ 验证码 API 通过")

def test_stats_overview():
    """测试统计概览"""
    response = requests.get(f"{BASE_URL}/api/stats/overview")
    if response.status_code != 200:
        print(f"响应：{response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "total_accounts" in data
    assert "active_accounts" in data
    print(f"✅ 统计概览通过 - 总账号：{data['total_accounts']}, 活跃：{data['active_accounts']}")

def test_accounts_list():
    """测试账号列表"""
    response = requests.get(f"{BASE_URL}/api/accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ 账号列表通过 - 共 {len(data)} 个账号")

def test_items_list():
    """测试商品列表"""
    response = requests.get(f"{BASE_URL}/api/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ 商品列表通过 - 共 {len(data)} 个商品")

def test_orders_list():
    """测试订单列表"""
    response = requests.get(f"{BASE_URL}/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ 订单列表通过 - 共 {len(data)} 个订单")

def test_notifications_channels():
    """测试通知渠道"""
    response = requests.get(f"{BASE_URL}/api/notifications/channels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ 通知渠道通过 - 共 {len(data)} 个渠道")

def test_auto_delivery_rules():
    """测试自动发货规则"""
    response = requests.get(f"{BASE_URL}/api/auto-delivery/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ 自动发货规则通过 - 共 {len(data)} 个规则")

def run_all_tests():
    """运行所有测试"""
    print("\n🧪 开始集成测试...\n")
    
    tests = [
        test_health,
        test_root,
        test_auth_captcha,
        test_stats_overview,
        test_accounts_list,
        test_items_list,
        test_orders_list,
        test_notifications_channels,
        test_auto_delivery_rules,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失败：{e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    print(f"{'='*50}\n")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
