# 导师查询接口文档

## 📋 概述

本文档说明导师信息查询功能，包括基础模糊查询和高级筛选功能，适用于普通用户查询导师信息。

**版本**: v1.0.0  
**最后更新**: 2024-03-01

---

## 🚀 功能特性

### 1. 基础查询
- ✅ 关键词搜索（姓名/研究方向/院校/专业）
- ✅ 按姓名模糊查询
- ✅ 按学校模糊查询
- ✅ 按院系模糊查询

### 2. 高级筛选
- ✅ 按研究方向筛选
- ✅ 按职称筛选（教授/副教授/讲师等）
- ✅ 按招生类型筛选（学硕/专硕/都招）
- ✅ 按是否有课题筛选
- ✅ 按是否有科研经费筛选
- ✅ 按标签筛选（支持多标签）
- ✅ 按论文数量范围筛选
- ✅ 按项目数量范围筛选

### 3. 分页和排序
- ✅ 分页查询（支持自定义每页数量）
- ✅ 多字段排序（创建时间/更新时间/姓名/论文数/项目数）
- ✅ 升序/降序排序

### 4. 筛选选项
- ✅ 获取可用的学校列表
- ✅ 获取可用的院系列表
- ✅ 获取可用的职称列表
- ✅ 获取热门研究方向
- ✅ 获取热门标签

---

## 📌 接口详情

### 1. 导师高级查询

**接口地址**: `GET /api/v1/tutor/search`

**功能**: 支持基础查询和高级筛选的导师搜索

**权限**: 公开接口（登录可获取收藏状态）

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词（姓名/研究方向/院校/专业） |
| name | string | 否 | 导师姓名（模糊匹配） |
| school | string | 否 | 学校名称（模糊匹配） |
| department | string | 否 | 院系名称（模糊匹配） |
| research_direction | string | 否 | 研究方向（模糊匹配） |
| title | string | 否 | 职称（模糊匹配） |
| recruitment_type | string | 否 | 招生类型：academic(学硕)/professional(专硕)/both(都招) |
| has_projects | boolean | 否 | 是否有课题/项目 |
| has_funding | boolean | 否 | 是否有科研经费 |
| tags | string | 否 | 标签列表（逗号分隔，任意匹配） |
| min_papers | integer | 否 | 最少论文数量 |
| max_papers | integer | 否 | 最多论文数量 |
| min_projects | integer | 否 | 最少项目数量 |
| max_projects | integer | 否 | 最多项目数量 |
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认10，最大100 |
| sort_by | string | 否 | 排序字段：created_at/updated_at/name/paper_count/project_count，默认created_at |
| sort_order | string | 否 | 排序方向：asc/desc，默认desc |

#### 响应示例

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
        "tags": ["AI", "机器学习", "深度学习"],
        "avatar": "https://example.com/avatar.jpg",
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

#### 使用示例

**Python**:
```python
import requests

# 基础查询
response = requests.get(
    "http://localhost:8000/api/v1/tutor/search",
    params={
        "keyword": "人工智能",
        "page": 1,
        "page_size": 10
    }
)

# 高级筛选
response = requests.get(
    "http://localhost:8000/api/v1/tutor/search",
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
```

**JavaScript**:
```javascript
// 基础查询
const response = await fetch(
  'http://localhost:8000/api/v1/tutor/search?keyword=人工智能&page=1&page_size=10'
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

const response = await fetch(
  `http://localhost:8000/api/v1/tutor/search?${params}`
);
```

**curl**:
```bash
# 基础查询
curl "http://localhost:8000/api/v1/tutor/search?keyword=人工智能&page=1&page_size=10"

# 高级筛选
curl "http://localhost:8000/api/v1/tutor/search?school=清华&department=计算机&title=教授&research_direction=人工智能&recruitment_type=academic&has_projects=true&min_papers=10&tags=AI,机器学习&sort_by=paper_count&sort_order=desc&page=1&page_size=20"
```

---

### 2. 获取筛选选项

**接口地址**: `GET /api/v1/tutor/filter-options`

**功能**: 获取导师筛选的可选项（学校、院系、职称等）

**权限**: 公开接口

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| school | string | 否 | 学校名称（获取该学校的院系列表） |

#### 响应示例

```json
{
  "code": 200,
  "message": "获取筛选选项成功",
  "data": {
    "schools": [
      "清华大学",
      "北京大学",
      "复旦大学",
      "上海交通大学"
    ],
    "departments": [
      "计算机科学与技术系",
      "软件学院",
      "信息科学技术学院"
    ],
    "titles": [
      "教授",
      "副教授",
      "讲师",
      "助理教授"
    ],
    "research_directions": [
      "人工智能",
      "机器学习",
      "计算机视觉",
      "自然语言处理"
    ],
    "tags": [
      "AI",
      "机器学习",
      "深度学习",
      "计算机视觉"
    ],
    "recruitment_types": [
      {"value": "academic", "label": "学硕"},
      {"value": "professional", "label": "专硕"},
      {"value": "both", "label": "学硕+专硕"}
    ]
  }
}
```

#### 使用示例

**Python**:
```python
import requests

# 获取所有筛选选项
response = requests.get(
    "http://localhost:8000/api/v1/tutor/filter-options"
)

# 获取指定学校的院系列表
response = requests.get(
    "http://localhost:8000/api/v1/tutor/filter-options",
    params={"school": "清华大学"}
)
```

**JavaScript**:
```javascript
// 获取所有筛选选项
const response = await fetch(
  'http://localhost:8000/api/v1/tutor/filter-options'
);

// 获取指定学校的院系列表
const response = await fetch(
  'http://localhost:8000/api/v1/tutor/filter-options?school=清华大学'
);
```

---

## 🔍 查询场景示例

### 场景1: 查找清华大学计算机系的AI教授

```python
params = {
    "school": "清华",
    "department": "计算机",
    "research_direction": "人工智能",
    "title": "教授",
    "page": 1,
    "page_size": 10
}
```

### 场景2: 查找有课题的学硕导师

```python
params = {
    "recruitment_type": "academic",
    "has_projects": True,
    "page": 1,
    "page_size": 20
}
```

### 场景3: 查找论文多的导师（按论文数排序）

```python
params = {
    "min_papers": 20,
    "sort_by": "paper_count",
    "sort_order": "desc",
    "page": 1,
    "page_size": 10
}
```

### 场景4: 查找特定标签的导师

```python
params = {
    "tags": "深度学习,计算机视觉",
    "page": 1,
    "page_size": 10
}
```

### 场景5: 组合查询

```python
params = {
    "school": "清华",
    "department": "计算机",
    "title": "教授",
    "research_direction": "人工智能",
    "recruitment_type": "both",
    "has_projects": True,
    "has_funding": True,
    "min_papers": 10,
    "tags": "AI,机器学习",
    "sort_by": "paper_count",
    "sort_order": "desc",
    "page": 1,
    "page_size": 20
}
```

---

## 📊 数据库字段说明

### tutors 集合

查询接口使用的主要字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 导师ID |
| name | string | 导师姓名 |
| title | string | 职称 |
| school_name | string | 学校名称 |
| department_name | string | 院系名称 |
| research_direction | string | 研究方向 |
| tags | array | 标签列表 |
| avatar_url | string | 头像URL |
| paper_count | integer | 论文数量 |
| project_count | integer | 项目数量 |
| recruitment_type | string | 招生类型 |
| has_funding | boolean | 是否有科研经费 |
| is_deleted | boolean | 是否已删除 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 索引建议

```javascript
// 文本搜索索引
db.tutors.createIndex({
  "name": "text",
  "research_direction": "text",
  "school_name": "text",
  "department_name": "text"
})

// 常用查询字段索引
db.tutors.createIndex({ "is_deleted": 1 })
db.tutors.createIndex({ "school_name": 1 })
db.tutors.createIndex({ "department_name": 1 })
db.tutors.createIndex({ "title": 1 })
db.tutors.createIndex({ "recruitment_type": 1 })
db.tutors.createIndex({ "tags": 1 })

// 复合索引
db.tutors.createIndex({ "is_deleted": 1, "created_at": -1 })
db.tutors.createIndex({ "school_name": 1, "department_name": 1 })

// 排序字段索引
db.tutors.createIndex({ "paper_count": -1 })
db.tutors.createIndex({ "project_count": -1 })
```

---

## ⚡ 性能优化

### 1. 查询优化

**使用索引**:
- 确保常用查询字段都有索引
- 使用复合索引优化组合查询
- 定期分析慢查询并优化

**分页优化**:
- 限制最大每页数量（100条）
- 避免查询超大页码
- 考虑使用游标分页

**缓存策略**:
```python
# 缓存热门查询结果
from functools import lru_cache

@lru_cache(maxsize=100)
def get_popular_tutors(school, department):
    # 查询逻辑
    pass
```

### 2. 响应优化

**字段选择**:
- 列表查询只返回必要字段
- 避免返回大字段（如bio、论文详情等）
- 使用投影减少数据传输

**数据压缩**:
- 启用GZip压缩
- 减少JSON响应大小

---

## 🧪 测试指南

### 运行测试

```bash
cd backend
python test_tutor_search_api.py
```

### 测试覆盖

测试脚本包含以下场景：

1. ✅ 基础查询 - 关键词搜索
2. ✅ 基础查询 - 按姓名查询
3. ✅ 基础查询 - 按学校查询
4. ✅ 基础查询 - 按院系查询
5. ✅ 高级筛选 - 按研究方向
6. ✅ 高级筛选 - 按职称
7. ✅ 高级筛选 - 按招生类型
8. ✅ 高级筛选 - 是否有课题
9. ✅ 高级筛选 - 标签筛选
10. ✅ 高级筛选 - 论文数量范围
11. ✅ 组合查询
12. ✅ 排序功能
13. ✅ 分页功能
14. ✅ 获取筛选选项
15. ✅ 边界情况处理

---

## ⚠️ 注意事项

### 1. 查询性能

**大数据量查询**:
- 避免不带条件的查询
- 限制每页数量
- 使用合适的索引

**复杂查询**:
- 组合条件过多可能影响性能
- 考虑使用缓存
- 监控慢查询

### 2. 数据一致性

**软删除过滤**:
- 所有查询自动过滤已删除数据
- 使用 `is_deleted` 字段标记

**数据更新**:
- 导师信息更新后自动反映在查询结果中
- 论文/项目数量需要定期同步

### 3. 用户体验

**搜索建议**:
- 提供搜索关键词建议
- 显示热门搜索
- 记录搜索历史

**筛选引导**:
- 显示每个筛选条件的结果数量
- 提供筛选条件重置功能
- 保存用户筛选偏好

---

## 📈 后续优化

### 短期（1-2周）

1. **搜索优化**
   - 添加全文搜索
   - 实现搜索建议
   - 添加搜索历史

2. **筛选增强**
   - 添加更多筛选维度
   - 实现筛选条件保存
   - 添加热门筛选推荐

### 中期（1-2月）

1. **性能优化**
   - 实现查询缓存
   - 优化数据库索引
   - 添加查询日志分析

2. **功能增强**
   - 添加导师推荐
   - 实现相似导师查找
   - 添加导师对比功能

### 长期（3-6月）

1. **智能搜索**
   - AI辅助搜索
   - 自然语言查询
   - 个性化推荐

2. **数据分析**
   - 搜索热度分析
   - 用户行为分析
   - 导师热度排行

---

## 📞 技术支持

**测试脚本**: test_tutor_search_api.py  
**相关文档**: 
- TUTOR_MANAGEMENT_README.md
- TUTOR_SOFT_DELETE_DOCUMENTATION.md

**问题反馈**: 
- 技术问题: 联系后端团队
- 功能建议: 提交issue

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
