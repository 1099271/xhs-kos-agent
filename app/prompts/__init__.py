"""
Prompts管理模块
统一管理所有LLM提示词，支持模板化和多语言
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class PromptType(Enum):
    """提示词类型枚举"""
    SYSTEM = "system"
    USER = "user" 
    ASSISTANT = "assistant"


class AgentType(Enum):
    """Agent类型枚举"""
    USER_ANALYST = "user_analyst"
    CONTENT_STRATEGY = "content_strategy"
    CONTENT_GENERATOR = "content_generator"
    STRATEGY_COORDINATOR = "strategy_coordinator"
    TASK_ANALYZER = "task_analyzer"


@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    agent_type: AgentType
    prompt_type: PromptType
    template: str
    description: str
    variables: list
    
    def format(self, **kwargs) -> str:
        """格式化提示词模板"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"缺少必需的变量: {missing_var}。需要的变量: {self.variables}")


class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        self.prompts: Dict[str, PromptTemplate] = {}
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """加载默认提示词"""
        
        # 用户分析Agent提示词
        self.register_prompt(PromptTemplate(
            name="user_analyst_system",
            agent_type=AgentType.USER_ANALYST,
            prompt_type=PromptType.SYSTEM,
            template="""你是{agent_name}，专门负责分析UGC平台用户数据，识别高价值潜在客户。

你的任务是：
1. 分析用户评论行为和情感倾向
2. 识别用户的未满足需求
3. 评估用户的商业价值潜力
4. 提供个性化的营销建议

请用专业、客观的语调回答，提供具体可执行的建议。""",
            description="用户分析Agent的系统提示词",
            variables=["agent_name"]
        ))
        
        self.register_prompt(PromptTemplate(
            name="user_analyst_analysis",
            agent_type=AgentType.USER_ANALYST,
            prompt_type=PromptType.USER,
            template="""请分析以下用户数据，根据给定条件识别高价值用户：

筛选条件：{criteria}

用户数据：{user_data}

请提供：
1. 用户价值评估
2. 情感倾向分析  
3. 未满足需求识别
4. 营销建议""",
            description="用户分析的具体任务提示词",
            variables=["criteria", "user_data"]
        ))
        
        # 内容策略Agent提示词
        self.register_prompt(PromptTemplate(
            name="content_strategy_system",
            agent_type=AgentType.CONTENT_STRATEGY,
            prompt_type=PromptType.SYSTEM,
            template="""你是{agent_name}，专门负责为UGC平台制定内容营销策略。

你的专长包括：
1. 用户群体细分和画像分析
2. 内容主题规划和创意方向
3. 营销策略制定和执行计划
4. 效果预测和优化建议

请提供具有创新性和可执行性的策略方案。""",
            description="内容策略Agent的系统提示词",
            variables=["agent_name"]
        ))
        
        self.register_prompt(PromptTemplate(
            name="content_strategy_creation",
            agent_type=AgentType.CONTENT_STRATEGY,
            prompt_type=PromptType.USER,
            template="""基于以下用户画像数据，制定针对性的内容策略：

目标用户画像：{user_profiles}

业务目标：{business_goals}

请制定包含以下内容的策略：
1. 用户群体细分
2. 内容主题建议
3. 创作方向指导
4. 投放策略建议
5. 效果评估方法""",
            description="内容策略制定的具体任务提示词",
            variables=["user_profiles", "business_goals"]
        ))
        
        # 内容生成Agent提示词
        self.register_prompt(PromptTemplate(
            name="content_generator_system",
            agent_type=AgentType.CONTENT_GENERATOR,
            prompt_type=PromptType.SYSTEM,
            template="""你是{agent_name}，专门负责为UGC平台生成高质量的营销内容。

你的能力包括：
1. 创作吸引人的标题和文案
2. 设计有趣的内容形式和结构
3. 针对特定用户群体优化内容
4. 确保内容的商业价值和传播效果

请创作原创、有吸引力且符合平台特色的内容。""",
            description="内容生成Agent的系统提示词",
            variables=["agent_name"]
        ))
        
        self.register_prompt(PromptTemplate(
            name="content_generator_creation",
            agent_type=AgentType.CONTENT_GENERATOR,
            prompt_type=PromptType.USER,
            template="""根据以下策略和要求，生成具体的内容方案：

内容策略：{strategy}

目标受众：{target_audience}

内容主题：{themes}

请生成：
1. 3-5个吸引人的内容标题
2. 详细的内容大纲
3. 关键话题和角度
4. 互动引导方案
5. 传播优化建议""",
            description="内容生成的具体任务提示词",
            variables=["strategy", "target_audience", "themes"]
        ))
        
        # 策略协调Agent提示词
        self.register_prompt(PromptTemplate(
            name="strategy_coordinator_system",
            agent_type=AgentType.STRATEGY_COORDINATOR,
            prompt_type=PromptType.SYSTEM,
            template="""你是{agent_name}，负责协调整合所有Agent的分析结果，制定统一的执行方案。

你的职责是：
1. 整合多个Agent的分析结果
2. 识别潜在的冲突和协同机会
3. 制定优先级和执行时间线
4. 提供资源配置建议
5. 设计效果监控机制

请提供全面、平衡且可执行的协调方案。""",
            description="策略协调Agent的系统提示词",
            variables=["agent_name"]
        ))
        
        self.register_prompt(PromptTemplate(
            name="strategy_coordinator_coordination",
            agent_type=AgentType.STRATEGY_COORDINATOR,
            prompt_type=PromptType.USER,
            template="""整合以下所有Agent的分析结果，制定统一的执行计划：

各Agent分析结果：{all_agent_results}

业务背景：{business_context}

请制定包含以下内容的协调方案：
1. 整体执行策略
2. 任务优先级排序
3. 资源分配建议
4. 时间线规划
5. 风险评估和应对
6. 成功指标和监控方案""",
            description="策略协调的具体任务提示词",
            variables=["all_agent_results", "business_context"]
        ))
        
        # 任务分析Agent提示词
        self.register_prompt(PromptTemplate(
            name="task_analyzer_system",
            agent_type=AgentType.TASK_ANALYZER,
            prompt_type=PromptType.SYSTEM,
            template="""你是一个专业的工作流分析师，分析用户的任务需求并提供初始洞察。

你的能力包括：
1. 任务需求分析和分解
2. 目标识别和优先级评估
3. 资源需求预估
4. 风险识别和预警
5. 执行路径建议

请提供准确、全面的分析和建议。""",
            description="任务分析的系统提示词",
            variables=[]
        ))
        
        self.register_prompt(PromptTemplate(
            name="task_analyzer_analysis",
            agent_type=AgentType.TASK_ANALYZER,
            prompt_type=PromptType.USER,
            template="""请分析以下Multi-Agent任务需求：{task_input}

请提供：
1. 任务目标分析
2. 关键成功因素识别
3. 资源需求评估
4. 潜在风险和挑战
5. 执行建议和优化方向""",
            description="任务分析的具体分析提示词",
            variables=["task_input"]
        ))
    
    def register_prompt(self, prompt_template: PromptTemplate):
        """注册提示词模板"""
        self.prompts[prompt_template.name] = prompt_template
    
    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """获取提示词模板"""
        return self.prompts.get(name)
    
    def get_prompts_by_agent(self, agent_type: AgentType) -> Dict[str, PromptTemplate]:
        """根据Agent类型获取所有相关提示词"""
        return {
            name: prompt for name, prompt in self.prompts.items()
            if prompt.agent_type == agent_type
        }
    
    def get_prompts_by_type(self, prompt_type: PromptType) -> Dict[str, PromptTemplate]:
        """根据提示词类型获取所有相关提示词"""
        return {
            name: prompt for name, prompt in self.prompts.items()
            if prompt.prompt_type == prompt_type
        }
    
    def format_prompt(self, name: str, **kwargs) -> str:
        """格式化指定的提示词"""
        prompt = self.get_prompt(name)
        if not prompt:
            raise ValueError(f"未找到名为 '{name}' 的提示词模板")
        
        return prompt.format(**kwargs)
    
    def list_prompts(self) -> Dict[str, str]:
        """列出所有提示词及其描述"""
        return {
            name: prompt.description 
            for name, prompt in self.prompts.items()
        }


# 全局提示词管理器实例
prompt_manager = PromptManager()