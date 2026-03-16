#!/usr/bin/env python3
"""
闲鱼登录流程测试脚本
测试完整的扫码登录流程
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.xianyu_oauth import xianyu_oauth

async def test_login_flow():
    """测试登录流程"""
    print("=" * 60)
    print("🔑 闲鱼登录流程测试")
    print("=" * 60)
    
    session_id = "test_session_001"
    
    try:
        # 1. 创建登录会话
        print("\n1️⃣ 创建登录会话...")
        login_url = await xianyu_oauth.create_login_session(session_id, headless=False)
        print(f"✅ 登录 URL: {login_url}")
        print("📱 请使用浏览器打开 URL 并登录")
        
        # 2. 轮询检查登录状态
        print("\n2️⃣ 开始检查登录状态（每 3 秒检查一次）...")
        max_attempts = 20  # 最多检查 60 秒
        
        for i in range(max_attempts):
            await asyncio.sleep(3)
            
            result = await xianyu_oauth.check_login_status(session_id)
            status = result.get('status')
            
            print(f"   第 {i+1} 次检查 - 状态：{status}")
            
            if status == 'logged_in':
                print("\n✅ 登录成功！")
                print(f"   用户：{result.get('user_info', {}).get('nick', 'Unknown')}")
                print(f"   Cookie 长度：{len(result.get('cookie', ''))} 字符")
                
                # 显示 Cookie 前 100 个字符（脱敏）
                cookie = result.get('cookie', '')
                if cookie:
                    print(f"   Cookie 预览：{cookie[:100]}...")
                
                break
            elif status == 'error':
                print(f"\n❌ 登录失败：{result.get('message')}")
                break
        
        else:
            print("\n⏰ 检查超时，仍未检测到登录")
        
        # 3. 关闭会话
        print("\n3️⃣ 关闭登录会话...")
        await xianyu_oauth.close_session(session_id)
        print("✅ 会话已关闭")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        print("\n4️⃣ 清理资源...")
        await xianyu_oauth.close_all()
        print("✅ 所有资源已清理")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_login_flow())
