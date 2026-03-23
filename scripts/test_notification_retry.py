#!/usr/bin/env python3
"""
测试通知服务的重试机制
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.notification_service import FeishuNotificationService
from loguru import logger
import time

# 配置日志
logger.add("logs/test_notification_{time}.log", rotation="10 MB", retention="7 days")

def test_retry_mechanism():
    """测试重试机制"""
    print("\n🧪 测试通知服务重试机制\n")
    
    # 使用一个无效的 webhook URL 来测试重试
    invalid_webhook = "https://httpstat.us/503"  # 返回 503 错误
    
    service = FeishuNotificationService(
        webhook_url=invalid_webhook,
        max_retries=3,
        retry_delay=1  # 为了快速测试，设置为 1 秒
    )
    
    print("📤 发送测试消息（使用无效的 webhook URL）...")
    start_time = time.time()
    
    result = service.send_text("这是一条测试消息")
    
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 测试结果:")
    print(f"  - 发送结果：{'✅ 成功' if result else '❌ 失败'}")
    print(f"  - 耗时：{elapsed_time:.2f}秒")
    print(f"  - 预期：应该失败，耗时约 6 秒（1+2+3 秒的重试间隔）")
    
    if elapsed_time >= 5:
        print("\n✅ 重试机制工作正常！")
    else:
        print("\n⚠️ 重试机制可能未正常工作")
    
    return result

def test_valid_webhook():
    """测试有效的 webhook（如果有的话）"""
    print("\n\n🧪 测试有效 Webhook（可选）\n")
    
    # 这里可以填入真实的 webhook URL 进行测试
    webhook_url = input("请输入飞书 Webhook URL（留空跳过）: ").strip()
    
    if not webhook_url:
        print("⏭️  跳过测试")
        return
    
    service = FeishuNotificationService(
        webhook_url=webhook_url,
        max_retries=3,
        retry_delay=2
    )
    
    print("📤 发送测试消息...")
    result = service.send_text("🥫 易拉罐测试消息 - 验证重试机制已启用")
    
    print(f"\n📊 测试结果: {'✅ 成功' if result else '❌ 失败'}")

if __name__ == "__main__":
    print("=" * 60)
    print("🥫 闲鱼机器人 - 通知服务重试机制测试")
    print("=" * 60)
    
    # 测试重试机制
    test_retry_mechanism()
    
    # 可选：测试真实 webhook
    test_valid_webhook()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
