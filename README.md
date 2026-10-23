# 🧠 RAG 智能知识库问答系统 (RAG Intelligent Knowledge Base)

> 基于 **Vue 3 + Spring Boot 3 + FastAPI + Qdrant** 构建的全栈检索增强生成（RAG）应用。支持多格式文档解析、GPU 加速向量化、语义检索与带引用溯源的大模型问答。

## 📖 项目简介

随着企业私有文档数量的激增，传统的关键词检索难以应对复杂的语义查询，而直接使用大语言模型（LLM）又容易产生“幻觉”且缺乏数据隐私保护。本项目实现了一套完整的 RAG 全栈解决方案，打通了从 **文档上传 -> 文本解析与分块 -> 向量化入库 -> 语义检索 -> 大模型生成 -> 引用溯源** 的全链路闭环。

## ✨ 核心功能与工程亮点

- **🛡️ 安全与数据隔离**：基于 JWT 实现用户登录认证，结合 Spring Boot 拦截器与 `ThreadLocal` 实现多用户间的数据严格隔离。
- **📄 多格式文档解析**：支持 PDF、DOCX、TXT 批量上传。内置多编码探测机制，彻底解决不同文件编码（UTF-8/GBK/UTF-16）导致的乱码与崩溃问题。
- **⚡ GPU 硬件加速**：Python 端接入本地 RTX 3050 显卡，利用 PyTorch 与 CUDA 加速 Embedding 运算，实现千页长文档秒级向量化。
- **🔍 动态维度适配与模型切换**：针对初期英文向量模型（384维）对中文专业文档检索命中率低的问题，**平滑替换为纯中文专精模型 `BAAI/bge-small-zh-v1.5`（512维）**。系统支持动态获取模型维度并无缝重建 Qdrant 集合。
- **📚 精准引用溯源**：大模型不仅生成回答，前端还提供折叠式“参考来源”片段，支持用户核验原文，有效降低幻觉。
- **💻 现代化极简 UI**：基于 Vue 3 + Element Plus 打造，参考 `shadcn/ui` 设计语言，提供快捷提问卡片、流式交互与 Markdown 渲染展示。

## 🏗️ 系统架构

- **前端 (Frontend)**：Vue 3 + TypeScript + Vite + Element Plus + Axios
- **业务后端 (Backend)**：Java 17 + Spring Boot 3 + MyBatis-Plus + MySQL 8
- **AI 服务 (AI Service)**：Python 3.12 + FastAPI + PyTorch + Sentence-Transformers
- **向量数据库 (Vector DB)**：Qdrant
- **大语言模型 (LLM)**：硅基流动 API (Qwen 2.5 72B)
- **容器化 (DevOps)**：Docker + Docker Compose

## 🚀 快速启动

### 1. 环境准备

- Docker Desktop
- JDK 17+
- Node.js 18+
- Python 3.10+ (建议 64位，支持 CUDA)

### 2. 启动基础服务 (Docker)

    cd docker
    docker-compose up -d
    # 启动 MySQL (3306) 与 Qdrant (6333)

### 3. 启动 AI 服务 (Python)

    cd ai-service
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # macOS/Linux
    pip install -r requirements.txt
    python main.py
    # 服务将运行在 http://localhost:18000

### 4. 启动业务后端 (Java)

    cd backend
    # 请确保 MySQL 已启动，且 application.properties 配置正确
    .\mvnw spring-boot:run      # Windows
    # ./mvnw spring-boot:run    # macOS/Linux
    # 服务将运行在 http://localhost:18080

### 5. 启动前端 (Vue)

    cd frontend
    npm install
    npm run dev
    # 访问 http://localhost:5173

## 📊 RAG 效果评估与踩坑记录

在项目开发中，我针对 RAG 的检索效果进行了严谨的基线测试：

1. **初期版本**：使用 `all-MiniLM-L6-v2`，在处理《招标投标法》等中文长文档时，向量召回经常出现偏差。
2. **优化方案**：更换为中文专精模型 `BAAI/bge-small-zh-v1.5`，并增加了针对 Query 的指令前缀（`为这个句子生成表示以用于检索相关文章：`）。
3. **优化结果**：抽取 5 道政企专业题目测试，**Top-5 检索命中率达到 100%，无答案拒答率 100%**。

## ⚠️ 注意事项

- 本地运行时，请确保显卡驱动与 CUDA 环境正常（推荐 PyTorch 2.5.0 + CUDA 12.1）。
- 生产环境部署时，务必将 `application.properties` 与 Python 脚本中的 API Key 更换为环境变量注入。