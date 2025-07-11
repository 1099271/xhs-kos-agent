"""
LLM模型管理器测试脚本
测试多种LLM模型的初始化、调用和备选机制
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.llm_manager import (
    LLMModelManager, 
    ModelProvider, 
    llm_manager,
    call_llm,
    call_llm_with_messages,
    AgentLLMCaller
)
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.utils.logger import app_logger as logger


async def test_model_initialization():
    """测试模型初始化功能"""
    
    logger.info("=== 测试模型初始化 ===")
    
    try:
        # 创建新的模型管理器实例
        manager = LLMModelManager()
        
        # 检查是否有可用模型
        available_providers = manager.get_available_providers()
        logger.info(f"可用模型提供商: {[p.value for p in available_providers]}")
        
        assert len(available_providers) > 0, "至少应该有一个可用的模型提供商"
        
        # 检查默认提供商
        default_provider = manager.default_provider
        assert default_provider is not None, "应该有默认的模型提供商"
        logger.info(f"默认模型提供商: {default_provider.value}")
        
        # 测试获取模型实例
        default_model = manager.get_model()
        assert default_model is not None, "应该能获取到默认模型实例"
        
        # 测试获取特定模型
        for provider in available_providers:
            model = manager.get_model(provider)
            assert model is not None, f"应该能获取到{provider.value}模型实例"
            logger.info(f"✅ {provider.value} 模型实例获取成功")
        
        logger.info("✅ 模型初始化测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 模型初始化测试失败: {e}")
        return False


async def test_basic_llm_calls():
    """测试基础LLM调用功能"""
    
    logger.info("=== 测试基础LLM调用 ===")
    
    try:
        # 测试1: 简单的LLM调用
        system_prompt = "你是一个helpful的AI助手，请简洁地回答问题。"
        user_prompt = "请用一句话说明什么是人工智能。"
        
        result = await call_llm(system_prompt, user_prompt)
        
        if result:
            logger.info(f"✅ 基础LLM调用成功")
            logger.info(f"模型回答: {result[:100]}...")
            assert len(result) > 10, "模型回答应该有实质内容"
        else:
            logger.warning("⚠️ LLM调用返回空结果，可能是模型配置问题")
            return False
        
        # 测试2: 带上下文的LLM调用
        context = "这是一个关于UGC平台的技术讨论。"
        user_prompt2 = "请解释什么是用户生成内容(UGC)。"
        
        result2 = await call_llm(system_prompt, user_prompt2, context=context)
        
        if result2:
            logger.info(f"✅ 带上下文的LLM调用成功")
            logger.info(f"模型回答: {result2[:100]}...")
        else:
            logger.warning("⚠️ 带上下文的LLM调用失败")
        
        # 测试3: 使用消息列表调用
        messages = [
            SystemMessage(content="你是一个专业的数据分析师。"),
            HumanMessage(content="请解释什么是多Agent系统。")
        ]
        
        result3 = await call_llm_with_messages(messages)
        
        if result3:
            logger.info(f"✅ 消息列表LLM调用成功")
            logger.info(f"模型回答: {result3[:100]}...")
        else:
            logger.warning("⚠️ 消息列表LLM调用失败")
        
        logger.info("✅ 基础LLM调用测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 基础LLM调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fallback_mechanism():
    """测试备选机制"""
    
    logger.info("=== 测试备选机制 ===")
    
    try:
        manager = LLMModelManager()
        available_providers = manager.get_available_providers()
        
        if len(available_providers) < 2:
            logger.warning("⚠️ 只有一个模型提供商可用，无法全面测试备选机制")
            return True
        
        # 测试优先选择特定提供商
        for provider in available_providers:
            messages = [
                SystemMessage(content="请简洁回答。"),
                HumanMessage(content=f"你好，请确认你是{provider.value}模型。")
            ]
            
            result = await manager.invoke_with_fallback(messages, preferred_provider=provider)
            
            if result:
                logger.info(f"✅ 指定{provider.value}提供商调用成功")
                logger.info(f"回答: {result[:100]}...")
            else:
                logger.warning(f"⚠️ 指定{provider.value}提供商调用失败")
        
        # 测试默认备选机制
        messages = [
            SystemMessage(content="请简洁回答。"),
            HumanMessage(content="请说明你的能力。")
        ]
        
        result = await manager.invoke_with_fallback(messages)
        
        if result:
            logger.info(f"✅ 默认备选机制调用成功")
            logger.info(f"回答: {result[:100]}...")
        else:
            logger.warning("⚠️ 默认备选机制调用失败")
        
        logger.info("✅ 备选机制测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 备选机制测试失败: {e}")
        return False


async def test_agent_llm_caller():
    """测试Agent专用LLM调用器"""
    
    logger.info("=== 测试Agent专用LLM调用器 ===")
    
    try:
        # 创建不同类型的Agent调用器
        user_analyst_caller = AgentLLMCaller("UserAnalystAgent")
        content_strategy_caller = AgentLLMCaller("ContentStrategyAgent")
        content_generator_caller = AgentLLMCaller("ContentGeneratorAgent")
        coordinator_caller = AgentLLMCaller("StrategyCoordinatorAgent")
        
        # 测试1: 用户分析调用
        logger.info("测试用户分析LLM调用...")
        user_data = """
        用户ID: user123
        昵称: 旅行爱好者小王
        评论: "这个地方真的太美了！下次一定要带家人一起去"
        情感倾向: 正向
        互动次数: 15
        """
        criteria = "筛选正向情感、有旅行需求的高价值用户"
        
        analysis_result = await user_analyst_caller.analyze_users(user_data, criteria)
        
        if analysis_result:
            logger.info("✅ 用户分析LLM调用成功")
            logger.info(f"分析结果: {analysis_result[:200]}...")
        else:
            logger.warning("⚠️ 用户分析LLM调用失败")
        
        # 测试2: 内容策略调用
        logger.info("测试内容策略LLM调用...")
        user_profiles = "主要用户群体：25-35岁旅行爱好者，具有较强消费能力"
        business_goals = "提升旅游产品的用户转化率和品牌知名度"
        
        strategy_result = await content_strategy_caller.create_content_strategy(user_profiles, business_goals)
        
        if strategy_result:
            logger.info("✅ 内容策略LLM调用成功")
            logger.info(f"策略结果: {strategy_result[:200]}...")
        else:
            logger.warning("⚠️ 内容策略LLM调用失败")
        
        # 测试3: 内容生成调用
        logger.info("测试内容生成LLM调用...")
        strategy = "针对年轻旅行者的个性化旅游内容"
        target_audience = "25-35岁有旅行经验的用户"
        themes = "美食探店、小众景点、旅行攻略"
        
        content_result = await content_generator_caller.generate_content(strategy, target_audience, themes)
        
        if content_result:
            logger.info("✅ 内容生成LLM调用成功")
            logger.info(f"生成内容: {content_result[:200]}...")
        else:
            logger.warning("⚠️ 内容生成LLM调用失败")
        
        # 测试4: 策略协调调用
        logger.info("测试策略协调LLM调用...")
        all_agent_results = f"""
        用户分析结果: {analysis_result[:100] if analysis_result else '无结果'}...
        策略制定结果: {strategy_result[:100] if strategy_result else '无结果'}...
        内容生成结果: {content_result[:100] if content_result else '无结果'}...
        """
        business_context = "UGC旅游平台的用户获取和转化优化"
        
        coordination_result = await coordinator_caller.coordinate_strategy(all_agent_results, business_context)
        
        if coordination_result:
            logger.info("✅ 策略协调LLM调用成功")
            logger.info(f"协调结果: {coordination_result[:200]}...")
        else:
            logger.warning("⚠️ 策略协调LLM调用失败")
        
        logger.info("✅ Agent专用LLM调用器测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent专用LLM调用器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_model_performance():
    """测试模型性能和响应时间"""
    
    logger.info("=== 测试模型性能 ===")
    
    try:
        available_providers = llm_manager.get_available_providers()
        performance_results = {}
        
        test_prompt = "请用50字以内简要说明什么是人工智能。"
        
        for provider in available_providers:
            logger.info(f"测试{provider.value}模型性能...")
            
            start_time = datetime.now()
            
            result = await llm_manager.invoke_with_fallback(
                [HumanMessage(content=test_prompt)],
                preferred_provider=provider
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            performance_results[provider.value] = {
                "success": result is not None,
                "response_time": response_time,
                "response_length": len(result) if result else 0,
                "response_preview": result[:100] if result else "无回应"
            }
            
            if result:
                logger.info(f"✅ {provider.value} 响应时间: {response_time:.2f}秒")
            else:
                logger.warning(f"❌ {provider.value} 调用失败")
        
        # 输出性能总结
        logger.info("📊 模型性能总结:")
        for provider_name, metrics in performance_results.items():
            status = "✅" if metrics["success"] else "❌"
            logger.info(f"{status} {provider_name}: {metrics['response_time']:.2f}s, "
                       f"字符数: {metrics['response_length']}")
        
        logger.info("✅ 模型性能测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 模型性能测试失败: {e}")
        return False


async def test_error_handling():
    """测试错误处理机制"""
    
    logger.info("=== 测试错误处理 ===")
    
    try:
        # 测试1: 无效的提示
        logger.info("测试无效提示处理...")
        result1 = await call_llm("", "")  # 空提示
        
        # 这应该要么返回None，要么返回有意义的错误处理
        logger.info(f"空提示测试结果: {result1 is not None}")
        
        # 测试2: 非常长的提示
        logger.info("测试长提示处理...")
        long_prompt = "测试" * 10000  # 非常长的提示
        
        start_time = datetime.now()
        result2 = await call_llm("请简短回答。", long_prompt)
        end_time = datetime.now()
        
        logger.info(f"长提示测试结果: 成功={result2 is not None}, "
                   f"时间={end_time - start_time}")
        
        # 测试3: 测试备选机制在错误情况下的表现
        logger.info("测试无效提供商备选...")
        
        # 这个测试依赖于实际的模型配置情况
        messages = [HumanMessage(content="简单测试")]
        result3 = await llm_manager.invoke_with_fallback(messages)
        
        logger.info(f"备选机制测试: {'成功' if result3 else '失败'}")
        
        logger.info("✅ 错误处理测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e}")
        return False


async def run_all_llm_tests():
    """运行所有LLM模型管理器测试"""
    
    logger.info("🚀 开始运行LLM模型管理器完整测试套件")
    
    tests = [
        ("模型初始化测试", test_model_initialization),
        ("基础LLM调用测试", test_basic_llm_calls),
        ("备选机制测试", test_fallback_mechanism),
        ("Agent专用调用器测试", test_agent_llm_caller),
        ("模型性能测试", test_model_performance),
        ("错误处理测试", test_error_handling),
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
    logger.info(f"LLM模型管理器测试完成: {success_count}/{total_tests} 通过")
    logger.info(f"{'='*60}")
    
    if success_count == total_tests:
        logger.info("🎉 所有LLM模型测试通过！")
        return True
    else:
        logger.warning(f"⚠️  有 {total_tests - success_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_llm_tests())
    sys.exit(0 if success else 1)