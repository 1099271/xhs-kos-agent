## 项目概述

本项目旨构建一套自部署、工程化的「小红书内容运营 Agent 系统」，覆盖从笔记采集、诊断、分析、价值筛选，到内容生成、人工审核、推送及记忆沉淀的完整业务流程。

### 核心业务流程

1. **产品特性分析** → 2. **笔记采集** → 3. **笔记诊断（主题/情感/用户画像）** → 4. **评论分析（情感/AIPS）** → 5. **高价值人群匹配** → 6. **内容生产（RAG 驱动）** → 7. **Human-in-the-Loop 审核** → 8. **推送评论/私信** → 9. **长期记忆更新**

---

## 实现目标

1. **工程化 Agent 系统**：可观测、可扩展、多账户并发、自主规划
2. **自定义 MCP 工具链**：以 OpenAI-style JSON-schema 暴露本地诊断/分析服务
3. **闭环业务跑通**：固定工作流先跑通各环节，后期逐步放权给 Agent 自主决策

---

## 技术栈

| 层级                | 技术/产品                                               |
| ------------------- | ------------------------------------------------------- |
| **语言 & 框架**     | Python 3.10+, FastAPI, LangGraph (LangChain), Pydantic  |
| **LLM & Embedding** | claude 3.7 / Qwen3 / Mistral-7B, bge-small-zh           |
| **向量存储**        | PGVector → Milvus GPU 集群                              |
| **短期缓存**        | Redis-Vector                                            |
| **持久存储**        | MySQL (SQLModel + Alembic)                              |
| **消息队列**        | Celery + RabbitMQ / Ray Worker                          |
| **MCP 服务**        | FastAPI + `mcp_sdk` 本地 MCP                            |
| **Workflow**        | LangGraph StateGraph + ReACT Router                     |
| **Observability**   | LangSmith trace, Prometheus metrics, Grafana dashboards |

---

## 文件模块分层

```
/xhs-kos-agent
├── apps/
│   ├── ingest/              # 爬虫及 ETL 逻辑
│   ├── mcp_tools/           # 自定义 MCP 工具：diagnose, comment, sentiment, aips
│   ├── agents/              # LangChain Agent 封装（DiagnosisAgent、ReplyAgent、PlannerAgent…）
│   ├── workflows/           # LangGraph 图定义（static_flow.py, planner_flow.py…）
│   ├── api/                 # FastAPI 服务（workflows, review, auth, xhs_notes…）
│   ├── llm_prompts/         # Prompt 模板、Jinja2 文件
│   └── memory/              # STM/ LTM 服务、Embedding 接口
├── infra/
│   ├── db/                  # MySQL + Alembic 迁移脚本
│   ├── vector/              # PGVector / Milvus 配置
└── scripts/                 # 数据迁移、批处理、运维脚本
```

---

## 阶段化里程碑

| 阶段   | 目标描述                              | 主要交付                             |
| ------ | ------------------------------------- | ------------------------------------ |
| **M0** | 固定工作流端到端跑通                  | `static_flow.py` + 两个 MCP 工具     |
| **M1** | 引入短期/长期记忆 + RAG               | `memory/` + `generate_reply_rag`     |
| **M2** | Human-in-the-Loop 审核                | `api/routers/review.py` + 前端审核页 |
| **M3** | PlannerAgent 自主演化（ReACT+Router） | `planner_flow.py` + `PlannerAgent`   |

---

## 核心逻辑拆解

### 1. Workflows（LangGraph）

- **`static_flow.py`**：固定流程，节点依次调用
- **`planner_flow.py`**：M3 阶段，PlannerAgent 下发执行计划

### 2. Agents & Tools

- **Agents**：`DiagnosisAgent`, `CommentAnalysisAgent`, `ReplyAgent`, `PlannerAgent`
- **LangChain Tools**：`NoteDBTool`, `VectorSearchTool`, `SendReplyTool`

### 3. MCP 工具（apps/mcp_tools）

- 快速构建本地 MCP Server（`server.py`）
- 各诊断函数加 `@mcp_function` 注解，暴露 OpenAI 兼容接口

### 4. Memory Service

- **STM**：Redis-Vector 存储当次上下文 embedding
- **LTM**：PGVector / Milvus 存储历史话术、用户画像

### 5. API 层（FastAPI）

- `/workflows/run`：触发工作流
- `/review/create` & `/review/{id}`：HITL 审核
- `/xhs/notes/*`：笔记数据 CRUD

---
