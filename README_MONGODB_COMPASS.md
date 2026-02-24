# 使用MongoDB Compass连接数据库

## MongoDB Compass简介

MongoDB Compass是MongoDB官方提供的图形化数据库管理工具，相比命令行界面更加直观易用。您可以使用它来：

- 可视化查看和管理数据库
- 执行查询操作
- 编辑文档
- 创建和管理索引
- 监控数据库性能

## 连接步骤

### 1. 安装MongoDB Compass

如果您还没有安装MongoDB Compass，请先下载并安装：

- **官方下载地址**: [MongoDB Compass Download](https://www.mongodb.com/try/download/compass)
- 支持Windows、macOS、Linux等多种操作系统

### 2. 启动后端服务

首先确保后端服务已经启动，MongoDB容器正在运行：

```bash
# 在backend目录下执行
./start.sh
```

启动脚本会自动启动MongoDB容器（端口27017）。

### 3. 连接到MongoDB

打开MongoDB Compass，使用以下连接信息：

#### 连接字符串方式（推荐）

```
mongodb://admin:password@localhost:27017/
```

#### 手动填写方式

- **Hostname**: localhost
- **Port**: 27017
- **Authentication**: Username/Password
- **Username**: admin
- **Password**: password
- **Authentication Database**: admin

### 4. 连接成功后

连接成功后，您可以看到以下数据库和集合：

#### 数据库：tutor_db

**主要集合（Collections）**:

- **users**: 用户信息
- **tutors**: 导师基本信息
- **tutor_details**: 导师详细信息
- **schools**: 学校信息
- **departments**: 院系信息
- **favorites**: 收藏记录
- **bookings**: 预约记录
- **match_histories**: 匹配历史
- **projects**: 合作项目
- **project_applications**: 项目申请
- **score_lines**: 分数线信息

## 使用示例

### 查看导师数据

1. 选择 `tutor_db` 数据库
2. 点击 `tutors` 集合
3. 查看导师列表和详细信息

### 执行查询

```javascript
// 查找所有教授职称的导师
{ "title": "教授" }

// 查找特定学校的导师
{ "school_name": "示例大学1" }

// 按研究方向搜索
{ "research_direction": { "$regex": "人工智能", "$options": "i" } }
```

### 查看用户收藏

```javascript
// 查看特定用户的收藏
{ "user_id": "用户ID" }
```

## 注意事项

1. **认证信息**: 用户名 `admin` 和密码 `password` 是在 `.env` 文件中配置的
2. **端口**: 默认使用27017端口，如果需要修改，请同时修改 `.env` 文件和 `docker-compose.yml`
3. **数据持久化**: 数据存储在 `./data/mongodb` 目录下，即使容器重启数据也不会丢失
4. **权限**: 当前配置使用的是管理员账户，具有所有操作权限

## 常见问题

### 连接失败怎么办？

1. 检查MongoDB容器是否正在运行：
   ```bash
   docker ps | grep mongodb
   ```

2. 检查端口是否被占用：
   ```bash
   netstat -an | grep 27017
   ```

3. 检查防火墙设置，确保27017端口已开放

4. 重新启动MongoDB容器：
   ```bash
   docker-compose restart mongodb
   ```

### 如何修改数据库密码？

1. 修改 `.env` 文件中的数据库配置
2. 删除 `./data/mongodb` 目录（注意：这会删除所有数据）
3. 重新运行启动脚本

## 数据备份和恢复

### 备份数据

```bash
# 备份tutor_db数据库
mongodump --uri="mongodb://admin:password@localhost:27017/" --db=tutor_db --out=./backup
```

### 恢复数据

```bash
# 恢复tutor_db数据库
mongorestore --uri="mongodb://admin:password@localhost:27017/" --db=tutor_db ./backup/tutor_db
```

## 相关资源

- [MongoDB Compass官方文档](https://www.mongodb.com/docs/compass/current/)
- [MongoDB查询操作文档](https://www.mongodb.com/docs/manual/crud/)