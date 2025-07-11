"""
用户分析Agent测试脚本
用于测试和演示User Analyst Agent的功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.agents.user_analyst_agent import UserAnalystAgent, UserProfile
from app.infra.db.async_database import get_session_context
from app.utils.logger import app_logger as logger


async def test_user_analyst_agent():
    """测试用户分析Agent"""
    
    logger.info("开始测试 User Analyst Agent")
    
    # 创建Agent实例
    analyst = UserAnalystAgent()
    
    # 使用上下文管理器自动处理数据库会话
    async with get_session_context() as session:
        # 测试1: 基础用户分析
        logger.info("=== 测试1: 基础高价值用户分析 ===")
        result = await analyst.execute(session)
        
        print(f"\n分析结果:")
        print(f"总共分析用户数: {result.total_analyzed}")
        print(f"分析时间: {result.analysis_time}")
        print(f"筛选条件: {result.criteria_used}")
        
        print(f"\n前10名高价值用户:")
        for i, user in enumerate(result.high_value_users[:10], 1):
            print(f"{i}. 用户ID: {user.user_id}")
            print(f"   昵称: {user.nickname}")
            print(f"   价值评分: {user.value_score}")
            print(f"   情感倾向: {user.emotional_preference}")
            print(f"   未满足需求: {user.unmet_preference}")
            print(f"   互动次数: {user.interaction_count}")
            print(f"   参与笔记数: {len(user.notes_engaged)}")
            print(f"   未满足需求描述: {user.unmet_desc[:50]}...")
            print("-" * 50)
        
        # 测试2: 自定义条件分析
        logger.info("\n=== 测试2: 自定义条件分析 ===")
        custom_criteria = {
            "emotional_preference": ["正向"],
            "unmet_preference": ["是"], 
            "exclude_visited": True,  # 排除已去过的用户
            "min_interaction_count": 2,
            "limit": 20
        }
        
        custom_result = await analyst.execute(session, custom_criteria)
        print(f"\n自定义条件分析结果:")
        print(f"分析用户数: {custom_result.total_analyzed}")
        if custom_result.high_value_users:
            print(f"平均价值评分: {sum(u.value_score for u in custom_result.high_value_users) / len(custom_result.high_value_users):.2f}")
        
        # 测试3: 特定用户详细分析
        if result.high_value_users:
            logger.info("\n=== 测试3: 特定用户详细分析 ===")
            target_user = result.high_value_users[0]
            detailed_analysis = await analyst.get_user_detailed_analysis(
                session, target_user.user_id
            )
            
            if detailed_analysis:
                print(f"\n用户 {target_user.user_id} 详细分析:")
                print(f"总分析次数: {detailed_analysis['total_analyses']}")
                print(f"总评论数: {detailed_analysis['total_comments']}")
                print(f"分析历史条目: {len(detailed_analysis['analysis_history'])}")
                print(f"评论历史条目: {len(detailed_analysis['comment_history'])}")
                
                # 显示最近的分析记录
                if detailed_analysis['analysis_history']:
                    recent_analysis = detailed_analysis['analysis_history'][0]
                    print(f"\n最近分析记录:")
                    print(f"  笔记ID: {recent_analysis['note_id']}")
                    print(f"  情感倾向: {recent_analysis['emotional_preference']}")
                    print(f"  AIPS偏好: {recent_analysis['aips_preference']}")
                    print(f"  未满足需求: {recent_analysis['unmet_desc'][:100]}...")
        
        # 生成总结报告
        logger.info("\n=== 分析总结 ===")
        if result.high_value_users:
            emotional_dist = {}
            aips_dist = {}
            unmet_count = 0
            
            for user in result.high_value_users:
                # 情感分布统计
                emotional_dist[user.emotional_preference] = emotional_dist.get(user.emotional_preference, 0) + 1
                # AIPS分布统计  
                aips_dist[user.aips_preference] = aips_dist.get(user.aips_preference, 0) + 1
                # 未满足需求统计
                if user.unmet_preference == "是":
                    unmet_count += 1
            
            print(f"\n高价值用户特征分析:")
            print(f"情感倾向分布: {emotional_dist}")
            print(f"AIPS偏好分布: {aips_dist}")
            print(f"有未满足需求用户: {unmet_count}/{len(result.high_value_users)} ({unmet_count/len(result.high_value_users)*100:.1f}%)")
            print(f"平均价值评分: {sum(u.value_score for u in result.high_value_users) / len(result.high_value_users):.2f}")
            print(f"平均互动次数: {sum(u.interaction_count for u in result.high_value_users) / len(result.high_value_users):.1f}")


if __name__ == "__main__":
    asyncio.run(test_user_analyst_agent())