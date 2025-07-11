"""
内容生成Agent专用提示词
包含创意生成、文案写作、多媒体内容制作等相关提示词
"""

from app.prompts import PromptTemplate, AgentType, PromptType


# 内容生成相关的专业提示词
CONTENT_GENERATOR_PROMPTS = {
    
    "creative_content_generation": PromptTemplate(
        name="creative_content_generation",
        agent_type=AgentType.CONTENT_GENERATOR,
        prompt_type=PromptType.USER,
        template="""作为创意内容专家，请基于以下要求生成高质量的原创内容：

内容需求概述：
{content_requirements}

目标受众画像：
{target_audience_profile}

品牌调性指南：
{brand_tone_guidelines}

创意限制条件：
{creative_constraints}

请生成以下类型的创意内容：

1. **吸引力标题创作**
   - 主标题 (核心吸引点)
   - 副标题 (价值补充说明)  
   - 标签标题 (SEO和发现性)
   - A/B测试备选标题

2. **核心内容创作**
   - 开头Hook设计 (前3秒抓住注意力)
   - 主体内容结构 (逻辑清晰、层次分明)
   - 关键信息突出 (重点内容强化)
   - 结尾Call-to-Action (引导用户行动)

3. **互动元素设计**
   - 问题引导 (激发用户思考)
   - 投票互动 (增加参与度)
   - 话题标签 (扩大传播范围)
   - 分享引导 (促进二次传播)

4. **视觉呈现建议**
   - 配图风格建议
   - 色彩搭配方案
   - 排版布局建议
   - 视觉焦点设计

5. **多平台适配**
   - 不同平台内容调整
   - 字数限制适配
   - 格式要求匹配
   - 算法友好优化

输出要求：完整可用的内容方案，包含执行细节。""",
        description="创意内容生成的专业提示词",
        variables=["content_requirements", "target_audience_profile", "brand_tone_guidelines", "creative_constraints"]
    ),
    
    "storytelling_content": PromptTemplate(
        name="storytelling_content",
        agent_type=AgentType.CONTENT_GENERATOR,
        prompt_type=PromptType.USER,
        template="""运用故事叙述技巧，创作引人入胜的故事性内容：

故事主题：
{story_theme}

角色设定：
{character_settings}

情节要求：
{plot_requirements}

情感目标：
{emotional_objectives}

请创作故事性内容：

1. **故事架构设计**
   - 故事背景设定
   - 主要角色塑造
   - 冲突设置与解决
   - 故事弧线规划

2. **情节发展脉络**
   - 引入阶段 (背景铺垫)
   - 发展阶段 (冲突升级)
   - 高潮阶段 (关键转折)
   - 结局阶段 (问题解决)

3. **情感层次构建**
   - 情感起伏设计
   - 共鸣点植入
   - 情感释放时机
   - 情感升华表达

4. **叙述技巧运用**
   - 视角选择 (第一/第三人称)
   - 时间线安排
   - 悬念设置
   - 细节描写

5. **价值传递融入**
   - 主题思想表达
   - 价值观传递
   - 行为引导暗示
   - 品牌价值植入

输出要求：完整的故事内容，具备强烈的情感感染力。""",
        description="故事性内容创作的专业提示词",
        variables=["story_theme", "character_settings", "plot_requirements", "emotional_objectives"]
    ),
    
    "educational_content": PromptTemplate(
        name="educational_content",
        agent_type=AgentType.CONTENT_GENERATOR,
        prompt_type=PromptType.USER,
        template="""创作具有教育价值的知识性内容：

知识主题：
{knowledge_topic}

受众知识水平：
{audience_knowledge_level}

学习目标：
{learning_objectives}

内容深度要求：
{content_depth_requirements}

请创作教育性内容：

1. **知识结构设计**
   - 核心概念界定
   - 知识点分解
   - 逻辑关系梳理
   - 难点重点标识

2. **教学方法应用**
   - 由浅入深progression
   - 类比举例说明
   - 图表辅助理解
   - 案例实践应用

3. **内容组织架构**
   - 引言导入 (激发兴趣)
   - 知识讲解 (系统阐述)
   - 实例分析 (加深理解)
   - 总结回顾 (强化记忆)

4. **互动学习设计**
   - 思考问题设置
   - 练习题目设计
   - 自测环节安排
   - 延伸学习建议

5. **记忆强化机制**
   - 关键信息重复
   - 口诀记忆技巧
   - 视觉记忆辅助
   - 应用场景关联

输出要求：系统完整的教育内容，易懂易记易应用。""",
        description="教育性内容创作的专业提示词",
        variables=["knowledge_topic", "audience_knowledge_level", "learning_objectives", "content_depth_requirements"]
    ),
    
    "entertainment_content": PromptTemplate(
        name="entertainment_content",
        agent_type=AgentType.CONTENT_GENERATOR,
        prompt_type=PromptType.USER,
        template="""创作具有娱乐性和趣味性的轻松内容：

娱乐主题：
{entertainment_theme}

幽默风格偏好：
{humor_style_preference}

受众兴趣特点：
{audience_interest_characteristics}

内容时长要求：
{content_duration_requirements}

请创作娱乐性内容：

1. **幽默元素设计**
   - 笑点设置策略
   - 幽默表达技巧
   - 反转惊喜设计
   - 段子包袱安排

2. **趣味互动元素**
   - 游戏化设计
   - 挑战任务设置
   - 互动问答环节
   - 用户参与引导

3. **视觉娱乐效果**
   - 表情包使用
   - GIF动图建议
   - 搞笑配图选择
   - 视觉特效建议

4. **情绪调动技巧**
   - 轻松氛围营造
   - 正面情绪激发
   - 压力释放设计
   - 快乐体验创造

5. **传播性增强**
   - 梗文化运用
   - 流行元素融入
   - 二次创作空间
   - 分享动机激发

输出要求：轻松有趣的娱乐内容，具备高传播潜力。""",
        description="娱乐性内容创作的专业提示词",
        variables=["entertainment_theme", "humor_style_preference", "audience_interest_characteristics", "content_duration_requirements"]
    ),
    
    "promotional_content": PromptTemplate(
        name="promotional_content",
        agent_type=AgentType.CONTENT_GENERATOR,
        prompt_type=PromptType.USER,
        template="""创作具有推广效果的营销性内容：

产品/服务信息：
{product_service_info}

销售目标：
{sales_objectives}

目标客户特征：
{target_customer_profile}

竞争优势：
{competitive_advantages}

请创作推广性内容：

1. **价值主张设计**
   - 核心卖点提炼
   - 用户痛点对应
   - 解决方案呈现
   - 独特价值强调

2. **说服力构建**
   - 权威性建立
   - 社会证明展示
   - 稀缺性营造
   - 紧迫感激发

3. **信任感建立**
   - 真实案例分享
   - 用户评价展示
   - 专业资质证明
   - 风险承诺保障

4. **行动引导设计**
   - 清晰的CTA设置
   - 行动步骤说明
   - 便利性强调
   - 激励机制设计

5. **情感连接建立**
   - 情感需求识别
   - 情感价值传递
   - 生活场景关联
   - 梦想愿景描绘

输出要求：有说服力的推广内容，平衡商业性和用户价值。""",
        description="推广性内容创作的专业提示词",
        variables=["product_service_info", "sales_objectives", "target_customer_profile", "competitive_advantages"]
    )
}


def get_content_generator_prompt(prompt_name: str) -> PromptTemplate:
    """获取内容生成Agent的特定提示词"""
    if prompt_name not in CONTENT_GENERATOR_PROMPTS:
        raise ValueError(f"未找到名为 '{prompt_name}' 的内容生成提示词")
    return CONTENT_GENERATOR_PROMPTS[prompt_name]


def list_content_generator_prompts() -> dict:
    """列出所有内容生成Agent提示词"""
    return {name: prompt.description for name, prompt in CONTENT_GENERATOR_PROMPTS.items()}