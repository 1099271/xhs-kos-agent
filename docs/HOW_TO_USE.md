# XHS KOS Multi-Agent系统使用手册

## 📋 目录
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [命令行使用](#命令行使用)
- [API接口](#api接口)
- [实际应用案例](#实际应用案例)
- [故障排除](#故障排除)
- [性能优化](#性能优化)

## 快速开始

### 1. 环境准备

#### 系统要求
- Python 3.8+
- MySQL 8.0+ 或 PostgreSQL 12+
- 8GB+ RAM (推荐16GB)
- 10GB+ 磁盘空间

#### 安装步骤
```bash
# 克隆项目
git clone https://github.com/your-org/xhs-kos-agent.git
cd xhs-kos-agent

# 使用uv安装依赖（推荐）
uv sync

# 或使用pip
pip install -e .

# 验证安装
xhs-agent --version
```

### 2. 配置文件设置

创建 `.env` 文件：
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=xhs_kos

# LLM API配置（至少配置一个）
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
OPENROUTER_API_KEY=sk-xxx

# 可选配置
DEBUG=false
LOG_LEVEL=INFO
MODEL_PROVIDER=OPENROUTER
```

### 3. 数据库初始化

```bash
# 运行数据库迁移
python -m app.infra.db.migrate

# 或手动执行SQL文件
mysql -u your_user -p xhs_kos < docs/database_structure.sql
```

## 命令行使用

### 基本命令结构
```bash
xhs-agent [全局选项] [命令组] [子命令] [参数]
```

### 全局选项
- `--verbose, -v`: 启用详细日志
- `--model-provider`: 选择LLM提供商 (OPENAI/OPENROUTER/ANTHROPIC/LOCAL)

### 核心命令

#### 1. 查看系统状态
```bash
# 查看所有Agent状态
xhs-agent agents status

# 查看详细状态
xhs-agent -v agents status
```

#### 2. 创建内容策略
```bash
# 简单策略
xhs-agent strategy create --type engagement --timeline 7 --audience-size 30

# 高级策略
xhs-agent strategy create \
    --type conversion \
    --metrics engagement_rate=0.08 reach=15000 conversion_rate=0.05 \
    --timeline 14 \
    --budget 2000 \
    --audience-size 50 \
    --min-engagement 0.04 \
    --min-comments 5
```

#### 3. 用户分析
```bash
# 识别高价值用户
xhs-agent users high-value --limit 100 --output high_value_users.json

# 获取特定用户洞察
xhs-agent users insights USER123 --output user_insights.json
```

#### 4. 内容生成
```bash
# 单条内容生成
xhs-agent content generate \
    --user-profile '{"nickname": "美妆达人", "interests": ["美妆", "护肤"], "pain_points": ["选择困难"]}' \
    --type creative \
    --topic "夏季护肤必备清单" \
    --platform xhs \
    --output content1.json

# 批量内容生成（使用配置文件）
xhs-agent content generate-batch --config content_batch.json
```

#### 5. 执行完整工作流
```bash
# 使用默认配置
xhs-agent workflow execute

# 使用自定义配置
xhs-agent workflow execute --config my_workflow.json --output result.json

# 异步执行
xhs-agent workflow execute --async
```

#### 6. 运行演示
```bash
# 快速体验系统功能
xhs-agent demo

# 使用特定模型
xhs-agent --model-provider OPENROUTER demo
```

## API接口

### 启动Web服务
```bash
# 开发模式
xhs-agent serve --reload

# 生产模式
xhs-agent serve --host 0.0.0.0 --port 8000
```

### API端点一览

#### 基础端点
- `GET /` - 系统信息
- `GET /health` - 健康检查
- `GET /docs` - Swagger文档

#### Agent管理
- `GET /api/v1/agents/status` - 获取Agent状态
- `GET /api/v1/agents/health` - 健康检查

#### 策略管理
- `POST /api/v1/agents/strategy/create` - 创建内容策略
- `POST /api/v1/agents/strategy/optimize` - 优化现有策略

#### 内容生成
- `POST /api/v1/agents/content/generate` - 生成单条内容
- `POST /api/v1/agents/content/generate-batch` - 批量生成内容

#### 用户分析
- `GET /api/v1/agents/users/high-value` - 获取高价值用户
- `GET /api/v1/agents/users/{user_id}/insights` - 获取用户洞察

#### 工作流
- `POST /api/v1/agents/workflow/execute` - 执行完整工作流

### API使用示例

#### 创建策略
```bash
curl -X POST "http://localhost:8000/api/v1/agents/strategy/create" \
  -H "Content-Type: application/json" \
  -d '{
    "objective_type": "engagement",
    "target_metrics": {"engagement_rate": 0.05, "reach": 10000},
    "timeline_days": 7,
    "budget_limit": 1000,
    "target_audience_size": 30
  }'
```

#### 生成内容
```bash
curl -X POST "http://localhost:8000/api/v1/agents/content/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "nickname": "小美",
      "interests": ["美妆", "护肤"],
      "pain_points": ["选择困难"]
    },
    "content_type": "creative",
    "topic": "夏季护肤心得",
    "platform": "xhs"
  }'
```

## 实际应用案例

### 案例1：新品上市推广

#### 场景描述
美妆品牌推出夏季新品防晒霜，需要在1个月内获得5000+互动和200+转化。

#### 执行步骤

1. **创建推广策略**
```bash
xhs-agent strategy create \
    --type conversion \
    --metrics engagement_rate=0.06 reach=20000 conversion_rate=0.04 \
    --timeline 30 \
    --budget 5000 \
    --audience-size 100 \
    --output summer_campaign_strategy.json
```

2. **识别目标用户**
```bash
xhs-agent users high-value \
    --limit 100 \
    --min-engagement 0.05 \
    --min-comments 3 \
    --output target_users.json
```

3. **生成系列内容**
```bash
# 创建内容配置文件
cat > content_plan.json <<EOF
{
  "content_series": [
    {
      "topic": "新品防晒霜开箱测评",
      "type": "creative",
      "user_group": "测评达人"
    },
    {
      "topic": "防晒霜正确使用方法",
      "type": "educational",
      "user_group": "护肤新手"
    },
    {
      "topic": "夏日防晒必备清单",
      "type": "promotional",
      "user_group": "美妆爱好者"
    }
  ]
}
EOF

xhs-agent workflow execute --config content_plan.json --output campaign_result.json
```

### 案例2：用户互动提升

#### 场景描述
账号互动率下降，需要在2周内提升互动率至8%以上。

#### 执行步骤
```bash
# 快速执行互动提升策略
xhs-agent strategy create \
    --type engagement \
    --metrics engagement_rate=0.08 reach=5000 \
    --timeline 14 \
    --audience-size 50 \
    --min-engagement 0.03

# 执行优化工作流
xhs-agent workflow execute --config engagement_boost.json
```

### 案例3：竞品分析

#### 场景描述
分析竞品在小红书上的表现，识别高价值用户群体。

#### 执行步骤
```bash
# 1. 收集竞品用户数据
xhs-agent users high-value \
    --limit 500 \
    --min-engagement 0.06 \
    --min-comments 5 \
    --output competitors_users.json

# 2. 分析用户洞察
xhs-agent users insights COMPETITOR_USER_ID --output insights.json

# 3. 制定差异化策略
xhs-agent strategy create \
    --type user_acquisition \
    --metrics new_followers=1000 reach=15000 \
    --timeline 21 \
    --audience-size 200
```

## 配置文件模板

### 工作流配置文件

#### `workflow_config.json`
```json
{
  "strategy_objective": {
    "type": "engagement",
    "metrics": {
      "engagement_rate": 0.08,
      "reach": 10000,
      "conversion_rate": 0.03
    },
    "timeline": 14,
    "budget": 1500,
    "audience_size": 50
  },
  "user_criteria": {
    "min_engagement_rate": 0.05,
    "min_comment_count": 3,
    "limit": 100,
    "demographics": {
      "age_range": "25-35",
      "location": ["一线城市", "新一线城市"]
    }
  },
  "content_config": {
    "content_mix": {
      "creative": 0.4,
      "educational": 0.3,
      "entertainment": 0.2,
      "promotional": 0.1
    },
    "posting_frequency": "daily",
    "optimal_time": ["20:00-22:00", "12:00-14:00"]
  },
  "optimization": {
    "a_b_testing": true,
    "real_time_adjustment": true,
    "performance_tracking": true
  }
}
```

### 用户画像模板

#### `user_profile_template.json`
```json
{
  "basic_info": {
    "nickname": "小美",
    "age_group": "25-34",
    "location": "上海",
    "occupation": "白领",
    "income_level": "中等"
  },
  "interests": [
    "美妆",
    "护肤",
    "时尚",
    "旅行"
  ],
  "pain_points": [
    "选择困难",
    "产品质量担忧",
    "价格敏感",
    "信息过载"
  ],
  "behavior": {
    "active_time": ["20:00-22:00", "12:00-13:00"],
    "content_preference": ["视频", "图文结合"],
    "engagement_type": ["点赞", "收藏", "评论"],
    "purchase_frequency": "每月2-3次"
  },
  "brand_affinity": {
    "preferred_brands": ["完美日记", "花西子", "3CE"],
    "price_range": "100-300元",
    "loyalty_level": "中等"
  }
}
```

## 故障排除

### 常见问题及解决方案

#### 1. 数据库连接问题
**症状**: `ConnectionError: Can't connect to MySQL server`
```bash
# 检查数据库服务
sudo systemctl status mysql

# 检查配置
mysql -h localhost -u your_user -p

# 测试连接
python -c "import aiomysql; print('OK')"
```

#### 2. API密钥问题
**症状**: `AuthenticationError: Invalid API key`
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 验证密钥
curl -H "Authorization: Bearer YOUR_KEY" https://api.openai.com/v1/models
```

#### 3. 内存不足
**症状**: `MemoryError` 或系统变慢
```bash
# 监控资源
htop

# 减少并发数
export MAX_WORKERS=2

# 使用轻量级模型
export MODEL_PROVIDER=LOCAL
```

#### 4. 内容生成质量低
**症状**: 生成的内容不符合预期
```bash
# 检查用户画像完整性
xhs-agent users insights USER_ID

# 调整提示词模板
# 编辑 app/prompts/content_generator_prompts.py

# 使用更详细的用户画像
# 增加兴趣点、痛点、行为特征
```

### 调试模式

#### 启用详细日志
```bash
# 全局调试
xhs-agent -v agents status

# 调试特定命令
xhs-agent -v strategy create --type engagement

# 查看API调用
export DEBUG_API=true
xhs-agent demo
```

#### 性能监控
```bash
# 系统资源监控
xhs-agent agents status --verbose

# 工作流性能分析
xhs-agent workflow execute --config config.json --output perf_result.json
```

## 性能优化

### 最佳实践

#### 1. 批量处理
```bash
# 批量用户分析
xhs-agent users high-value --limit 500 --batch-size 50

# 批量内容生成
xhs-agent content generate-batch --config batch_config.json
```

#### 2. 缓存优化
```python
# 在.env中配置缓存
CACHE_ENABLED=true
CACHE_TTL=3600
REDIS_URL=redis://localhost:6379
```

#### 3. 并发控制
```bash
# 限制并发数
export MAX_CONCURRENT_TASKS=5
export MAX_WORKERS=3
```

#### 4. 模型选择
```bash
# 根据场景选择模型
xhs-agent --model-provider OPENAI strategy create  # 高质量
xhs-agent --model-provider LOCAL strategy create   # 低成本
xhs-agent --model-provider OPENROUTER strategy create  # 平衡
```

### 扩展开发

#### 添加新Agent
1. 创建Agent类：`app/agents/my_new_agent.py`
2. 注册到工作流：`app/agents/enhanced_multi_agent_workflow.py`
3. 添加CLI命令：`cli/multi_agent_cli.py`
4. 添加API端点：`app/api/routers/agent_routes.py`

#### 自定义提示词
1. 编辑提示词文件：`app/prompts/`
2. 测试新提示词：
```bash
xhs-agent content generate --topic "测试新提示词" --type creative
```

## 联系方式

- **技术支持**: support@xhs-kos.com
- **文档更新**: docs@xhs-kos.com
- **问题反馈**: https://github.com/your-org/xhs-kos-agent/issues

---

*最后更新: 2025-07-17*
*版本: v1.0.0*