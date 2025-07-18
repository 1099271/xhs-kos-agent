# XHS KOS Multi-Agent系统使用指南

## 快速开始

### 1. 安装依赖
```bash
# 使用uv安装依赖
uv sync

# 或者使用pip
pip install -e .
```

### 2. 配置环境变量
创建 `.env` 文件：
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=xhs_kos

# LLM API配置
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENROUTER_API_KEY=your_openrouter_key

# 其他配置
DEBUG=false
LOG_LEVEL=INFO
```

### 3. 命令行使用

#### 查看Agent状态
```bash
xhs-agent agents status
```

#### 创建内容策略
```bash
# 基本用法
xhs-agent strategy create --type engagement --timeline 7 --audience-size 30

# 高级用法
xhs-agent strategy create \
    --type conversion \
    --metrics engagement_rate=0.08 reach=10000 \
    --timeline 14 \
    --budget 1000 \
    --audience-size 50
```

#### 生成个性化内容
```bash
# 使用JSON格式用户画像
xhs-agent content generate \
    --user-profile '{"nickname": "美妆达人", "interests": ["美妆", "护肤"], "pain_points": ["选择困难"]}' \
    --type creative \
    --topic "夏季护肤心得" \
    --platform xhs
```

#### 执行完整工作流
```bash
# 使用默认配置
xhs-agent workflow execute

# 使用配置文件
xhs-agent workflow execute --config workflow_config.json --output result.json
```

#### 识别高价值用户
```bash
# 基本用法
xhs-agent users high-value --limit 20

# 指定筛选条件
xhs-agent users high-value \
    --limit 50 \
    --min-engagement 0.05 \
    --min-comments 5 \
    --output users.json
```

#### 获取用户洞察
```bash
xhs-agent users insights USER_ID --output insights.json
```

#### 运行演示
```bash
xhs-agent demo
```

### 4. FastAPI服务

#### 启动服务
```bash
# 开发模式
xhs-agent serve --reload

# 生产模式
xhs-agent serve --host 0.0.0.0 --port 8000
```

#### API端点
- `GET /` - 系统信息
- `GET /docs` - Swagger文档
- `GET /health` - 健康检查
- `GET /api/v1/agents/status` - Agent状态
- `POST /api/v1/agents/strategy/create` - 创建策略
- `POST /api/v1/agents/content/generate` - 生成内容
- `POST /api/v1/agents/workflow/execute` - 执行工作流
- `GET /api/v1/agents/users/high-value` - 高价值用户
- `GET /api/v1/agents/users/{user_id}/insights` - 用户洞察

### 5. 配置文件示例

#### 工作流配置文件 (workflow_config.json)
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
    "budget": 1000,
    "audience_size": 50
  },
  "user_criteria": {
    "min_engagement_rate": 0.05,
    "min_comment_count": 5,
    "limit": 100
  },
  "workflow_config": {
    "optimize_strategy": true,
    "generate_reports": true,
    "send_notifications": false
  }
}
```

#### 用户画像示例
```json
{
  "nickname": "美妆达人小雅",
  "age_group": "25-34",
  "location": "上海",
  "interests": ["美妆", "护肤", "时尚"],
  "pain_points": ["选择困难", "产品质量担忧", "价格敏感"],
  "content_preferences": ["教程", "评测", "对比"],
  "platform_behavior": {
    "active_time": "晚上8-10点",
    "content_type": "视频+图文",
    "engagement_style": "点赞+收藏"
  }
}
```

## 使用场景示例

### 场景1：品牌新品推广
```bash
# 1. 创建用户获取策略
xhs-agent strategy create \
    --type acquisition \
    --metrics reach=20000 new_followers=500 \
    --timeline 10 \
    --budget 2000 \
    --audience-size 100

# 2. 识别目标用户
xhs-agent users high-value \
    --limit 100 \
    --min-engagement 0.04 \
    --output target_users.json

# 3. 生成个性化内容
xhs-agent content generate \
    --user-profile @target_user_profile.json \
    --type promotional \
    --topic "新品上市体验" \
    --output content_batch.json

# 4. 执行完整工作流
xhs-agent workflow execute \
    --config brand_campaign.json \
    --output campaign_result.json
```

### 场景2：用户互动提升
```bash
# 快速执行提升互动的工作流
xhs-agent workflow execute --config engagement_boost.json
```

### 场景3：竞品分析
```bash
# 分析竞品用户群体
xhs-agent users high-value \
    --min-engagement 0.06 \
    --min-comments 10 \
    --limit 200 > competitors_users.json
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置是否正确
   - 确保数据库服务正在运行
   - 检查网络连接和防火墙设置

2. **LLM API调用失败**
   - 检查API密钥是否正确设置
   - 确认账户余额充足
   - 检查网络代理设置

3. **内容生成质量不高**
   - 调整用户画像的详细程度
   - 尝试不同的内容类型
   - 优化提示词模板

### 调试模式
```bash
# 启用详细日志
xhs-agent --verbose agents status

# 使用本地模型
xhs-agent --model-provider LOCAL strategy create --type engagement
```

## 性能优化

### 批量处理
- 使用批量内容生成功能减少API调用
- 合理设置并发任务数量
- 利用缓存机制避免重复计算

### 资源监控
```bash
# 监控系统资源使用
xhs-agent agents status --verbose

# 查看工作流执行性能
xhs-agent workflow execute --config config.json --output result.json
```

## 扩展开发

### 添加新的Agent类型
1. 在 `app/agents/` 目录创建新的Agent类
2. 继承基础Agent接口
3. 在CLI中添加对应命令
4. 更新API端点

### 自定义内容模板
1. 修改 `app/prompts/` 目录下的提示词模板
2. 使用PromptManager统一管理
3. 测试新模板效果

## 最佳实践

1. **用户画像构建**
   - 收集多维度用户数据
   - 定期更新用户标签
   - 结合语义搜索优化精准度

2. **内容策略制定**
   - 设定SMART目标（具体、可衡量、可达成、相关、时限）
   - 基于数据制定策略，避免主观判断
   - 建立A/B测试机制

3. **效果评估**
   - 建立完整的KPI体系
   - 定期回顾和优化策略
   - 利用机器学习持续改进