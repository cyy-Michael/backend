# 导师详情接口快速参考

## 🚀 快速开始

### 基础用法

```bash
# 获取导师详情（未登录）
GET /api/v1/tutor/detail/{tutor_id}

# 获取导师详情（已登录，可获取收藏状态）
GET /api/v1/tutor/detail/{tutor_id}
Authorization: Bearer {token}
```

---

## 📋 返回的信息

| 类别 | 包含内容 |
|------|---------|
| 基本信息 | 姓名、职称、学校、院系、头像、简介、研究方向、标签 |
| 联系方式 | 邮箱、电话、个人主页 |
| 招生信息 | 招生类型、是否有科研经费 |
| 学术成果 | 论文列表、项目列表、成果总结 |
| 社交信息 | 社交账号列表 |
| 学生信息 | 指导的学生列表 |
| 合作信息 | 合作者列表 |
| 风险信息 | 风险提示列表 |
| 统计信息 | 论文数、项目数、学生数 |
| 收藏状态 | 是否已收藏（需登录） |

---

## 💻 代码示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 未登录查询
response = requests.get(f"{BASE_URL}/tutor/detail/tutor_123")
detail = response.json()["data"]

print(f"{detail['name']} - {detail['title']}")
print(f"{detail['school']} {detail['department']}")
print(f"论文: {detail['paper_count']}篇")
print(f"项目: {detail['project_count']}个")

# 登录后查询
login_res = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "wx_code"}
)
token = login_res.json()["data"]["token"]

response = requests.get(
    f"{BASE_URL}/tutor/detail/tutor_123",
    headers={"Authorization": f"Bearer {token}"}
)
detail = response.json()["data"]
print(f"已收藏: {detail['is_collected']}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 未登录查询
const response = await fetch(
  `${BASE_URL}/tutor/detail/tutor_123`
);
const data = await response.json();
const detail = data.data;

console.log(`${detail.name} - ${detail.title}`);
console.log(`${detail.school} ${detail.department}`);
console.log(`论文: ${detail.paper_count}篇`);
console.log(`项目: ${detail.project_count}个`);

// 登录后查询
const loginRes = await fetch(
  `${BASE_URL}/auth/login`,
  {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code: 'wx_code'})
  }
);
const {token} = (await loginRes.json()).data;

const authRes = await fetch(
  `${BASE_URL}/tutor/detail/tutor_123`,
  {
    headers: {'Authorization': `Bearer ${token}`}
  }
);
const authData = await authRes.json();
console.log(`已收藏: ${authData.data.is_collected}`);
```

---

## 📊 响应结构

```json
{
  "code": 200,
  "message": "获取导师详情成功",
  "data": {
    "id": "tutor_123",
    "name": "张三",
    "title": "教授",
    "school": "清华大学",
    "department": "计算机科学与技术系",
    "avatar": "https://...",
    "bio": "个人简介...",
    
    "email": "zhangsan@example.com",
    "phone": "010-12345678",
    "personal_page": "https://...",
    
    "research_direction": "人工智能、机器学习",
    "tags": ["AI", "机器学习"],
    "recruitment_type": "both",
    "has_funding": true,
    
    "paper_count": 25,
    "project_count": 8,
    "student_count": 15,
    
    "papers": [...],
    "projects": [...],
    "students": [...],
    "coops": [...],
    "socials": [...],
    "risks": [...],
    
    "is_collected": false
  }
}
```

---

## 🎯 常用字段

### 基本信息
- `name`: 导师姓名
- `title`: 职称
- `school`: 学校
- `department`: 院系
- `research_direction`: 研究方向

### 统计信息
- `paper_count`: 论文数量
- `project_count`: 项目数量
- `student_count`: 学生数量

### 招生信息
- `recruitment_type`: 
  - `"academic"`: 学硕
  - `"professional"`: 专硕
  - `"both"`: 都招
- `has_funding`: 是否有科研经费

### 论文对象
- `title`: 论文标题
- `authors`: 作者列表
- `journal`: 期刊
- `year`: 年份
- `citations`: 引用数

### 项目对象
- `title`: 项目标题
- `funding`: 资助来源
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status`: 状态（ongoing/completed）

---

## ⚡ 测试命令

```bash
# 运行测试
cd backend
python test_tutor_detail_api.py

# 测试覆盖：
# ✅ 基本信息查询
# ✅ 论文列表
# ✅ 项目列表
# ✅ 学生信息
# ✅ 合作信息
# ✅ 社交信息
# ✅ 收藏状态
# ✅ 错误处理
# ✅ 性能测试
```

---

## 🔍 使用场景

### 1. 查看基本信息
```python
detail = response.json()["data"]
print(f"{detail['name']} - {detail['title']}")
print(f"{detail['school']} {detail['department']}")
```

### 2. 查看学术成果
```python
print(f"论文: {detail['paper_count']}篇")
print(f"项目: {detail['project_count']}个")

for paper in detail['papers'][:5]:
    print(f"{paper['title']} ({paper['year']})")
```

### 3. 查看招生信息
```python
recruitment_map = {
    "academic": "学硕",
    "professional": "专硕",
    "both": "学硕+专硕"
}
print(f"招生: {recruitment_map[detail['recruitment_type']]}")
print(f"经费: {'充足' if detail['has_funding'] else '一般'}")
```

### 4. 联系导师
```python
if detail['email']:
    print(f"邮箱: {detail['email']}")
if detail['phone']:
    print(f"电话: {detail['phone']}")
if detail['personal_page']:
    print(f"主页: {detail['personal_page']}")
```

---

## ⚠️ 注意事项

1. **收藏状态**: 需要登录才能获取真实的收藏状态
2. **软删除**: 已删除的导师返回404
3. **数据完整性**: 某些字段可能为空，需要安全访问
4. **性能**: 包含论文和项目查询，响应时间约500-1000ms

---

## 🐛 常见问题

**Q: 如何获取收藏状态？**  
A: 需要在请求头中添加 `Authorization: Bearer {token}`

**Q: 论文和项目数量有限制吗？**  
A: 论文最多返回100篇，项目最多返回50个

**Q: 导师不存在返回什么？**  
A: 返回404错误，错误码为 `TUTOR_NOT_FOUND`

**Q: 如何优化查询性能？**  
A: 使用数据库索引，考虑缓存热门导师数据

---

**快速参考版本**: v1.0.0  
**对应完整文档**: TUTOR_DETAIL_API_DOCUMENTATION.md
