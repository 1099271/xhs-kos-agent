# XHS KOS Agent 项目

基于 LangGraph 和大语言模型构建的智能营销 Agent 系统，专门针对小红书平台的自动化内容采集、分析与用户互动。

## 📋 项目概述

本项目旨在构建一套基于大语言模型（LLM）和 LangGraph 的智能营销 Agent 系统。该系统主要服务于小红书平台，通过自动化内容采集、分析、互动等方式，提升营销效率和效果。

## 🎯 核心业务目标

- **产品知识管理**: 根据输入信息，分析制定的产品能力，汇总输出整理成产品知识
- **小红书笔记采集**: 根据产品定位的目标人群，采集特定的小红书笔记信息（包括笔记内容、详情、评论等）
- **笔记分析与报告**: 对笔记信息进行判断和分析，根据各种指标生成对应报告
- **高价值人群互动**: 对笔记中的高价值人群做漏洞筛选，根据人群偏好生成个性化评论和私信消息
- **用户反馈收集**: 对用户的反馈做整理和收集，供后续分析和模型迭代

## 🏗️ 技术架构

- **核心框架**: LangGraph + LangChain
- **Web 框架**: FastAPI
- **数据库**: MySQL + SQLAlchemy
- **包管理**: uv
- **Python 版本**: >= 3.12
- **爬虫模块**: Git Submodule (XHS Spider)

## 🛠️ 快速开始

### 环境要求

- Python >= 3.12
- Node.js (用于 XHS 爬虫模块)
- MySQL 数据库
- Git

### 1. 克隆项目

```bash
# 克隆主项目
git clone <repository-url>
cd xhs-kos-agent

# 初始化并更新子模块
git submodule init
git submodule update
```

### 2. 使用 uv 安装依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 作为快速的 Python 包管理器。

#### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

#### 项目环境设置

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装项目依赖
uv sync

# 或者直接运行（会自动创建环境）
uv run python main.py
```

### 3. 配置环境变量

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=xhs-kos-agent

# 小红书配置
XHS_COOKIE=your_xhs_cookie

# LLM 模型配置
MODEL_API_KEY=your_api_key
MODEL_BASE_URL=your_model_base_url
MODEL_NAME=your_model_name

# OpenAI/OpenRouter 配置（可选）
OPENAI_KEY=your_openai_key
OPENROUTER_KEY=your_openrouter_key

# Coze API 配置
COZE_API_TOKEN=your_coze_token

# 其他配置
DEBUG=true
LOG_LEVEL=INFO
```

### 4. 数据库初始化

```bash
# 创建数据库表
uv run python app/scripts/init_db.py

# 或使用 CLI 工具
uv run python cli/main.py --help
```

## 🚀 使用方法

### 命令行界面 (CLI)

项目提供了丰富的 CLI 工具：

```bash
# 查看所有可用命令
uv run python cli/main.py --help

# 小红书笔记相关操作
uv run python cli/main.py xhs_note --help

# LLM标签处理
uv run python cli/main.py llm_tag --help
```

### API 服务

启动 FastAPI 服务：

```bash
# 开发模式
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 项目结构

```
xhs-kos-agent/
├── app/                    # 主应用代码
│   ├── agents/            # LangGraph Agents
│   ├── api/               # FastAPI 路由
│   ├── config/            # 配置文件
│   ├── infra/             # 基础设施层
│   │   ├── dao/          # 数据访问对象
│   │   ├── db/           # 数据库连接
│   │   ├── models/       # 数据库模型
│   │   └── rag/          # RAG 相关
│   ├── ingest/            # 数据采集模块
│   │   └── xhs_spider/   # 小红书爬虫 (Git Submodule)
│   ├── services/          # 业务服务层
│   ├── schemas/           # Pydantic 数据模型
│   └── workflows/         # LangGraph 工作流
├── cli/                   # 命令行工具
├── docs/                  # 项目文档
└── examples/              # 使用示例
```

## 🔧 Git Submodule 管理

项目使用 Git Submodule 管理小红书爬虫模块：

### 子模块信息

- **路径**: `app/ingest/xhs_spider`
- **仓库**: `git@github.com:1099271/Spider_XHS.git`
- **分支**: `dev_kos`

### 常用子模块命令

```bash
# 查看子模块状态
git submodule status

# 更新子模块到最新版本
git submodule update --remote

# 更新特定子模块
git submodule update --remote app/ingest/xhs_spider

# 在子模块中切换分支
cd app/ingest/xhs_spider
git checkout dev_kos
cd ../../..

# 推送子模块更改
git add app/ingest/xhs_spider
git commit -m "Update xhs_spider submodule"
git push
```

## 🔍 开发指南

### 使用 uv 进行开发

```bash
# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 移除依赖
uv remove package-name

# 运行脚本
uv run python script.py

# 运行特定命令
uv run --with package-name command

# 查看依赖树
uv tree
```

### 代码风格

项目遵循以下最佳实践：

- 使用 Python 3.12+ 的新特性
- 遵循 PEP 8 代码规范
- 使用 Type Hints
- 异步编程优先
- 模块化设计

### 测试

```bash
# 运行测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_specific.py

# 生成覆盖率报告
uv run pytest --cov=app
```

## 📊 项目状态

项目当前处于早期设计和开发阶段。

### 已实现功能

- [x] 基础项目架构
- [x] 数据库模型设计
- [x] CLI 工具框架
- [x] FastAPI 基础设置
- [x] 小红书爬虫集成

### 开发中功能

- [ ] LangGraph Agents 实现
- [ ] 用户行为分析服务
- [ ] 内容生成与优化
- [ ] 自动化互动流程

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件至项目维护者

## 🔗 相关链接

- [系统设计文档](docs/system_design.md)
- [项目结构说明](docs/folder_structure.md)
- [数据库结构](docs/database_structure.sql)
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [uv 官方文档](https://github.com/astral-sh/uv)
