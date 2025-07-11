# Claude 使用指南 - XHS KOS Agent

## 项目概述
这是一个针对小红书(XHS)数据处理的KOS(知识组织系统)智能代理项目。项目包含网络爬虫、数据存储和AI驱动的内容分析功能。

## 项目结构
- `app/` - 主应用代码
  - `infra/` - 基础设施层 (数据库、模型、数据访问对象)
  - `ingest/` - 数据采集模块 (小红书爬虫)
  - `services/` - 业务逻辑服务
  - `api/` - API接口
  - `schemas/` - 数据模式定义
  - `utils/` - 工具函数
  - `agents/` - Multi-Agent系统 (新增)
- `cli/` - 命令行界面
- `docs/` - 项目文档
- `logs/` - 应用日志

## 核心组件
- 作者、评论、笔记、话题、关键词的数据库模型
- 小红书数据采集爬虫
- Coze服务集成
- 基于FastAPI的Web API
- 各种操作的CLI工具
- Multi-Agent智能分析系统

## Multi-Agent系统架构
- `UserAnalystAgent` - 用户分析智能体：基于LLM评论分析识别高价值用户 ✅
- `EnhancedUserAnalystAgent` - 增强版用户分析智能体：集成LlamaIndex语义搜索 ✅
- `ContentGeneratorAgent` - 内容生成智能体：为目标用户生成个性化互动内容 🔄
- `StrategyCoordinatorAgent` - 策略协调智能体：整体策略制定和Agent协调 🔄
- `LlamaIndexManager` - 智能文档索引管理器：提供语义搜索和知识检索 ✅

## 开发指南
- 使用Python异步编程模式 (async/await)
- 遵循现有代码风格和模式
- 数据库操作使用异步模式
- 日志记录已配置 - 使用logger工具
- 配置文件位于 `app/config/settings.py`

## 数据库设计
- 核心表：`xhs_notes`, `xhs_comments`, `xhs_authors`
- LLM分析表：`llm_comment_analysis`, `llm_note_diagnosis`
- 关键词管理：`xhs_keyword_groups`, `xhs_keyword_group_notes`

## 测试
- 运行测试前检查仓库中的测试脚本
- 在pyproject.toml中查找pytest配置或测试命令
- 测试文件位于 `test/` 目录
- Agent测试脚本：`test/test_user_analyst.py`

## 常用命令
- 运行代码检查：检查pyproject.toml中的linter配置
- 运行测试：检查pytest或其他测试运行器配置
- 启动应用：检查main.py或pyproject.toml中的入口点
- 测试User Analyst Agent：`uv run python test/test_user_analyst.py`

## 数据库
- 使用异步数据库模式
- 模型定义在 `app/infra/models/`
- 数据访问对象(DAO)在 `app/infra/dao/`
- 数据库配置在 `app/infra/db/`

## 依赖管理
- 项目使用uv进行依赖管理 (存在uv.lock文件)
- 主要依赖包括FastAPI、asyncio库、数据库驱动程序
- LangGraph和LlamaIndex用于Multi-Agent系统
- **新增依赖**: llama-index (智能文档索引), psutil (性能监控)

## Agent系统使用说明
- 使用LangGraph进行Agent工作流编排
- 使用LlamaIndex连接MySQL数据进行智能检索
- 基于现有的评论分析数据识别高价值用户
- 支持自定义筛选条件和价值评分算法
- **集成Prompt管理系统**：统一管理所有Agent提示词模板
- **语义搜索功能**：基于向量相似度的智能内容检索
- **智能问答系统**：支持自然语言查询用户数据

## 系统最佳实践（已验证）
### 数据库会话管理
```python
from app.infra.db.async_database import AsyncSessionLocal

session = AsyncSessionLocal()
try:
    # 数据库操作
    await session.commit()
except Exception:
    await session.rollback()
    raise
finally:
    await session.close()
```

### 日志使用方式
```python
from app.utils.logger import app_logger as logger
```

### 异常处理模式
- 使用try/except/finally模式
- 明确的事务提交和回滚
- 详细的错误日志记录

## 已修复的问题
- 修复了数据库会话管理（AsyncSessionLocal替代get_async_session）
- 统一了日志导入方式（app_logger as logger）
- 添加了cryptography依赖以支持MySQL认证
- 验证了测试脚本可以正常运行
- **修复了aiomysql连接清理问题**：在程序结束前调用 `await async_engine.dispose()` 正确关闭数据库引擎

## 常见问题解决方案
### aiomysql "Event loop is closed" 错误
**问题**: `RuntimeError: Event loop is closed` 在程序结束时出现

**原因**: 程序结束时事件循环已关闭，但aiomysql连接对象在垃圾回收时试图异步关闭连接

**解决方案**: 在主函数中正确关闭数据库引擎
```python
from app.infra.db.async_database import async_engine

async def main():
    try:
        # 你的主要逻辑
        pass
    finally:
        # 在程序结束前正确关闭数据库引擎
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
```

## 备忘录
- 待记忆

## 最新更新 (2025-07-11)

### ✅ 已完成功能
#### 1. Prompt管理系统重构
- **位置**: `app/prompts/`
- **功能**: 统一管理所有Agent的提示词模板
- **文件结构**:
  - `__init__.py` - PromptManager核心类和模板系统
  - `user_analyst_prompts.py` - 用户分析相关提示词
  - `content_strategy_prompts.py` - 内容策略提示词
  - `content_generator_prompts.py` - 内容生成提示词

#### 2. LlamaIndex智能索引系统
- **位置**: `app/agents/llamaindex_manager.py`
- **核心功能**:
  - 向量索引构建 (评论、笔记、LLM分析数据)
  - 语义搜索 (基于相似度阈值)
  - 智能问答 (RAG检索增强生成)
  - 用户洞察提取
  - 批量索引操作
- **支持模型**: OpenAI Embeddings, HuggingFace Embeddings
- **测试覆盖**: 7/7测试全部通过

#### 3. 增强版用户分析Agent
- **位置**: `app/agents/enhanced_user_analyst_agent.py`
- **新增功能**:
  - 结合传统数据分析和语义搜索
  - 增强版用户画像 (包含AI洞察)
  - 智能用户查询接口
  - 语义分析和内容分析

#### 4. 更新的Multi-Agent工作流
- **位置**: `app/agents/enhanced_multi_agent_workflow.py`
- **集成**: Prompt管理 + LlamaIndex + 增强分析

### 🔄 待完成任务
1. **ContentGeneratorAgent** - 内容生成智能体实现
2. **StrategyCoordinatorAgent** - 策略协调智能体实现
3. **FastAPI端点** - Web API接口
4. **CLI命令行接口** - 命令行工具

### 🧪 测试命令
```bash
# 测试LlamaIndex集成
uv run python test/test_llamaindex_manager.py

# 测试增强版用户分析
uv run python test/test_enhanced_user_analyst.py

# 测试增强版工作流
uv run python test/test_enhanced_multi_agent_workflow.py
```

### 📁 新增文件清单
- `app/prompts/__init__.py` - Prompt管理核心
- `app/prompts/*_prompts.py` - 各Agent提示词模板
- `app/agents/llamaindex_manager.py` - LlamaIndex集成
- `app/agents/enhanced_user_analyst_agent.py` - 增强版用户分析
- `test/test_llamaindex_manager.py` - LlamaIndex测试套件