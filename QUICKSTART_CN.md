# 暖洋洋 - 中文模式快速启动指南

## 🎯 当前配置：仅中文模式

您当前的配置只需要DeepSeek API（已配置），可以直接测试中文对话功能！

> [!NOTE]
> OpenAI API密钥是可选的，仅在使用荷兰语/英语时需要。

---

## 🚀 快速启动（3步）

### 步骤1：启动Docker服务

```powershell
cd e:\AI\nuanyangyang
docker-compose up -d
```

**等待10秒**让服务完全启动。

### 步骤2：初始化数据库

```powershell
python -c "from database import init_db; init_db()"
```

### 步骤3：启动应用

```powershell
python app.py
```

然后访问：http://localhost:8000

---

## 💬 测试中文对话

### 测试1：基础问候
```
输入：你好，我是王奶奶
预期：温暖的中文回复，记住您的名字
```

### 测试2：健康咨询
```
输入：我今天有点头晕
预期：关心的询问，引导您提供更多信息
```

### 测试3：记忆测试
```
第一轮：我今年75岁了
第二轮：我多大年纪了？
预期：能记住您的年龄
```

---

## 📊 当前功能状态

### ✅ 可用功能（中文模式）
- ✅ 中文对话（DeepSeek模型）
- ✅ 会话记忆（Redis，最近10条）
- ✅ 数据持久化（PostgreSQL）
- ⚠️ RAG检索（需要OpenAI API，当前不可用）

### ⏸️ 暂不可用
- ❌ 荷兰语对话（需要OpenAI API）
- ❌ 英语对话（需要OpenAI API）
- ❌ 向量检索（需要OpenAI Embeddings）

---

## 🔧 如果想启用完整功能

### 添加OpenAI API密钥

1. 获取API密钥：https://platform.openai.com/api-keys
2. 编辑 `.env` 文件：

```env
# 取消注释并填入您的密钥
OPENAI_API_KEY=sk-your-actual-key-here
```

3. 重启应用

---

## ⚠️ 故障排除

### Docker服务未启动
```powershell
# 检查Docker
docker ps

# 如果没有容器运行
docker-compose up -d
```

### 端口被占用
```powershell
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :6333
netstat -ano | findstr :5432
netstat -ano | findstr :6379
```

### 数据库连接错误
```powershell
# 查看PostgreSQL日志
docker logs nuanyangyang-postgres-1

# 重新初始化
python -c "from database import init_db; init_db()"
```

---

## 📝 注意事项

1. **RAG功能暂时不可用**：由于未配置OpenAI API，向量检索功能将被跳过。这意味着系统不会检索历史相似对话，但会话记忆（最近10条）仍然有效。

2. **只能使用中文**：如果输入荷兰语或英语，系统会提示需要配置OpenAI API密钥。

3. **数据仍会保存**：所有对话仍会保存到PostgreSQL数据库，只是不会生成向量embeddings。

---

## 🎉 开始测试吧！

现在您可以：
1. 启动Docker服务
2. 初始化数据库
3. 运行应用
4. 用中文聊天测试

祝测试愉快！🌟
