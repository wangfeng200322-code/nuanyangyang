# 暖洋洋 Docker部署指南

## 🐳 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                            │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP :80
                       ▼
┌─────────────────────────────────────────────────────────┐
│              前端容器 (Nginx)                             │
│  - 静态文件服务                                           │
│  - API请求代理到后端                                      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP :8000
                       ▼
┌─────────────────────────────────────────────────────────┐
│              后端容器 (FastAPI + Python)                  │
│  - LangChain对话处理                                      │
│  - 健康监测分析                                           │
│  - 多租户管理                                             │
└──────┬────────┬─────────┬──────────────────────────────┘
       │        │         │
       │        │         │
       ▼        ▼         ▼
┌──────────┐ ┌────────┐ ┌──────────┐
│PostgreSQL│ │ Redis  │ │ Qdrant   │
│  数据库   │ │  缓存  │ │ 向量库   │
└──────────┘ └────────┘ └──────────┘
```

## 📦 容器说明

### 1. Frontend容器
- **基础镜像**: nginx:alpine
- **端口**: 80
- **功能**:
  - 提供静态HTML/CSS/JS
  - 反向代理API请求到后端
  - Gzip压缩
  - 安全headers

### 2. Backend容器
- **基础镜像**: ubuntu:22.04
- **端口**: 8000
- **功能**:
  - FastAPI应用服务器
  - LangChain对话处理
  - 多租户数据隔离
  - 健康监测分析

### 3. PostgreSQL容器
- **镜像**: postgres:15-alpine
- **端口**: 5432
- **数据持久化**: postgres-data卷

### 4. Redis容器
- **镜像**: redis:7-alpine
- **端口**: 6379
- **数据持久化**: redis-data卷

### 5. Qdrant容器
- **镜像**: qdrant/qdrant:latest
- **端口**: 6333, 6334
- **数据持久化**: qdrant-data卷

---

## 🚀 快速部署

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存
- 至少10GB可用磁盘空间

### 步骤1：准备环境变量

创建 `.env.prod` 文件：
```env
# API密钥
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key  # 可选

# 数据库配置
POSTGRES_USER=nuanyangyang
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=nuanyangyang

# Embedding模型
EMBEDDING_MODEL=bge-m3
```

### 步骤2：构建镜像

```bash
# 构建所有镜像
docker-compose -f docker-compose.prod.yml build

# 或分别构建
docker build -f Dockerfile.backend -t nuanyangyang-backend .
docker build -f Dockerfile.frontend -t nuanyangyang-frontend .
```

### 步骤3：启动服务

```bash
# 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 步骤4：初始化数据库

```bash
# 数据库会自动执行schema.sql初始化
# 如需手动执行：
docker exec -it nuanyangyang-postgres psql -U nuanyangyang -d nuanyangyang -f /docker-entrypoint-initdb.d/schema.sql
```

### 步骤5：访问应用

- **前端**: http://localhost
- **后端API**: http://localhost/api/
- **健康检查**: http://localhost/api/health
- **Qdrant UI**: http://localhost:6333/dashboard

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| DEEPSEEK_API_KEY | DeepSeek API密钥 | - | ✅ |
| OPENAI_API_KEY | OpenAI API密钥 | - | ❌ |
| POSTGRES_USER | 数据库用户名 | nuanyangyang | ✅ |
| POSTGRES_PASSWORD | 数据库密码 | nuanyangyang123 | ✅ |
| POSTGRES_DB | 数据库名称 | nuanyangyang | ✅ |
| EMBEDDING_MODEL | Embedding模型 | bge-m3 | ✅ |

### 数据卷

| 卷名 | 用途 | 大小估算 |
|------|------|---------|
| postgres-data | PostgreSQL数据 | 1-10GB |
| redis-data | Redis持久化 | 100MB-1GB |
| qdrant-data | 向量数据 | 1-5GB |
| model-cache | BGE-M3模型缓存 | ~2GB |

---

## 📊 监控与维护

### 健康检查

所有服务都配置了健康检查：

```bash
# 查看健康状态
docker-compose -f docker-compose.prod.yml ps

# 手动检查
curl http://localhost/api/health
```

### 日志管理

```bash
# 查看所有日志
docker-compose -f docker-compose.prod.yml logs

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# 实时跟踪日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

---

## 🔄 更新部署

### 更新应用代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 3. 重启服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 清理旧镜像
docker image prune -f
```

### 滚动更新（零停机）

```bash
# 1. 构建新镜像
docker-compose -f docker-compose.prod.yml build backend

# 2. 逐个重启容器
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=2 backend
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=1 backend
```

---

## 💾 备份与恢复

### 数据库备份

```bash
# 备份PostgreSQL
docker exec nuanyangyang-postgres pg_dump -U nuanyangyang nuanyangyang > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i nuanyangyang-postgres psql -U nuanyangyang nuanyangyang < backup_20240115.sql
```

### 向量数据库备份

```bash
# 备份Qdrant数据
docker cp nuanyangyang-qdrant:/qdrant/storage ./qdrant_backup_$(date +%Y%m%d)

# 恢复
docker cp ./qdrant_backup_20240115 nuanyangyang-qdrant:/qdrant/storage
```

### 完整备份

```bash
# 停止服务
docker-compose -f docker-compose.prod.yml stop

# 备份所有数据卷
docker run --rm -v nuanyangyang_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
docker run --rm -v nuanyangyang_qdrant-data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz /data

# 重启服务
docker-compose -f docker-compose.prod.yml start
```

---

## 🔒 安全加固

### 1. 使用Secrets管理敏感信息

```yaml
# docker-compose.prod.yml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  deepseek_api_key:
    file: ./secrets/deepseek_api_key.txt

services:
  backend:
    secrets:
      - db_password
      - deepseek_api_key
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
```

### 2. 限制容器资源

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 3. 使用非root用户

已在Dockerfile中配置：
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### 4. 网络隔离

```yaml
networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
    internal: true  # 不允许外部访问
```

---

## 🚨 故障排除

### 问题1：容器无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend

# 检查容器状态
docker inspect nuanyangyang-backend
```

### 问题2：数据库连接失败

```bash
# 检查PostgreSQL是否运行
docker-compose -f docker-compose.prod.yml ps postgres

# 测试连接
docker exec -it nuanyangyang-postgres psql -U nuanyangyang -d nuanyangyang
```

### 问题3：内存不足

```bash
# 清理未使用的资源
docker system prune -a

# 增加Docker内存限制（Docker Desktop）
# Settings -> Resources -> Memory: 8GB
```

### 问题4：BGE-M3模型下载失败

```bash
# 手动下载模型
docker exec -it nuanyangyang-backend bash
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

---

## 📈 性能优化

### 1. 使用多阶段构建

```dockerfile
# Dockerfile.backend
FROM ubuntu:22.04 as builder
# 安装依赖...

FROM ubuntu:22.04
COPY --from=builder /app /app
```

### 2. 启用缓存

```bash
# 使用BuildKit
DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml build
```

### 3. 优化镜像大小

```bash
# 查看镜像大小
docker images | grep nuanyangyang

# 分析镜像层
docker history nuanyangyang-backend
```

---

## 🎯 生产环境建议

### 1. 使用Nginx作为反向代理

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
}

server {
    listen 443 ssl http2;
    server_name nuanyangyang.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://frontend;
    }
    
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### 2. 使用Docker Swarm或Kubernetes

```bash
# Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.prod.yml nuanyangyang

# Kubernetes
kubectl apply -f k8s/
```

### 3. 配置日志收集

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## ✅ 部署检查清单

- [ ] 环境变量已配置
- [ ] API密钥已设置
- [ ] 数据库密码已修改
- [ ] 数据卷已创建
- [ ] 网络已配置
- [ ] 健康检查通过
- [ ] 备份策略已制定
- [ ] 监控已配置
- [ ] 日志已配置
- [ ] SSL证书已配置（生产环境）

---

## 📞 支持

如有问题，请查看：
- 日志: `docker-compose logs`
- 健康检查: `http://localhost/api/health`
- Qdrant UI: `http://localhost:6333/dashboard`
