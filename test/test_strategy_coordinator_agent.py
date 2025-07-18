"""
StrategyCoordinatorAgent测试套件
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from app.agents.strategy_coordinator_agent import (
    StrategyCoordinatorAgent,
    StrategyObjective,
    StrategyType,
    ContentPlan,
    ExecutionResult,
    AgentTask,
    ContentPriority
)


class TestStrategyCoordinatorAgent:
    """StrategyCoordinatorAgent测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.agent = StrategyCoordinatorAgent()
        self.test_objective = StrategyObjective(
            objective_type=StrategyType.ENGAGEMENT,
            target_metrics={"engagement_rate": 0.05, "reach": 10000},
            timeline_days=7,
            budget_limit=1000.0,
            target_audience_size=50
        )
        self.test_user_criteria = {
            "min_engagement_rate": 0.03,
            "min_comment_count": 5,
            "limit": 100
        }
    
    @pytest.mark.asyncio
    async def test_create_content_strategy(self):
        """测试创建内容策略"""
        with patch.object(self.agent.user_analyst, 'identify_high_value_users') as mock_identify:
            # 模拟用户分析结果
            mock_user = Mock(
                user_id="test_user",
                influence_score=0.8,
                engagement_rate=0.06,
                follower_count=1000,
                interests=["美妆", "旅行"],
                pain_points=["选择困难"],
                conversion_potential=0.7
            )
            mock_identify.return_value = [mock_user]
            
            plan = await self.agent.create_content_strategy(
                self.test_objective,
                self.test_user_criteria
            )
            
            assert isinstance(plan, ContentPlan)
            assert plan.plan_id is not None
            assert len(plan.target_users) > 0
            assert len(plan.content_calendar) > 0
            assert plan.strategy_objective.objective_type == StrategyType.ENGAGEMENT
    
    @pytest.mark.asyncio
    async def test_execute_content_plan(self):
        """测试执行内容计划"""
        # 创建测试计划
        test_plan = ContentPlan(
            plan_id="test_plan_123",
            strategy_objective=self.test_objective,
            target_users=[],
            content_calendar=[
                {
                    'scheduled_date': 1,
                    'content_type': 'creative',
                    'target_user_id': 'user1',
                    'user_profile': {'user_id': 'user1', 'nickname': '测试用户'},
                    'platform': 'xhs',
                    'expected_engagement': 0.05,
                    'priority': 1
                }
            ],
            expected_outcomes={'expected_reach': 5000, 'expected_engagement': 250},
            risk_assessment={'content_saturation': {'level': 'medium'}},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with patch.object(self.agent.content_generator, 'generate_content_batch') as mock_gen:
            # 模拟内容生成
            mock_content = Mock(
                content_id="content_123",
                title="测试内容",
                main_content="这是测试内容",
                hashtags=["测试"],
                platform_specific={},
                generation_timestamp=datetime.now(),
                ai_explanation="测试"
            )
            mock_gen.return_value = [mock_content]
            
            result = await self.agent.execute_content_plan(test_plan)
            
            assert isinstance(result, ExecutionResult)
            assert result.plan_id == test_plan.plan_id
            assert len(result.executed_content) > 0
            assert 'expected_reach' in result.actual_metrics
    
    @pytest.mark.asyncio
    async def test_optimize_strategy(self):
        """测试策略优化"""
        # 创建测试执行结果
        execution_result = ExecutionResult(
            result_id="test_result_123",
            plan_id="test_plan_123",
            executed_content=[],
            actual_metrics={'expected_reach': 4000, 'expected_engagement': 200},
            success_indicators={'expected_reach': True, 'expected_engagement': False},
            optimization_suggestions=["提高互动率"],
            lessons_learned=["需要更多互动元素"],
            executed_at=datetime.now()
        )
        
        original_plan = ContentPlan(
            plan_id="original_plan_123",
            strategy_objective=self.test_objective,
            target_users=[],
            content_calendar=[],
            expected_outcomes={'expected_reach': 5000, 'expected_engagement': 250},
            risk_assessment={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with patch.object(self.agent, 'create_content_strategy') as mock_create:
            mock_create.return_value = ContentPlan(
                plan_id="optimized_plan_123",
                strategy_objective=self.test_objective,
                target_users=[],
                content_calendar=[],
                expected_outcomes={'expected_reach': 4000, 'expected_engagement': 200},
                risk_assessment={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            optimized_plan = await self.agent.optimize_strategy(
                execution_result,
                original_plan
            )
            
            assert isinstance(optimized_plan, ContentPlan)
            assert optimized_plan.plan_id != original_plan.plan_id
    
    @pytest.mark.asyncio
    async def test_identify_target_users(self):
        """测试识别目标用户"""
        with patch.object(self.agent.user_analyst, 'identify_high_value_users') as mock_identify:
            mock_user = Mock(
                user_id="test_user",
                influence_score=0.8,
                engagement_rate=0.06,
                follower_count=1000,
                interests=["美妆"],
                pain_points=["选择困难"],
                conversion_potential=0.7
            )
            mock_identify.return_value = [mock_user]
            
            users = await self.agent._identify_target_users(
                self.test_user_criteria,
                self.test_objective
            )
            
            assert len(users) > 0
            assert users[0].user_id == "test_user"
    
    def test_strategy_type_enum(self):
        """测试策略类型枚举"""
        assert StrategyType.ACQUISITION.value == "user_acquisition"
        assert StrategyType.ENGAGEMENT.value == "user_engagement"
        assert StrategyType.CONVERSION.value == "user_conversion"
        assert StrategyType.RETENTION.value == "user_retention"
        assert StrategyType.VIRAL.value == "viral_growth"
    
    def test_content_priority_enum(self):
        """测试内容优先级枚举"""
        assert ContentPriority.HIGH.value == 1
        assert ContentPriority.MEDIUM.value == 2
        assert ContentPriority.LOW.value == 3
    
    def test_sort_tasks_by_dependencies(self):
        """测试任务依赖排序"""
        # 创建测试任务
        task1 = AgentTask(
            task_id="task1",
            agent_name="TestAgent",
            task_type="test",
            parameters={},
            priority=ContentPriority.HIGH,
            dependencies=[],
            estimated_duration=5
        )
        
        task2 = AgentTask(
            task_id="task2",
            agent_name="TestAgent",
            task_type="test",
            parameters={},
            priority=ContentPriority.MEDIUM,
            dependencies=["task1"],
            estimated_duration=5
        )
        
        self.agent.task_queue = [task2, task1]
        sorted_tasks = self.agent._sort_tasks_by_dependencies()
        
        # task1应该在task2之前（无依赖）
        assert sorted_tasks[0].task_id == "task1"
        assert sorted_tasks[1].task_id == "task2"
    
    def test_calculate_success_indicators(self):
        """测试成功指标计算"""
        actual = {'expected_reach': 4000, 'expected_engagement': 200}
        expected = {'expected_reach': 5000, 'expected_engagement': 250}
        
        indicators = self.agent._calculate_success_indicators(actual, expected)
        
        assert isinstance(indicators, dict)
        assert 'expected_reach' in indicators
        assert 'expected_engagement' in indicators
        # 4000/5000 = 0.8 >= 0.8, 应该为True
        assert indicators['expected_reach'] == True
        # 200/250 = 0.8 >= 0.8, 应该为True
        assert indicators['expected_engagement'] == True
    
    def test_determine_content_type(self):
        """测试内容类型确定"""
        strategy = {'content_mix': {'creative': 0.4, 'educational': 0.3, 'entertainment': 0.3}}
        
        content_type = self.agent._determine_content_type(strategy, 1, 0)
        assert content_type in ['creative', 'educational', 'entertainment']
    
    def test_estimate_engagement(self):
        """测试互动率估算"""
        mock_user = Mock(
            engagement_rate=0.05,
            influence_score=0.7
        )
        
        engagement = self.agent._estimate_engagement(mock_user, 'creative')
        assert engagement == 0.06  # 0.05 * 1.2
    
    def test_calculate_priority(self):
        """测试优先级计算"""
        priority = self.agent._calculate_priority(1, {})
        assert priority == 3
        
        priority = self.agent._calculate_priority(3, {})
        assert priority == 1
    
    def test_summarize_user_profiles(self):
        """测试用户画像总结"""
        mock_users = [
            Mock(
                user_id="user1",
                influence_score=0.8,
                engagement_rate=0.06,
                follower_count=1000,
                interests=["美妆"],
                pain_points=["选择困难"]
            ),
            Mock(
                user_id="user2",
                influence_score=0.7,
                engagement_rate=0.05,
                follower_count=800,
                interests=["旅行"],
                pain_points=["信息过载"]
            )
        ]
        
        summary = self.agent._summarize_user_profiles(mock_users)
        
        assert "目标用户总数: 2" in summary
        assert "美妆" in summary or "旅行" in summary
        assert "选择困难" in summary or "信息过载" in summary
    
    @pytest.mark.asyncio
    async def test_create_task_queue(self):
        """测试创建任务队列"""
        test_plan = ContentPlan(
            plan_id="test_plan",
            strategy_objective=self.test_objective,
            target_users=[],
            content_calendar=[
                {
                    'scheduled_date': 1,
                    'content_type': 'creative',
                    'target_user_id': 'user1',
                    'user_profile': {'user_id': 'user1'},
                    'platform': 'xhs',
                    'expected_engagement': 0.05,
                    'priority': 1
                }
            ],
            expected_outcomes={},
            risk_assessment={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await self.agent._create_task_queue(test_plan)
        
        assert len(self.agent.task_queue) > 0
        assert any(task.task_type == "user_insights" for task in self.agent.task_queue)
        assert any(task.task_type == "content_creation" for task in self.agent.task_queue)


if __name__ == "__main__":
    pytest.main([__file__])