"""
增强版Multi-Agent工作流系统
集成LLM模型，实现真正的智能化Multi-Agent协作
包含StrategyCoordinatorAgent和ContentGeneratorAgent的完整集成
"""

from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent, EnhancedUserProfile
from app.agents.content_generator_agent import ContentGeneratorAgent, ContentGenerationRequest, GeneratedContent
from app.agents.strategy_coordinator_agent import StrategyCoordinatorAgent, StrategyObjective, StrategyType, ContentPlan
from app.agents.llamaindex_manager import LlamaIndexManager
from app.agents.llm_manager import AgentLLMCaller, ModelProvider
from app.prompts.content_strategy_prompts import get_content_strategy_prompt
from app.utils.logger import app_logger as logger


@dataclass
class EnhancedAgentResult:
    """增强版Agent执行结果"""
    agent_name: str
    success: bool
    data: Any
    message: str
    llm_analysis: Optional[str]  # LLM分析结果
    timestamp: datetime
    execution_time: float


class EnhancedMultiAgentState(TypedDict):
    """增强版Multi-Agent工作流状态"""
    messages: List[BaseMessage]
    current_task: str
    strategy_objective: Optional[StrategyObjective]
    content_plan: Optional[ContentPlan]
    target_users: List[EnhancedUserProfile]
    generated_content: List[GeneratedContent]
    agent_results: List[EnhancedAgentResult]
    llm_insights: Dict[str, str]  # 各阶段的LLM洞察
    execution_context: Dict[str, Any]  # 执行上下文
    preferred_model: Optional[str]  # 首选模型


class EnhancedMultiAgentWorkflow:
    """增强版Multi-Agent工作流引擎 - 集成所有Agent"""
    
    def __init__(self, preferred_model_provider: Optional[ModelProvider] = None):
        self.graph = None
        self.strategy_coordinator = StrategyCoordinatorAgent(preferred_model_provider)
        self.user_analyst = EnhancedUserAnalystAgent(preferred_model_provider)
        self.content_generator = ContentGeneratorAgent(preferred_model_provider)
        self.llamaindex_manager = LlamaIndexManager()
        self.preferred_provider = preferred_model_provider
        
        # 为各Agent创建专用LLM调用器
        self.coordinator_llm = AgentLLMCaller("StrategyCoordinatorAgent", preferred_model_provider)
        self.user_analyst_llm = AgentLLMCaller("UserAnalystAgent", preferred_model_provider)
        self.content_generator_llm = AgentLLMCaller("ContentGeneratorAgent", preferred_model_provider)
        
        self._build_workflow()
        
    def _build_workflow(self):
        """构建增强版LangGraph工作流"""
        
        # 创建状态图
        workflow = StateGraph(EnhancedMultiAgentState)
        
        # 添加节点
        workflow.add_node("initialize_workflow", self._initialize_workflow)
        workflow.add_node("strategy_planning", self._strategy_planning)
        workflow.add_node("user_analysis", self._user_analysis)
        workflow.add_node("content_generation", self._content_generation)
        workflow.add_node("strategy_execution", self._strategy_execution)
        workflow.add_node("finalize_workflow", self._finalize_workflow)
        
        # 设置入口点
        workflow.set_entry_point("initialize_workflow")
        
        # 添加边（工作流路径）
        workflow.add_edge("initialize_workflow", "strategy_planning")
        workflow.add_edge("strategy_planning", "user_analysis")
        workflow.add_edge("user_analysis", "content_generation")
        workflow.add_edge("content_generation", "strategy_execution")
        workflow.add_edge("strategy_execution", "finalize_workflow")
        workflow.add_edge("finalize_workflow", END)
        
        # 编译图
        self.graph = workflow.compile()
        
    async def _initialize_workflow(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """初始化工作流"""
        logger.info("🚀 启动增强版Multi-Agent工作流")
        
        start_time = datetime.now()
        state["current_task"] = "workflow_initialization"
        state["agent_results"] = []
        state["llm_insights"] = {}
        state["execution_context"] = {
            "workflow_start_time": start_time,
            "llm_provider": self.preferred_provider.value if self.preferred_provider else "auto"
        }
        
        # 设置默认策略目标
        state["strategy_objective"] = StrategyObjective(
            objective_type=StrategyType.ENGAGEMENT,
            target_metrics={"engagement_rate": 0.05, "reach": 10000},
            timeline_days=7,
            budget_limit=1000.0,
            target_audience_size=30
        )
        
        state["messages"] = [
            HumanMessage(content="启动增强版Multi-Agent工作流：策略制定 → 用户分析 → 内容生成 → 策略执行")
        ]
        
        return state
    
    async def _strategy_planning(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """策略规划阶段"""
        logger.info("📋 执行策略规划阶段")
        
        start_time = datetime.now()
        state["current_task"] = "strategy_planning"
        
        try:
            strategy_objective = state["strategy_objective"]
            
            # 使用策略协调Agent创建内容计划
            content_plan = await self.strategy_coordinator.create_content_strategy(
                strategy_objective,
                {
                    "min_engagement_rate": 0.03,
                    "min_comment_count": 3,
                    "limit": strategy_objective.target_audience_size
                }
            )
            
            state["content_plan"] = content_plan
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=True,
                data=content_plan,
                message=f"成功制定内容策略，包含{len(content_plan.target_users)}个目标用户",
                llm_analysis=f"AI优化策略：基于{len(content_plan.target_users)}个用户画像制定个性化内容策略",
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            logger.info(f"✅ 策略规划完成，识别{len(content_plan.target_users)}个目标用户")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 策略规划失败: {e}")
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=False,
                data=None,
                message=f"策略规划失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
        
        return state
    
    async def _user_analysis(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """用户分析阶段"""
        logger.info("👥 执行用户分析阶段")
        
        start_time = datetime.now()
        state["current_task"] = "user_analysis"
        
        try:
            content_plan = state["content_plan"]
            target_users = content_plan.target_users
            
            # 增强用户洞察
            enhanced_users = []
            for user in target_users:
                # 使用增强版用户分析获取更深入的洞察
                user_insights = await self.user_analyst.get_user_insights(user.user_id)
                enhanced_users.append(user_insights)
            
            state["target_users"] = enhanced_users
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="EnhancedUserAnalystAgent",
                success=True,
                data=enhanced_users,
                message=f"成功分析{len(enhanced_users)}个高价值用户",
                llm_analysis=f"AI洞察：识别用户行为模式和内容偏好",
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            logger.info(f"✅ 用户分析完成，分析{len(enhanced_users)}个用户")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 用户分析失败: {e}")
            result = EnhancedAgentResult(
                agent_name="EnhancedUserAnalystAgent",
                success=False,
                data=None,
                message=f"用户分析失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
        
        return state
    
    async def _content_generation(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """内容生成阶段"""
        logger.info("✍️ 执行内容生成阶段")
        
        start_time = datetime.now()
        state["current_task"] = "content_generation"
        
        try:
            target_users = state["target_users"]
            content_plan = state["content_plan"]
            
            # 为每个用户生成个性化内容
            content_requests = []
            for user in target_users:
                request = ContentGenerationRequest(
                    user_profile=asdict(user),
                    content_type="creative",
                    topic="个性化UGC内容",
                    platform="xhs",
                    requirements={
                        "tone": "friendly",
                        "key_points": ["个性化", "高价值", "社区互动"]
                    },
                    brand_guidelines={"voice": "authentic", "style": "casual"}
                )
                content_requests.append(request)
            
            # 批量生成内容
            generated_content = await self.content_generator.generate_content_batch(content_requests)
            
            state["generated_content"] = generated_content
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="ContentGeneratorAgent",
                success=True,
                data=generated_content,
                message=f"成功生成{len(generated_content)}个个性化内容",
                llm_analysis=f"AI创意：为{len(target_users)}个用户生成个性化内容",
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            logger.info(f"✅ 内容生成完成，生成{len(generated_content)}个内容")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 内容生成失败: {e}")
            result = EnhancedAgentResult(
                agent_name="ContentGeneratorAgent",
                success=False,
                data=None,
                message=f"内容生成失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
        
        return state
    
    async def _strategy_execution(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """策略执行阶段"""
        logger.info("🎯 执行策略执行阶段")
        
        start_time = datetime.now()
        state["current_task"] = "strategy_execution"
        
        try:
            content_plan = state["content_plan"]
            generated_content = state["generated_content"]
            
            # 执行内容计划
            execution_result = await self.strategy_coordinator.execute_content_plan(content_plan)
            
            # 获取执行指标
            actual_metrics = execution_result.actual_metrics
            success_indicators = execution_result.success_indicators
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=True,
                data={
                    "execution_result": execution_result,
                    "actual_metrics": actual_metrics,
                    "success_indicators": success_indicators
                },
                message=f"策略执行完成，成功率{sum(success_indicators.values())/len(success_indicators)*100:.1f}%",
                llm_analysis=f"AI优化：基于实际结果生成{len(execution_result.optimization_suggestions)}个优化建议",
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            logger.info("✅ 策略执行完成")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 策略执行失败: {e}")
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=False,
                data=None,
                message=f"策略执行失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
        
        return state
    
    async def _finalize_workflow(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """工作流完成阶段"""
        logger.info("📊 生成最终执行报告")
        
        state["current_task"] = "workflow_finalization"
        
        # 统计结果
        results = state["agent_results"]
        successful_agents = [r for r in results if r.success]
        failed_agents = [r for r in results if not r.success]
        
        # 计算性能指标
        total_execution_time = sum(r.execution_time for r in results)
        avg_execution_time = total_execution_time / len(results) if results else 0
        
        final_report = f"""
🎉 增强版Multi-Agent工作流执行完成！

📈 执行统计:
✅ 成功的Agent: {len(successful_agents)}
❌ 失败的Agent: {len(failed_agents)}
⏱️  总执行时间: {total_execution_time:.2f}秒
⏱️  平均执行时间: {avg_execution_time:.2f}秒

🎯 工作流成果:
"""
        
        # 添加具体成果
        if state.get("content_plan"):
            plan = state["content_plan"]
            final_report += f"📋 内容计划: 针对{len(plan.target_users)}个用户制定策略\n"
        
        if state.get("generated_content"):
            content = state["generated_content"]
            final_report += f"✍️  生成内容: {len(content)}个个性化内容\n"
        
        if state.get("target_users"):
            users = state["target_users"]
            final_report += f"👥 目标用户: 分析{len(users)}个高价值用户\n"
        
        # 添加Agent详细结果
        final_report += "\n📊 Agent执行详情:\n"
        for result in results:
            status = "✅" if result.success else "❌"
            final_report += f"{status} {result.agent_name}: {result.message}\n"
            if result.llm_analysis:
                final_report += f"   💡 AI洞察: {result.llm_analysis[:100]}...\n"
        
        state["messages"].append(AIMessage(content=final_report))
        
        logger.info("🎉 增强版Multi-Agent工作流完成")
        return state
    
    async def execute_complete_workflow(
        self, 
        initial_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行完整的增强版Multi-Agent工作流"""
        
        if not self.graph:
            raise ValueError("工作流图未初始化")
        
        # 初始化状态
        initial_state = EnhancedMultiAgentState(
            messages=[],
            current_task="",
            strategy_objective=None,
            content_plan=None,
            target_users=[],
            generated_content=[],
            agent_results=[],
            llm_insights={},
            execution_context={},
            preferred_model=self.preferred_provider.value if self.preferred_provider else None
        )
        
        # 自定义策略目标
        if initial_input and "strategy_objective" in initial_input:
            strategy_data = initial_input["strategy_objective"]
            initial_state["strategy_objective"] = StrategyObjective(
                objective_type=StrategyType(strategy_data.get("type", "engagement")),
                target_metrics=strategy_data.get("metrics", {"engagement_rate": 0.05}),
                timeline_days=strategy_data.get("timeline", 7),
                budget_limit=strategy_data.get("budget", 1000.0),
                target_audience_size=strategy_data.get("audience_size", 30)
            )
        
        try:
            logger.info("🚀 开始执行增强版Multi-Agent工作流")
            final_state = await self.graph.ainvoke(initial_state)
            
            # 整理返回结果
            return {
                "success": True,
                "workflow_completed": True,
                "final_state": final_state,
                "agent_results": final_state.get("agent_results", []),
                "content_plan": final_state.get("content_plan"),
                "target_users": final_state.get("target_users", []),
                "generated_content": final_state.get("generated_content", []),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "execution_summary": self._generate_execution_summary(final_state),
                "performance_metrics": self._generate_performance_metrics(final_state)
            }
            
        except Exception as e:
            logger.error(f"❌ 增强版Multi-Agent工作流执行失败: {e}")
            return {
                "success": False,
                "workflow_completed": False,
                "error": str(e),
                "execution_summary": f"工作流执行失败: {str(e)}"
            }
    
    def _generate_execution_summary(self, final_state: EnhancedMultiAgentState) -> str:
        """生成执行摘要"""
        results = final_state.get("agent_results", [])
        successful = len([r for r in results if r.success])
        total = len(results)
        
        summary = f"增强版Multi-Agent工作流完成：{successful}/{total} 个Agent成功执行"
        
        if final_state.get("content_plan"):
            plan = final_state["content_plan"]
            summary += f"，制定{len(plan.target_users)}个用户的内容策略"
        
        if final_state.get("generated_content"):
            content = final_state["generated_content"]
            summary += f"，生成{len(content)}个个性化内容"
        
        return summary
    
    def _generate_performance_metrics(self, final_state: EnhancedMultiAgentState) -> Dict[str, Any]:
        """生成性能指标"""
        results = final_state.get("agent_results", [])
        
        return {
            "total_agents": len(results),
            "successful_agents": len([r for r in results if r.success]),
            "failed_agents": len([r for r in results if not r.success]),
            "target_users": len(final_state.get("target_users", [])),
            "generated_content": len(final_state.get("generated_content", [])),
            "total_execution_time": sum(r.execution_time for r in results)
        }


# 使用示例和测试函数
async def test_enhanced_multi_agent_workflow():
    """测试增强版Multi-Agent工作流"""
    
    workflow = EnhancedMultiAgentWorkflow(preferred_model_provider=ModelProvider.OPENROUTER)
    
    # 执行工作流
    result = await workflow.execute_complete_workflow({
        "strategy_objective": {
            "type": "engagement",
            "metrics": {"engagement_rate": 0.05, "reach": 5000},
            "timeline": 7,
            "budget": 500,
            "audience_size": 20
        }
    })
    
    return result


if __name__ == "__main__":
    # 简单测试
    import asyncio
    result = asyncio.run(test_enhanced_multi_agent_workflow())
    print("增强版Multi-Agent工作流测试结果:", result.get("execution_summary", "执行失败"))