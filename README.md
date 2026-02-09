# 暖洋洋 (Nuanyangyang) - 老年人陪伴机器人

一个专门为老年人设计的智能陪伴机器人，提供温暖的对话、健康监测和心理关怀。

## 功能特性

- ✅ **多语言支持**：中文、荷兰语、英语
- ✅ **智能对话**：基于LangChain的自然对话
- ✅ **记忆系统**：RAG + Redis双层记忆
- ✅ **健康监测**：基础症状检测（开发中）
- ✅ **个性化**：记住每位老人的偏好

## 技术栈

- **CI/CD**: GitHub Actions + Trivy (容器安全扫描)
- **后端**: FastAPI + LangChain
- **LLM**: DeepSeek (中文) + GPT-4o-mini (荷兰语/英语)
- **向量数据库**: Qdrant
- **关系数据库**: PostgreSQL
- **缓存**: Redis
- **前端**: HTML + JavaScript

## 快速开始

### 1. 环境要求

- Python 3.9+
- Docker & Docker Compose
- OpenAI API Key
- DeepSeek API Key

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv_nuanyangyang

# 激活虚拟环境
# Windows:
venv_nuanyangyang\Scripts\activate
# Linux/Mac:
source venv_nuanyangyang/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑 `.env` 文件，添加您的API密钥：

```env
OPENAI_API_KEY=your_openai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 4. 启动服务

```bash
# 启动Docker服务（Qdrant, PostgreSQL, Redis）
docker-compose up -d

# 等待几秒让服务完全启动
# 然后运行应用
python app.py
```

### 5. 访问应用

打开浏览器访问：http://localhost:8000

## 项目结构

```
nuanyangyang/
├── app.py                      # FastAPI主应用
├── requirements.txt            # Python依赖
├── docker-compose.yml          # Docker服务配置
├── .env                        # 环境变量
├── config/
│   └── settings.py            # 配置管理
├── core/
│   ├── language_router.py     # 语言检测
│   ├── llm_manager.py         # LLM管理
│   └── prompts.py             # Prompt模板
├── agents/
│   └── chat_agent.py          # 对话Agent
├── memory/
│   ├── vector_store.py        # 向量存储（RAG）
│   └── conversation_memory.py # 会话记忆（Redis）
├── database/
│   ├── models.py              # 数据库模型
│   └── crud.py                # 数据库操作
└── static/
    ├── index.html             # 前端页面
    ├── script.js              # 前端脚本
    └── style.css              # 样式文件
```

## 使用说明

### 基础对话

直接在网页输入框中输入消息，系统会：
1. 自动检测语言（中文/荷兰语/英语）
2. 检索相关历史对话
3. 生成温暖、个性化的回复
4. 保存对话到数据库和向量库

### 多语言切换

系统会自动检测您的输入语言：
- 输入中文 → 使用DeepSeek模型
- 输入荷兰语/英语 → 使用GPT-4o-mini模型

### 记忆系统

- **短期记忆**（Redis）：记住最近10条对话，1小时过期
- **长期记忆**（Qdrant）：永久存储，用于RAG检索相似对话

## 开发计划

- [ ] 语音输入/输出
- [ ] 高级健康监测
- [ ] 预警系统
- [ ] 管理后台
- [ ] 移动端适配

## 故障排除

### Docker服务无法启动

```bash
# 检查Docker是否运行
docker ps

# 查看服务日志
docker-compose logs
```

### 数据库连接错误

```bash
# 重新初始化数据库
python -c "from database import init_db; init_db()"
```

### API调用失败

检查 `.env` 文件中的API密钥是否正确配置。

## 许可证

MIT License

## 联系方式

如有问题，请联系开发团队。
