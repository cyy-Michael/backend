# 导师详情接口文档

## 📋 概述

本文档说明导师详情查询接口，返回导师的完整信息，包括基本信息、学术成果、联系方式、学生信息、合作信息等。

**版本**: v1.0.0  
**最后更新**: 2024-03-01

---

## 🚀 功能特性

### 返回的信息类别

1. **基本信息**
   - 姓名、职称、学校、院系
   - 头像、个人简介
   - 研究方向、标签

2. **联系方式**
   - 邮箱
   - 电话
   - 个人主页

3. **招生信息**
   - 招生类型（学硕/专硕/都招）
   - 是否有科研经费

4. **学术成果**
   - 论文列表（标题、作者、期刊、年份、引用数等）
   - 项目列表（标题、资助来源、时间、金额、状态等）
   - 成果总结

5. **社交信息**
   - 社交账号列表

6. **学生信息**
   - 指导的学生列表

7. **合作信息**
   - 合作者列表

8. **风险信息**
   - 风险提示列表

9. **统计信息**
   - 论文数量
   - 项目数量
   - 学生数量

10. **收藏状态**
    - 是否被当前用户收藏（需登录）

---

## 📌 接口详情

### 导师详情查询

**接口地址**: `GET /api/v1/tutor/detail/{tutor_id}`

**功能**: 获取指定导师的完整详细信息

**权限**: 公开接口（登录可获取收藏状态）

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tutor_id | string | 是 | 导师ID |

#### 请求头（可选）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | string | 否 | Bearer {token}，登录后可获取收藏状态 |

#### 响应示例

```json
{
  "code": 200,
  "message": "获取导师详情成功",
  "data": {
    "id": "tutor_123",
    "name": "张三",
    "title": "教授",
    "school": "清华大学",
    "school_id": "school_001",
    "department": "计算机科学与技术系",
    "department_id": "dept_001",
    "avatar": "https://example.com/avatar.jpg",
    "bio": "张三教授，博士生导师，主要研究方向为人工智能...",
    
    "email": "zhangsan@tsinghua.edu.cn",
    "phone": "010-12345678",
    "personal_page": "https://www.tsinghua.edu.cn/zhangsan",
    
    "research_direction": "人工智能、机器学习、深度学习",
    "tags": ["AI", "机器学习", "深度学习", "计算机视觉"],
    "recruitment_type": "both",
    "has_funding": true,
    
    "paper_count": 25,
    "project_count": 8,
    "student_count": 15,
    
    "papers": [
      {
        "id": "paper_001",
        "title": "Deep Learning for Computer Vision",
        "authors": ["张三", "李四", "王五"],
        "journal": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "year": 2023,
        "doi": "10.1109/TPAMI.2023.123456",
        "abstract": "本文提出了一种新的深度学习方法...",
        "citations": 150,
        "url": "https://ieeexplore.ieee.org/document/123456"
      }
    ],
    
    "projects": [
      {
        "id": "project_001",
        "title": "基于深度学习的图像识别研究",
        "funding": "国家自然科学基金",
        "start_date": "2022-01-01T00:00:00Z",
        "end_date": "2024-12-31T00:00:00Z",
        "description": "本项目旨在研究基于深度学习的图像识别技术...",
        "amount": 500000,
        "status": "ongoing"
      }
    ],
    
    "achievements_summary": "发表SCI论文25篇，主持国家自然科学基金项目3项...",
    
    "socials": [
      {
        "platform": "微信",
        "account": "zhangsan_ai",
        "url": null
      },
      {
        "platform": "GitHub",
        "account": "zhangsan",
        "url": "https://github.com/zhangsan"
      }
    ],
    
    "students": [
      {
        "name": "李明",
        "degree": "博士",
        "year": "2020",
        "research": "计算机视觉"
      }
    ],
    
    "coops": [
      {
        "name": "王教授",
        "school": "北京大学",
        "field": "机器学习"
      }
    ],
    
    "risks": [
      {
        "type": "warning",
        "content": "该导师项目较多，可能较忙"
      }
    ],
    
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2024-03-01T00:00:00Z",
    "crawled_at": "2024-02-28T00:00:00Z",
    
    "is_collected": false
  }
}
```

#### 错误响应

**导师不存在（404）**:
```json
{
  "code": 404,
  "message": "导师不存在或已被删除",
  "data": {
    "code": "TUTOR_NOT_FOUND",
    "message": "导师不存在或已被删除"
  }
}
```

**服务器错误（500）**:
```json
{
  "code": 500,
  "message": "获取导师详情失败",
  "data": {
    "request_id": "req_123456"
  }
}
```

---

## 💻 使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 未登录查询
response = requests.get(
    f"{BASE_URL}/tutor/detail/tutor_123"
)

if response.status_code == 200:
    detail = response.json()["data"]
    print(f"导师姓名: {detail['name']}")
    print(f"职称: {detail['title']}")
    print(f"学校: {detail['school']}")
    print(f"研究方向: {detail['research_direction']}")
    print(f"论文数量: {detail['paper_count']}")
    print(f"项目数量: {detail['project_count']}")
    
    # 打印论文列表
    for paper in detail['papers']:
        print(f"论文: {paper['title']} ({paper['year']})")
    
    # 打印项目列表
    for project in detail['projects']:
        print(f"项目: {project['title']}")

# 登录后查询（可获取收藏状态）
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "wx_code"}
)
token = login_response.json()["data"]["token"]

response = requests.get(
    f"{BASE_URL}/tutor/detail/tutor_123",
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    detail = response.json()["data"]
    print(f"是否已收藏: {detail['is_collected']}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 未登录查询
async function getTutorDetail(tutorId) {
  const response = await fetch(
    `${BASE_URL}/tutor/detail/${tutorId}`
  );
  
  if (response.ok) {
    const data = await response.json();
    const detail = data.data;
    
    console.log(`导师姓名: ${detail.name}`);
    console.log(`职称: ${detail.title}`);
    console.log(`学校: ${detail.school}`);
    console.log(`研究方向: ${detail.research_direction}`);
    console.log(`论文数量: ${detail.paper_count}`);
    console.log(`项目数量: ${detail.project_count}`);
    
    // 打印论文列表
    detail.papers.forEach(paper => {
      console.log(`论文: ${paper.title} (${paper.year})`);
    });
    
    // 打印项目列表
    detail.projects.forEach(project => {
      console.log(`项目: ${project.title}`);
    });
    
    return detail;
  }
}

// 登录后查询
async function getTutorDetailWithAuth(tutorId, token) {
  const response = await fetch(
    `${BASE_URL}/tutor/detail/${tutorId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (response.ok) {
    const data = await response.json();
    const detail = data.data;
    console.log(`是否已收藏: ${detail.is_collected}`);
    return detail;
  }
}

// 使用示例
getTutorDetail('tutor_123');
```

### curl

```bash
# 未登录查询
curl "http://localhost:8000/api/v1/tutor/detail/tutor_123"

# 登录后查询
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/tutor/detail/tutor_123"
```

---

## 📊 数据字段说明

### 基本信息字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 导师ID |
| name | string | 导师姓名 |
| title | string | 职称 |
| school | string | 学校名称 |
| school_id | string | 学校ID |
| department | string | 院系名称 |
| department_id | string | 院系ID |
| avatar | string | 头像URL |
| bio | string | 个人简介 |

### 联系方式字段

| 字段 | 类型 | 说明 |
|------|------|------|
| email | string | 邮箱 |
| phone | string | 电话 |
| personal_page | string | 个人主页URL |

### 研究信息字段

| 字段 | 类型 | 说明 |
|------|------|------|
| research_direction | string | 研究方向 |
| tags | array | 标签列表 |
| recruitment_type | string | 招生类型：academic/professional/both |
| has_funding | boolean | 是否有科研经费 |

### 统计信息字段

| 字段 | 类型 | 说明 |
|------|------|------|
| paper_count | integer | 论文数量 |
| project_count | integer | 项目数量 |
| student_count | integer | 学生数量 |

### 论文对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 论文ID |
| title | string | 论文标题 |
| authors | array | 作者列表 |
| journal | string | 期刊名称 |
| year | integer | 发表年份 |
| doi | string | DOI |
| abstract | string | 摘要 |
| citations | integer | 引用数 |
| url | string | 论文URL |

### 项目对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 项目ID |
| title | string | 项目标题 |
| funding | string | 资助来源 |
| start_date | datetime | 开始日期 |
| end_date | datetime | 结束日期 |
| description | string | 项目描述 |
| amount | integer | 项目金额 |
| status | string | 项目状态：ongoing/completed |

---

## 🔍 使用场景

### 场景1: 查看导师基本信息

用户浏览导师列表后，点击某个导师查看详细信息。

```python
# 获取导师详情
response = requests.get(f"{BASE_URL}/tutor/detail/{tutor_id}")
detail = response.json()["data"]

# 显示基本信息
print(f"{detail['name']} - {detail['title']}")
print(f"{detail['school']} {detail['department']}")
print(f"研究方向: {detail['research_direction']}")
```

### 场景2: 查看导师学术成果

用户想了解导师的学术成果和研究实力。

```python
detail = response.json()["data"]

# 显示学术统计
print(f"发表论文: {detail['paper_count']}篇")
print(f"主持项目: {detail['project_count']}个")

# 显示近期论文
recent_papers = sorted(
    detail['papers'],
    key=lambda x: x['year'],
    reverse=True
)[:5]

for paper in recent_papers:
    print(f"{paper['title']} - {paper['journal']} ({paper['year']})")
    print(f"引用数: {paper['citations']}")
```

### 场景3: 查看招生信息

用户想了解导师是否招生以及招生类型。

```python
detail = response.json()["data"]

recruitment_map = {
    "academic": "招收学硕",
    "professional": "招收专硕",
    "both": "学硕和专硕都招"
}

print(f"招生情况: {recruitment_map.get(detail['recruitment_type'], '未知')}")
print(f"科研经费: {'充足' if detail['has_funding'] else '一般'}")
```

### 场景4: 联系导师

用户想联系导师咨询相关问题。

```python
detail = response.json()["data"]

print("联系方式:")
if detail['email']:
    print(f"邮箱: {detail['email']}")
if detail['phone']:
    print(f"电话: {detail['phone']}")
if detail['personal_page']:
    print(f"个人主页: {detail['personal_page']}")
```

### 场景5: 收藏导师

用户登录后查看导师详情，并收藏感兴趣的导师。

```python
# 登录
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "wx_code"}
)
token = login_response.json()["data"]["token"]

# 查看详情（获取收藏状态）
response = requests.get(
    f"{BASE_URL}/tutor/detail/{tutor_id}",
    headers={"Authorization": f"Bearer {token}"}
)
detail = response.json()["data"]

if not detail['is_collected']:
    # 收藏导师
    requests.post(
        f"{BASE_URL}/user/favorite/toggle",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "target_id": tutor_id,
            "target_type": "tutor"
        }
    )
```

---

## ⚡ 性能优化

### 1. 数据库查询优化

**使用索引**:
```javascript
// 导师基本信息查询
db.tutors.createIndex({ "id": 1, "is_deleted": 1 })

// 论文查询
db.papers.createIndex({ "tutor_id": 1, "year": -1 })

// 项目查询
db.projects.createIndex({ "tutor_id": 1, "start_date": -1 })

// 收藏查询
db.favorites.createIndex({ "user_id": 1, "target_id": 1, "target_type": 1 })
```

### 2. 响应优化

**字段投影**:
```python
# 只查询需要的字段
tutor = await db.tutors.find_one(
    {"id": tutor_id},
    {
        "id": 1,
        "name": 1,
        "title": 1,
        "school_name": 1,
        "department_name": 1,
        # ... 其他需要的字段
    }
)
```

**分批加载**:
- 基本信息立即返回
- 论文、项目等详细信息可以分批加载
- 考虑使用懒加载策略

### 3. 缓存策略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_tutor_detail_cached(tutor_id):
    # 缓存导师详情
    return get_tutor_detail(tutor_id)

# 设置缓存过期时间
# 使用Redis等缓存系统
```

---

## 🧪 测试指南

### 运行测试

```bash
cd backend
python test_tutor_detail_api.py
```

### 测试覆盖

测试脚本包含17个测试场景：

1. ✅ 获取导师详情（未登录）
2. ✅ 获取导师详情（已登录）
3. ✅ 基本信息字段验证
4. ✅ 论文列表验证
5. ✅ 项目列表验证
6. ✅ 学生信息验证
7. ✅ 合作信息验证
8. ✅ 社交信息验证
9. ✅ 标签信息验证
10. ✅ 联系方式验证
11. ✅ 招生信息验证
12. ✅ 不存在的导师处理
13. ✅ 无效ID处理
14. ✅ 响应时间测试
15. ✅ 数据一致性测试

---

## ⚠️ 注意事项

### 1. 数据完整性

**可能为空的字段**:
- 联系方式（email, phone, personal_page）
- 社交账号（socials）
- 学生信息（students）
- 合作信息（coops）
- 风险信息（risks）

**处理建议**:
```python
# 安全访问可能为空的字段
email = detail.get('email', '未提供')
papers = detail.get('papers', [])
```

### 2. 收藏状态

- 未登录时，`is_collected` 始终为 `false`
- 登录后，会查询用户的收藏记录
- 收藏状态实时查询，不缓存

### 3. 软删除过滤

- 查询自动过滤已删除的导师
- 已删除导师返回404错误
- 管理员可以查看已删除导师（需要特殊接口）

### 4. 性能考虑

**大数据量处理**:
- 论文列表限制100篇
- 项目列表限制50个
- 考虑分页加载详细信息

**响应时间**:
- 目标响应时间：< 500ms
- 包含论文和项目查询：< 1000ms
- 超时时间设置：3000ms

---

## 📈 后续优化

### 短期（1-2周）

1. **数据增强**
   - 添加导师影响力指数
   - 添加导师活跃度评分
   - 添加导师推荐指数

2. **性能优化**
   - 实现详情缓存
   - 优化数据库查询
   - 添加CDN加速

### 中期（1-2月）

1. **功能增强**
   - 添加相似导师推荐
   - 添加导师对比功能
   - 添加导师动态更新

2. **数据完善**
   - 补充导师详细信息
   - 添加导师评价系统
   - 添加导师问答功能

### 长期（3-6月）

1. **智能推荐**
   - 基于用户行为的导师推荐
   - 基于研究方向的导师匹配
   - AI辅助导师选择

2. **数据分析**
   - 导师热度分析
   - 用户浏览行为分析
   - 导师竞争力分析

---

## 📞 技术支持

**测试脚本**: test_tutor_detail_api.py  
**相关文档**: 
- TUTOR_MANAGEMENT_README.md
- TUTOR_SEARCH_API_DOCUMENTATION.md
- TUTOR_SOFT_DELETE_DOCUMENTATION.md

**问题反馈**: 
- 技术问题: 联系后端团队
- 功能建议: 提交issue

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
