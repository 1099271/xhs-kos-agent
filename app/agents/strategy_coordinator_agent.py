"""
策略协调Agent
负责整体内容策略制定、Agent间协调、工作流编排
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import json
from enum import Enum

from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent, EnhancedUserProfile
from app.agents.content_generator_agent import ContentGeneratorAgent, ContentGenerationRequest, GeneratedContent
from app.agents.llamaindex_manager import LlamaIndexManager
from app.agents.llm_manager import AgentLLMCaller, ModelProvider
from app.prompts.content_strategy_prompts import get_content_strategy_prompt
from app.utils.logger import app_logger as logger


class StrategyType(Enum):
    """策略类型"""
    ACQUISITION = "user_acquisition"  # 用户获取
    ENGAGEMENT = "user_engagement"    # 用户互动
    CONVERSION = "user_conversion"    # 用户转化
    RETENTION = "user_retention"      # 用户留存
    VIRAL = "viral_growth"           # 病毒传播


class ContentPriority(Enum):
    """内容优先级"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class StrategyObjective:
    """策略目标"""
    objective_type: StrategyType
    target_metrics: Dict[str, float]  # {"engagement_rate": 0.05, "conversion_rate": 0.02}
    timeline_days: int
    budget_limit: Optional[float] = None
    target_audience_size: Optional[int] = None


@dataclass
class ContentPlan:
    """内容计划"""
    plan_id: str
    strategy_objective: StrategyObjective
    target_users: List[EnhancedUserProfile]
    content_calendar: List[Dict[str, Any]]  # 包含发布时间、内容类型、目标用户等
    expected_outcomes: Dict[str, float]
    risk_assessment: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class ExecutionResult:
    """执行结果"""
    result_id: str
    plan_id: str
    executed_content: List[GeneratedContent]
    actual_metrics: Dict[str, float]
    success_indicators: Dict[str, bool]
    optimization_suggestions: List[str]
    lessons_learned: List[str]
    executed_at: datetime


@dataclass
class AgentTask:
    """Agent任务"""
    task_id: str
    agent_name: str
    task_type: str
    parameters: Dict[str, Any]
    priority: ContentPriority
    dependencies: List[str]
    estimated_duration: int  # 分钟
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    status: str = "pending"


class StrategyCoordinatorAgent:
    """策略协调智能体 - 负责整体策略制定和Agent协调"""
    
    def __init__(self, preferred_model_provider: Optional[ModelProvider] = None):
        self.name = "StrategyCoordinatorAgent"
        self.llm_caller = AgentLLMCaller(self.name, preferred_model_provider)
        self.user_analyst = EnhancedUserAnalystAgent(preferred_model_provider)
        self.content_generator = ContentGeneratorAgent(preferred_model_provider)
        self.llamaindex_manager = LlamaIndexManager()
        
        # 任务队列
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: Dict[str, AgentTask] = {}
        
        logger.info("StrategyCoordinatorAgent initialized")
    
    async def create_content_strategy(
        self, 
        objective: StrategyObjective,
        user_criteria: Dict[str, Any]
    ) -> ContentPlan:
        """基于目标创建内容策略"""
        try:
            logger.info(f"Creating content strategy for {objective.objective_type.value}")
            
            # 1. 分析目标用户群体
            target_users = await self._identify_target_users(user_criteria, objective)
            
            # 2. 制定内容策略
            strategy_details = await self._develop_strategy_details(objective, target_users)
            
            # 3. 创建内容日历
            content_calendar = await self._create_content_calendar(
                strategy_details, target_users, objective.timeline_days
            )
            
            # 4. 评估预期结果和风险
            expected_outcomes = await self._calculate_expected_outcomes(
                strategy_details, target_users, objective
            )
            risk_assessment = await self._assess_risks(strategy_details)
            
            import uuid
            plan = ContentPlan(
                plan_id=str(uuid.uuid4()),
                strategy_objective=objective,
                target_users=target_users,
                content_calendar=content_calendar,
                expected_outcomes=expected_outcomes,
                risk_assessment=risk_assessment,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            logger.info(f"Content strategy created: {plan.plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error creating content strategy: {str(e)}")
            raise
    
    async def execute_content_plan(self, plan: ContentPlan) -> ExecutionResult:
        """执行内容计划"""
        try:
            logger.info(f"Executing content plan: {plan.plan_id}")
            
            # 1. 创建任务队列
            await self._create_task_queue(plan)
            
            # 2. 并行执行Agent任务
            execution_results = await self._execute_agent_tasks()
            
            # 3. 生成实际内容
            generated_content = await self._generate_content_batch(plan, execution_results)
            
            # 4. 评估执行结果
            actual_metrics = await self._measure_actual_results(generated_content)
            success_indicators = self._calculate_success_indicators(
                actual_metrics, plan.expected_outcomes
            )
            
            # 5. 生成优化建议
            optimization_suggestions = await self._generate_optimization_suggestions(
                actual_metrics, plan.expected_outcomes, execution_results
            )
            
            # 6. 总结经验教训
            lessons_learned = await self._extract_lessons_learned(
                execution_results, actual_metrics
            )
            
            import uuid
            result = ExecutionResult(
                result_id=str(uuid.uuid4()),
                plan_id=plan.plan_id,
                executed_content=generated_content,
                actual_metrics=actual_metrics,
                success_indicators=success_indicators,
                optimization_suggestions=optimization_suggestions,
                lessons_learned=lessons_learned,
                executed_at=datetime.now()
            )
            
            logger.info(f"Content plan execution completed: {result.result_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing content plan: {str(e)}")
            raise
    
    async def optimize_strategy(
        self, 
        execution_result: ExecutionResult,
        original_plan: ContentPlan
    ) -> ContentPlan:
        """基于执行结果优化策略"""
        try:
            logger.info(f"Optimizing strategy for plan: {original_plan.plan_id}")
            
            # 1. 分析执行数据
            performance_analysis = await self._analyze_performance(execution_result)
            
            # 2. 识别优化机会
            optimization_opportunities = await self._identify_optimization_opportunities(
                performance_analysis, execution_result
            )
            
            # 3. 调整策略参数
            adjusted_strategy = await self._adjust_strategy_parameters(
                original_plan.strategy_objective, optimization_opportunities
            )
            
            # 4. 创建优化后的内容计划
            optimized_plan = await self.create_content_strategy(
                adjusted_strategy,
                {"user_ids": [u.user_id for u in original_plan.target_users]}
            )
            
            logger.info(f"Strategy optimization completed: {optimized_plan.plan_id}")
            return optimized_plan
            
        except Exception as e:
            logger.error(f"Error optimizing strategy: {str(e)}")
            raise
    
    async def _identify_target_users(
        self, 
        user_criteria: Dict[str, Any],
        objective: StrategyObjective
    ) -> List[EnhancedUserProfile]:
        """识别目标用户群体"""
        try:
            # 使用增强版用户分析Agent识别高价值用户
            high_value_users = await self.user_analyst.identify_high_value_users(
                min_engagement_rate=user_criteria.get('min_engagement_rate', 0.05),
                min_comment_count=user_criteria.get('min_comment_count', 5),
                limit=user_criteria.get('limit', 100)
            )
            
            # 按策略目标筛选用户
            filtered_users = []
            for user in high_value_users:
                # 根据策略类型进行额外筛选
                if objective.objective_type == StrategyType.ACQUISITION:
                    # 新用户获取：关注潜在用户
                    if user.influence_score > 0.7:
                        filtered_users.append(user)
                elif objective.objective_type == StrategyType.ENGAGEMENT:
                    # 用户互动：选择活跃度高但互动率低的用户
                    if 0.3 < user.engagement_rate < 0.8:
                        filtered_users.append(user)
                elif objective.objective_type == StrategyType.CONVERSION:
                    # 用户转化：选择有意向但未转化的用户
                    if user.sentiment_score > 0.6 and user.conversion_potential > 0.7:
                        filtered_users.append(user)
                else:
                    # 默认策略：选择综合评分高的用户
                    filtered_users.append(user)
            
            # 限制用户数量
            max_users = min(objective.target_audience_size or 50, len(filtered_users))
            return filtered_users[:max_users]
            
        except Exception as e:
            logger.error(f"Error identifying target users: {str(e)}")
            return []
    
    async def _develop_strategy_details(
        self, 
        objective: StrategyObjective,
        target_users: List[EnhancedUserProfile]
    ) -> Dict[str, Any]:
        """制定策略细节"""
        try:
            # 获取策略提示词
            strategy_prompt = get_content_strategy_prompt("strategy_development")
            
            # 构建用户画像摘要
            user_summary = self._summarize_user_profiles(target_users)
            
            # 构建策略变量
            variables = {
                "strategy_type": objective.objective_type.value,
                "target_metrics": json.dumps(objective.target_metrics, ensure_ascii=False),
                "timeline_days": str(objective.timeline_days),
                "user_profile_summary": user_summary,
                "budget_limit": str(objective.budget_limit or 0),
                "audience_size": str(len(target_users))
            }
            
            # 调用LLM生成策略详情
            strategy_response = await self.llm_caller.call_llm(
                strategy_prompt.format(**variables)
            )
            
            return self._parse_strategy_response(strategy_response)
            
        except Exception as e:
            logger.error(f"Error developing strategy details: {str(e)}")
            return self._get_default_strategy_details()
    
    async def _create_content_calendar(
        self,
        strategy_details: Dict[str, Any],
        target_users: List[EnhancedUserProfile],
        timeline_days: int
    ) -> List[Dict[str, Any]]:
        """创建内容日历"""
        try:
            calendar = []
            
            # 计算内容发布频率
            content_frequency = strategy_details.get('content_frequency', 'daily')
            posts_per_day = {'daily': 1, 'twice_daily': 2, 'weekly': 0.14}.get(content_frequency, 1)
            
            # 为每个用户创建个性化内容计划
            for day in range(1, timeline_days + 1):
                daily_posts = int(posts_per_day)
                
                for post_index in range(daily_posts):
                    # 选择目标用户（轮询分配）
                    user_index = (day * daily_posts + post_index) % len(target_users)
                    target_user = target_users[user_index]
                    
                    # 确定内容类型
                    content_type = self._determine_content_type(
                        strategy_details, day, post_index
                    )
                    
                    calendar.append({
                        'scheduled_date': day,
                        'content_type': content_type,
                        'target_user_id': target_user.user_id,
                        'user_profile': asdict(target_user),
                        'platform': strategy_details.get('primary_platform', 'xhs'),
                        'expected_engagement': self._estimate_engagement(target_user, content_type),
                        'priority': self._calculate_priority(day, strategy_details)
                    })
            
            return calendar
            
        except Exception as e:
            logger.error(f"Error creating content calendar: {str(e)}")
            return []
    
    async def _calculate_expected_outcomes(
        self,
        strategy_details: Dict[str, Any],
        target_users: List[EnhancedUserProfile],
        objective: StrategyObjective
    ) -> Dict[str, float]:
        """计算预期结果"""
        try:
            base_metrics = {
                'expected_reach': sum(u.follower_count for u in target_users) * 0.1,
                'expected_engagement': sum(u.engagement_rate * u.follower_count for u in target_users) * 0.05,
                'expected_conversion': len(target_users) * 0.02,
                'expected_viral_potential': sum(u.influence_score for u in target_users) * 0.15
            }
            
            # 根据目标类型调整预期
            if objective.objective_type == StrategyType.ACQUISITION:
                base_metrics['expected_new_followers'] = len(target_users) * 0.1
            elif objective.objective_type == StrategyType.ENGAGEMENT:
                base_metrics['expected_comments'] = len(target_users) * 2
                base_metrics['expected_likes'] = len(target_users) * 10
            elif objective.objective_type == StrategyType.CONVERSION:
                base_metrics['expected_clicks'] = len(target_users) * 0.3
                base_metrics['expected_purchases'] = len(target_users) * 0.05
            
            return base_metrics
            
        except Exception as e:
            logger.error(f"Error calculating expected outcomes: {str(e)}")
            return {}
    
    async def _assess_risks(self, strategy_details: Dict[str, Any]) -> Dict[str, Any]:
        """评估策略风险"""
        try:
            risks = {
                'content_saturation': {
                    'level': 'medium',
                    'probability': 0.4,
                    'impact': 'reduced_engagement',
                    'mitigation': 'diversify_content_types'
                },
                'audience_fatigue': {
                    'level': 'low',
                    'probability': 0.2,
                    'impact': 'unfollows',
                    'mitigation': 'frequency_optimization'
                },
                'platform_algorithm_changes': {
                    'level': 'high',
                    'probability': 0.6,
                    'impact': 'reduced_reach',
                    'mitigation': 'multi_platform_strategy'
                },
                'competitive_response': {
                    'level': 'medium',
                    'probability': 0.5,
                    'impact': 'diluted_impact',
                    'mitigation': 'unique_value_proposition'
                }
            }
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return {}
    
    async def _create_task_queue(self, plan: ContentPlan) -> None:
        """创建任务队列"""
        try:
            self.task_queue.clear()
            
            for idx, calendar_item in enumerate(plan.content_calendar):
                # 用户分析任务
                user_analysis_task = AgentTask(
                    task_id=f"user_analysis_{idx}",
                    agent_name="EnhancedUserAnalystAgent",
                    task_type="user_insights",
                    parameters={'user_id': calendar_item['target_user_id']},
                    priority=ContentPriority.HIGH,
                    dependencies=[],
                    estimated_duration=5
                )
                
                # 内容生成任务
                content_gen_task = AgentTask(
                    task_id=f"content_gen_{idx}",
                    agent_name="ContentGeneratorAgent",
                    task_type="content_creation",
                    parameters={
                        'user_profile': calendar_item['user_profile'],
                        'content_type': calendar_item['content_type'],
                        'platform': calendar_item['platform']
                    },
                    priority=ContentPriority(calendar_item['priority']),
                    dependencies=[f"user_analysis_{idx}"],
                    estimated_duration=10
                )
                
                self.task_queue.extend([user_analysis_task, content_gen_task])
                
        except Exception as e:
            logger.error(f"Error creating task queue: {str(e)}")
    
    async def _execute_agent_tasks(self) -> Dict[str, Any]:
        """执行Agent任务"""
        try:
            results = {}
            
            # 按依赖关系排序任务
            sorted_tasks = self._sort_tasks_by_dependencies()
            
            # 并行执行无依赖任务
            tasks_to_execute = []
            for task in sorted_tasks:
                if not task.dependencies:
                    tasks_to_execute.append(self._execute_single_task(task))
            
            if tasks_to_execute:
                task_results = await asyncio.gather(*tasks_to_execute)
                for task, result in zip([t for t in sorted_tasks if not t.dependencies], task_results):
                    task.status = "completed"
                    task.result = result
                    task.completed_at = datetime.now()
                    results[task.task_id] = result
                    self.completed_tasks[task.task_id] = task
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing agent tasks: {str(e)}")
            return {}
    
    async def _execute_single_task(self, task: AgentTask) -> Any:
        """执行单个任务"""
        try:
            task.assigned_at = datetime.now()
            
            if task.agent_name == "EnhancedUserAnalystAgent":
                # 执行用户分析任务
                user_id = task.parameters.get('user_id')
                if user_id:
                    return await self.user_analyst.get_user_insights(user_id)
            
            elif task.agent_name == "ContentGeneratorAgent":
                # 执行内容生成任务
                user_profile = task.parameters.get('user_profile')
                content_type = task.parameters.get('content_type')
                platform = task.parameters.get('platform')
                
                if user_profile and content_type and platform:
                    request = ContentGenerationRequest(
                        user_profile=user_profile,
                        content_type=content_type,
                        topic="基于策略的个性化内容",
                        platform=platform,
                        requirements={}
                    )
                    return await self.content_generator.generate_content(request)
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            return None
    
    async def _generate_content_batch(
        self, 
        plan: ContentPlan,
        execution_results: Dict[str, Any]
    ) -> List[GeneratedContent]:
        """批量生成内容"""
        try:
            content_requests = []
            
            for calendar_item in plan.content_calendar:
                user_profile = calendar_item['user_profile']
                content_type = calendar_item['content_type']
                platform = calendar_item['platform']
                
                request = ContentGenerationRequest(
                    user_profile=user_profile,
                    content_type=content_type,
                    topic=f"策略内容-{calendar_item['scheduled_date']}",
                    platform=platform,
                    requirements={
                        'strategy_type': plan.strategy_objective.objective_type.value,
                        'target_metrics': plan.strategy_objective.target_metrics
                    }
                )
                
                content_requests.append(request)
            
            # 批量生成内容
            generated_content = await self.content_generator.generate_content_batch(content_requests)
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating content batch: {str(e)}")
            return []
    
    def _summarize_user_profiles(self, users: List[EnhancedUserProfile]) -> str:
        """总结用户画像"""
        if not users:
            return "无目标用户"
        
        summary_parts = [
            f"目标用户总数: {len(users)}",
            f"平均影响力评分: {sum(u.influence_score for u in users) / len(users):.2f}",
            f"平均互动率: {sum(u.engagement_rate for u in users) / len(users):.2f}",
            f"主要兴趣领域: {', '.join(set(i for u in users for i in u.interests))}",
            f"主要痛点: {', '.join(set(p for u in users for p in u.pain_points))}"
        ]
        
        return "\n".join(summary_parts)
    
    def _parse_strategy_response(self, response: str) -> Dict[str, Any]:
        """解析策略响应"""
        # 简化处理，实际应该解析结构化响应
        return {
            'content_frequency': 'daily',
            'primary_platform': 'xhs',
            'content_mix': {'creative': 0.4, 'educational': 0.3, 'entertainment': 0.3},
            'tone_strategy': 'friendly_and_authentic',
            'engagement_tactics': ['questions', 'polls', 'user_features']
        }
    
    def _get_default_strategy_details(self) -> Dict[str, Any]:
        """获取默认策略详情"""
        return {
            'content_frequency': 'daily',
            'primary_platform': 'xhs',
            'content_mix': {'creative': 0.5, 'educational': 0.5},
            'tone_strategy': 'balanced',
            'engagement_tactics': ['questions', 'comments']
        }
    
    def _determine_content_type(self, strategy: Dict[str, Any], day: int, index: int) -> str:
        """确定内容类型"""
        content_mix = strategy.get('content_mix', {})
        types = list(content_mix.keys())
        weights = list(content_mix.values())
        
        # 简单的轮询选择
        total_items = len(types)
        selected_index = (day + index) % total_items
        return types[selected_index] if selected_index < len(types) else 'creative'
    
    def _estimate_engagement(self, user: EnhancedUserProfile, content_type: str) -> float:
        """估算互动率"""
        base_rate = user.engagement_rate
        type_multiplier = {'creative': 1.2, 'educational': 1.0, 'entertainment': 1.5}
        return base_rate * type_multiplier.get(content_type, 1.0)
    
    def _calculate_priority(self, day: int, strategy: Dict[str, Any]) -> int:
        """计算优先级"""
        # 越接近当前日期的内容优先级越高
        return max(1, 4 - day)
    
    def _sort_tasks_by_dependencies(self) -> List[AgentTask]:
        """按依赖关系排序任务"""
        # 简单的依赖排序
        return sorted(self.task_queue, key=lambda t: len(t.dependencies))
    
    async def _measure_actual_results(self, content: List[GeneratedContent]) -> Dict[str, float]:
        """测量实际结果"""
        # 这里应该集成实际的社交媒体API
        return {
            'actual_reach': len(content) * 1000,  # 模拟数据
            'actual_engagement': len(content) * 50,
            'actual_conversion': len(content) * 2,
            'actual_viral_coefficient': 1.2
        }
    
    def _calculate_success_indicators(
        self,
        actual: Dict[str, float],
        expected: Dict[str, float]
    ) -> Dict[str, bool]:
        """计算成功指标"""
        indicators = {}
        
        for metric, expected_value in expected.items():
            actual_value = actual.get(metric, 0)
            # 80%以上为成功
            indicators[metric] = actual_value >= expected_value * 0.8
        
        return indicators
    
    async def _generate_optimization_suggestions(
        self,
        actual: Dict[str, float],
        expected: Dict[str, float],
        execution_results: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        for metric, expected_value in expected.items():
            actual_value = actual.get(metric, 0)
            if actual_value < expected_value * 0.8:
                suggestions.append(
                    f"{metric}低于预期，建议调整内容类型或发布时间"
                )
        
        return suggestions
    
    async def _extract_lessons_learned(
        self,
        execution_results: Dict[str, Any],
        actual_metrics: Dict[str, float]
    ) -> List[str]:
        """提取经验教训"""
        lessons = [
            "内容策略需要根据用户反馈及时调整",
            "不同用户群体对内容类型的偏好差异显著",
            "发布时间对互动率有重要影响",
            "个性化内容比通用内容效果更好"
        ]
        
        return lessons
    
    async def _analyze_performance(self, result: ExecutionResult) -> Dict[str, Any]:
        """分析执行表现"""
        return {
            'overall_success_rate': sum(result.success_indicators.values()) / len(result.success_indicators),
            'best_performing_content': max(result.executed_content, key=lambda c: len(c.hashtags)),
            'underperforming_metrics': [
                metric for metric, success in result.success_indicators.items() 
                if not success
            ]
        }
    
    async def _identify_optimization_opportunities(
        self,
        analysis: Dict[str, Any],
        result: ExecutionResult
    ) -> List[str]:
        """识别优化机会"""
        opportunities = []
        
        if analysis['overall_success_rate'] < 0.7:
            opportunities.append("整体成功率较低，需要重新评估目标用户")
        
        if 'expected_engagement' in result.underperforming_metrics:
            opportunities.append("互动率未达预期，建议优化内容质量")
        
        return opportunities
    
    async def _adjust_strategy_parameters(
        self,
        original: StrategyObjective,
        opportunities: List[str]
    ) -> StrategyObjective:
        """调整策略参数"""
        # 根据优化机会调整目标
        adjusted_metrics = original.target_metrics.copy()
        
        for opportunity in opportunities:
            if "engagement" in opportunity:
                adjusted_metrics['engagement_rate'] *= 0.8
            elif "conversion" in opportunity:
                adjusted_metrics['conversion_rate'] *= 0.9
        
        return StrategyObjective(
            objective_type=original.objective_type,
            target_metrics=adjusted_metrics,
            timeline_days=original.timeline_days + 7,  # 延长时间线
            budget_limit=original.budget_limit,
            target_audience_size=original.target_audience_size
        )