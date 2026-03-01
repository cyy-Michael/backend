# 导师查询接口快速参考

## 🚀 快速开始

### 基础查询

```bash
# 关键词搜索
GET /api/v1/tutor/search?keyword=人工智能&page=1&page_size=10

# 按姓名查询
GET /api/v1/tutor/search?name=张三&page=1&page_size=10

# 按学校查询
GET /api/v1/tutor/search?school=清华&page=1&page_size=10

# 按院系查询
GET /api/v1/tutor/search?department=计算机&page=1&page_size=10
```

### 高级筛选

```bash
# 按研究方向
GET /api/v1/tutor/search?research_direction=机器学习

# 按职称
GET /api/v1/tutor/search?title=教授

# 按招生类型
GET /api/v1/tutor/search?recruitment_type=academic

# 有课题的导师
GET /api/v1/tutor/search?has_projects=true

# 按标签
GET /api/v1/tutor/search?tags=AI,机器学习

# 按论文数量
GET /api/v1/tutor/search?min_papers=10&max_papers=50
```

### 组合查询

```bash
GET /api/v1/tutor/search?school=清华&department=计算机&title=教授&research_direction=人工智能&has_projects=true&min_papers=10&sort_by=paper_count&sort_order=desc&page=1&page_size=20
```

### 获取筛选选项

```bash
# 获取所有筛选选项
GET /api/v1/tutor/filter-options

# 获取指定学校的院系
GET /api/v1/tutor/filter-options?school=清华大学
```

---

## 📋 参数速查表

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| keyword | string | 关键词搜索 | `人工智能` |
| name | string | 姓名 | `张三` |
| school | string | 学校 | `清华` |
| department | string | 院系 | `计算机` |
| research_direction | string | 研究方向 | `机器学习` |
| title | string | 职称 | `教授` |
| recruitment_type | string | 招生类型 | `academic`/`professional`/`both` |
| has_projects | boolean | 是否有课题 | `true`/`false` |
| has_funding | boolean | 是否有经费 | `true`/`false` |
| tags | string | 标签（逗号分隔） | `AI,机器学习` |
| min_papers | integer | 最少论文数 | `10` |
| max_papers | integer | 最多论文数 | `50` |
| min_projects | integer | 最少项目数 | `5` |
| max_projects | integer | 最多项目数 | `20` |
| page | integer | 页码 | `1` |
| page_size | integer | 每页数量 | `10` |
| sort_by | string | 排序字段 | `created_at`/`paper_count` |
| sort_order | string | 排序方向 | `asc`/`desc` |

---

## 💻 代码示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 基础查询
response = requests.get(
    f"{BASE_URL}/tutor/search",
    params={"keyword": "人工智能", "page": 1, "page_size": 10}
)

# 高级筛选
response = requests.get(
    f"{BASE_URL}/tutor/search",
    params={
        "school": "清华",
        "department": "计算机",
        "title": "教授",
        "research_direction": "人工智能",
        "recruitment_type": "academic",
        "has_projects": True,
        "min_papers": 10,
        "tags": "AI,机器学习",
        "sort_by": "paper_count",
        "sort_order": "desc",
        "page": 1,
        "page_size": 20
    }
)

# 获取筛选选项
options = requests.get(f"{BASE_URL}/tutor/filter-options")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 基础查询
const response = await fetch(
  `${BASE_URL}/tutor/search?keyword=人工智能&page=1&page_size=10`
);

// 高级筛选
const params = new URLSearchParams({
  school: '清华',
  department: '计算机',
  title: '教授',
  research_direction: '人工智能',
  recruitment_type: 'academic',
  has_projects: true,
  min_papers: 10,
  tags: 'AI,机器学习',
  sort_by: 'paper_count',
  sort_order: 'desc',
  page: 1,
  page_size: 20
});

const response = await fetch(`${BASE_URL}/tutor/search?${params}`);
```

---

## 📊 响应格式

```json
{
  "code": 200,
  "message": "查询导师列表成功",
  "data": {
    "list": [
      {
        "id": "tutor_123",
        "name": "张三",
        "title": "教授",
        "school": "清华大学",
        "department": "计算机科学与技术系",
        "research_direction": "人工智能、机器学习",
        "tags": ["AI", "机器学习"],
        "avatar": "https://...",
        "paper_count": 25,
        "project_count": 8,
        "recruitment_type": "both",
        "has_funding": true
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 10,
    "total_pages": 15
  }
}
```

---

## 🎯 常用查询场景

### 1. 查找有课题的学硕导师
```
?recruitment_type=academic&has_projects=true
```

### 2. 查找论文多的教授（排序）
```
?title=教授&min_papers=20&sort_by=paper_count&sort_order=desc
```

### 3. 查找特定学校和专业
```
?school=清华&department=计算机&research_direction=人工智能
```

### 4. 查找有经费的导师
```
?has_funding=true&has_projects=true
```

### 5. 按标签查找
```
?tags=深度学习,计算机视觉
```

---

## ⚡ 测试命令

```bash
# 运行测试
cd backend
python test_tutor_search_api.py

# 测试覆盖：
# ✅ 基础查询（关键词、姓名、学校、院系）
# ✅ 高级筛选（研究方向、职称、招生类型、课题、标签、论文数）
# ✅ 组合查询
# ✅ 排序功能
# ✅ 分页功能
# ✅ 筛选选项
# ✅ 边界情况
```

---

## 🔑 排序字段

| 字段 | 说明 |
|------|------|
| created_at | 创建时间（默认） |
| updated_at | 更新时间 |
| name | 姓名 |
| paper_count | 论文数量 |
| project_count | 项目数量 |

---

## 📝 招生类型

| 值 | 说明 |
|----|------|
| academic | 学硕 |
| professional | 专硕 |
| both | 学硕+专硕 |

---

## ⚠️ 注意事项

1. **分页限制**: 每页最多100条
2. **查询性能**: 避免不带条件的大量查询
3. **软删除**: 自动过滤已删除导师
4. **登录状态**: 登录后可获取收藏状态

---

## 🐛 常见问题

**Q: 如何搜索多个标签？**  
A: 使用逗号分隔，如 `tags=AI,机器学习`

**Q: 如何按论文数排序？**  
A: 使用 `sort_by=paper_count&sort_order=desc`

**Q: 如何查找有课题的导师？**  
A: 使用 `has_projects=true`

**Q: 如何获取可用的筛选选项？**  
A: 调用 `/tutor/filter-options` 接口

---

**快速参考版本**: v1.0.0  
**对应完整文档**: TUTOR_SEARCH_API_DOCUMENTATION.md
