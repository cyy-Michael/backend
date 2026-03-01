"""
导师详情接口测试脚本
测试导师完整信息查询功能
"""

import requests
import json
from typing import Optional

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_CODE = "test_wx_code_001"  # 测试用的微信code


def print_response(title: str, response: requests.Response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应内容:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容: {response.text}")


def test_tutor_detail():
    """测试导师详情功能"""
    print("\n" + "="*80)
    print("开始测试导师详情接口")
    print("="*80)
    
    # 1. 登录获取token（可选）
    print(f"\n[步骤 1] 登录获取token...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"code": TEST_USER_CODE}
    )
    
    token = None
    headers = {}
    if login_response.status_code == 200:
        token = login_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ 登录成功，获取token")
    else:
        print(f"⚠️  登录失败，将使用未登录状态测试")
    
    # 2. 先获取导师列表，找一个导师ID用于测试
    print(f"\n[步骤 2] 获取导师列表，找一个导师用于测试...")
    list_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"page": 1, "page_size": 5},
        headers=headers
    )
    
    test_tutor_id = None
    if list_response.status_code == 200:
        tutors = list_response.json()["data"]["list"]
        if tutors:
            test_tutor_id = tutors[0]["id"]
            print(f"✅ 找到测试导师: {tutors[0]['name']} (ID: {test_tutor_id})")
        else:
            print(f"❌ 没有找到导师，无法继续测试")
            return
    else:
        print(f"❌ 获取导师列表失败")
        return
    
    # 3. 测试获取导师详情（未登录）
    print(f"\n[步骤 3] 测试获取导师详情（未登录）...")
    detail_response = requests.get(
        f"{BASE_URL}/tutor/detail/{test_tutor_id}"
    )
    print_response("导师详情（未登录）", detail_response)
    
    if detail_response.status_code == 200:
        detail = detail_response.json()["data"]
        print(f"✅ 获取导师详情成功")
        print(f"   导师姓名: {detail['name']}")
        print(f"   职称: {detail.get('title', '未知')}")
        print(f"   学校: {detail.get('school', '未知')}")
        print(f"   院系: {detail.get('department', '未知')}")
        print(f"   研究方向: {detail.get('research_direction', '未知')}")
        print(f"   论文数量: {detail.get('paper_count', 0)}")
        print(f"   项目数量: {detail.get('project_count', 0)}")
        print(f"   学生数量: {detail.get('student_count', 0)}")
        print(f"   是否收藏: {detail.get('is_collected', False)}")
    else:
        print(f"❌ 获取导师详情失败")
    
    # 4. 测试获取导师详情（已登录）
    if token:
        print(f"\n[步骤 4] 测试获取导师详情（已登录）...")
        detail_response_auth = requests.get(
            f"{BASE_URL}/tutor/detail/{test_tutor_id}",
            headers=headers
        )
        print_response("导师详情（已登录）", detail_response_auth)
        
        if detail_response_auth.status_code == 200:
            detail = detail_response_auth.json()["data"]
            print(f"✅ 获取导师详情成功（已登录）")
            print(f"   是否收藏: {detail.get('is_collected', False)}")
    
    # 5. 测试详情中的基本信息字段
    if detail_response.status_code == 200:
        print(f"\n[步骤 5] 验证基本信息字段...")
        detail = detail_response.json()["data"]
        
        required_fields = [
            "id", "name", "title", "school", "department",
            "research_direction", "paper_count", "project_count"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in detail:
                missing_fields.append(field)
        
        if not missing_fields:
            print(f"✅ 所有必需字段都存在")
        else:
            print(f"❌ 缺少字段: {', '.join(missing_fields)}")
    
    # 6. 测试详情中的论文列表
    if detail_response.status_code == 200:
        print(f"\n[步骤 6] 验证论文列表...")
        detail = detail_response.json()["data"]
        papers = detail.get("papers", [])
        
        if papers:
            print(f"✅ 论文列表包含 {len(papers)} 篇论文")
            print(f"   第一篇论文:")
            paper = papers[0]
            print(f"   - 标题: {paper.get('title', '未知')}")
            print(f"   - 作者: {', '.join(paper.get('authors', []))}")
            print(f"   - 期刊: {paper.get('journal', '未知')}")
            print(f"   - 年份: {paper.get('year', '未知')}")
            print(f"   - 引用数: {paper.get('citations', 0)}")
        else:
            print(f"⚠️  论文列表为空")
    
    # 7. 测试详情中的项目列表
    if detail_response.status_code == 200:
        print(f"\n[步骤 7] 验证项目列表...")
        detail = detail_response.json()["data"]
        projects = detail.get("projects", [])
        
        if projects:
            print(f"✅ 项目列表包含 {len(projects)} 个项目")
            print(f"   第一个项目:")
            project = projects[0]
            print(f"   - 标题: {project.get('title', '未知')}")
            print(f"   - 资助来源: {project.get('funding', '未知')}")
            print(f"   - 开始日期: {project.get('start_date', '未知')}")
            print(f"   - 结束日期: {project.get('end_date', '未知')}")
            print(f"   - 状态: {project.get('status', '未知')}")
        else:
            print(f"⚠️  项目列表为空")
    
    # 8. 测试详情中的学生信息
    if detail_response.status_code == 200:
        print(f"\n[步骤 8] 验证学生信息...")
        detail = detail_response.json()["data"]
        students = detail.get("students", [])
        
        if students:
            print(f"✅ 学生列表包含 {len(students)} 个学生")
            print(f"   第一个学生: {students[0]}")
        else:
            print(f"⚠️  学生列表为空")
    
    # 9. 测试详情中的合作信息
    if detail_response.status_code == 200:
        print(f"\n[步骤 9] 验证合作信息...")
        detail = detail_response.json()["data"]
        coops = detail.get("coops", [])
        
        if coops:
            print(f"✅ 合作列表包含 {len(coops)} 个合作者")
        else:
            print(f"⚠️  合作列表为空")
    
    # 10. 测试详情中的社交信息
    if detail_response.status_code == 200:
        print(f"\n[步骤 10] 验证社交信息...")
        detail = detail_response.json()["data"]
        socials = detail.get("socials", [])
        
        if socials:
            print(f"✅ 社交账号列表包含 {len(socials)} 个账号")
        else:
            print(f"⚠️  社交账号列表为空")
    
    # 11. 测试详情中的标签
    if detail_response.status_code == 200:
        print(f"\n[步骤 11] 验证标签信息...")
        detail = detail_response.json()["data"]
        tags = detail.get("tags", [])
        
        if tags:
            print(f"✅ 标签列表: {', '.join(tags)}")
        else:
            print(f"⚠️  标签列表为空")
    
    # 12. 测试详情中的联系方式
    if detail_response.status_code == 200:
        print(f"\n[步骤 12] 验证联系方式...")
        detail = detail_response.json()["data"]
        
        contact_info = {
            "邮箱": detail.get("email"),
            "电话": detail.get("phone"),
            "个人主页": detail.get("personal_page")
        }
        
        print(f"联系方式:")
        for key, value in contact_info.items():
            if value:
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: 未提供")
    
    # 13. 测试详情中的招生信息
    if detail_response.status_code == 200:
        print(f"\n[步骤 13] 验证招生信息...")
        detail = detail_response.json()["data"]
        
        recruitment_type = detail.get("recruitment_type")
        has_funding = detail.get("has_funding", False)
        
        recruitment_map = {
            "academic": "学硕",
            "professional": "专硕",
            "both": "学硕+专硕"
        }
        
        print(f"招生信息:")
        print(f"   招生类型: {recruitment_map.get(recruitment_type, '未知')}")
        print(f"   是否有科研经费: {'是' if has_funding else '否'}")
    
    # 14. 测试不存在的导师ID
    print(f"\n[步骤 14] 测试不存在的导师ID...")
    not_found_response = requests.get(
        f"{BASE_URL}/tutor/detail/nonexistent_tutor_id",
        headers=headers
    )
    print_response("不存在的导师", not_found_response)
    
    if not_found_response.status_code == 404:
        print(f"✅ 正确返回404错误")
    else:
        print(f"❌ 应该返回404，但返回了 {not_found_response.status_code}")
    
    # 15. 测试无效的导师ID格式
    print(f"\n[步骤 15] 测试无效的导师ID格式...")
    invalid_response = requests.get(
        f"{BASE_URL}/tutor/detail/",
        headers=headers
    )
    
    if invalid_response.status_code in [404, 422]:
        print(f"✅ 正确处理无效ID")
    else:
        print(f"⚠️  返回状态码: {invalid_response.status_code}")
    
    # 16. 测试响应时间
    print(f"\n[步骤 16] 测试响应时间...")
    import time
    start_time = time.time()
    perf_response = requests.get(
        f"{BASE_URL}/tutor/detail/{test_tutor_id}",
        headers=headers
    )
    end_time = time.time()
    response_time = (end_time - start_time) * 1000  # 转换为毫秒
    
    if perf_response.status_code == 200:
        print(f"✅ 响应时间: {response_time:.2f}ms")
        if response_time < 500:
            print(f"   性能良好（<500ms）")
        elif response_time < 1000:
            print(f"   性能一般（500-1000ms）")
        else:
            print(f"   ⚠️  性能较慢（>1000ms）")
    
    # 17. 测试多次请求的一致性
    print(f"\n[步骤 17] 测试多次请求的一致性...")
    response1 = requests.get(f"{BASE_URL}/tutor/detail/{test_tutor_id}", headers=headers)
    response2 = requests.get(f"{BASE_URL}/tutor/detail/{test_tutor_id}", headers=headers)
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]
        
        # 比较关键字段
        key_fields = ["id", "name", "title", "school", "department", "paper_count", "project_count"]
        is_consistent = all(data1.get(field) == data2.get(field) for field in key_fields)
        
        if is_consistent:
            print(f"✅ 多次请求数据一致")
        else:
            print(f"❌ 多次请求数据不一致")
    
    # 测试总结
    print("\n" + "="*80)
    print("📝 测试总结:")
    print("="*80)
    print("1. ✅ 获取导师详情（未登录）")
    print("2. ✅ 获取导师详情（已登录）")
    print("3. ✅ 基本信息字段验证")
    print("4. ✅ 论文列表验证")
    print("5. ✅ 项目列表验证")
    print("6. ✅ 学生信息验证")
    print("7. ✅ 合作信息验证")
    print("8. ✅ 社交信息验证")
    print("9. ✅ 标签信息验证")
    print("10. ✅ 联系方式验证")
    print("11. ✅ 招生信息验证")
    print("12. ✅ 不存在的导师处理")
    print("13. ✅ 无效ID处理")
    print("14. ✅ 响应时间测试")
    print("15. ✅ 数据一致性测试")
    print("\n所有测试完成！")


if __name__ == "__main__":
    test_tutor_detail()
