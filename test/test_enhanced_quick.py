"""
快速AI增强版Multi-Agent测试
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow
from app.agents.llm_manager import ModelProvider
from app.utils.logger import app_logger as logger


async def quick_enhanced_test():
    """快速AI增强版功能测试"""
    
    logger.info("🚀 快速AI增强版Multi-Agent测试")
    
    try:
        # 创建增强版工作流
        workflow = EnhancedMultiAgentWorkflow(
            preferred_model_provider=ModelProvider.OPENROUTER
        )
        logger.info("✅ 增强版工作流创建成功")
        
        # 检查LLM组件
        available_providers = workflow.llm_manager.get_available_providers()
        logger.info(f"✅ 可用LLM模型: {[p.value for p in available_providers]}")
        
        if not available_providers:
            logger.error("❌ 没有可用LLM模型")
            return False
        
        # 执行简化版工作流测试
        result = await workflow.execute_enhanced_workflow({
            "task": "快速AI增强版测试",
            "parameters": {"quick_test": True}
        })
        
        if result.get("success"):
            logger.info("✅ 工作流执行成功")
            logger.info(f"AI洞察数: {len(result.get('llm_insights', {}))}")
            logger.info(f"执行摘要: {result.get('execution_summary', '')[:100]}...")
        else:
            logger.error("❌ 工作流执行失败")
            return False
        
        logger.info("🎉 快速AI增强版测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_enhanced_test())
    print(f"测试结果: {'成功' if success else '失败'}")