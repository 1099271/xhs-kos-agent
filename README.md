# XHS KOS Agent - AI驱动的智能营销系统

基于 **LlamaIndex** 和 **LangGraph** 构建的AI智能营销Agent系统，专门针对小红书平台的用户分析、内容生成和智能决策。

## 🎯 **核心能力**

- 🧠 **AI智能用户分析** - 基于LLM和语义搜索的高价值用户识别
- 🔍 **语义内容检索** - LlamaIndex驱动的智能文档索引和搜索
- 📝 **智能内容策略** - AI驱动的个性化内容生成和策略制定
- 🤖 **Multi-Agent协作** - LangGraph编排的端到端智能工作流
- 💬 **自然语言查询** - 支持自然语言查询业务数据和洞察

## 🚀 **快速开始**

### **1. 环境准备**
```bash
# 克隆项目
git clone <repository-url>
cd xhs-kos-agent

# 使用uv安装依赖
uv sync

# 配置环境变量
export OPENAI_KEY="your_openai_key"
export MYSQL_URL="mysql+aiomysql://user:pass@host:port/dbname"
```

### **2. 快速体验**
```bash
# 测试智能用户分析
uv run python -c "
import asyncio
from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
from app.infra.db.async_database import get_session_context

async def main():
    agent = EnhancedUserAnalystAgent()
    async with get_session_context() as session:
        result = await agent.execute_enhanced_analysis(session)
        print(f'✅ 分析完成: {result.retrieval_summary}')
        
        # 智能问答
        answer = await agent.smart_user_query('哪些用户最活跃？')
        print(f'🤖 AI回答: {answer}')

asyncio.run(main())
"

# 测试完整AI工作流
uv run python -c "
import asyncio
from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow

async def main():
    workflow = EnhancedMultiAgentWorkflow()
    result = await workflow.execute_enhanced_workflow({
        'task': 'UGC平台用户获取分析',
        'ai_enhancement': True
    })
    print(f'🚀 工作流结果: {result[\"execution_summary\"]}')

asyncio.run(main())
"
```

## 🎪 **核心功能演示**

### **智能用户分析**
```python
# 识别高价值用户并获取AI洞察
agent = EnhancedUserAnalystAgent()
result = await agent.execute_enhanced_analysis(session, {
    "emotional_preference": ["正向"],
    "exclude_visited": True,
    "ai_enhancement": True
})

print(f"发现 {len(result.high_value_users)} 个高价值用户")
print(f"AI洞察: {result.semantic_insights}")
```

### **语义搜索与问答**
```python
# 自然语言查询业务数据
manager = LlamaIndexManager()

# 语义搜索
results = await manager.semantic_search("高价值用户特征", top_k=5)

# 智能问答
answer = await manager.intelligent_query("用户最关心什么话题？")
print(f"AI回答: {answer}")
```

### **Multi-Agent智能工作流**
```python
# 端到端AI分析流程
workflow = EnhancedMultiAgentWorkflow()
result = await workflow.execute_enhanced_workflow({
    'target_user_count': 30,
    'content_themes': ['AI个性化', '智能推荐'],
    'ai_enhancement': True
})

# 获取综合分析结果
print(f"用户分析: {result['user_analysis']}")
print(f"内容策略: {result['content_strategy']}")
print(f"AI增强摘要: {result['ai_enhancement_summary']}")
```

## 📊 **技术架构**

```mermaid
graph TB
    A[自然语言查询] --> B[Enhanced Multi-Agent Workflow]
    B --> C[LlamaIndex Manager]
    C --> D[向量索引/语义搜索]
    
    B --> E[Enhanced User Analyst]
    B --> F[Content Strategy Agent]
    B --> G[Content Generator Agent]
    B --> H[Strategy Coordinator]
    
    E --> I[AI用户洞察]
    F --> J[智能内容策略]
    G --> K[AI内容生成]
    H --> L[智能协调优化]
    
    C --> M[MySQL数据库]
    E --> M
    F --> M
    G --> M
    H --> M
```

## 🛠️ **系统特性**

### **AI智能增强**
- ✅ **LlamaIndex集成** - 智能文档索引和语义搜索
- ✅ **多模型支持** - OpenAI、OpenRouter、Anthropic等
- ✅ **智能问答系统** - 自然语言查询业务数据
- ✅ **AI洞察生成** - 深度用户行为分析和建议

### **Multi-Agent协作**
- ✅ **LangGraph工作流** - 状态驱动的Agent编排
- ✅ **增强版用户分析** - 传统分析+AI语义搜索
- ✅ **智能内容策略** - AI驱动的策略制定
- ✅ **自动化协调** - 智能任务分配和优化

### **企业级特性**
- ✅ **异步架构** - 高性能异步操作设计
- ✅ **健壮性** - 完整的错误处理和恢复机制
- ✅ **可扩展性** - 模块化设计，易于扩展
- ✅ **测试覆盖** - 全面的测试套件

## 📁 **项目结构**

```
xhs-kos-agent/
├── app/
│   ├── agents/                 # AI Agent系统
│   │   ├── llamaindex_manager.py          # LlamaIndex智能索引
│   │   ├── enhanced_user_analyst_agent.py # 增强版用户分析
│   │   ├── enhanced_multi_agent_workflow.py # AI工作流
│   │   └── llm_manager.py                 # LLM模型管理
│   ├── prompts/               # AI提示词管理
│   ├── infra/                 # 基础设施层
│   └── config/                # 配置管理
├── docs/                      # 项目文档
│   ├── USAGE_GUIDE.md        # 详细使用指南
│   ├── PROJECT_SUMMARY.md    # 项目技术总结
│   └── system_design.md      # 系统设计文档
├── test/                      # 测试套件
└── cli/                       # 命令行工具
```

## 🧪 **测试验证**

```bash
# 运行完整测试套件
uv run python test/test_llamaindex_manager.py    # LlamaIndex测试
uv run python test/test_enhanced_multi_agent_workflow.py  # AI工作流测试

# 快速功能验证
uv run python test/test_enhanced_quick.py        # 快速功能测试
uv run python test/test_llm_quick.py            # LLM连接测试
```

## 📚 **文档资源**

- 📖 **[详细使用指南](docs/USAGE_GUIDE.md)** - 完整的功能介绍和代码示例
- 🏗️ **[项目技术总结](docs/PROJECT_SUMMARY.md)** - 技术架构和开发历程
- 🎯 **[系统设计文档](docs/system_design.md)** - 系统架构设计
- 🗂️ **[项目结构说明](docs/folder_structure.md)** - 代码组织结构

## 🎯 **实际应用**

这个系统可以帮助你：
- 🎯 **精准识别**高价值用户和潜在客户
- 🧠 **智能分析**用户行为模式和内容偏好
- 📝 **自动生成**个性化内容策略和营销方案
- 🔍 **语义搜索**历史数据，快速获取业务洞察
- 💬 **自然语言**查询复杂业务问题
- 🤖 **AI协作**多个智能体协同工作

## 🚨 **系统要求**

- **Python**: >= 3.12
- **依赖管理**: uv (推荐) 或 pip
- **数据库**: MySQL >= 8.0
- **API Keys**: OpenAI/OpenRouter/Anthropic (任选其一)

## 🤝 **贡献指南**

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

**🚀 Ready to revolutionize your UGC platform with AI? Let's get started!**

> 💡 **提示**: 查看 [详细使用指南](docs/USAGE_GUIDE.md) 了解完整功能和使用方法