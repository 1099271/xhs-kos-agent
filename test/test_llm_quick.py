"""
快速LLM测试 - 仅测试核心功能
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.llm_manager import LLMModelManager, call_llm, AgentLLMCaller, ModelProvider
from app.utils.logger import app_logger as logger


async def quick_llm_test():
    """快速LLM功能测试"""
    
    logger.info("🚀 快速LLM功能测试")
    
    try:
        # 测试模型管理器初始化
        manager = LLMModelManager()
        available_providers = manager.get_available_providers()
        logger.info(f"✅ 可用模型: {[p.value for p in available_providers]}")
        
        if not available_providers:
            logger.error("❌ 没有可用模型")
            return False
        
        # 测试基础调用
        result = await call_llm(
            "你是一个helpful的AI助手。",
            "请简短说明什么是AI。"
        )
        
        if result:
            logger.info(f"✅ LLM调用成功: {result[:100]}...")
        else:
            logger.error("❌ LLM调用失败")
            return False
        
        # 测试Agent调用器
        agent_caller = AgentLLMCaller("TestAgent")
        analysis_result = await agent_caller.analyze_users(
            "用户: 喜欢旅游的小王，评论积极",
            "寻找高价值用户"
        )
        
        if analysis_result:
            logger.info(f"✅ Agent LLM调用成功: {analysis_result[:100]}...")
        else:
            logger.warning("⚠️ Agent LLM调用返回空")
        
        logger.info("🎉 快速LLM测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_llm_test())
    print(f"测试结果: {'成功' if success else '失败'}")