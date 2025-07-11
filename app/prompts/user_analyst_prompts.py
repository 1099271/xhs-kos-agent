"""
用户分析Agent专用提示词
包含用户行为分析、价值评估、需求识别等相关提示词
"""

from app.prompts import PromptTemplate, AgentType, PromptType


# 用户分析相关的专业提示词
USER_ANALYST_PROMPTS = {
    
    "deep_user_analysis": PromptTemplate(
        name="deep_user_analysis",
        agent_type=AgentType.USER_ANALYST,
        prompt_type=PromptType.USER,
        template="""作为专业的用户行为分析师，请对以下用户数据进行深度分析：

用户基础信息：
{user_basic_info}

用户行为数据：
{user_behavior_data}

评论情感分析：
{comment_sentiment_data}

请从以下维度进行专业分析：

1. **用户画像构建**
   - 人口统计学特征
   - 兴趣偏好标签
   - 消费行为特征
   - 社交影响力评估

2. **价值潜力评估**
   - 商业价值指数 (1-100分)
   - 转化可能性评估
   - 生命周期价值预测
   - 风险因素识别

3. **需求洞察分析**
   - 显性需求识别
   - 隐性需求挖掘
   - 痛点问题分析
   - 解决方案建议

4. **营销策略建议**
   - 最佳触达时机
   - 个性化内容偏好
   - 沟通渠道建议
   - 转化路径设计

请提供详细、可执行的分析报告。""",
        description="深度用户分析的专业提示词",
        variables=["user_basic_info", "user_behavior_data", "comment_sentiment_data"]
    ),
    
    "user_segmentation": PromptTemplate(
        name="user_segmentation",
        agent_type=AgentType.USER_ANALYST,
        prompt_type=PromptType.USER,
        template="""基于以下用户群体数据，进行智能用户细分：

用户群体数据：
{user_group_data}

分析维度：
{segmentation_dimensions}

请执行以下用户细分任务：

1. **细分策略制定**
   - 选择最佳细分维度组合
   - 确定细分粒度和数量
   - 制定细分标准和阈值

2. **用户群体识别**
   - 高价值用户群 (核心目标)
   - 潜力用户群 (培育目标)  
   - 活跃用户群 (维护目标)
   - 流失风险用户群 (挽回目标)

3. **群体特征描述**
   - 每个细分群体的典型特征
   - 行为模式和偏好分析
   - 价值贡献和增长潜力
   - 差异化特点总结

4. **营销应用建议**
   - 针对每个群体的营销策略
   - 个性化内容建议
   - 触达渠道优化
   - 转化路径设计

输出格式要求：结构化的细分报告，包含数据支撑和可执行建议。""",
        description="用户细分分析的专业提示词",
        variables=["user_group_data", "segmentation_dimensions"]
    ),
    
    "churn_risk_analysis": PromptTemplate(
        name="churn_risk_analysis", 
        agent_type=AgentType.USER_ANALYST,
        prompt_type=PromptType.USER,
        template="""请分析以下用户的流失风险并提供预防策略：

用户历史行为：
{user_history_data}

最近活动变化：
{recent_activity_changes}

同群体对比数据：
{cohort_comparison_data}

分析任务：

1. **流失风险评估**
   - 流失概率评分 (0-100%)
   - 风险等级分类 (低/中/高/极高)
   - 关键风险指标识别
   - 流失时间窗口预测

2. **流失原因分析**
   - 行为变化模式识别
   - 触发因素分析
   - 内外部环境影响
   - 竞品流失分析

3. **预防策略制定**
   - 即时干预措施
   - 中期挽留策略
   - 长期关系维护
   - 个性化挽回方案

4. **监控预警机制**
   - 关键指标监控
   - 预警阈值设定
   - 自动化触发条件
   - 响应处理流程

请提供可操作的风险防控方案。""",
        description="用户流失风险分析的专业提示词",
        variables=["user_history_data", "recent_activity_changes", "cohort_comparison_data"]
    ),
    
    "user_journey_mapping": PromptTemplate(
        name="user_journey_mapping",
        agent_type=AgentType.USER_ANALYST,
        prompt_type=PromptType.USER,
        template="""基于用户数据，绘制完整的用户旅程地图：

用户接触点数据：
{touchpoint_data}

行为转化数据：
{conversion_funnel_data}

用户反馈数据：
{user_feedback_data}

请构建用户旅程地图：

1. **旅程阶段划分**
   - 认知阶段 (Awareness)
   - 兴趣阶段 (Interest)  
   - 考虑阶段 (Consideration)
   - 购买阶段 (Purchase)
   - 使用阶段 (Usage)
   - 推荐阶段 (Advocacy)

2. **关键触点分析**
   - 每个阶段的主要触点
   - 触点效果和转化率
   - 用户体验质量评估
   - 痛点和摩擦点识别

3. **情感曲线描绘**
   - 用户情感变化轨迹
   - 满意度波动分析
   - 关键情感转折点
   - 情感驱动因素

4. **优化机会识别**
   - 转化瓶颈分析
   - 体验提升机会
   - 新触点设计建议
   - 旅程个性化策略

输出要求：可视化的旅程地图和详细的优化建议。""",
        description="用户旅程地图分析的专业提示词",
        variables=["touchpoint_data", "conversion_funnel_data", "user_feedback_data"]
    )
}


def get_user_analyst_prompt(prompt_name: str) -> PromptTemplate:
    """获取用户分析Agent的特定提示词"""
    if prompt_name not in USER_ANALYST_PROMPTS:
        raise ValueError(f"未找到名为 '{prompt_name}' 的用户分析提示词")
    return USER_ANALYST_PROMPTS[prompt_name]


def list_user_analyst_prompts() -> dict:
    """列出所有用户分析Agent提示词"""
    return {name: prompt.description for name, prompt in USER_ANALYST_PROMPTS.items()}