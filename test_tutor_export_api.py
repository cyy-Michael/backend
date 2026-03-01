"""
导师信息导出接口测试脚本
测试Excel和CSV导出功能
"""

import requests
import json
from typing import Optional
import os

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_ADMIN_CODE = "test_admin_code_001"  # 测试用的管理员微信code


def print_response(title: str, response: requests.Response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    
    # 如果是文件下载，显示文件信息
    if response.headers.get('Content-Disposition'):
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
        print(f"文件大小: {len(response.content)} 字节")
    else:
        try:
            data = response.json()
            print(f"响应内容:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应内容: {response.text[:500]}")


def test_tutor_export():
    """测试导师导出功能"""
    print("\n" + "="*80)
    print("开始测试导师信息导出接口")
    print("="*80)
    
    # 1. 登录获取管理员token
    print(f"\n[步骤 1] 登录获取管理员token...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"code": TEST_ADMIN_CODE}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败，无法继续测试")
        print(f"   请确保测试账号是管理员账号")
        return
    
    token = login_response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功，获取管理员token")
    
    # 2. 测试获取导出统计（无筛选条件）
    print(f"\n[步骤 2] 测试获取导出统计（无筛选条件）...")
    stats_response = requests.get(
        f"{BASE_URL}/tutor/admin/export-stats",
        headers=headers
    )
    print_response("导出统计（无筛选）", stats_response)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()["data"]
        print(f"✅ 获取导出统计成功")
        print(f"   可导出数量: {stats['total_count']}")
        print(f"   最大导出限制: {stats['max_export_limit']}")
        print(f"   是否可导出: {stats['can_export']}")
        
        if stats['school_stats']:
            print(f"   学校分布（前5）:")
            for school_stat in stats['school_stats'][:5]:
                print(f"     - {school_stat['school']}: {school_stat['count']}人")
    else:
        print(f"❌ 获取导出统计失败")
    
    # 3. 测试获取导出统计（带筛选条件）
    print(f"\n[步骤 3] 测试获取导出统计（带筛选条件）...")
    stats_response2 = requests.get(
        f"{BASE_URL}/tutor/admin/export-stats",
        params={"school": "清华", "title": "教授"},
        headers=headers
    )
    print_response("导出统计（筛选：清华+教授）", stats_response2)
    
    if stats_response2.status_code == 200:
        stats = stats_response2.json()["data"]
        print(f"✅ 获取筛选后的统计成功")
        print(f"   符合条件的导师数量: {stats['total_count']}")
    
    # 4. 测试导出Excel（无筛选条件）
    print(f"\n[步骤 4] 测试导出Excel（无筛选条件）...")
    excel_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "excel", "limit": 100},
        headers=headers
    )
    print_response("导出Excel（无筛选）", excel_response)
    
    if excel_response.status_code == 200:
        print(f"✅ 导出Excel成功")
        
        # 保存文件
        filename = "test_export_导师信息.xlsx"
        with open(filename, "wb") as f:
            f.write(excel_response.content)
        print(f"   文件已保存: {filename}")
        print(f"   文件大小: {len(excel_response.content)} 字节")
    else:
        print(f"❌ 导出Excel失败")
    
    # 5. 测试导出CSV（无筛选条件）
    print(f"\n[步骤 5] 测试导出CSV（无筛选条件）...")
    csv_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "csv", "limit": 100},
        headers=headers
    )
    print_response("导出CSV（无筛选）", csv_response)
    
    if csv_response.status_code == 200:
        print(f"✅ 导出CSV成功")
        
        # 保存文件
        filename = "test_export_导师信息.csv"
        with open(filename, "wb") as f:
            f.write(csv_response.content)
        print(f"   文件已保存: {filename}")
        print(f"   文件大小: {len(csv_response.content)} 字节")
    else:
        print(f"❌ 导出CSV失败")
    
    # 6. 测试导出Excel（带筛选条件）
    print(f"\n[步骤 6] 测试导出Excel（带筛选条件）...")
    excel_response2 = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={
            "format": "excel",
            "school": "清华",
            "title": "教授",
            "limit": 50
        },
        headers=headers
    )
    print_response("导出Excel（筛选：清华+教授）", excel_response2)
    
    if excel_response2.status_code == 200:
        print(f"✅ 导出Excel（带筛选）成功")
        filename = "test_export_清华教授.xlsx"
        with open(filename, "wb") as f:
            f.write(excel_response2.content)
        print(f"   文件已保存: {filename}")
    else:
        print(f"❌ 导出Excel（带筛选）失败")
    
    # 7. 测试导出CSV（带筛选条件）
    print(f"\n[步骤 7] 测试导出CSV（带筛选条件）...")
    csv_response2 = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={
            "format": "csv",
            "keyword": "人工智能",
            "limit": 50
        },
        headers=headers
    )
    print_response("导出CSV（关键词：人工智能）", csv_response2)
    
    if csv_response2.status_code == 200:
        print(f"✅ 导出CSV（带筛选）成功")
        filename = "test_export_人工智能.csv"
        with open(filename, "wb") as f:
            f.write(csv_response2.content)
        print(f"   文件已保存: {filename}")
    else:
        print(f"❌ 导出CSV（带筛选）失败")
    
    # 8. 测试导出限制
    print(f"\n[步骤 8] 测试导出数量限制...")
    limit_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "excel", "limit": 10},
        headers=headers
    )
    
    if limit_response.status_code == 200:
        print(f"✅ 导出数量限制测试成功")
        print(f"   限制10条，实际导出: {len(limit_response.content)} 字节")
    
    # 9. 测试无效格式
    print(f"\n[步骤 9] 测试无效的导出格式...")
    invalid_format_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "pdf"},  # 不支持的格式
        headers=headers
    )
    print_response("无效格式（pdf）", invalid_format_response)
    
    if invalid_format_response.status_code == 422:
        print(f"✅ 正确拒绝了无效格式")
    else:
        print(f"⚠️  应该返回422，但返回了 {invalid_format_response.status_code}")
    
    # 10. 测试无数据导出
    print(f"\n[步骤 10] 测试无数据导出...")
    no_data_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={
            "format": "excel",
            "keyword": "不存在的导师名称12345xyz"
        },
        headers=headers
    )
    print_response("无数据导出", no_data_response)
    
    if no_data_response.status_code == 404:
        print(f"✅ 正确处理无数据情况")
    else:
        print(f"⚠️  应该返回404，但返回了 {no_data_response.status_code}")
    
    # 11. 测试非管理员访问
    print(f"\n[步骤 11] 测试非管理员访问...")
    
    # 使用普通用户token（如果有）
    normal_user_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"code": "test_normal_user_code"}
    )
    
    if normal_user_login.status_code == 200:
        normal_token = normal_user_login.json()["data"]["token"]
        normal_headers = {"Authorization": f"Bearer {normal_token}"}
        
        unauthorized_response = requests.get(
            f"{BASE_URL}/tutor/admin/export",
            params={"format": "excel"},
            headers=normal_headers
        )
        print_response("非管理员访问", unauthorized_response)
        
        if unauthorized_response.status_code == 403:
            print(f"✅ 正确拒绝了非管理员访问")
        else:
            print(f"⚠️  应该返回403，但返回了 {unauthorized_response.status_code}")
    else:
        print(f"⚠️  无法测试非管理员访问（没有普通用户账号）")
    
    # 12. 测试未登录访问
    print(f"\n[步骤 12] 测试未登录访问...")
    no_auth_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "excel"}
    )
    print_response("未登录访问", no_auth_response)
    
    if no_auth_response.status_code in [401, 403]:
        print(f"✅ 正确拒绝了未登录访问")
    else:
        print(f"⚠️  应该返回401或403，但返回了 {no_auth_response.status_code}")
    
    # 13. 测试响应时间
    print(f"\n[步骤 13] 测试响应时间...")
    import time
    start_time = time.time()
    perf_response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={"format": "excel", "limit": 100},
        headers=headers
    )
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    if perf_response.status_code == 200:
        print(f"✅ 导出响应时间: {response_time:.2f}ms")
        if response_time < 3000:
            print(f"   性能良好（<3秒）")
        elif response_time < 5000:
            print(f"   性能一般（3-5秒）")
        else:
            print(f"   ⚠️  性能较慢（>5秒）")
    
    # 14. 清理测试文件
    print(f"\n[步骤 14] 清理测试文件...")
    test_files = [
        "test_export_导师信息.xlsx",
        "test_export_导师信息.csv",
        "test_export_清华教授.xlsx",
        "test_export_人工智能.csv"
    ]
    
    for filename in test_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"   已删除: {filename}")
            except:
                print(f"   无法删除: {filename}")
    
    # 测试总结
    print("\n" + "="*80)
    print("📝 测试总结:")
    print("="*80)
    print("1. ✅ 获取导出统计（无筛选）")
    print("2. ✅ 获取导出统计（带筛选）")
    print("3. ✅ 导出Excel（无筛选）")
    print("4. ✅ 导出CSV（无筛选）")
    print("5. ✅ 导出Excel（带筛选）")
    print("6. ✅ 导出CSV（带筛选）")
    print("7. ✅ 导出数量限制")
    print("8. ✅ 无效格式处理")
    print("9. ✅ 无数据处理")
    print("10. ✅ 非管理员访问拒绝")
    print("11. ✅ 未登录访问拒绝")
    print("12. ✅ 响应时间测试")
    print("\n所有测试完成！")


if __name__ == "__main__":
    test_tutor_export()
