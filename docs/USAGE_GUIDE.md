# XHS KOS Agent 使用指南

## 🚀 **快速开始**

### **环境准备**

```bash
# 确保使用uv管理依赖
uv sync

# 配置环境变量 (参考 app/config/settings.py)
export OPENAI_KEY="your_openai_key"
export OPENROUTER_KEY="your_openrouter_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export MYSQL_URL="mysql+aiomysql://user:pass@host:port/dbname"
```

### **核心功能概览**

- 🎯 **智能用户分析** - 基于 LLM 的高价值用户识别
- 🧠 **语义搜索** - LlamaIndex 驱动的智能内容检索
- 📝 **内容策略** - AI 驱动的个性化内容生成
- 🔄 **Multi-Agent 协作** - 端到端的智能工作流

---

## 📋 **使用场景指南**

### **1. 基础用户分析**

**快速测试：**

```bash
uv run python test/test_user_analyst.py
```

**代码示例：**

```python
from app.agents.user_analyst_agent import UserAnalystAgent
from app.infra.db.async_database import get_session_context

async def analyze_users():
    agent = UserAnalystAgent()

    # 设置分析条件
    criteria = {
        "emotional_preference": ["正向"],  # 正向情感用户
        "unmet_preference": ["是"],       # 有未满足需求
        "exclude_visited": True,          # 排除已访问用户
        "min_interaction_count": 2,       # 最少互动次数
        "limit": 20                       # 限制结果数量
    }

    async with get_session_context() as session:
        result = await agent.execute(session, criteria)

    print(f"发现 {len(result.high_value_users)} 个高价值用户")
    for user in result.high_value_users[:3]:
        print(f"用户: {user.nickname}, 价值评分: {user.value_score}")
```

**输出示例：**

```
发现 15 个高价值用户
用户: 小红书达人A, 价值评分: 8.5
用户: 旅游爱好者B, 价值评分: 8.2
用户: 美食博主C, 价值评分: 7.9
```

---

### **2. 增强版用户分析 (集成 LlamaIndex)**

**特点：** 结合传统数据分析和 AI 语义搜索

```python
from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
from app.infra.db.async_database import get_session_context

async def enhanced_analysis():
    agent = EnhancedUserAnalystAgent()

    async with get_session_context() as session:
        # 执行增强版分析
        result = await agent.execute_enhanced_analysis(session)

        print(f"分析摘要: {result.retrieval_summary}")
        print(f"语义洞察: {result.semantic_insights}")

        # 智能问答
        answer = await agent.smart_user_query("哪些用户最活跃？")
        print(f"AI回答: {answer}")

# 运行
import asyncio
asyncio.run(enhanced_analysis())
```

**一键测试：**

```bash
uv run python -c "
import asyncio
from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
from app.infra.db.async_database import get_session_context

async def main():
    agent = EnhancedUserAnalystAgent()
    async with get_session_context() as session:
        result = await agent.execute_enhanced_analysis(session)
        print(f'✅ 分析完成: {result.retrieval_summary}')

asyncio.run(main())
"
```

---

### **3. LlamaIndex 智能索引系统**

**核心功能：**

- 📊 **向量索引构建** - 评论、笔记、LLM 分析数据
- 🔍 **语义搜索** - 基于相似度的智能检索
- 💬 **智能问答** - 自然语言查询系统
- 👤 **用户洞察** - 个性化用户画像分析

```python
from app.agents.llamaindex_manager import LlamaIndexManager

async def use_llamaindex():
    manager = LlamaIndexManager()

    # 1. 构建索引 (首次使用)
    print("🔧 构建索引...")
    results = await manager.build_all_indexes()
    print(f"索引构建结果: {results}")

    # 2. 语义搜索
    print("🔍 语义搜索...")
    search_results = await manager.semantic_search(
        query="高价值用户特征",
        top_k=5,
        similarity_threshold=0.7
    )
    print(f"找到 {len(search_results)} 个相关结果")

    # 3. 智能问答
    print("💬 智能问答...")
    answer = await manager.intelligent_query(
        question="用户最关心什么话题？"
    )
    print(f"AI回答: {answer}")

    # 4. 用户洞察
    print("👤 用户洞察...")
    insights = await manager.get_user_insights("target_user_id")
    print(f"用户数据: {insights['total_records']} 条记录")
    print(f"分析摘要: {insights['summary']}")

# 运行
import asyncio
asyncio.run(use_llamaindex())
```

**快速测试：**

```bash
# 完整测试套件
uv run python test/test_llamaindex_manager.py
```

---

### **4. 完整 Multi-Agent 工作流**

**端到端智能分析流程：**

```python
from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow
from app.agents.llm_manager import ModelProvider

async def run_full_workflow():
    # 创建增强版工作流
    workflow = EnhancedMultiAgentWorkflow(
        preferred_model_provider=ModelProvider.OPENROUTER  # 可选择模型
    )

    # 执行完整分析
    result = await workflow.execute_enhanced_workflow({
        'task': 'UGC平台用户获取分析',
        'target_user_count': 30,
        'content_themes': ['AI个性化', '智能推荐', '数据洞察'],
        'ai_enhancement': True
    })

    # 输出结果
    if result['success']:
        print("🎉 工作流执行成功！")
        print(f"📊 执行摘要: {result['execution_summary']}")
        print(f"🤖 AI增强: {result['ai_enhancement_summary']}")

        # 详细结果
        if result.get('user_analysis'):
            users = result['user_analysis'].high_value_users
            print(f"🎯 识别高价值用户: {len(users)} 个")

        if result.get('content_strategy'):
            strategy = result['content_strategy']
            print(f"📝 内容策略: {strategy.get('strategy_summary', 'N/A')}")

        if result.get('generated_content'):
            content = result['generated_content']
            pieces = content.get('content_pieces', [])
            print(f"✍️ 生成内容: {len(pieces)} 个片段")
    else:
        print(f"❌ 工作流失败: {result.get('error', '未知错误')}")

# 运行
import asyncio
asyncio.run(run_full_workflow())
```

**一键执行：**

```bash
uv run python -c "
import asyncio
from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow

async def main():
    workflow = EnhancedMultiAgentWorkflow()
    result = await workflow.execute_enhanced_workflow({
        'task': 'UGC平台用户获取分析',
        'ai_enhancement': True
    })
    print(f'✅ 工作流结果: {result[\"execution_summary\"]}')

asyncio.run(main())
"
```

---

## 🎯 **实际业务场景**

### **场景 1: 潜在客户识别**

```python
async def find_potential_customers():
    """识别有潜在价值的未访问用户"""
    agent = EnhancedUserAnalystAgent()

    async with get_session_context() as session:
        result = await agent.execute_enhanced_analysis(session, {
            "emotional_preference": ["正向"],  # 正向用户
            "exclude_visited": True,           # 未访问过
            "min_interaction_count": 3,        # 活跃用户
            "limit": 50
        })

    # 按价值评分排序
    potential_customers = sorted(
        result.high_value_users,
        key=lambda x: x.value_score,
        reverse=True
    )

    return potential_customers[:10]  # 返回Top10
```

### **场景 2: 内容策略优化**

```python
async def optimize_content_strategy():
    """分析用户偏好，优化内容策略"""
    manager = LlamaIndexManager()

    # 分析热门话题
    trends = await manager.intelligent_query(
        "最近用户最关注哪些内容主题和话题？"
    )

    # 找出高互动内容特征
    high_engagement = await manager.semantic_search(
        "高点赞 高评论 高分享 热门内容",
        top_k=10,
        similarity_threshold=0.8
    )

    # 分析未满足需求
    unmet_needs = await manager.semantic_search(
        "未满足需求 用户痛点 改进建议",
        top_k=15
    )

    return {
        "热门趋势": trends,
        "高互动内容": high_engagement,
        "未满足需求": unmet_needs
    }
```

### **场景 3: 个性化用户画像**

```python
async def create_detailed_persona(user_id: str):
    """为特定用户创建详细画像"""
    manager = LlamaIndexManager()

    # 获取用户基础洞察
    insights = await manager.get_user_insights(user_id)

    # 分析用户行为偏好
    preferences = await manager.intelligent_query(
        f"分析用户{user_id}的行为偏好和兴趣特点"
    )

    # 生成个性化推荐
    recommendations = await manager.intelligent_query(
        f"基于用户{user_id}的行为数据，推荐最适合的内容类型和互动方式"
    )

    return {
        "用户档案": insights,
        "行为偏好": preferences,
        "个性化推荐": recommendations,
        "价值评级": _calculate_user_value(insights)
    }

def _calculate_user_value(insights):
    """计算用户价值评级"""
    records = insights.get('total_records', 0)
    engagement = insights.get('comments_count', 0) + insights.get('notes_count', 0)

    if engagement > 10 and records > 20:
        return "高价值用户"
    elif engagement > 5 and records > 10:
        return "中等价值用户"
    else:
        return "潜在用户"
```

---

## 🧪 **测试和调试**

### **运行测试套件**

```bash
# LlamaIndex功能测试
uv run python test/test_llamaindex_manager.py

# 增强版工作流测试
uv run python test/test_enhanced_multi_agent_workflow.py

# 快速功能测试
uv run python test/test_enhanced_quick.py
uv run python test/test_llm_quick.py

# 运行所有测试
uv run python test/run_tests.py
```

### **调试和监控**

```bash
# 查看实时日志
tail -f logs/app.log

# 检查数据库连接
uv run python -c "
from app.infra.db.async_database import test_connection
import asyncio
asyncio.run(test_connection())
"

# 验证LLM连接
uv run python test/test_llm_manager.py
```

### **性能监控**

```python
# 监控索引构建性能
async def monitor_indexing_performance():
    import time
    from app.agents.llamaindex_manager import LlamaIndexManager

    manager = LlamaIndexManager()

    start_time = time.time()
    results = await manager.build_all_indexes()
    end_time = time.time()

    print(f"⏱️ 索引构建耗时: {end_time - start_time:.2f}秒")
    print(f"📊 构建结果: {results}")

    # 测试搜索性能
    start_time = time.time()
    search_results = await manager.semantic_search("测试查询", top_k=5)
    search_time = time.time() - start_time

    print(f"🔍 搜索耗时: {search_time:.3f}秒")
    print(f"📝 搜索结果: {len(search_results)} 条")
```

---

## 🛠️ **配置和自定义**

### **模型配置**

```python
# 在代码中指定首选模型
from app.agents.llm_manager import ModelProvider

# 可选择的模型提供商
providers = [
    ModelProvider.OPENROUTER,  # 推荐 - 稳定性好
    ModelProvider.ANTHROPIC,   # Claude系列
    ModelProvider.OPENAI,      # GPT系列
    ModelProvider.QWEN,        # 通义千问
    ModelProvider.DEEPSEEK     # DeepSeek
]

# 在Agent中使用
agent = EnhancedUserAnalystAgent(preferred_model_provider=ModelProvider.OPENROUTER)
```

### **自定义分析条件**

```python
# 高级筛选条件示例
advanced_criteria = {
    "emotional_preference": ["正向", "中性"],
    "aips_preference": ["高"],
    "unmet_preference": ["是"],
    "exclude_visited": True,
    "min_interaction_count": 5,
    "max_interaction_count": 100,
    "value_score_threshold": 7.0,
    "gender_filter": ["女"],
    "age_range": [18, 35],
    "created_after": "2024-01-01",
    "limit": 100
}
```

### **自定义 Prompt 模板**

```python
# 在 app/prompts/ 中添加自定义模板
from app.prompts import prompt_manager

# 添加新的提示词
prompt_manager.add_prompt(
    "custom_analysis",
    "请分析以下用户数据，重点关注{focus_area}，提供{analysis_type}分析。"
)

# 使用自定义提示词
formatted_prompt = prompt_manager.format_prompt(
    "custom_analysis",
    focus_area="购买意向",
    analysis_type="深度"
)
```

---

## 📊 **输出示例**

### **工作流完整输出**

```
🎉 AI增强版Multi-Agent工作流执行完成！

📈 执行统计:
✅ 成功的Agent: 4
❌ 失败的Agent: 0
⏱️  平均执行时间: 2.34秒
🧠 LLM洞察数: 4

🤖 AI增强功能:
- ✓ 智能用户洞察分析
- ✓ AI驱动策略制定
- ✓ 创意内容自动生成
- ✓ 智能协调优化

详细结果:
✅ UserAnalystAgent: 成功识别25个高价值用户
   🧠 AI洞察: 发现正向情感用户占比78%，主要集中在美食和旅游领域...

✅ ContentStrategyAgent: 成功制定内容策略，包含3个用户细分
   🧠 AI洞察: 建议针对不同用户群体采用差异化内容策略...

✅ ContentGeneratorAgent: 成功生成5个内容片段
   🧠 AI洞察: 生成的内容主题包括个性化推荐、用户体验优化等...

✅ StrategyCoordinatorAgent: 成功整合所有Agent结果
   🧠 AI洞察: 综合分析显示应优先关注高互动用户群体...

🔍 关键AI洞察摘要:
- user_analysis: 高价值用户主要特征为正向情感、高互动频次...
- content_strategy: 个性化内容策略可提升用户参与度35%...
- content_generation: AI生成内容与用户偏好匹配度达85%...
- coordination: 建议优先投入资源在Top20%用户群体...
```

### **语义搜索结果**

```
🔍 执行语义搜索: '高价值用户特征' (类型: all, Top-K: 5)

找到 5 个相关结果:
1. 类型: analysis, 分数: 0.892
   内容: 分析ID: 12345, 情感倾向: 正向, 未满足需求: 是...

2. 类型: comment, 分数: 0.847
   内容: 评论ID: 67890, 用户昵称: 旅游达人, 点赞数: 156...

3. 类型: note, 分数: 0.823
   内容: 笔记ID: 54321, 标题: 美食探店攻略, 点赞数: 892...
```

---

## 🚨 **常见问题排查**

### **连接问题**

```bash
# 测试数据库连接
uv run python -c "
from app.infra.db.async_database import test_connection
import asyncio
asyncio.run(test_connection())
"

# 测试LLM连接
uv run python -c "
from app.agents.llm_manager import llm_manager
print('可用模型:', llm_manager.get_available_providers())
"
```

### **性能优化**

```python
# 批量操作优化
async def batch_analysis(user_ids: list, batch_size: int = 10):
    """批量处理用户分析，避免单个请求过大"""
    results = []

    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        batch_results = await process_user_batch(batch)
        results.extend(batch_results)

        # 添加延迟避免API限流
        await asyncio.sleep(0.1)

    return results
```

### **错误处理**

```python
# 带重试的操作
async def robust_analysis(max_retries: int = 3):
    """带重试机制的分析操作"""
    for attempt in range(max_retries):
        try:
            result = await agent.execute_enhanced_analysis(session)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"⚠️ 尝试 {attempt + 1} 失败，重试中...")
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

---

## 🎯 **下一步计划**

当前系统已实现的功能：

- ✅ 基础用户分析 Agent
- ✅ 增强版用户分析 Agent (集成 LlamaIndex)
- ✅ LLM 模型管理和 Prompt 管理
- ✅ 智能文档索引和语义搜索
- ✅ 完整的测试套件

待实现功能：

- 🔄 ContentGeneratorAgent - 内容生成智能体
- 🔄 StrategyCoordinatorAgent - 策略协调智能体
- 🔄 FastAPI Web 接口
- 🔄 CLI 命令行工具扩展

## 📞 **技术支持**

如遇到问题，请参考：

1. 查看 `logs/app.log` 日志文件
2. 运行对应的测试脚本进行诊断
3. 检查 `app/config/settings.py` 配置
4. 确认数据库连接和 API 密钥配置

---

**Happy Coding! 🚀**
