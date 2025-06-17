# 文件夹结构说明

```
xhs-kos-agent/
├── .venv/                     # Python 虚拟环境
├── apps/                      # 核心应用代码
│   ├── agents/                # LangGraph Agent 定义 (e.g., part_a_agent.py, part_b_agent.py, part_c_agent.py)
│   ├── api/                   # FastAPI 接口 (如果需要)
│   │   └── routers/           # API 路由
│   ├── config/                # 应用配置模块
│   ├── infra/                      # 基础设施层 (数据库、向量索引、缓存等)
│   │   ├── db/
│   │   │   ├── models/             # SQLAlchemy 模型 (e.g., note_models.py, user_models.py)
│   │   │   └── dao/                # Data Access Objects (e.g., note_dao.py)
│   │   ├── rag/                    # LlamaIndex 相关 (向量存储、索引管理)
│   │   │   ├── vector_store.py     # 封装向量数据库操作 (e.g., FAISS, Qdrant)
│   │   │   └── index_manager.py    # 高层索引管理接口 (加载、保存、更新、查询)
│   │   └── cache/                  # Redis客户端配置与辅助函数
│   ├── ingest/                # 数据提取/采集模块
│   ├── prompts/               # LLM 提示模板
│   ├── mcp_tools/             # MCP (Model Context Protocol) 相关工具
│   ├── memory/                # Agent 记忆模块
│   ├── schemas/                    # Pydantic模型 (API请求/响应, AgentState等)
│   │   └── workflow_schemas.py     # AgentState 定义 (e.g., PartA_State, PartB_State, PartC_State)
│   ├── scripts/               # 应用主要脚本/入口
│   ├── services/                   # 核心业务逻辑服务 (原子性操作)
│   │   ├── collection/             # 数据采集相关服务
│   │   │   ├── collection_service.py # 协调 spider_service, coze_service
│   │   │   ├── spider_service.py     # 封装爬虫组件调用
│   │   │   └── coze_service.py       # 封装Coze API调用
│   │   ├── analysis/               # 数据分析相关服务
│   │   │   ├── analysis_service.py   # 综合分析服务
│   │   │   ├── user_targeting.py   # (可选) 用户筛选子模块
│   │   │   └── topic_analysis.py     # (可选) 话题内容分析子模块
│   │   ├── generation/             # 内容生成相关服务
│   │   │   ├── content_generation_service.py # 主要文案生成服务
│   │   │   ├── prompt_templates.py # (可选) 模板管理逻辑
│   │   │   └── llm_client.py         # (可选) LLM API调用封装
│   │   └── feedback/               # 反馈处理相关服务
│   │       └── feedback_service.py   # 整体反馈处理服务
│   ├── tools/                      # LangGraph Tools (作为Services的封装，供Agent调用)
│   │   ├── collection_tools.py
│   │   ├── analysis_tools.py
│   │   ├── generation_tools.py
│   │   └── feedback_tools.py
│   ├── utils/                 # 通用工具函数
│   └── workflows/             # LangGraph workflow 编译与图定义 (e.g., part_a_workflow.py, part_b_workflow.py, part_c_workflow.py)
├── cli/                            # 命令行接口
│   ├── agent_cli.py                # 用于触发和管理Agent工作流的新CLI入口
│   └── xhs/                        # 按业务组织的CLI命令 (e.g., note.py)
├── docs/                      # 项目文档
├── logs/                      # 日志文件
├── scripts/                   # 辅助脚本
├── .env                       # 环境变量 (不提交到git)
├── .envrc                     # Direnv 配置
├── .gitignore                 # Git 忽略配置
├── .python-version            # Pyenv Python 版本配置
├── main.py                    # 项目主入口 (FastAPI app / CLI)
├── pyproject.toml             # 项目构建和依赖配置
├── README.md                  # 项目根 README
└── uv.lock                    # uv 包管理器锁文件
```

## 主要目录和文件说明

### `/apps` - 核心应用代码

- **`agents/`**: 定义和实现基于 LangGraph 的 Agent。包含状态、节点(Nodes)、边(Edges)的定义及协同方式。
- **`api/`**: FastAPI 相关代码，如路由、依赖、请求/响应模型等（可选，若需提供 API）。
- **`config/`**: 存放应用配置，如 `settings.py`，用于管理环境变量和应用参数。
- **`infra/`**: 基础设施配置
  - **`db/`**: 数据库相关配置和定义，如 SQLAlchemy ORM 模型(`models.py`)、数据库迁移脚本等。
  - **`rag/`**: 若使用 RAG 技术，存放相关组件如向量数据库配置、检索逻辑等。
- **`ingest/`**: 数据采集模块，负责从小红书平台获取笔记、评论等数据。
- **`llm_prompts/`**: LLM 提示模板集中管理，便于版本控制和优化。
- **`mcp_tools/`**: MCP 协议实现代码，可作为 Server 暴露功能或作为 Client 连接外部服务。
- **`memory/`**: Agent 记忆模块，管理对话历史、状态信息等。
- **`schemas/`**: Pydantic 数据模型，用于数据校验、API 请求/响应、内部数据结构定义等。
- **`scripts/`**: 应用的主要可执行脚本，例如 Agent 的启动脚本、特定的工作流触发器等。
- **`services/`**: 核心业务服务，如数据采集(`CollectionService`)、分析(`AnalysisService`)、内容生成(`ContentGenerationService`)等。
- **`tools/`**: LangGraph Agent 可调用的工具，通常是对 `services` 的封装。
- **`utils/`**: 通用工具函数和辅助模块，如日志配置 (`logger.py`)、字符串处理等。
- **`workflows/`**: LangGraph 工作流定义，描述任务执行的步骤和逻辑流转。

### `/cli` - 命令行工具

CLI 是项目早期任务触发和调试的主要入口。使用 Click/Typer 库构建用户友好的命令行界面。

### `/docs` - 项目文档

- **`system_design.md`**: 系统设计文档，包含架构和技术栈说明。
- **`folder_structure.md`**: 本文档，详细说明项目文件夹结构。

### `/logs` 和 `/scripts`

- **`logs/`**: 存放应用程序运行日志。
- **`scripts/`**: 辅助脚本，如一次性数据处理、构建工具等。

### 配置和入口文件

- **`.env`**: 环境变量，包含敏感配置，不应提交到版本控制。
- **`main.py`**: 项目主入口（FastAPI 应用/CLI）。
- **`pyproject.toml`**: 项目元数据和依赖配置。

这个结构遵循关注点分离原则，使代码易于理解、维护和扩展。
