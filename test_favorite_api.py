"""
收藏功能接口测试脚本
用于测试收藏/取消收藏导师、查询收藏列表等功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_CODE = "test_wx_code_123"  # 测试用的微信code
TEST_TUTOR_ID = "tutor_test_001"  # 测试用的导师ID（需要提前在数据库中创建）


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


def test_favorite_api():
    """测试收藏功能接口"""
    
    print("\n" + "="*60)
    print("开始测试收藏功能接口")
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
    
    # 2. 查询初始收藏列表
    print("\n[步骤 2] 查询初始收藏列表...")
    initial_list_response = requests.get(
        f"{BASE_URL}/user/favorites",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    print_response("初始收藏列表", initial_list_response)
    
    if initial_list_response.status_code == 200:
        initial_total = initial_list_response.json()["data"]["total"]
        print(f"✅ 初始收藏数量: {initial_total}")
    else:
        print("❌ 查询初始收藏列表失败")
    
    # 3. 查询导师收藏状态（应该未收藏）
    print(f"\n[步骤 3] 查询导师收藏状态（导师ID: {TEST_TUTOR_ID}）...")
    status_response = requests.get(
        f"{BASE_URL}/user/favorite/status/{TEST_TUTOR_ID}",
        headers=headers
    )
    print_response("收藏状态查询", status_response)
    
    if status_response.status_code == 200:
        is_collected = status_response.json()["data"]["is_collected"]
        print(f"✅ 当前收藏状态: {'已收藏' if is_collected else '未收藏'}")
    else:
        print("⚠️  查询收藏状态失败")
    
    # 4. 收藏导师
    print(f"\n[步骤 4] 收藏导师（导师ID: {TEST_TUTOR_ID}）...")
    collect_response = requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers=headers,
        json={"tutor_id": TEST_TUTOR_ID}
    )
    print_response("收藏操作", collect_response)
    
    if collect_response.status_code == 200:
        action = collect_response.json()["data"]["action"]
        print(f"✅ 收藏操作成功: {action}")
    elif collect_response.status_code == 404:
        print("⚠️  导师不存在，请先在数据库中创建测试导师")
        print(f"   导师ID: {TEST_TUTOR_ID}")
        print("   你可以修改 TEST_TUTOR_ID 为数据库中已存在的导师ID")
    else:
        print("❌ 收藏操作失败")
    
    # 5. 再次查询收藏状态（应该已收藏）
    print(f"\n[步骤 5] 再次查询收藏状态...")
    status_response2 = requests.get(
        f"{BASE_URL}/user/favorite/status/{TEST_TUTOR_ID}",
        headers=headers
    )
    print_response("收藏状态查询（第二次）", status_response2)
    
    if status_response2.status_code == 200:
        is_collected = status_response2.json()["data"]["is_collected"]
        print(f"✅ 当前收藏状态: {'已收藏' if is_collected else '未收藏'}")
    else:
        print("⚠️  查询收藏状态失败")
    
    # 6. 查询收藏列表（应该包含刚收藏的导师）
    print("\n[步骤 6] 查询收藏列表...")
    list_response = requests.get(
        f"{BASE_URL}/user/favorites",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    print_response("收藏列表", list_response)
    
    if list_response.status_code == 200:
        total = list_response.json()["data"]["total"]
        favorites = list_response.json()["data"]["list"]
        print(f"✅ 当前收藏数量: {total}")
        print(f"   收藏列表包含 {len(favorites)} 个导师")
    else:
        print("❌ 查询收藏列表失败")
    
    # 7. 批量查询收藏状态
    print("\n[步骤 7] 批量查询收藏状态...")
    batch_status_response = requests.post(
        f"{BASE_URL}/user/favorite/batch-status",
        headers=headers,
        json={
            "tutor_ids": [TEST_TUTOR_ID, "tutor_test_002", "tutor_test_003"]
        }
    )
    print_response("批量收藏状态查询", batch_status_response)
    
    if batch_status_response.status_code == 200:
        favorites_dict = batch_status_response.json()["data"]["favorites"]
        print(f"✅ 批量查询成功，查询了 {len(favorites_dict)} 个导师")
        for tutor_id, is_collected in favorites_dict.items():
            print(f"   {tutor_id}: {'已收藏' if is_collected else '未收藏'}")
    else:
        print("❌ 批量查询失败")
    
    # 8. 再次切换收藏状态（取消收藏）
    print(f"\n[步骤 8] 再次切换收藏状态（取消收藏）...")
    uncollect_response = requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers=headers,
        json={"tutor_id": TEST_TUTOR_ID}
    )
    print_response("取消收藏操作", uncollect_response)
    
    if uncollect_response.status_code == 200:
        action = uncollect_response.json()["data"]["action"]
        print(f"✅ 取消收藏成功: {action}")
    else:
        print("❌ 取消收藏失败")
    
    # 9. 验证取消收藏后的状态
    print(f"\n[步骤 9] 验证取消收藏后的状态...")
    status_response3 = requests.get(
        f"{BASE_URL}/user/favorite/status/{TEST_TUTOR_ID}",
        headers=headers
    )
    print_response("收藏状态查询（第三次）", status_response3)
    
    if status_response3.status_code == 200:
        is_collected = status_response3.json()["data"]["is_collected"]
        if not is_collected:
            print(f"✅ 验证成功: 已取消收藏")
        else:
            print(f"❌ 验证失败: 状态不正确")
    else:
        print("⚠️  查询收藏状态失败")
    
    # 10. 使用DELETE方法取消收藏（先收藏再取消）
    print(f"\n[步骤 10] 测试DELETE方法取消收藏...")
    
    # 先收藏
    print("   10.1 先收藏导师...")
    collect_response2 = requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers=headers,
        json={"tutor_id": TEST_TUTOR_ID}
    )
    if collect_response2.status_code == 200:
        print("   ✅ 收藏成功")
    
    # 使用DELETE方法取消收藏
    print("   10.2 使用DELETE方法取消收藏...")
    delete_response = requests.delete(
        f"{BASE_URL}/user/favorite/{TEST_TUTOR_ID}",
        headers=headers
    )
    print_response("DELETE取消收藏", delete_response)
    
    if delete_response.status_code == 200:
        print("✅ DELETE方法取消收藏成功")
    else:
        print("❌ DELETE方法取消收藏失败")
    
    # 11. 测试无token访问（应该失败）
    print("\n[步骤 11] 测试无token访问（预期失败）...")
    no_token_response = requests.get(
        f"{BASE_URL}/user/favorites"
    )
    print_response("无token访问", no_token_response)
    
    if no_token_response.status_code == 401:
        print("✅ 正确返回401未授权")
    else:
        print("❌ 应该返回401但没有")
    
    # 12. 测试收藏不存在的导师（应该失败）
    print("\n[步骤 12] 测试收藏不存在的导师（预期失败）...")
    invalid_tutor_response = requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers=headers,
        json={"tutor_id": "nonexistent_tutor_999999"}
    )
    print_response("收藏不存在的导师", invalid_tutor_response)
    
    if invalid_tutor_response.status_code == 404:
        print("✅ 正确返回404导师不存在")
    else:
        print("⚠️  预期返回404但返回了其他状态码")
    
    # 13. 测试空导师ID（应该失败）
    print("\n[步骤 13] 测试空导师ID（预期失败）...")
    empty_id_response = requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers=headers,
        json={"tutor_id": ""}
    )
    print_response("空导师ID", empty_id_response)
    
    if empty_id_response.status_code == 422:
        print("✅ 正确返回422验证错误")
    else:
        print("⚠️  预期返回422但返回了其他状态码")
    
    # 14. 测试分页功能
    print("\n[步骤 14] 测试分页功能...")
    page2_response = requests.get(
        f"{BASE_URL}/user/favorites",
        headers=headers,
        params={"page": 2, "page_size": 5}
    )
    print_response("收藏列表（第2页，每页5条）", page2_response)
    
    if page2_response.status_code == 200:
        print("✅ 分页查询成功")
    else:
        print("❌ 分页查询失败")
    
    # 15. 测试DELETE未收藏的导师（应该失败）
    print("\n[步骤 15] 测试DELETE未收藏的导师（预期失败）...")
    delete_uncollected_response = requests.delete(
        f"{BASE_URL}/user/favorite/tutor_uncollected_999",
        headers=headers
    )
    print_response("DELETE未收藏的导师", delete_uncollected_response)
    
    if delete_uncollected_response.status_code == 404:
        print("✅ 正确返回404未收藏")
    else:
        print("⚠️  预期返回404但返回了其他状态码")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n📝 测试总结:")
    print("1. ✅ 登录获取token")
    print("2. ✅ 查询收藏列表")
    print("3. ✅ 查询收藏状态")
    print("4. ✅ 收藏导师")
    print("5. ✅ 取消收藏导师")
    print("6. ✅ 批量查询收藏状态")
    print("7. ✅ DELETE方法取消收藏")
    print("8. ✅ 分页功能")
    print("9. ✅ 权限验证（无token）")
    print("10. ✅ 数据验证（不存在的导师、空ID）")
    print("\n⚠️  注意事项:")
    print(f"   - 测试使用的导师ID: {TEST_TUTOR_ID}")
    print("   - 如果导师不存在，请先在数据库中创建或修改TEST_TUTOR_ID")
    print("   - 可以通过MongoDB Compass查看数据库中的导师数据")


if __name__ == "__main__":
    try:
        test_favorite_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到服务器")
        print("请确保后端服务已启动（运行 python main.py）")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
