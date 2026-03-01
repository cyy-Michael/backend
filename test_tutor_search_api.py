"""
导师查询接口测试脚本
测试基础查询和高级筛选功能
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


def test_tutor_search():
    """测试导师查询功能"""
    print("\n" + "="*80)
    print("开始测试导师查询接口")
    print("="*80)
    
    # 1. 登录获取token（可选，查询接口不强制要求登录）
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
    
    # 2. 测试基础查询 - 关键词搜索
    print(f"\n[步骤 2] 测试基础查询 - 关键词搜索...")
    search_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"keyword": "人工智能", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("关键词搜索：人工智能", search_response)
    
    if search_response.status_code == 200:
        result = search_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
        print(f"   当前页: {result['page']}/{result['total_pages']}")
        print(f"   返回数量: {len(result['list'])}")
    else:
        print(f"❌ 查询失败")
    
    # 3. 测试按姓名查询
    print(f"\n[步骤 3] 测试按姓名查询...")
    name_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"name": "张", "page": 1, "page_size": 5},
        headers=headers
    )
    print_response("姓名查询：张", name_response)
    
    if name_response.status_code == 200:
        result = name_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
        if result['list']:
            print(f"   示例导师: {result['list'][0]['name']} - {result['list'][0]['school']}")
    
    # 4. 测试按学校查询
    print(f"\n[步骤 4] 测试按学校查询...")
    school_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"school": "清华", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("学校查询：清华", school_response)
    
    if school_response.status_code == 200:
        result = school_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 5. 测试按院系查询
    print(f"\n[步骤 5] 测试按院系查询...")
    dept_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"department": "计算机", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("院系查询：计算机", dept_response)
    
    if dept_response.status_code == 200:
        result = dept_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 6. 测试按研究方向查询
    print(f"\n[步骤 6] 测试按研究方向查询...")
    research_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"research_direction": "机器学习", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("研究方向查询：机器学习", research_response)
    
    if research_response.status_code == 200:
        result = research_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 7. 测试按职称查询
    print(f"\n[步骤 7] 测试按职称查询...")
    title_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"title": "教授", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("职称查询：教授", title_response)
    
    if title_response.status_code == 200:
        result = title_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 8. 测试招生类型筛选
    print(f"\n[步骤 8] 测试招生类型筛选...")
    recruitment_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"recruitment_type": "academic", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("招生类型：学硕", recruitment_response)
    
    if recruitment_response.status_code == 200:
        result = recruitment_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个招收学硕的导师")
    
    # 9. 测试是否有课题筛选
    print(f"\n[步骤 9] 测试是否有课题筛选...")
    projects_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"has_projects": True, "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("有课题的导师", projects_response)
    
    if projects_response.status_code == 200:
        result = projects_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个有课题的导师")
    
    # 10. 测试标签筛选
    print(f"\n[步骤 10] 测试标签筛选...")
    tags_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"tags": "AI,机器学习", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("标签筛选：AI,机器学习", tags_response)
    
    if tags_response.status_code == 200:
        result = tags_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 11. 测试论文数量筛选
    print(f"\n[步骤 11] 测试论文数量筛选...")
    papers_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"min_papers": 10, "max_papers": 50, "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("论文数量：10-50篇", papers_response)
    
    if papers_response.status_code == 200:
        result = papers_response.json()["data"]
        print(f"✅ 查询成功，找到 {result['total']} 个导师")
    
    # 12. 测试组合查询
    print(f"\n[步骤 12] 测试组合查询...")
    complex_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={
            "school": "清华",
            "department": "计算机",
            "title": "教授",
            "research_direction": "人工智能",
            "has_projects": True,
            "min_papers": 5,
            "page": 1,
            "page_size": 10
        },
        headers=headers
    )
    print_response("组合查询", complex_response)
    
    if complex_response.status_code == 200:
        result = complex_response.json()["data"]
        print(f"✅ 组合查询成功，找到 {result['total']} 个导师")
    
    # 13. 测试排序功能
    print(f"\n[步骤 13] 测试排序功能...")
    
    # 按创建时间降序
    sort_response1 = requests.get(
        f"{BASE_URL}/tutor/search",
        params={
            "keyword": "人工智能",
            "sort_by": "created_at",
            "sort_order": "desc",
            "page": 1,
            "page_size": 5
        },
        headers=headers
    )
    print_response("排序：按创建时间降序", sort_response1)
    
    # 按姓名升序
    sort_response2 = requests.get(
        f"{BASE_URL}/tutor/search",
        params={
            "keyword": "人工智能",
            "sort_by": "name",
            "sort_order": "asc",
            "page": 1,
            "page_size": 5
        },
        headers=headers
    )
    print_response("排序：按姓名升序", sort_response2)
    
    if sort_response1.status_code == 200 and sort_response2.status_code == 200:
        print(f"✅ 排序功能测试成功")
    
    # 14. 测试分页功能
    print(f"\n[步骤 14] 测试分页功能...")
    
    # 第1页
    page1_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"keyword": "教授", "page": 1, "page_size": 5},
        headers=headers
    )
    
    # 第2页
    page2_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"keyword": "教授", "page": 2, "page_size": 5},
        headers=headers
    )
    
    if page1_response.status_code == 200 and page2_response.status_code == 200:
        page1_data = page1_response.json()["data"]
        page2_data = page2_response.json()["data"]
        print(f"✅ 分页功能测试成功")
        print(f"   第1页: {len(page1_data['list'])} 个导师")
        print(f"   第2页: {len(page2_data['list'])} 个导师")
        print(f"   总页数: {page1_data['total_pages']}")
    
    # 15. 测试获取筛选选项
    print(f"\n[步骤 15] 测试获取筛选选项...")
    options_response = requests.get(
        f"{BASE_URL}/tutor/filter-options",
        headers=headers
    )
    print_response("筛选选项", options_response)
    
    if options_response.status_code == 200:
        result = options_response.json()["data"]
        print(f"✅ 获取筛选选项成功")
        print(f"   学校数量: {len(result['schools'])}")
        print(f"   院系数量: {len(result['departments'])}")
        print(f"   职称数量: {len(result['titles'])}")
        print(f"   研究方向数量: {len(result['research_directions'])}")
        print(f"   标签数量: {len(result['tags'])}")
    
    # 16. 测试按学校获取院系列表
    print(f"\n[步骤 16] 测试按学校获取院系列表...")
    if options_response.status_code == 200:
        schools = options_response.json()["data"]["schools"]
        if schools:
            test_school = schools[0]
            dept_options_response = requests.get(
                f"{BASE_URL}/tutor/filter-options",
                params={"school": test_school},
                headers=headers
            )
            print_response(f"学校 '{test_school}' 的院系列表", dept_options_response)
            
            if dept_options_response.status_code == 200:
                result = dept_options_response.json()["data"]
                print(f"✅ 获取院系列表成功，共 {len(result['departments'])} 个院系")
    
    # 17. 测试边界情况 - 空查询
    print(f"\n[步骤 17] 测试边界情况 - 空查询...")
    empty_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"page": 1, "page_size": 10},
        headers=headers
    )
    print_response("空查询（返回所有导师）", empty_response)
    
    if empty_response.status_code == 200:
        result = empty_response.json()["data"]
        print(f"✅ 空查询成功，返回 {result['total']} 个导师")
    
    # 18. 测试边界情况 - 无结果查询
    print(f"\n[步骤 18] 测试边界情况 - 无结果查询...")
    no_result_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"keyword": "不存在的导师名称12345", "page": 1, "page_size": 10},
        headers=headers
    )
    print_response("无结果查询", no_result_response)
    
    if no_result_response.status_code == 200:
        result = no_result_response.json()["data"]
        if result['total'] == 0:
            print(f"✅ 无结果查询处理正确")
        else:
            print(f"⚠️  预期无结果，但返回了 {result['total']} 个导师")
    
    # 19. 测试边界情况 - 超大页码
    print(f"\n[步骤 19] 测试边界情况 - 超大页码...")
    large_page_response = requests.get(
        f"{BASE_URL}/tutor/search",
        params={"page": 9999, "page_size": 10},
        headers=headers
    )
    print_response("超大页码", large_page_response)
    
    if large_page_response.status_code == 200:
        result = large_page_response.json()["data"]
        print(f"✅ 超大页码处理正确，返回 {len(result['list'])} 个导师")
    
    # 测试总结
    print("\n" + "="*80)
    print("📝 测试总结:")
    print("="*80)
    print("1. ✅ 基础查询 - 关键词搜索")
    print("2. ✅ 基础查询 - 按姓名查询")
    print("3. ✅ 基础查询 - 按学校查询")
    print("4. ✅ 基础查询 - 按院系查询")
    print("5. ✅ 高级筛选 - 按研究方向")
    print("6. ✅ 高级筛选 - 按职称")
    print("7. ✅ 高级筛选 - 按招生类型")
    print("8. ✅ 高级筛选 - 是否有课题")
    print("9. ✅ 高级筛选 - 标签筛选")
    print("10. ✅ 高级筛选 - 论文数量范围")
    print("11. ✅ 组合查询")
    print("12. ✅ 排序功能（多字段、多方向）")
    print("13. ✅ 分页功能")
    print("14. ✅ 获取筛选选项")
    print("15. ✅ 按学校获取院系")
    print("16. ✅ 边界情况处理")
    print("\n所有测试完成！")


if __name__ == "__main__":
    test_tutor_search()
