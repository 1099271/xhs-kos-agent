"""
Multi-Agent工作流测试脚本
测试LangGraph框架下的多Agent协作系统
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.multi_agent_workflow import MultiAgentWorkflow, test_multi_agent_workflow
from app.utils.logger import app_logger as logger


async def test_complete_workflow():
    """测试完整的Multi-Agent工作流"""
    
    logger.info("🚀 开始测试Multi-Agent工作流系统")
    
    try:
        # 创建工作流实例
        workflow = MultiAgentWorkflow()
        logger.info("✅ Multi-Agent工作流实例创建成功")
        
        # 测试1: 基础工作流执行
        logger.info("\n=== 测试1: 基础工作流执行 ===")
        start_time = datetime.now()
        
        result = await workflow.execute_workflow({
            "task": "UGC平台高价值用户分析与内容策略制定",
            "parameters": {
                "target_user_count": 30,
                "content_themes": ["美食探店", "旅游攻略", "生活方式"],
                "emotional_focus": "正向",
                "exclude_visited": True
            }
        })
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"工作流执行结果:")
        print(f"{'='*60}")
        print(f"执行成功: {result.get('success', False)}")
        print(f"执行时间: {execution_time:.2f}秒")
        print(f"执行摘要: {result.get('execution_summary', '无摘要')}")
        
        # 显示各Agent执行结果
        if result.get('agent_results'):
            print(f"\n各Agent执行详情:")
            for agent_result in result['agent_results']:
                status = "✅" if agent_result.success else "❌"
                print(f"{status} {agent_result.agent_name}: {agent_result.message}")
        
        # 显示用户分析结果
        if result.get('user_analysis'):
            user_analysis = result['user_analysis']
            print(f"\n用户分析结果:")
            print(f"- 识别用户数: {user_analysis.total_analyzed}")
            print(f"- 分析时间: {user_analysis.analysis_time}")
            print(f"- 筛选条件: {user_analysis.criteria_used}")
            
            if user_analysis.high_value_users:
                print(f"- 前3名高价值用户:")
                for i, user in enumerate(user_analysis.high_value_users[:3], 1):
                    print(f"  {i}. 用户ID: {user.user_id}, 价值评分: {user.value_score}, 昵称: {user.nickname}")
        
        # 显示内容策略
        if result.get('content_strategy'):
            strategy = result['content_strategy']
            print(f"\n内容策略:")
            print(f"- 策略摘要: {strategy.get('strategy_summary', '无')}")
            print(f"- 目标用户群体数: {len(strategy.get('target_segments', []))}")
            
            for segment in strategy.get('target_segments', []):
                print(f"  · {segment.get('segment_name', '未命名群体')}: {segment.get('size', 0)}人")
                themes = segment.get('content_themes', [])
                if themes:
                    print(f"    推荐内容主题: {', '.join(themes[:3])}")
        
        # 显示生成内容
        if result.get('generated_content'):
            content = result['generated_content']
            print(f"\n生成内容:")
            print(f"- 生成摘要: {content.get('generation_summary', '无')}")
            print(f"- 内容片段数: {len(content.get('content_pieces', []))}")
            
            for i, piece in enumerate(content.get('content_pieces', [])[:3], 1):
                print(f"  {i}. {piece.get('title', '无标题')} (主题: {piece.get('theme', '未知')})")
        
        # 显示协调计划
        if result.get('coordination_plan'):
            plan = result['coordination_plan']
            print(f"\n协调执行计划:")
            print(f"- 计划摘要: {plan.get('plan_summary', '无')}")
            print(f"- 执行阶段数: {len(plan.get('execution_phases', []))}")
            
            for i, phase in enumerate(plan.get('execution_phases', []), 1):
                print(f"  阶段{i}: {phase.get('phase', '未命名')} - {phase.get('description', '无描述')}")
        
        # 测试2: 错误处理测试
        logger.info("\n=== 测试2: 错误处理能力 ===")
        
        # 模拟空数据库场景（实际会返回0个用户）
        empty_result = await workflow.execute_workflow({
            "task": "空数据测试",
            "parameters": {"test_mode": "empty_data"}
        })
        
        print(f"\n空数据测试结果:")
        print(f"执行成功: {empty_result.get('success', False)}")
        print(f"执行摘要: {empty_result.get('execution_summary', '无摘要')}")
        
        # 输出工作流消息链
        if result.get('messages'):
            print(f"\n工作流消息链:")
            for i, message in enumerate(result['messages'], 1):
                print(f"{i}. {message}")
        
        logger.info("✅ Multi-Agent工作流测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ Multi-Agent工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_components():
    """测试各个组件的独立功能"""
    
    logger.info("\n=== 测试各组件独立功能 ===")
    
    try:
        workflow = MultiAgentWorkflow()
        
        # 测试图构建
        assert workflow.graph is not None, "工作流图未正确构建"
        logger.info("✅ LangGraph工作流图构建成功")
        
        # 测试状态初始化
        from app.agents.multi_agent_workflow import MultiAgentState
        test_state = MultiAgentState(
            messages=[],
            current_task="test",
            user_analysis_result=None,
            content_strategy=None,
            generated_content=None,
            coordination_plan=None,
            agent_results=[],
            session_context=None
        )
        
        logger.info("✅ 状态结构定义正确")
        
        # 测试内容主题建议
        themes = workflow._suggest_content_themes("正向", "注意")
        assert len(themes) > 0, "内容主题建议功能异常"
        logger.info(f"✅ 内容主题建议功能正常，生成{len(themes)}个主题")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 组件测试失败: {e}")
        return False


async def run_all_multi_agent_tests():
    """运行所有Multi-Agent测试"""
    
    logger.info("🚀 开始运行Multi-Agent系统完整测试套件")
    
    tests = [
        ("组件独立功能测试", test_individual_components),
        ("完整工作流测试", test_complete_workflow),
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
    logger.info(f"Multi-Agent测试完成: {success_count}/{total_tests} 通过")
    logger.info(f"{'='*60}")
    
    if success_count == total_tests:
        logger.info("🎉 所有Multi-Agent测试通过！")
        return True
    else:
        logger.warning(f"⚠️  有 {total_tests - success_count} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_multi_agent_tests())
    sys.exit(0 if success else 1)