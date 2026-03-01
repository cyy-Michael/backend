# 导师信息导出接口文档

## 📋 概述

本文档说明导师信息导出功能，支持将导师列表导出为Excel和CSV格式，仅限管理员使用。

**版本**: v1.0.0  
**最后更新**: 2024-03-01

---

## 🚀 功能特性

### 1. 支持的导出格式
- ✅ **Excel格式**（.xlsx）
  - 带表头样式（蓝色背景、白色字体）
  - 自动调整列宽
  - 支持中文
  
- ✅ **CSV格式**（.csv）
  - UTF-8编码（带BOM）
  - 解决Excel打开中文乱码问题
  - 轻量级文件

### 2. 筛选条件
- 关键词搜索（姓名/研究方向/学校/院系）
- 按学校筛选
- 按院系筛选
- 按职称筛选

### 3. 导出限制
- 单次最多导出10000条记录
- 默认导出1000条记录
- 支持自定义导出数量

### 4. 导出字段
- ID、姓名、职称
- 学校、院系
- 研究方向、标签
- 邮箱、电话、个人主页
- 招生类型、是否有经费
- 论文数量、项目数量
- 创建时间、更新时间

### 5. 权限控制
- 仅管理员可访问
- 需要JWT认证
- 操作日志记录

---

## 📌 接口详情

### 1. 导出导师信息

**接口地址**: `GET /api/v1/tutor/admin/export`

**功能**: 将导师列表导出为Excel或CSV格式

**权限**: 管理员

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| format | string | 否 | excel | 导出格式：excel 或 csv |
| keyword | string | 否 | - | 搜索关键词 |
| school | string | 否 | - | 学校筛选 |
| department | string | 否 | - | 院系筛选 |
| title | string | 否 | - | 职称筛选 |
| limit | integer | 否 | 1000 | 最大导出数量（1-10000） |

#### 请求头

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | string | 是 | Bearer {admin_token} |

#### 响应

**成功（200）**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`（Excel）
- Content-Type: `text/csv; charset=utf-8`（CSV）
- Content-Disposition: `attachment; filename*=UTF-8''导师信息_20240301_120000.xlsx`

**导师不存在（404）**:
```json
{
  "code": 404,
  "message": "没有符合条件的导师数据",
  "data": {
    "code": "NO_DATA",
    "message": "没有符合条件的导师数据"
  }
}
```

**权限不足（403）**:
```json
{
  "code": 403,
  "message": "需要管理员权限才能访问此资源",
  "data": {
    "code": "ADMIN_REQUIRED",
    "message": "需要管理员权限才能访问此资源"
  }
}
```

---

### 2. 获取导出统计

**接口地址**: `GET /api/v1/tutor/admin/export-stats`

**功能**: 获取符合条件的导师数量，用于导出前预览

**权限**: 管理员

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| school | string | 否 | 学校筛选 |
| department | string | 否 | 院系筛选 |
| title | string | 否 | 职称筛选 |

#### 响应示例

```json
{
  "code": 200,
  "message": "获取导出统计成功",
  "data": {
    "total_count": 1523,
    "max_export_limit": 10000,
    "can_export": true,
    "school_stats": [
      {"school": "清华大学", "count": 256},
      {"school": "北京大学", "count": 198},
      {"school": "复旦大学", "count": 145}
    ],
    "title_stats": [
      {"title": "教授", "count": 589},
      {"title": "副教授", "count": 456},
      {"title": "讲师", "count": 478}
    ]
  }
}
```

---

## 💻 使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. 登录获取管理员token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"code": "admin_wx_code"}
)
token = login_response.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 获取导出统计
stats_response = requests.get(
    f"{BASE_URL}/tutor/admin/export-stats",
    params={"school": "清华"},
    headers=headers
)
stats = stats_response.json()["data"]
print(f"符合条件的导师数量: {stats['total_count']}")

# 3. 导出Excel
excel_response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "excel",
        "school": "清华",
        "title": "教授",
        "limit": 500
    },
    headers=headers
)

if excel_response.status_code == 200:
    with open("导师信息.xlsx", "wb") as f:
        f.write(excel_response.content)
    print("Excel文件已保存")

# 4. 导出CSV
csv_response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "csv",
        "keyword": "人工智能",
        "limit": 500
    },
    headers=headers
)

if csv_response.status_code == 200:
    with open("导师信息.csv", "wb") as f:
        f.write(csv_response.content)
    print("CSV文件已保存")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// 1. 登录获取管理员token
const loginRes = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({code: 'admin_wx_code'})
});
const {token} = (await loginRes.json()).data;

// 2. 获取导出统计
const statsRes = await fetch(
  `${BASE_URL}/tutor/admin/export-stats?school=清华`,
  {headers: {'Authorization': `Bearer ${token}`}}
);
const stats = (await statsRes.json()).data;
console.log(`符合条件的导师数量: ${stats.total_count}`);

// 3. 导出Excel
const excelRes = await fetch(
  `${BASE_URL}/tutor/admin/export?format=excel&school=清华&title=教授&limit=500`,
  {headers: {'Authorization': `Bearer ${token}`}}
);

if (excelRes.ok) {
  const blob = await excelRes.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '导师信息.xlsx';
  a.click();
}

// 4. 导出CSV
const csvRes = await fetch(
  `${BASE_URL}/tutor/admin/export?format=csv&keyword=人工智能&limit=500`,
  {headers: {'Authorization': `Bearer ${token}`}}
);

if (csvRes.ok) {
  const blob = await csvRes.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '导师信息.csv';
  a.click();
}
```

### curl

```bash
# 1. 登录获取token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"code":"admin_wx_code"}' | jq -r '.data.token')

# 2. 获取导出统计
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tutor/admin/export-stats?school=清华"

# 3. 导出Excel
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tutor/admin/export?format=excel&school=清华&limit=500" \
  -o 导师信息.xlsx

# 4. 导出CSV
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tutor/admin/export?format=csv&keyword=人工智能&limit=500" \
  -o 导师信息.csv
```

---

## 📊 导出字段说明

### Excel/CSV包含的字段

| 字段 | 说明 | 示例 |
|------|------|------|
| ID | 导师ID | tutor_123 |
| 姓名 | 导师姓名 | 张三 |
| 职称 | 职称 | 教授 |
| 学校 | 学校名称 | 清华大学 |
| 院系 | 院系名称 | 计算机科学与技术系 |
| 研究方向 | 研究方向 | 人工智能、机器学习 |
| 邮箱 | 邮箱地址 | zhangsan@example.com |
| 电话 | 电话号码 | 010-12345678 |
| 个人主页 | 个人主页URL | https://... |
| 招生类型 | 招生类型 | 学硕+专硕 |
| 是否有经费 | 是否有科研经费 | 是/否 |
| 论文数量 | 论文数量 | 25 |
| 项目数量 | 项目数量 | 8 |
| 标签 | 标签列表 | AI, 机器学习, 深度学习 |
| 创建时间 | 创建时间 | 2023-01-01 12:00:00 |
| 更新时间 | 更新时间 | 2024-03-01 12:00:00 |

---

## 🔍 使用场景

### 场景1: 导出所有导师信息

管理员需要导出所有导师的完整信息用于备份或分析。

```python
# 先查看数量
stats = requests.get(
    f"{BASE_URL}/tutor/admin/export-stats",
    headers=headers
).json()["data"]

print(f"总共 {stats['total_count']} 个导师")

# 导出Excel
response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={"format": "excel", "limit": 10000},
    headers=headers
)

with open("所有导师信息.xlsx", "wb") as f:
    f.write(response.content)
```

### 场景2: 导出特定学校的导师

导出某个学校的所有导师信息。

```python
response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "excel",
        "school": "清华大学",
        "limit": 1000
    },
    headers=headers
)

with open("清华大学导师.xlsx", "wb") as f:
    f.write(response.content)
```

### 场景3: 导出特定研究方向的导师

导出研究某个方向的导师列表。

```python
response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "csv",
        "keyword": "人工智能",
        "limit": 500
    },
    headers=headers
)

with open("人工智能导师.csv", "wb") as f:
    f.write(response.content)
```

### 场景4: 导出教授列表

导出所有教授的信息。

```python
response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "excel",
        "title": "教授",
        "limit": 2000
    },
    headers=headers
)

with open("教授列表.xlsx", "wb") as f:
    f.write(response.content)
```

### 场景5: 组合筛选导出

组合多个条件导出特定导师。

```python
response = requests.get(
    f"{BASE_URL}/tutor/admin/export",
    params={
        "format": "excel",
        "school": "清华",
        "department": "计算机",
        "title": "教授",
        "keyword": "人工智能",
        "limit": 100
    },
    headers=headers
)

with open("清华计算机AI教授.xlsx", "wb") as f:
    f.write(response.content)
```

---

## ⚡ 性能优化

### 1. 数据库查询优化

**使用索引**:
```javascript
// 常用查询字段索引
db.tutors.createIndex({ "is_deleted": 1 })
db.tutors.createIndex({ "school_name": 1 })
db.tutors.createIndex({ "department_name": 1 })
db.tutors.createIndex({ "title": 1 })

// 复合索引
db.tutors.createIndex({ "is_deleted": 1, "school_name": 1 })
```

### 2. 导出优化

**分批导出**:
```python
# 对于大量数据，建议分批导出
total_count = stats['total_count']
batch_size = 1000

for i in range(0, total_count, batch_size):
    response = requests.get(
        f"{BASE_URL}/tutor/admin/export",
        params={
            "format": "excel",
            "limit": batch_size,
            "skip": i  # 需要添加skip参数支持
        },
        headers=headers
    )
    # 处理每批数据
```

### 3. 文件大小优化

**Excel优化**:
- 限制导出数量
- 移除不必要的字段
- 压缩文件

**CSV优化**:
- CSV文件更小
- 适合大量数据导出
- 加载速度更快

---

## 🧪 测试指南

### 运行测试

```bash
cd backend
python test_tutor_export_api.py
```

### 测试覆盖

测试脚本包含14个测试场景：

1. ✅ 获取导出统计（无筛选）
2. ✅ 获取导出统计（带筛选）
3. ✅ 导出Excel（无筛选）
4. ✅ 导出CSV（无筛选）
5. ✅ 导出Excel（带筛选）
6. ✅ 导出CSV（带筛选）
7. ✅ 导出数量限制
8. ✅ 无效格式处理
9. ✅ 无数据处理
10. ✅ 非管理员访问拒绝
11. ✅ 未登录访问拒绝
12. ✅ 响应时间测试

---

## ⚠️ 注意事项

### 1. 权限控制

- **管理员验证**: 所有导出接口都需要管理员权限
- **Token验证**: 需要有效的JWT token
- **操作日志**: 所有导出操作都会记录日志

### 2. 数据限制

- **最大导出**: 单次最多10000条记录
- **默认数量**: 默认导出1000条
- **建议**: 大量数据建议分批导出

### 3. 文件格式

**Excel**:
- 文件较大
- 支持样式
- 适合查看和编辑

**CSV**:
- 文件较小
- 纯文本格式
- 适合数据处理

### 4. 中文支持

**Excel**:
- 原生支持中文
- 无需特殊处理

**CSV**:
- 使用UTF-8编码
- 添加BOM解决Excel乱码
- 建议使用专业工具打开

### 5. 性能考虑

**响应时间**:
- 100条记录: < 1秒
- 1000条记录: 1-3秒
- 10000条记录: 5-10秒

**建议**:
- 避免一次性导出过多数据
- 使用筛选条件减少数据量
- 考虑异步导出（未来优化）

---

## 📈 后续优化

### 短期（1-2周）

1. **功能增强**
   - 添加自定义字段选择
   - 支持导出模板
   - 添加导出历史记录

2. **性能优化**
   - 实现异步导出
   - 添加导出队列
   - 支持断点续传

### 中期（1-2月）

1. **格式扩展**
   - 支持PDF格式
   - 支持JSON格式
   - 支持XML格式

2. **高级功能**
   - 定时导出任务
   - 邮件发送导出文件
   - 导出数据加密

### 长期（3-6月）

1. **智能导出**
   - AI推荐导出字段
   - 智能数据分析
   - 可视化报表生成

2. **集成功能**
   - 与BI工具集成
   - 与数据仓库集成
   - API批量导出

---

## 📞 技术支持

**测试脚本**: test_tutor_export_api.py  
**依赖库**: openpyxl, pandas, motor

**相关文档**: 
- TUTOR_MANAGEMENT_README.md
- TUTOR_SEARCH_API_DOCUMENTATION.md

**问题反馈**: 
- 技术问题: 联系后端团队
- 功能建议: 提交issue

---

**文档版本**: v1.0.0  
**最后更新**: 2024-03-01  
**维护者**: Backend Team
