"""
内容策略Agent专用提示词
包含内容规划、策略制定、效果预测等相关提示词
"""

from app.prompts import PromptTemplate, AgentType, PromptType


# 内容策略相关的专业提示词
CONTENT_STRATEGY_PROMPTS = {
    
    "content_strategy_framework": PromptTemplate(
        name="content_strategy_framework",
        agent_type=AgentType.CONTENT_STRATEGY,
        prompt_type=PromptType.USER,
        template="""作为资深内容策略专家，请基于以下信息制定完整的内容营销策略框架：

业务背景：
{business_context}

目标用户画像：
{target_audience_profiles}

竞品分析数据：
{competitor_analysis}

平台特性数据：
{platform_characteristics}

请制定包含以下要素的内容策略框架：

1. **内容战略定位**
   - 内容使命和愿景
   - 核心价值主张
   - 差异化定位策略
   - 品牌声音和调性

2. **内容主题矩阵**
   - 核心内容支柱 (3-5个)
   - 内容主题分类体系
   - 话题优先级排序
   - 内容深度层次规划

3. **用户内容旅程**
   - 认知阶段内容策略
   - 兴趣培养内容策略
   - 决策支持内容策略
   - 用户留存内容策略

4. **内容形式组合**
   - 内容格式选择 (图文/视频/音频等)
   - 各格式的使用场景
   - 内容长度和复杂度规划
   - 互动性设计考虑

5. **发布节奏规划**
   - 内容发布频率
   - 最佳发布时间
   - 季节性内容规划
   - 热点事件响应策略

请提供系统化、可执行的策略框架。""",
        description="内容策略框架制定的专业提示词",
        variables=["business_context", "target_audience_profiles", "competitor_analysis", "platform_characteristics"]
    ),
    
    "content_calendar_planning": PromptTemplate(
        name="content_calendar_planning",
        agent_type=AgentType.CONTENT_STRATEGY,
        prompt_type=PromptType.USER,
        template="""请基于内容策略制定详细的内容日历规划：

内容策略概览：
{content_strategy_overview}

业务关键节点：
{business_milestones}

用户活跃时间分析：
{user_activity_patterns}

竞品内容节奏：
{competitor_content_rhythm}

请制定内容日历规划：

1. **月度内容主题**
   - 每月核心主题确定
   - 主题与业务目标关联
   - 季节性和节日规划
   - 热点话题储备计划

2. **周度内容分布**
   - 工作日内容安排
   - 周末内容特色规划
   - 内容类型轮换机制
   - 互动内容穿插策略

3. **日度发布节奏**
   - 最佳发布时间点
   - 内容密度控制
   - 多平台协调发布
   - 用户反馈收集时机

4. **内容制作时间线**
   - 内容策划提前期
   - 创作制作周期
   - 审核发布流程
   - 应急内容储备

5. **效果监控节点**
   - 关键指标监控时间
   - 策略调整评估点
   - A/B测试安排
   - 优化迭代计划

输出要求：可执行的内容日历模板和操作指南。""",
        description="内容日历规划的专业提示词",
        variables=["content_strategy_overview", "business_milestones", "user_activity_patterns", "competitor_content_rhythm"]
    ),
    
    "content_performance_prediction": PromptTemplate(
        name="content_performance_prediction",
        agent_type=AgentType.CONTENT_STRATEGY,
        prompt_type=PromptType.USER,
        template="""基于历史数据和内容特征，预测内容表现：

历史内容表现数据：
{historical_performance_data}

内容特征数据：
{content_features_data}

用户互动模式：
{user_engagement_patterns}

平台算法变化：
{platform_algorithm_updates}

请进行内容表现预测分析：

1. **表现预测模型**
   - 关键影响因子识别
   - 表现预测算法设计
   - 置信度区间设定
   - 预测准确性验证

2. **内容分类预测**
   - 高表现内容特征
   - 中等表现内容特征
   - 低表现内容特征
   - 风险内容识别

3. **优化建议生成**
   - 标题优化建议
   - 内容结构调整
   - 发布时机优化
   - 推广策略建议

4. **风险评估预警**
   - 表现不佳风险因素
   - 负面反馈可能性
   - 平台限流风险
   - 应对策略准备

5. **ROI预测分析**
   - 预期曝光量估算
   - 互动率预测范围
   - 转化效果预估
   - 投入产出比分析

请提供数据支撑的预测报告和优化建议。""",
        description="内容表现预测的专业提示词",
        variables=["historical_performance_data", "content_features_data", "user_engagement_patterns", "platform_algorithm_updates"]
    ),
    
    "viral_content_strategy": PromptTemplate(
        name="viral_content_strategy",
        agent_type=AgentType.CONTENT_STRATEGY,
        prompt_type=PromptType.USER,
        template="""基于病毒传播理论，制定高传播性内容策略：

平台传播特性：
{platform_viral_characteristics}

用户分享行为分析：
{user_sharing_behavior}

成功病毒案例研究：
{viral_case_studies}

目标传播目标：
{viral_objectives}

请制定病毒内容策略：

1. **病毒传播机制设计**
   - 情感触发点设计
   - 分享动机激发
   - 传播路径优化
   - 病毒系数提升策略

2. **内容病毒要素**
   - 话题争议性控制
   - 情感共鸣点强化
   - 参与门槛设计
   - 传播奖励机制

3. **传播节点布局**
   - KOL合作策略
   - 社群传播布局
   - 跨平台传播协调
   - 媒体放大策略

4. **传播时机把控**
   - 最佳发布时间窗口
   - 热点事件结合策略
   - 传播节奏控制
   - 持续热度维护

5. **风险控制措施**
   - 负面传播预防
   - 争议内容边界
   - 危机应对预案
   - 品牌形象保护

输出要求：可执行的病毒传播策略和风险控制方案。""",
        description="病毒内容策略制定的专业提示词",
        variables=["platform_viral_characteristics", "user_sharing_behavior", "viral_case_studies", "viral_objectives"]
    ),
    
    "content_personalization_strategy": PromptTemplate(
        name="content_personalization_strategy",
        agent_type=AgentType.CONTENT_STRATEGY,
        prompt_type=PromptType.USER,
        template="""制定基于用户画像的个性化内容策略：

用户细分数据：
{user_segmentation_data}

个性化标签体系：
{personalization_tags}

用户偏好分析：
{user_preference_analysis}

技术实现能力：
{technical_capabilities}

请设计个性化内容策略：

1. **个性化维度设计**
   - 人口统计学维度
   - 行为偏好维度
   - 兴趣标签维度
   - 生命周期阶段维度

2. **内容个性化规则**
   - 内容推荐算法
   - 个性化程度控制
   - 新用户冷启动策略
   - 偏好学习机制

3. **个性化内容矩阵**
   - 不同群体内容偏好
   - 内容形式个性化
   - 互动方式个性化
   - 推送时间个性化

4. **动态调优机制**
   - 用户反馈收集
   - 偏好变化追踪
   - 算法持续优化
   - 效果评估调整

5. **规模化实施方案**
   - 内容生产流程
   - 自动化推荐系统
   - 人工审核机制
   - 质量控制标准

请提供可落地的个性化内容策略方案。""",
        description="个性化内容策略制定的专业提示词",
        variables=["user_segmentation_data", "personalization_tags", "user_preference_analysis", "technical_capabilities"]
    )
}


def get_content_strategy_prompt(prompt_name: str) -> PromptTemplate:
    """获取内容策略Agent的特定提示词"""
    if prompt_name not in CONTENT_STRATEGY_PROMPTS:
        raise ValueError(f"未找到名为 '{prompt_name}' 的内容策略提示词")
    return CONTENT_STRATEGY_PROMPTS[prompt_name]


def list_content_strategy_prompts() -> dict:
    """列出所有内容策略Agent提示词"""
    return {name: prompt.description for name, prompt in CONTENT_STRATEGY_PROMPTS.items()}