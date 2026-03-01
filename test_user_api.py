"""
用户信息接口测试脚本
用于测试用户信息查询和更新接口的功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_CODE = "test_wx_code_123"  # 测试用的微信code


def print_response(title: str, response: requests.Response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'='*60}\n")


def test_user_profile_api():
    """测试用户信息接口"""
    
    print("\n" + "="*60)
    print("开始测试用户信息管理接口")
    print("="*60)
    
    # 1. 登录获取token
    print("\n[步骤 1] 登录获取token...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"code": TEST_CODE}
    )
    print_response("登录响应", login_response)
    
    if login_response.status_code != 200:
        print("❌ 登录失败，测试终止")
        return
    
    token = login_response.json()["data"]["token"]
    user_id = login_response.json()["data"]["user"]["id"]
    print(f"✅ 登录成功，获得token和用户ID: {user_id}")
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 获取用户信息
    print("\n[步骤 2] 获取用户信息...")
    profile_response = requests.get(
        f"{BASE_URL}/user/profile",
        headers=headers
    )
    print_response("获取用户信息响应", profile_response)
    
    if profile_response.status_code == 200:
        print("✅ 获取用户信息成功")
    else:
        print("❌ 获取用户信息失败")
    
    # 3. 更新用户昵称
    print("\n[步骤 3] 更新用户昵称...")
    update_nickname_response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={
            "nickname": f"测试用户_{datetime.now().strftime('%H%M%S')}"
        }
    )
    print_response("更新昵称响应", update_nickname_response)
    
    if update_nickname_response.status_code == 200:
        print("✅ 更新昵称成功")
    else:
        print("❌ 更新昵称失败")
    
    # 4. 更新多个字段
    print("\n[步骤 4] 更新多个字段（昵称、院校、专业）...")
    update_multiple_response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={
            "nickname": "张三",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2024级"
        }
    )
    print_response("更新多个字段响应", update_multiple_response)
    
    if update_multiple_response.status_code == 200:
        updated_fields = update_multiple_response.json()["data"]["updated_fields"]
        print(f"✅ 更新成功，更新的字段: {', '.join(updated_fields)}")
    else:
        print("❌ 更新多个字段失败")
    
    # 5. 使用PATCH方法更新
    print("\n[步骤 5] 使用PATCH方法更新院校...")
    patch_response = requests.patch(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={
            "school": "北京大学"
        }
    )
    print_response("PATCH更新响应", patch_response)
    
    if patch_response.status_code == 200:
        print("✅ PATCH更新成功")
    else:
        print("❌ PATCH更新失败")
    
    # 6. 再次获取用户信息验证更新
    print("\n[步骤 6] 再次获取用户信息验证更新结果...")
    final_profile_response = requests.get(
        f"{BASE_URL}/user/profile",
        headers=headers
    )
    print_response("最终用户信息", final_profile_response)
    
    if final_profile_response.status_code == 200:
        print("✅ 验证成功")
    else:
        print("❌ 验证失败")
    
    # 7. 测试无token访问（应该失败）
    print("\n[步骤 7] 测试无token访问（预期失败）...")
    no_token_response = requests.get(
        f"{BASE_URL}/user/profile"
    )
    print_response("无token访问响应", no_token_response)
    
    if no_token_response.status_code == 401:
        print("✅ 正确返回401未授权")
    else:
        print("❌ 应该返回401但没有")
    
    # 8. 测试无效token（应该失败）
    print("\n[步骤 8] 测试无效token（预期失败）...")
    invalid_headers = {
        "Authorization": "Bearer invalid_token_12345",
        "Content-Type": "application/json"
    }
    invalid_token_response = requests.get(
        f"{BASE_URL}/user/profile",
        headers=invalid_headers
    )
    print_response("无效token访问响应", invalid_token_response)
    
    if invalid_token_response.status_code == 401:
        print("✅ 正确返回401未授权")
    else:
        print("❌ 应该返回401但没有")
    
    # 9. 测试数据验证（昵称过长）
    print("\n[步骤 9] 测试数据验证 - 昵称过长（预期失败）...")
    long_nickname_response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={
            "nickname": "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的昵称超过了50个字符的限制"
        }
    )
    print_response("昵称过长响应", long_nickname_response)
    
    if long_nickname_response.status_code == 422:
        print("✅ 正确返回422验证错误")
    else:
        print("⚠️  预期返回422但返回了其他状态码")
    
    # 10. 测试数据验证（无效的头像URL）
    print("\n[步骤 10] 测试数据验证 - 无效的头像URL（预期失败）...")
    invalid_avatar_response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={
            "avatar": "not_a_valid_url"
        }
    )
    print_response("无效头像URL响应", invalid_avatar_response)
    
    if invalid_avatar_response.status_code == 422:
        print("✅ 正确返回422验证错误")
    else:
        print("⚠️  预期返回422但返回了其他状态码")
    
    # 11. 测试空更新（不传任何字段）
    print("\n[步骤 11] 测试空更新（不传任何字段）...")
    empty_update_response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers,
        json={}
    )
    print_response("空更新响应", empty_update_response)
    
    if empty_update_response.status_code == 200:
        print("✅ 空更新成功处理")
    else:
        print("❌ 空更新处理失败")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    try:
        test_user_profile_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到服务器")
        print("请确保后端服务已启动（运行 python main.py）")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
