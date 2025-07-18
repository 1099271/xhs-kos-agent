"""
Multi-Agent系统的命令行接口
提供命令行工具来管理和执行Agent工作流
"""

import asyncio
import json
import click
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# 添加项目根目录到Python路径
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.strategy_coordinator_agent import StrategyCoordinatorAgent, StrategyObjective, StrategyType
from app.agents.content_generator_agent import ContentGeneratorAgent, ContentGenerationRequest
from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow
from app.agents.llm_manager import ModelProvider
from app.utils.logger import app_logger as logger


@click.group()
@click.version_option(version="1.0.0")
@click.option('--verbose', '-v', is_flag=True, help='启用详细日志')
@click.option('--model-provider', 
              type=click.Choice(['OPENAI', 'OPENROUTER', 'ANTHROPIC', 'LOCAL'], case_sensitive=False),
              default='OPENROUTER',
              help='选择LLM模型提供商')
@click.pass_context
def cli(ctx, verbose, model_provider):
    """XHS KOS Multi-Agent系统命令行工具"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['model_provider'] = ModelProvider[model_provider.upper()]
    
    # 日志配置通过logger模块自动处理


@cli.group()
def agents():
    """Agent管理命令"""
    pass


@cli.group()
def strategy():
    """内容策略管理"""
    pass


@cli.group()
def content():
    """内容生成管理"""
    pass


@cli.group()
def workflow():
    """工作流执行"""
    pass


@cli.group()
def users():
    """用户分析"""
    pass


@agents.command()
@click.pass_context
def status(ctx):
    """查看所有Agent状态"""
    async def _show_status():
        try:
            coordinator = StrategyCoordinatorAgent(ctx.obj['model_provider'])
            content_gen = ContentGeneratorAgent(ctx.obj['model_provider'])
            analyst = EnhancedUserAnalystAgent(ctx.obj['model_provider'])
            workflow_engine = EnhancedMultiAgentWorkflow(ctx.obj['model_provider'])
            
            status_info = [
                {"Agent": "StrategyCoordinatorAgent", "Status": "✅ Active", "Version": "1.0.0"},
                {"Agent": "ContentGeneratorAgent", "Status": "✅ Active", "Version": "1.0.0"},
                {"Agent": "EnhancedUserAnalystAgent", "Status": "✅ Active", "Version": "1.0.0"},
                {"Agent": "EnhancedMultiAgentWorkflow", "Status": "✅ Active", "Version": "1.0.0"}
            ]
            
            click.echo("📊 Agent状态摘要:")
            for info in status_info:
                click.echo(f"  {info['Agent']}: {info['Status']} (v{info['Version']})")
                
        except Exception as e:
            click.echo(f"❌ 获取Agent状态失败: {e}", err=True)
    
    asyncio.run(_show_status())


@strategy.command()
@click.option('--type', 'strategy_type', 
              type=click.Choice(['engagement', 'conversion', 'acquisition', 'retention', 'viral'], case_sensitive=False),
              default='engagement',
              help='策略类型')
@click.option('--metrics', '-m', 
              multiple=True,
              default=['engagement_rate=0.05', 'reach=10000'],
              help='目标指标 (格式: key=value)')
@click.option('--timeline', '-t', default=7, help='时间周期(天)')
@click.option('--budget', '-b', type=float, help='预算限制')
@click.option('--audience-size', '-a', default=30, help='目标受众数量')
@click.option('--min-engagement', default=0.03, help='最低互动率')
@click.option('--min-comments', default=3, help='最低评论数')
@click.pass_context
def create(ctx, strategy_type, metrics, timeline, budget, audience_size, min_engagement, min_comments):
    """创建内容策略"""
    async def _create_strategy():
        try:
            # 解析指标
            target_metrics = {}
            for metric in metrics:
                if '=' in metric:
                    key, value = metric.split('=', 1)
                    try:
                        target_metrics[key] = float(value)
                    except ValueError:
                        target_metrics[key] = value
            
            # 创建策略目标
            strategy_objective = StrategyObjective(
                objective_type=StrategyType[strategy_type.upper()],
                target_metrics=target_metrics,
                timeline_days=timeline,
                budget_limit=budget,
                target_audience_size=audience_size
            )
            
            # 创建策略
            coordinator = StrategyCoordinatorAgent(ctx.obj['model_provider'])
            plan = await coordinator.create_content_strategy(
                strategy_objective,
                {
                    'min_engagement_rate': min_engagement,
                    'min_comment_count': min_comments,
                    'limit': audience_size
                }
            )
            
            click.echo("🎯 策略创建成功!")
            click.echo(f"  计划ID: {plan.plan_id}")
            click.echo(f"  策略类型: {strategy_type}")
            click.echo(f"  目标用户: {len(plan.target_users)} 人")
            click.echo(f"  内容日历: {len(plan.content_calendar)} 条内容")
            click.echo(f"  预期结果: {json.dumps(plan.expected_outcomes, ensure_ascii=False, indent=2)}")
            
            # 保存策略到文件
            with open(f'strategy_{plan.plan_id}.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'plan_id': plan.plan_id,
                    'strategy_objective': {
                        'type': strategy_type,
                        'metrics': target_metrics,
                        'timeline': timeline,
                        'budget': budget
                    },
                    'target_users': len(plan.target_users),
                    'content_calendar': len(plan.content_calendar),
                    'expected_outcomes': plan.expected_outcomes
                }, f, ensure_ascii=False, indent=2)
            
            click.echo(f"  策略已保存至: strategy_{plan.plan_id}.json")
            
        except Exception as e:
            click.echo(f"❌ 创建策略失败: {e}", err=True)
    
    asyncio.run(_create_strategy())


@content.command()
@click.option('--user-profile', '-u', required=True, help='用户画像JSON字符串')
@click.option('--type', 'content_type', default='creative', help='内容类型')
@click.option('--topic', '-t', required=True, help='内容主题')
@click.option('--platform', '-p', default='xhs', help='发布平台')
@click.option('--output', '-o', help='输出文件路径')
@click.pass_context
def generate(ctx, user_profile, content_type, topic, platform, output):
    """生成个性化内容"""
    async def _generate_content():
        try:
            # 解析用户画像
            try:
                profile = json.loads(user_profile)
            except json.JSONDecodeError:
                click.echo("❌ 用户画像必须是有效的JSON格式", err=True)
                return
            
            # 创建内容生成请求
            request = ContentGenerationRequest(
                user_profile=profile,
                content_type=content_type,
                topic=topic,
                platform=platform,
                requirements={}
            )
            
            # 生成内容
            generator = ContentGeneratorAgent(ctx.obj['model_provider'])
            content = await generator.generate_content(request)
            
            # 显示结果
            click.echo("✍️  内容生成成功!")
            click.echo(f"  内容ID: {content.content_id}")
            click.echo(f"  标题: {content.title}")
            click.echo(f"  主要内容: {content.main_content[:200]}...")
            click.echo(f"  标签: {', '.join(content.hashtags)}")
            click.echo(f"  平台特定: {json.dumps(content.platform_specific, ensure_ascii=False)}")
            
            # 保存到文件
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump({
                        'content_id': content.content_id,
                        'title': content.title,
                        'main_content': content.main_content,
                        'hashtags': content.hashtags,
                        'media_suggestions': content.media_suggestions,
                        'platform_specific': content.platform_specific,
                        'ai_explanation': content.ai_explanation
                    }, f, ensure_ascii=False, indent=2)
                click.echo(f"  内容已保存至: {output}")
            
        except Exception as e:
            click.echo(f"❌ 内容生成失败: {e}", err=True)
    
    asyncio.run(_generate_content())


@workflow.command()
@click.option('--config', '-c', help='工作流配置文件路径')
@click.option('--async/--sync', default=False, help='异步/同步执行')
@click.option('--output', '-o', help='输出结果文件路径')
@click.pass_context
def execute(ctx, config, async_execution, output):
    """执行完整工作流"""
    async def _execute_workflow():
        try:
            workflow_config = {}
            
            # 加载配置文件
            if config:
                try:
                    with open(config, 'r', encoding='utf-8') as f:
                        workflow_config = json.load(f)
                except FileNotFoundError:
                    click.echo(f"❌ 配置文件不存在: {config}", err=True)
                    return
                except json.JSONDecodeError:
                    click.echo(f"❌ 配置文件格式错误: {config}", err=True)
                    return
            
            # 使用默认配置
            else:
                workflow_config = {
                    "strategy_objective": {
                        "type": "engagement",
                        "metrics": {"engagement_rate": 0.05, "reach": 5000},
                        "timeline": 7,
                        "budget": 500,
                        "audience_size": 20
                    },
                    "user_criteria": {
                        "min_engagement_rate": 0.03,
                        "min_comment_count": 3,
                        "limit": 20
                    }
                }
            
            click.echo("🚀 开始执行工作流...")
            
            # 执行工作流
            workflow_engine = EnhancedMultiAgentWorkflow(ctx.obj['model_provider'])
            result = await workflow_engine.execute_complete_workflow(workflow_config)
            
            if result['success']:
                click.echo("✅ 工作流执行完成!")
                click.echo(f"  执行摘要: {result['execution_summary']}")
                click.echo(f"  性能指标: {json.dumps(result['performance_metrics'], ensure_ascii=False, indent=2)}")
                
                # 保存结果
                if output:
                    with open(output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
                    click.echo(f"  结果已保存至: {output}")
                else:
                    # 使用默认文件名
                    filename = f"workflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
                    click.echo(f"  结果已保存至: {filename}")
            else:
                click.echo(f"❌ 工作流执行失败: {result.get('error', '未知错误')}", err=True)
                
        except Exception as e:
            click.echo(f"❌ 工作流执行失败: {e}", err=True)
    
    asyncio.run(_execute_workflow())


@users.command()
@click.option('--limit', '-l', default=50, help='返回用户数量限制')
@click.option('--min-engagement', default=0.03, help='最低互动率')
@click.option('--min-comments', default=3, help='最低评论数')
@click.option('--output', '-o', help='输出文件路径')
@click.pass_context
def high_value(ctx, limit, min_engagement, min_comments, output):
    """识别高价值用户"""
    async def _identify_users():
        try:
            analyst = EnhancedUserAnalystAgent(ctx.obj['model_provider'])
            users = await analyst.identify_high_value_users(
                min_engagement_rate=min_engagement,
                min_comment_count=min_comments,
                limit=limit
            )
            
            click.echo("👥 高价值用户识别完成!")
            click.echo(f"  发现 {len(users)} 个高价值用户")
            
            # 显示前5个用户
            for i, user in enumerate(users[:5]):
                click.echo(f"  {i+1}. {user.nickname} (ID: {user.user_id})")
                click.echo(f"     价值分数: {user.value_score:.2f}")
                click.echo(f"     互动率: {user.engagement_rate:.3f}")
                click.echo(f"     粉丝数: {user.follower_count}")
                click.echo(f"     情感偏好: {user.emotional_preference}")
                click.echo()
            
            if len(users) > 5:
                click.echo(f"  ... 还有 {len(users) - 5} 个用户未显示")
            
            # 保存结果
            users_data = [
                {
                    'user_id': u.user_id,
                    'nickname': u.nickname,
                    'value_score': u.value_score,
                    'engagement_rate': u.engagement_rate,
                    'follower_count': u.follower_count,
                    'emotional_preference': u.emotional_preference,
                    'unmet_desc': u.unmet_desc,
                    'interaction_count': u.interaction_count
                }
                for u in users
            ]
            
            if output:
                filename = output
            else:
                filename = f"high_value_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            
            click.echo(f"  用户列表已保存至: {filename}")
            
        except Exception as e:
            click.echo(f"❌ 用户识别失败: {e}", err=True)
    
    asyncio.run(_identify_users())


@users.command()
@click.argument('user_id')
@click.option('--output', '-o', help='输出文件路径')
@click.pass_context
def insights(ctx, user_id, output):
    """获取用户洞察"""
    async def _get_insights():
        try:
            analyst = EnhancedUserAnalystAgent(ctx.obj['model_provider'])
            insights = await analyst.get_user_insights(user_id)
            
            if not insights:
                click.echo(f"❌ 用户 {user_id} 未找到", err=True)
                return
            
            click.echo("🔍 用户洞察分析完成!")
            click.echo(f"  用户ID: {insights.user_id}")
            click.echo(f"  昵称: {insights.nickname}")
            click.echo(f"  价值分数: {insights.value_score:.2f}")
            click.echo(f"  互动率: {insights.engagement_rate:.3f}")
            click.echo(f"  影响力分数: {insights.influence_score:.2f}")
            click.echo(f"  兴趣: {', '.join(insights.interests)}")
            click.echo(f"  痛点: {', '.join(insights.pain_points)}")
            click.echo(f"  内容偏好: {insights.content_preferences}")
            
            if insights.semantic_search_results:
                click.echo(f"  语义搜索结果: {len(insights.semantic_search_results)} 条")
            
            if insights.ai_insights:
                click.echo(f"  AI洞察: {insights.ai_insights}")
            
            # 保存洞察结果
            insights_data = {
                'user_id': insights.user_id,
                'nickname': insights.nickname,
                'value_score': insights.value_score,
                'engagement_rate': insights.engagement_rate,
                'influence_score': insights.influence_score,
                'interests': insights.interests,
                'pain_points': insights.pain_points,
                'content_preferences': insights.content_preferences,
                'semantic_search_results': insights.semantic_search_results,
                'ai_insights': insights.ai_insights,
                'retrieval_score': insights.retrieval_score
            }
            
            if output:
                filename = output
            else:
                filename = f"user_insights_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(insights_data, f, ensure_ascii=False, indent=2)
            
            click.echo(f"  洞察结果已保存至: {filename}")
            
        except Exception as e:
            click.echo(f"❌ 获取用户洞察失败: {e}", err=True)
    
    asyncio.run(_get_insights())


@cli.command()
@click.pass_context
def demo(ctx):
    """运行演示工作流"""
    async def _run_demo():
        try:
            click.echo("🎭 运行Multi-Agent系统演示...")
            
            # 创建演示配置
            demo_config = {
                "strategy_objective": {
                    "type": "engagement",
                    "metrics": {"engagement_rate": 0.08, "reach": 3000},
                    "timeline": 3,
                    "budget": 200,
                    "audience_size": 10
                },
                "user_criteria": {
                    "min_engagement_rate": 0.05,
                    "min_comment_count": 2,
                    "limit": 10
                }
            }
            
            # 执行演示
            workflow_engine = EnhancedMultiAgentWorkflow(ctx.obj['model_provider'])
            result = await workflow_engine.execute_complete_workflow(demo_config)
            
            if result['success']:
                click.echo("\n🎉 演示工作流执行成功!")
                click.echo("="*50)
                click.echo(result['execution_summary'])
                click.echo("="*50)
                
                # 保存演示结果
                filename = f"demo_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2, default=str)
                
                click.echo(f"\n📁 演示结果已保存至: {filename}")
            else:
                click.echo(f"❌ 演示失败: {result.get('error', '未知错误')}", err=True)
                
        except Exception as e:
            click.echo(f"❌ 演示运行失败: {e}", err=True)
    
    asyncio.run(_run_demo())


@cli.command()
@click.option('--host', default='0.0.0.0', help='服务主机地址')
@click.option('--port', default=8000, help='服务端口')
@click.option('--reload', is_flag=True, help='启用重载模式')
def serve(host, port, reload):
    """启动FastAPI服务"""
    try:
        import uvicorn
        from app.api.main import app
        
        click.echo(f"🚀 启动FastAPI服务: http://{host}:{port}")
        click.echo(f"📖 API文档: http://{host}:{port}/docs")
        
        uvicorn.run(
            "app.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        click.echo("❌ 需要安装uvicorn: pip install uvicorn", err=True)
    except Exception as e:
        click.echo(f"❌ 启动服务失败: {e}", err=True)


if __name__ == '__main__':
    cli()