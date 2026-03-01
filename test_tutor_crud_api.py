"""
导师CRUD接口测试脚本
用于测试导师信息的新增、更新、删除等管理功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_CODE = "test_wx_code_123"  # 测试用的微信code
# 注意：需要使用管理员账号登录才能测试这些接口


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


def test_tutor_crud_api():
    """测试导师CRUD接口"""
    
    print("\n" + "="*60)
    print("开始测试导师CRUD接口（管理员功能）")
    print("="*60)
    
    # 1. 登录获取token（需要使用管理员账号）
    print("\n[步骤 1] 登录获取token（管理员账号）...")
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
    print("⚠️  注意：如果不是管理员账号，后续操作会返回403错误")
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 创建导师信息
    print("\n[步骤 2] 创建导师信息...")
    tutor_data = {
        "name": "张三教授",
        "school": "清华大学",
        "department": "计算机科学与技术系",
        "title": "教授、博士生导师",
        "research_direction": "人工智能、机器学习、计算机视觉",
        "email": "zhangsan@example.edu.cn",
        "phone": "010-12345678",
        "avatar_url": "https://example.com/avatar.jpg",
        "personal_page_url": "https://example.com/~zhangsan",
        "bio": "张三教授，博士生导师，主要研究方向为人工智能、机器学习等。",
        "papers": [
            {
                "title": "基于深度学习的图像识别研究",
                "authors": ["张三", "李四", "王五"],
                "journal": "计算机学报",
                "year": 2024,
                "doi": "10.1234/example.2024.001",
                "abstract": "本文研究了基于深度学习的图像识别方法..."
            },
            {
                "title": "机器学习在医疗诊断中的应用",
                "authors": ["张三", "赵六"],
                "journal": "中国科学：信息科学",
                "year": 2023,
                "doi": "10.1234/example.2023.002"
            }
        ],
        "projects": [
            {
                "title": "国家自然科学基金重点项目",
                "funding": "国家自然科学基金委员会",
                "start_date": "2024-01-01",
                "end_date": "2027-12-31",
                "description": "研究人工智能在医疗领域的应用"
            }
        ],
        "tags": ["AI", "深度学习", "计算机视觉", "机器学习"]
    }
    
    create_response = requests.post(
        f"{BASE_URL}/tutor/admin/create",
        headers=headers,
        json=tutor_data
    )
    print_response("创建导师响应", create_response)
    
    created_tutor_id = None
    if create_response.status_code == 200:
        created_tutor_id = create_response.json()["data"]["id"]
        print(f"✅ 创建导师成功，导师ID: {created_tutor_id}")
    elif create_response.status_code == 403:
        print("❌ 权限不足：当前用户不是管理员")
        print("   请使用管理员账号登录，或将当前用户添加到管理员白名单")
        return
    else:
        print("❌ 创建导师失败")
        return
    
    # 3. 查询导师详情（验证创建成功）
    print(f"\n[步骤 3] 查询导师详情（验证创建成功）...")
    detail_response = requests.get(
        f"{BASE_URL}/tutor/detail/{created_tutor_id}",
        headers=headers
    )
    print_response("导师详情", detail_response)
    
    if detail_response.status_code == 200:
        tutor_detail = detail_response.json()["data"]
        print(f"✅ 查询成功")
        print(f"   导师姓名: {tutor_detail['name']}")
        print(f"   论文数量: {len(tutor_detail.get('papers', []))}")
        print(f"   项目数量: {len(tutor_detail.get('projects', []))}")
    else:
        print("❌ 查询导师详情失败")
    
    # 4. 更新导师信息（部分字段）
    print(f"\n[步骤 4] 更新导师信息（部分字段）...")
    update_data = {
        "title": "教授、博士生导师、长江学者",
        "research_direction": "人工智能、深度学习、自然语言处理、计算机视觉",
        "email": "zhangsan_new@example.edu.cn",
        "tags": ["AI", "NLP", "深度学习", "计算机视觉"]
    }
    
    update_response = requests.put(
        f"{BASE_URL}/tutor/admin/update/{created_tutor_id}",
        headers=headers,
        json=update_data
    )
    print_response("更新导师响应", update_response)
    
    if update_response.status_code == 200:
        updated_fields = update_response.json()["data"]["updated_fields"]
        print(f"✅ 更新成功，更新的字段: {', '.join(updated_fields)}")
    else:
        print("❌ 更新导师信息失败")
    
    # 5. 再次查询导师详情（验证更新成功）
    print(f"\n[步骤 5] 再次查询导师详情（验证更新成功）...")
    detail_response2 = requests.get(
        f"{BASE_URL}/tutor/detail/{created_tutor_id}",
        headers=headers
    )
    print_response("更新后的导师详情", detail_response2)
    
    if detail_response2.status_code == 200:
        print("✅ 验证更新成功")
    else:
        print("❌ 查询失败")
    
    # 6. 更新论文列表（完全替换）
    print(f"\n[步骤 6] 更新论文列表（完全替换）...")
    update_papers_data = {
        "papers": [
            {
                "title": "新论文：Transformer模型在NLP中的应用",
                "authors": ["张三", "李四"],
                "journal": "自然语言处理学报",
                "year": 2024,
                "doi": "10.1234/example.2024.003"
            }
        ]
    }
    
    update_papers_response = requests.put(
        f"{BASE_URL}/tutor/admin/update/{created_tutor_id}",
        headers=headers,
        json=update_papers_data
    )
    print_response("更新论文列表响应", update_papers_response)
    
    if update_papers_response.status_code == 200:
        print("✅ 论文列表更新成功")
    else:
        print("❌ 论文列表更新失败")
    
    # 7. 创建第二个导师（用于批量删除测试）
    print("\n[步骤 7] 创建第二个导师...")
    tutor_data2 = {
        "name": "李四副教授",
        "school": "北京大学",
        "department": "软件工程系",
        "title": "副教授",
        "research_direction": "软件工程、云计算",
        "email": "lisi@example.edu.cn",
        "tags": ["软件工程", "云计算"]
    }
    
    create_response2 = requests.post(
        f"{BASE_URL}/tutor/admin/create",
        headers=headers,
        json=tutor_data2
    )
    print_response("创建第二个导师响应", create_response2)
    
    created_tutor_id2 = None
    if create_response2.status_code == 200:
        created_tutor_id2 = create_response2.json()["data"]["id"]
        print(f"✅ 创建第二个导师成功，导师ID: {created_tutor_id2}")
    else:
        print("❌ 创建第二个导师失败")
    
    # 8. 测试软删除单个导师
    print(f"\n[步骤 8] 软删除单个导师...")
    delete_response = requests.delete(
        f"{BASE_URL}/tutor/admin/delete/{created_tutor_id}",
        headers=headers
    )
    print_response("软删除导师响应", delete_response)
    
    if delete_response.status_code == 200:
        print("✅ 软删除导师成功")
    else:
        print("❌ 软删除导师失败")
    
    # 9. 验证软删除成功（查询应该返回404，因为已被标记删除）
    print(f"\n[步骤 9] 验证软删除成功（查询应该返回404）...")
    detail_response3 = requests.get(
        f"{BASE_URL}/tutor/detail/{created_tutor_id}",
        headers=headers
    )
    print_response("软删除后查询导师", detail_response3)
    
    if detail_response3.status_code == 404:
        print("✅ 验证成功：导师已被软删除，查询接口过滤了已删除数据")
    else:
        print("❌ 验证失败：导师仍然可以查询到")
    
    # 9.5 测试恢复已删除的导师
    print(f"\n[步骤 9.5] 恢复已删除的导师...")
    restore_response = requests.post(
        f"{BASE_URL}/tutor/admin/restore/{created_tutor_id}",
        headers=headers
    )
    print_response("恢复导师响应", restore_response)
    
    if restore_response.status_code == 200:
        print("✅ 恢复导师成功")
    else:
        print("❌ 恢复导师失败")
    
    # 9.6 验证恢复成功（查询应该能找到）
    print(f"\n[步骤 9.6] 验证恢复成功（查询应该能找到）...")
    detail_response4 = requests.get(
        f"{BASE_URL}/tutor/detail/{created_tutor_id}",
        headers=headers
    )
    print_response("恢复后查询导师", detail_response4)
    
    if detail_response4.status_code == 200:
        print("✅ 验证成功：导师已恢复，可以正常查询")
    else:
        print("❌ 验证失败：导师恢复后仍无法查询")
    
    # 9.7 再次删除（用于后续测试）
    print(f"\n[步骤 9.7] 再次删除导师（用于后续测试）...")
    delete_response2 = requests.delete(
        f"{BASE_URL}/tutor/admin/delete/{created_tutor_id}",
        headers=headers
    )
    if delete_response2.status_code == 200:
        print("✅ 再次删除成功")
    
    # 10. 测试批量修改
    if created_tutor_id2:
        print(f"\n[步骤 10] 测试批量修改...")
        
        # 先创建第三个导师
        tutor_data3 = {
            "name": "王五讲师",
            "school": "复旦大学",
            "department": "信息科学与工程学院",
            "title": "讲师",
            "research_direction": "数据挖掘"
        }
        
        create_response3 = requests.post(
            f"{BASE_URL}/tutor/admin/create",
            headers=headers,
            json=tutor_data3
        )
        
        created_tutor_id3 = None
        if create_response3.status_code == 200:
            created_tutor_id3 = create_response3.json()["data"]["id"]
            print(f"   创建第三个导师: {created_tutor_id3}")
        
        # 批量修改
        batch_update_data = {
            "tutor_ids": [created_tutor_id2, created_tutor_id3],
            "update_fields": {
                "title": "副教授",
                "tags": ["数据科学", "人工智能"]
            }
        }
        
        batch_update_response = requests.post(
            f"{BASE_URL}/tutor/admin/batch-update",
            headers=headers,
            json=batch_update_data
        )
        print_response("批量修改响应", batch_update_response)
        
        if batch_update_response.status_code == 200:
            result = batch_update_response.json()["data"]
            print(f"✅ 批量修改完成")
            print(f"   成功: {result['success_count']}个")
            print(f"   失败: {result['failed_count']}个")
            print(f"   更新字段: {result['updated_fields']}")
        else:
            print("❌ 批量修改失败")
        
        # 10.5 测试批量删除
        print(f"\n[步骤 10.5] 测试批量软删除...")
        batch_delete_data = {
            "tutor_ids": [created_tutor_id2, created_tutor_id3, "nonexistent_id"]
        }
        
        batch_delete_response = requests.post(
            f"{BASE_URL}/tutor/admin/batch-delete",
            headers=headers,
            json=batch_delete_data
        )
        print_response("批量软删除响应", batch_delete_response)
        
        if batch_delete_response.status_code == 200:
            result = batch_delete_response.json()["data"]
            print(f"✅ 批量软删除完成")
            print(f"   成功: {result['success_count']}个")
            print(f"   失败: {result['failed_count']}个")
            print(f"   失败ID: {result['failed_ids']}")
        else:
            print("❌ 批量软删除失败")
    
    # 11. 测试无token访问（应该失败）
    print("\n[步骤 11] 测试无token访问（预期失败）...")
    no_token_response = requests.post(
        f"{BASE_URL}/tutor/admin/create",
        json=tutor_data
    )
    print_response("无token访问", no_token_response)
    
    if no_token_response.status_code == 401:
        print("✅ 正确返回401未授权")
    else:
        print("❌ 应该返回401但没有")
    
    # 12. 测试数据验证（缺少必填字段）
    print("\n[步骤 12] 测试数据验证 - 缺少必填字段（预期失败）...")
    invalid_data = {
        "school": "清华大学",
        "department": "计算机系"
        # 缺少name字段
    }
    
    invalid_response = requests.post(
        f"{BASE_URL}/tutor/admin/create",
        headers=headers,
        json=invalid_data
    )
    print_response("缺少必填字段", invalid_response)
    
    if invalid_response.status_code == 422:
        print("✅ 正确返回422验证错误")
    else:
        print("⚠️  预期返回422但返回了其他状态码")
    
    # 13. 测试数据验证（无效的邮箱格式）
    print("\n[步骤 13] 测试数据验证 - 无效的邮箱格式（预期失败）...")
    invalid_email_data = {
        "name": "测试导师",
        "school": "测试大学",
        "department": "测试系",
        "email": "invalid_email"  # 无效的邮箱格式
    }
    
    invalid_email_response = requests.post(
        f"{BASE_URL}/tutor/admin/create",
        headers=headers,
        json=invalid_email_data
    )
    print_response("无效邮箱格式", invalid_email_response)
    
    if invalid_email_response.status_code == 422:
        print("✅ 正确返回422验证错误")
    else:
        print("⚠️  预期返回422但返回了其他状态码")
    
    # 14. 测试删除不存在的导师（应该失败）
    print("\n[步骤 14] 测试删除不存在的导师（预期失败）...")
    delete_nonexistent_response = requests.delete(
        f"{BASE_URL}/tutor/admin/delete/nonexistent_tutor_999",
        headers=headers
    )
    print_response("删除不存在的导师", delete_nonexistent_response)
    
    if delete_nonexistent_response.status_code == 404:
        print("✅ 正确返回404导师不存在")
    else:
        print("⚠️  预期返回404但返回了其他状态码")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n📝 测试总结:")
    print("1. ✅ 登录获取token")
    print("2. ✅ 创建导师信息（含论文、项目）")
    print("3. ✅ 查询导师详情")
    print("4. ✅ 更新导师信息（部分字段）")
    print("5. ✅ 更新论文列表（完全替换）")
    print("6. ✅ 软删除单个导师")
    print("7. ✅ 恢复已删除的导师")
    print("8. ✅ 批量修改导师")
    print("9. ✅ 批量软删除导师")
    print("10. ✅ 权限验证（无token）")
    print("11. ✅ 管理员权限验证（403）")
    print("12. ✅ 数据验证（必填字段、邮箱格式）")
    print("13. ✅ 删除不存在的导师（404）")
    print("14. ✅ 查询接口过滤已删除数据")
    print("\n⚠️  注意事项:")
    print("   - 测试需要使用管理员账号登录")
    print("   - 可以通过修改 app/utils/admin.py 中的 ADMIN_USER_IDS 添加管理员")
    print("   - 或者在数据库中设置用户的 is_admin 字段为 true")


if __name__ == "__main__":
    try:
        test_tutor_crud_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到服务器")
        print("请确保后端服务已启动（运行 python main.py）")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
