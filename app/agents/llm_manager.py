"""
LLM模型管理器
统一管理Anthropic、OpenRouter等多种LLM模型的访问
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models import BaseChatModel

from app.config.settings import settings
from app.utils.logger import app_logger as logger


class ModelProvider(Enum):
    """模型提供商枚举"""

    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"


class LLMModelManager:
    """LLM模型管理器 - 统一管理多种模型访问"""

    def __init__(self):
        self.models: Dict[ModelProvider, Optional[BaseChatModel]] = {}
        self.default_provider = None
        self._initialize_models()

    def _initialize_models(self):
        """初始化所有可用的模型"""

        # 1. 尝试初始化Anthropic (通过anyrouter)
        if settings.ANTHROPIC_KEY and settings.ANTHROPIC_URL:
            try:
                self.models[ModelProvider.ANTHROPIC] = ChatAnthropic(
                    api_key=settings.ANTHROPIC_KEY,
                    base_url=settings.ANTHROPIC_URL,
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.7,
                    max_tokens=4000,
                )
                if not self.default_provider:
                    self.default_provider = ModelProvider.ANTHROPIC
                logger.info("✅ Anthropic模型初始化成功 (通过anyrouter)")
            except Exception as e:
                logger.warning(f"❌ Anthropic模型初始化失败: {e}")

        # 2. 尝试初始化OpenRouter
        if settings.OPENROUTER_KEY:
            try:
                self.models[ModelProvider.OPENROUTER] = ChatOpenAI(
                    api_key=settings.OPENROUTER_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    model="anthropic/claude-3.5-sonnet",
                    temperature=0.7,
                    max_tokens=4000,
                )
                if not self.default_provider:
                    self.default_provider = ModelProvider.OPENROUTER
                logger.info("✅ OpenRouter模型初始化成功")
            except Exception as e:
                logger.warning(f"❌ OpenRouter模型初始化失败: {e}")

        # 3. 尝试初始化OpenAI
        if settings.OPENAI_KEY:
            try:
                self.models[ModelProvider.OPENAI] = ChatOpenAI(
                    api_key=settings.OPENAI_KEY,
                    base_url="https://api.openai.com/v1",
                    model="gpt-4o-mini",
                    temperature=0.7,
                    max_tokens=4000,
                )
                if not self.default_provider:
                    self.default_provider = ModelProvider.OPENAI
                logger.info("✅ OpenAI模型初始化成功")
            except Exception as e:
                logger.warning(f"❌ OpenAI模型初始化失败: {e}")

        # 4. 尝试初始化Qwen
        if settings.QWEN_MODEL_API_KEY:
            try:
                self.models[ModelProvider.QWEN] = ChatOpenAI(
                    api_key=settings.QWEN_MODEL_API_KEY,
                    base_url=settings.QWEN_MODEL_BASE_URL,
                    model=settings.QWEN_MODEL_NAME,
                    temperature=0.7,
                    max_tokens=4000,
                )
                if not self.default_provider:
                    self.default_provider = ModelProvider.QWEN
                logger.info("✅ Qwen模型初始化成功")
            except Exception as e:
                logger.warning(f"❌ Qwen模型初始化失败: {e}")

        # 5. 尝试初始化DeepSeek
        if settings.DEEPSEEK_MODEL_API_KEY:
            try:
                self.models[ModelProvider.DEEPSEEK] = ChatOpenAI(
                    api_key=settings.DEEPSEEK_MODEL_API_KEY,
                    base_url=settings.DEEPSEEK_MODEL_BASE_URL,
                    model=settings.DEEPSEEK_MODEL_NAME,
                    temperature=0.7,
                    max_tokens=4000,
                )
                if not self.default_provider:
                    self.default_provider = ModelProvider.DEEPSEEK
                logger.info("✅ DeepSeek模型初始化成功")
            except Exception as e:
                logger.warning(f"❌ DeepSeek模型初始化失败: {e}")

        if self.default_provider:
            logger.info(f"🎯 默认模型提供商: {self.default_provider.value}")
        else:
            logger.error("❌ 没有可用的模型提供商！请检查配置")

    def get_model(
        self, provider: Optional[ModelProvider] = None
    ) -> Optional[BaseChatModel]:
        """获取指定的模型实例"""
        if provider is None:
            provider = self.default_provider

        if provider is None:
            logger.error("没有可用的模型提供商")
            return None

        return self.models.get(provider)

    def get_available_providers(self) -> List[ModelProvider]:
        """获取所有可用的模型提供商"""
        return [
            provider for provider, model in self.models.items() if model is not None
        ]

    async def invoke_with_fallback(
        self,
        messages: List[BaseMessage],
        preferred_provider: Optional[ModelProvider] = None,
    ) -> Optional[str]:
        """
        使用备选机制调用模型
        如果首选提供商失败，会自动尝试其他可用提供商
        """

        providers_to_try = []

        # 确定尝试顺序
        if preferred_provider and preferred_provider in self.models:
            providers_to_try.append(preferred_provider)

        # 添加其他可用提供商作为备选
        for provider in [
            ModelProvider.ANTHROPIC,
            ModelProvider.OPENROUTER,
            ModelProvider.QWEN,
            ModelProvider.DEEPSEEK,
            ModelProvider.OPENAI,
        ]:
            if provider not in providers_to_try and provider in self.models:
                providers_to_try.append(provider)

        last_error = None

        for provider in providers_to_try:
            model = self.models.get(provider)
            if model is None:
                continue

            try:
                logger.info(f"🤖 尝试使用 {provider.value} 模型")
                result = await model.ainvoke(messages)
                logger.info(f"✅ {provider.value} 模型调用成功")
                return result.content if hasattr(result, "content") else str(result)

            except Exception as e:
                last_error = e
                logger.warning(f"❌ {provider.value} 模型调用失败: {e}")
                continue

        logger.error(f"💥 所有模型提供商都失败了，最后一个错误: {last_error}")
        return None

    def create_prompt_messages(
        self, system_prompt: str, user_prompt: str, context: Optional[str] = None
    ) -> List[BaseMessage]:
        """创建标准的提示消息格式"""

        messages = [SystemMessage(content=system_prompt)]

        if context:
            messages.append(HumanMessage(content=f"背景信息：\n{context}"))

        messages.append(HumanMessage(content=user_prompt))

        return messages


# 全局模型管理器实例
llm_manager = LLMModelManager()


# 便捷函数
async def call_llm(
    system_prompt: str,
    user_prompt: str,
    context: Optional[str] = None,
    preferred_provider: Optional[ModelProvider] = None,
) -> Optional[str]:
    """便捷的LLM调用函数"""

    messages = llm_manager.create_prompt_messages(system_prompt, user_prompt, context)
    return await llm_manager.invoke_with_fallback(messages, preferred_provider)


async def call_llm_with_messages(
    messages: List[BaseMessage], preferred_provider: Optional[ModelProvider] = None
) -> Optional[str]:
    """使用消息列表调用LLM"""

    return await llm_manager.invoke_with_fallback(messages, preferred_provider)


from app.prompts import prompt_manager
from app.utils.logger import app_logger as logger


class AgentLLMCaller:
    """为Agent定制的LLM调用器"""

    def __init__(
        self, agent_name: str, preferred_provider: Optional[ModelProvider] = None
    ):
        self.agent_name = agent_name
        self.preferred_provider = preferred_provider

    async def analyze_users(self, user_data: str, criteria: str) -> Optional[str]:
        """用户分析LLM调用"""

        system_prompt = prompt_manager.format_prompt(
            "user_analyst_system", agent_name=self.agent_name
        )

        user_prompt = prompt_manager.format_prompt(
            "user_analyst_analysis", criteria=criteria, user_data=user_data
        )

        return await call_llm(
            system_prompt, user_prompt, preferred_provider=self.preferred_provider
        )

    async def create_content_strategy(
        self, user_profiles: str, business_goals: str
    ) -> Optional[str]:
        """内容策略制定LLM调用"""

        system_prompt = prompt_manager.format_prompt(
            "content_strategy_system", agent_name=self.agent_name
        )

        user_prompt = prompt_manager.format_prompt(
            "content_strategy_creation",
            user_profiles=user_profiles,
            business_goals=business_goals,
        )

        return await call_llm(
            system_prompt, user_prompt, preferred_provider=self.preferred_provider
        )

    async def generate_content(
        self, strategy: str, target_audience: str, themes: str
    ) -> Optional[str]:
        """内容生成LLM调用"""

        system_prompt = prompt_manager.format_prompt(
            "content_generator_system", agent_name=self.agent_name
        )

        user_prompt = prompt_manager.format_prompt(
            "content_generator_creation",
            strategy=strategy,
            target_audience=target_audience,
            themes=themes,
        )

        return await call_llm(
            system_prompt, user_prompt, preferred_provider=self.preferred_provider
        )

    async def coordinate_strategy(
        self, all_agent_results: str, business_context: str
    ) -> Optional[str]:
        """策略协调LLM调用"""

        system_prompt = prompt_manager.format_prompt(
            "strategy_coordinator_system", agent_name=self.agent_name
        )

        user_prompt = prompt_manager.format_prompt(
            "strategy_coordinator_coordination",
            all_agent_results=all_agent_results,
            business_context=business_context,
        )

        return await call_llm(
            system_prompt, user_prompt, preferred_provider=self.preferred_provider
        )
