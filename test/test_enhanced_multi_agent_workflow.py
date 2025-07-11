"""
AI增强版Multi-Agent工作流测试脚本
测试集成LLM模型的智能化多Agent协作系统
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.enhanced_multi_agent_workflow import (
    EnhancedMultiAgentWorkflow, 
    test_enhanced_multi_agent_workflow
)
from app.agents.llm_manager import ModelProvider
from app.utils.logger import app_logger as logger


async def test_enhanced_workflow_basic():
    """测试AI增强版工作流基础功能"""
    
    logger.info("=== 测试AI增强版工作流基础功能 ===")
    
    try:
        # 创建增强版工作流实例
        workflow = EnhancedMultiAgentWorkflow()
        logger.info("✅ AI增强版工作流实例创建成功")
        
        # 检查图是否正确构建
        assert workflow.graph is not None, "工作流图未正确构建"
        logger.info("✅ 工作流图构建成功")
        
        # 检查LLM组件是否初始化
        assert workflow.llm_manager is not None, "LLM管理器未初始化"
        assert workflow.user_analyst_llm is not None, "用户分析LLM调用器未初始化"
        logger.info("✅ LLM组件初始化成功")
        
        # 检查可用模型
        available_providers = workflow.llm_manager.get_available_providers()
        logger.info(f"可用LLM模型: {[p.value for p in available_providers]}")
        
        assert len(available_providers) > 0, "至少应该有一个可用的LLM模型"
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 基础功能测试失败: {e}")
        return False


async def test_enhanced_workflow_execution():
    """测试AI增强版工作流完整执行"""
    
    logger.info("=== 测试AI增强版工作流完整执行 ===")
    
    try:
        # 使用OpenRouter作为首选模型（通常比较稳定）
        workflow = EnhancedMultiAgentWorkflow(
            preferred_model_provider=ModelProvider.OPENROUTER
        )
        
        start_time = datetime.now()
        
        # 执行增强版工作流
        result = await workflow.execute_enhanced_workflow({
            "task": "AI增强版UGC平台高价值用户分析与智能内容策略",
            "parameters": {
                "target_user_count": 20,
                "content_themes": ["AI个性化推荐", "智能数据洞察", "用户体验优化"],
                "ai_enhancement": True,
                "preferred_model": "openrouter"
            }
        })
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 验证结果
        assert result.get("success"), "工作流执行应该成功"
        assert result.get("enhanced_features"), "应该启用增强功能"
        
        logger.info(f"✅ 工作流执行成功，耗时: {execution_time:.2f}秒")
        
        # 检查AI增强功能
        llm_insights = result.get("llm_insights", {})
        logger.info(f"生成的AI洞察数: {len(llm_insights)}")
        
        agent_results = result.get("agent_results", [])
        enhanced_agents = [r for r in agent_results if hasattr(r, 'llm_analysis') and r.llm_analysis]
        logger.info(f"包含LLM分析的Agent数: {len(enhanced_agents)}")
        
        # 输出详细结果
        print(f"\n{'='*60}")
        print(f"AI增强版工作流执行结果:")
        print(f"{'='*60}")
        print(f"执行成功: {result.get('success')}")
        print(f"执行时间: {execution_time:.2f}秒")
        print(f"AI增强: {result.get('enhanced_features')}")
        print(f"执行摘要: {result.get('execution_summary', '无摘要')}")
        print(f"AI增强摘要: {result.get('ai_enhancement_summary', '无AI摘要')}")
        
        # 显示Agent执行结果
        if agent_results:
            print(f"\n各Agent执行详情:")
            for agent_result in agent_results:
                status = "✅" if agent_result.success else "❌"
                print(f"{status} {agent_result.agent_name}:")
                print(f"   执行时间: {agent_result.execution_time:.2f}秒")
                print(f"   结果: {agent_result.message}")
                if hasattr(agent_result, 'llm_analysis') and agent_result.llm_analysis:
                    print(f"   🧠 AI洞察: {agent_result.llm_analysis[:150]}...")
        
        # 显示LLM洞察
        if llm_insights:
            print(f"\n🔍 LLM洞察汇总:")
            for phase, insight in llm_insights.items():
                print(f"- {phase}: {insight[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 完整执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_different_model_providers():
    """测试不同模型提供商的兼容性"""
    
    logger.info("=== 测试不同模型提供商兼容性 ===")
    
    # 可用的模型提供商
    providers_to_test = [
        ModelProvider.OPENROUTER,
        ModelProvider.QWEN,
        ModelProvider.DEEPSEEK,
        # ModelProvider.ANTHROPIC,  # 可能连接不稳定，先跳过
    ]
    
    results = {}
    
    for provider in providers_to_test:
        try:
            logger.info(f"测试模型提供商: {provider.value}")
            
            workflow = EnhancedMultiAgentWorkflow(preferred_model_provider=provider)
            
            # 简化的测试任务
            start_time = datetime.now()
            result = await workflow.execute_enhanced_workflow({
                "task": f"使用{provider.value}模型的简化测试",
                "parameters": {"test_mode": True}
            })
            execution_time = (datetime.now() - start_time).total_seconds()
            
            results[provider.value] = {
                "success": result.get("success", False),
                "execution_time": execution_time,
                "ai_insights_count": len(result.get("llm_insights", {})),
                "error": result.get("error") if not result.get("success") else None
            }
            
            logger.info(f"✅ {provider.value} 测试完成: {execution_time:.2f}秒")
            
        except Exception as e:
            logger.warning(f"⚠️ {provider.value} 测试失败: {e}")
            results[provider.value] = {
                "success": False,
                "execution_time": 0,
                "ai_insights_count": 0,
                "error": str(e)
            }
    
    # 输出测试结果
    print(f"\n📊 模型提供商兼容性测试结果:")
    for provider, metrics in results.items():
        status = "✅" if metrics["success"] else "❌"
        print(f"{status} {provider}: "
              f"耗时{metrics['execution_time']:.2f}s, "
              f"AI洞察{metrics['ai_insights_count']}个")
        if metrics.get("error"):
            print(f"   错误: {metrics['error']}")
    
    # 统计成功率
    successful_providers = [p for p, m in results.items() if m["success"]]
    success_rate = len(successful_providers) / len(results) if results else 0
    
    logger.info(f"模型提供商兼容性: {len(successful_providers)}/{len(results)} "
               f"({success_rate*100:.1f}%) 成功")
    
    return success_rate > 0.5  # 至少50%成功率


async def test_llm_enhancement_quality():
    """测试LLM增强功能的质量"""
    
    logger.info("=== 测试LLM增强功能质量 ===")
    
    try:
        workflow = EnhancedMultiAgentWorkflow()
        
        # 执行测试
        result = await workflow.execute_enhanced_workflow({
            "task": "LLM增强功能质量测试",
            "parameters": {
                "test_quality": True,
                "expected_insights": ["用户分析", "策略制定", "内容生成", "协调优化"]
            }
        })
        
        # 质量检查
        quality_metrics = {
            "workflow_success": result.get("success", False),
            "ai_insights_generated": len(result.get("llm_insights", {})),
            "agents_with_llm_analysis": 0,
            "content_pieces_generated": 0,
            "strategy_segments_created": 0
        }
        
        # 检查Agent LLM分析
        agent_results = result.get("agent_results", [])
        for agent_result in agent_results:
            if hasattr(agent_result, 'llm_analysis') and agent_result.llm_analysis:
                quality_metrics["agents_with_llm_analysis"] += 1
        
        # 检查内容生成质量
        generated_content = result.get("generated_content", {})
        if generated_content:
            quality_metrics["content_pieces_generated"] = len(
                generated_content.get("content_pieces", [])
            )
        
        # 检查策略质量
        content_strategy = result.get("content_strategy", {})
        if content_strategy:
            quality_metrics["strategy_segments_created"] = len(
                content_strategy.get("target_segments", [])
            )
        
        # 输出质量报告
        print(f"\n📊 LLM增强功能质量报告:")
        print(f"工作流成功: {quality_metrics['workflow_success']}")
        print(f"AI洞察生成数: {quality_metrics['ai_insights_generated']}")
        print(f"包含LLM分析的Agent数: {quality_metrics['agents_with_llm_analysis']}")
        print(f"生成内容片段数: {quality_metrics['content_pieces_generated']}")
        print(f"策略细分数: {quality_metrics['strategy_segments_created']}")
        
        # 计算质量分数
        max_possible_score = 10  # 假设的最高分
        actual_score = (
            (3 if quality_metrics["workflow_success"] else 0) +
            min(quality_metrics["ai_insights_generated"], 3) +
            min(quality_metrics["agents_with_llm_analysis"], 2) +
            min(quality_metrics["content_pieces_generated"] / 2, 2)
        )
        
        quality_score = actual_score / max_possible_score
        logger.info(f"LLM增强功能质量分数: {quality_score*100:.1f}%")
        
        return quality_score > 0.6  # 至少60%质量分数
        
    except Exception as e:
        logger.error(f"❌ LLM增强功能质量测试失败: {e}")
        return False


async def test_error_handling_and_fallback():
    """测试错误处理和备选机制"""
    
    logger.info("=== 测试错误处理和备选机制 ===")
    
    try:
        # 测试1: 使用可能不可用的模型
        workflow_with_fallback = EnhancedMultiAgentWorkflow(
            preferred_model_provider=ModelProvider.ANTHROPIC  # 可能连接失败
        )
        
        start_time = datetime.now()
        result = await workflow_with_fallback.execute_enhanced_workflow({
            "task": "备选机制测试",
            "parameters": {"test_fallback": True}
        })
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 即使首选模型失败，工作流应该仍能完成
        logger.info(f"备选机制测试结果: {'成功' if result.get('success') else '失败'}")
        logger.info(f"执行时间: {execution_time:.2f}秒")
        
        # 检查是否使用了备选模型
        llm_insights = result.get("llm_insights", {})
        if llm_insights:
            logger.info("✅ 备选机制工作正常，生成了LLM洞察")
        else:
            logger.warning("⚠️ 备选机制可能需要优化")
        
        return result.get("success", False)
        
    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e}")
        return False


async def run_all_enhanced_multi_agent_tests():
    """运行所有AI增强版Multi-Agent测试"""
    
    logger.info("🚀 开始运行AI增强版Multi-Agent系统完整测试套件")
    
    tests = [
        ("基础功能测试", test_enhanced_workflow_basic),
        ("完整执行测试", test_enhanced_workflow_execution),
        ("模型提供商兼容性测试", test_different_model_providers),
        ("LLM增强功能质量测试", test_llm_enhancement_quality),
        ("错误处理和备选机制测试", test_error_handling_and_fallback),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"正在运行: {test_name}")
            logger.info(f"{'='*60}")
            
            result = await test_func()
            if result:
                logger.info(f"✅ {test_name} - 通过")
                success_count += 1
            else:
                logger.error(f"❌ {test_name} - 失败")
                
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"AI增强版Multi-Agent测试完成: {success_count}/{total_tests} 通过")
    logger.info(f"{'='*60}")
    
    if success_count == total_tests:
        logger.info("🎉 所有AI增强版Multi-Agent测试通过！")
        return True
    else:
        logger.warning(f"⚠️  有 {total_tests - success_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_enhanced_multi_agent_tests())
    sys.exit(0 if success else 1)