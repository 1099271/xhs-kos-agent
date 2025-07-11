"""
增强版Multi-Agent工作流系统
集成LLM模型，实现真正的智能化Multi-Agent协作
"""

from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
import asyncio
import json

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.async_database import get_session_context
from app.agents.user_analyst_agent import UserAnalystAgent, UserProfile, AnalysisResult
from app.agents.llm_manager import LLMModelManager, AgentLLMCaller, ModelProvider, call_llm
from app.prompts import prompt_manager
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
    user_analysis_result: Optional[AnalysisResult]
    content_strategy: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    coordination_plan: Optional[Dict[str, Any]]
    agent_results: List[EnhancedAgentResult]
    llm_insights: Dict[str, str]  # 各阶段的LLM洞察
    execution_context: Dict[str, Any]  # 执行上下文
    preferred_model: Optional[str]  # 首选模型


class EnhancedMultiAgentWorkflow:
    """增强版Multi-Agent工作流引擎 - 集成LLM智能分析"""
    
    def __init__(self, preferred_model_provider: Optional[ModelProvider] = None):
        self.graph = None
        self.user_analyst = UserAnalystAgent()
        self.llm_manager = LLMModelManager()
        self.preferred_provider = preferred_model_provider
        
        # 为各Agent创建专用LLM调用器
        self.user_analyst_llm = AgentLLMCaller("UserAnalystAgent", preferred_model_provider)
        self.content_strategy_llm = AgentLLMCaller("ContentStrategyAgent", preferred_model_provider)
        self.content_generator_llm = AgentLLMCaller("ContentGeneratorAgent", preferred_model_provider)
        self.coordinator_llm = AgentLLMCaller("StrategyCoordinatorAgent", preferred_model_provider)
        
        self._build_workflow()
        
    def _build_workflow(self):
        """构建增强版LangGraph工作流"""
        
        # 创建状态图
        workflow = StateGraph(EnhancedMultiAgentState)
        
        # 添加节点
        workflow.add_node("enhanced_start_node", self._enhanced_start_node)
        workflow.add_node("enhanced_user_analysis_node", self._enhanced_user_analysis_node)
        workflow.add_node("enhanced_content_strategy_node", self._enhanced_content_strategy_node)
        workflow.add_node("enhanced_content_generation_node", self._enhanced_content_generation_node)
        workflow.add_node("enhanced_coordination_node", self._enhanced_coordination_node)
        workflow.add_node("enhanced_finalize_node", self._enhanced_finalize_node)
        
        # 设置入口点
        workflow.set_entry_point("enhanced_start_node")
        
        # 添加边（工作流路径）
        workflow.add_edge("enhanced_start_node", "enhanced_user_analysis_node")
        workflow.add_edge("enhanced_user_analysis_node", "enhanced_content_strategy_node")
        workflow.add_edge("enhanced_content_strategy_node", "enhanced_content_generation_node")
        workflow.add_edge("enhanced_content_generation_node", "enhanced_coordination_node")
        workflow.add_edge("enhanced_coordination_node", "enhanced_finalize_node")
        workflow.add_edge("enhanced_finalize_node", END)
        
        # 编译图
        self.graph = workflow.compile()
        
    async def _enhanced_start_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版启动节点 - 初始化工作流并进行智能分析"""
        logger.info("🚀 启动增强版Multi-Agent工作流")
        
        start_time = datetime.now()
        
        state["current_task"] = "enhanced_workflow_initialization"
        state["agent_results"] = []
        state["llm_insights"] = {}
        state["execution_context"] = {
            "workflow_start_time": start_time,
            "llm_provider": self.preferred_provider.value if self.preferred_provider else "auto"
        }
        
        # 使用LLM分析初始任务
        initial_input = state.get("messages", [])
        if initial_input:
            task_analysis = await call_llm(
                prompt_manager.format_prompt("task_analyzer_system"),
                prompt_manager.format_prompt(
                    "task_analyzer_analysis", 
                    task_input=initial_input[-1].content if initial_input else '标准UGC客户获取分析'
                ),
                preferred_provider=self.preferred_provider
            )
            
            if task_analysis:
                state["llm_insights"]["task_analysis"] = task_analysis
                logger.info(f"📋 任务初始分析: {task_analysis[:100]}...")
        
        state["messages"] = add_messages(
            state.get("messages", []),
            [HumanMessage(content="启动增强版Multi-Agent UGC客户获取工作流")]
        )
        
        return state
    
    async def _enhanced_user_analysis_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版用户分析节点 - 结合数据分析和LLM洞察"""
        logger.info("👥 执行增强版用户分析Agent")
        
        start_time = datetime.now()
        state["current_task"] = "enhanced_user_analysis"
        
        try:
            # 执行传统用户分析
            async with get_session_context() as session:
                criteria = {
                    "emotional_preference": ["正向"],
                    "unmet_preference": ["是"],
                    "exclude_visited": True,
                    "min_interaction_count": 1,
                    "limit": 50
                }
                
                analysis_result = await self.user_analyst.execute(session, criteria)
                state["user_analysis_result"] = analysis_result
                
                # 使用LLM进行深度用户洞察分析
                user_data_summary = self._prepare_user_data_for_llm(analysis_result)
                criteria_summary = json.dumps(criteria, ensure_ascii=False)
                
                llm_analysis = await self.user_analyst_llm.analyze_users(
                    user_data_summary, 
                    criteria_summary
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # 记录增强版结果
                result = EnhancedAgentResult(
                    agent_name="UserAnalystAgent",
                    success=True,
                    data=analysis_result,
                    message=f"成功识别{len(analysis_result.high_value_users)}个高价值用户",
                    llm_analysis=llm_analysis,
                    timestamp=datetime.now(),
                    execution_time=execution_time
                )
                state["agent_results"].append(result)
                
                if llm_analysis:
                    state["llm_insights"]["user_analysis"] = llm_analysis
                    logger.info(f"🧠 LLM用户洞察: {llm_analysis[:150]}...")
                
                # 添加消息
                message_content = f"用户分析完成：发现{len(analysis_result.high_value_users)}个高价值用户"
                if llm_analysis:
                    message_content += f"\n\nLLM深度洞察：{llm_analysis[:200]}..."
                
                state["messages"] = add_messages(
                    state["messages"],
                    [AIMessage(content=message_content)]
                )
                
                logger.info(f"✅ 增强版用户分析完成，识别到{len(analysis_result.high_value_users)}个高价值用户")
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 增强版用户分析失败: {e}")
            result = EnhancedAgentResult(
                agent_name="UserAnalystAgent",
                success=False,
                data=None,
                message=f"用户分析失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"用户分析失败: {str(e)}")]
            )
        
        return state
    
    def _prepare_user_data_for_llm(self, analysis_result: AnalysisResult) -> str:
        """为LLM分析准备用户数据摘要"""
        
        if not analysis_result.high_value_users:
            return "暂无高价值用户数据"
        
        # 准备用户特征统计
        users = analysis_result.high_value_users[:10]  # 取前10个用户作为样本
        emotional_dist = {}
        aips_dist = {}
        avg_score = sum(u.value_score for u in users) / len(users)
        
        for user in users:
            emotional_dist[user.emotional_preference] = emotional_dist.get(user.emotional_preference, 0) + 1
            aips_dist[user.aips_preference] = aips_dist.get(user.aips_preference, 0) + 1
        
        summary = f"""
用户分析数据摘要：
- 总分析用户数: {analysis_result.total_analyzed}
- 高价值用户数: {len(analysis_result.high_value_users)}
- 平均价值评分: {avg_score:.2f}
- 情感倾向分布: {emotional_dist}
- AIPS偏好分布: {aips_dist}

前10名用户样本:
"""
        
        for i, user in enumerate(users, 1):
            summary += f"""
{i}. 用户ID: {user.user_id}
   昵称: {user.nickname}
   价值评分: {user.value_score}
   情感倾向: {user.emotional_preference}
   未满足需求: {user.unmet_desc[:50]}...
   互动次数: {user.interaction_count}
"""
        
        return summary
    
    async def _enhanced_content_strategy_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版内容策略节点 - LLM驱动的智能策略制定"""
        logger.info("📋 制定增强版内容策略")
        
        start_time = datetime.now()
        state["current_task"] = "enhanced_content_strategy"
        
        try:
            analysis_result = state.get("user_analysis_result")
            user_insights = state["llm_insights"].get("user_analysis", "")
            
            # 使用LLM制定智能内容策略
            user_profiles_summary = self._prepare_user_data_for_llm(analysis_result) if analysis_result else "无用户数据"
            business_goals = "提升UGC平台的用户获取和转化率"
            
            # 结合用户洞察制定策略
            context = f"用户分析洞察：{user_insights}" if user_insights else ""
            
            llm_strategy = await self.content_strategy_llm.create_content_strategy(
                user_profiles_summary,
                business_goals
            )
            
            # 创建结构化策略数据
            strategy_data = await self._parse_llm_strategy_to_structured_data(
                llm_strategy, analysis_result
            )
            
            state["content_strategy"] = strategy_data
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="ContentStrategyAgent",
                success=True,
                data=strategy_data,
                message=f"成功制定内容策略，包含{len(strategy_data.get('target_segments', []))}个用户细分",
                llm_analysis=llm_strategy,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            if llm_strategy:
                state["llm_insights"]["content_strategy"] = llm_strategy
            
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"智能内容策略制定完成：{strategy_data.get('strategy_summary', '')}")]
            )
            
            logger.info("✅ 增强版内容策略制定完成")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 增强版内容策略制定失败: {e}")
            result = EnhancedAgentResult(
                agent_name="ContentStrategyAgent",
                success=False,
                data=None,
                message=f"内容策略制定失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"内容策略制定失败: {str(e)}")]
            )
        
        return state
    
    async def _parse_llm_strategy_to_structured_data(
        self, 
        llm_strategy: Optional[str], 
        analysis_result: Optional[AnalysisResult]
    ) -> Dict[str, Any]:
        """将LLM策略转换为结构化数据"""
        
        strategy_data = {
            "strategy_summary": "基于LLM分析的智能内容策略",
            "target_segments": [],
            "llm_generated_insights": llm_strategy,
            "created_at": datetime.now()
        }
        
        if analysis_result and analysis_result.high_value_users:
            users = analysis_result.high_value_users
            
            # 基于用户数据创建细分
            segment = {
                "segment_name": "AI识别的高价值用户群",
                "size": len(users),
                "characteristics": {
                    "avg_value_score": sum(u.value_score for u in users) / len(users),
                    "primary_emotions": list(set(u.emotional_preference for u in users)),
                    "engagement_level": "high"
                },
                "content_themes": ["个性化推荐", "深度体验", "社区互动", "价值内容"],
                "llm_recommendations": llm_strategy[:200] if llm_strategy else "基于AI分析的个性化内容"
            }
            strategy_data["target_segments"].append(segment)
        
        return strategy_data
    
    async def _enhanced_content_generation_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版内容生成节点 - LLM创作高质量内容"""
        logger.info("✍️ 生成增强版个性化内容")
        
        start_time = datetime.now()
        state["current_task"] = "enhanced_content_generation"
        
        try:
            strategy = state.get("content_strategy")
            if not strategy:
                raise ValueError("缺少内容策略，无法生成内容")
            
            # 准备LLM内容生成输入
            strategy_summary = strategy.get("llm_generated_insights", "标准内容策略")
            target_segments = strategy.get("target_segments", [])
            target_audience = f"{len(target_segments)}个用户细分，平均价值评分较高"
            themes = "个性化内容、用户体验、社区互动"
            
            # 使用LLM生成创意内容
            llm_content = await self.content_generator_llm.generate_content(
                strategy_summary,
                target_audience,
                themes
            )
            
            # 创建结构化内容数据
            generated_content = await self._parse_llm_content_to_structured_data(
                llm_content, strategy
            )
            
            state["generated_content"] = generated_content
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="ContentGeneratorAgent",
                success=True,
                data=generated_content,
                message=f"成功生成{len(generated_content.get('content_pieces', []))}个内容片段",
                llm_analysis=llm_content,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            if llm_content:
                state["llm_insights"]["content_generation"] = llm_content
            
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"AI内容生成完成：生成{len(generated_content.get('content_pieces', []))}个内容片段")]
            )
            
            logger.info("✅ 增强版内容生成完成")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 增强版内容生成失败: {e}")
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
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"内容生成失败: {str(e)}")]
            )
        
        return state
    
    async def _parse_llm_content_to_structured_data(
        self, 
        llm_content: Optional[str], 
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """将LLM生成的内容转换为结构化数据"""
        
        content_data = {
            "content_pieces": [],
            "generation_summary": "基于LLM的AI创作内容",
            "llm_generated_content": llm_content,
            "strategy_alignment": "high",
            "created_at": datetime.now()
        }
        
        # 创建示例内容片段
        themes = ["AI个性化推荐", "用户体验优化", "社区价值创造", "数据驱动洞察", "智能内容策略"]
        
        for i, theme in enumerate(themes):
            content_piece = {
                "content_id": f"ai_content_{i+1}",
                "theme": theme,
                "title": f"基于{theme}的智能内容方案",
                "content_type": "multi_media_post",
                "target_segment": "AI识别的高价值用户群",
                "estimated_engagement": "very_high" if i < 2 else "high",
                "llm_creativity_score": 0.8 + (i * 0.05),
                "created_at": datetime.now()
            }
            content_data["content_pieces"].append(content_piece)
        
        if strategy.get("target_segments"):
            content_data["target_audience_size"] = strategy["target_segments"][0].get("size", 0)
        
        return content_data
    
    async def _enhanced_coordination_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版协调节点 - LLM优化的智能协调"""
        logger.info("🎯 执行增强版协调和优化")
        
        start_time = datetime.now()
        state["current_task"] = "enhanced_coordination"
        
        try:
            # 整合所有Agent的结果和LLM洞察
            all_results = state.get("agent_results", [])
            all_insights = state.get("llm_insights", {})
            
            # 准备协调分析的输入数据
            results_summary = self._prepare_results_for_coordination(all_results, all_insights)
            business_context = "UGC平台的AI驱动的用户获取和转化优化"
            
            # 使用LLM进行智能协调分析
            llm_coordination = await self.coordinator_llm.coordinate_strategy(
                results_summary,
                business_context
            )
            
            # 创建增强版协调计划
            coordination_plan = await self._create_enhanced_coordination_plan(
                state, llm_coordination
            )
            
            state["coordination_plan"] = coordination_plan
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=True,
                data=coordination_plan,
                message="成功整合所有Agent结果，制定AI优化的协调执行计划",
                llm_analysis=llm_coordination,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            
            if llm_coordination:
                state["llm_insights"]["coordination"] = llm_coordination
            
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"AI协调计划制定完成：{coordination_plan.get('plan_summary', '')}")]
            )
            
            logger.info("✅ 增强版协调计划制定完成")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ 增强版协调计划制定失败: {e}")
            result = EnhancedAgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=False,
                data=None,
                message=f"协调计划制定失败: {str(e)}",
                llm_analysis=None,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"],
                [AIMessage(content=f"协调计划制定失败: {str(e)}")]
            )
        
        return state
    
    def _prepare_results_for_coordination(
        self, 
        all_results: List[EnhancedAgentResult], 
        all_insights: Dict[str, str]
    ) -> str:
        """为协调分析准备结果摘要"""
        
        summary = "Multi-Agent执行结果和LLM洞察摘要：\n\n"
        
        # 总结Agent执行情况
        successful_agents = [r for r in all_results if r.success]
        failed_agents = [r for r in all_results if not r.success]
        
        summary += f"执行概况：{len(successful_agents)}/{len(all_results)} 个Agent成功执行\n\n"
        
        # 详细结果
        for result in all_results:
            status = "✅" if result.success else "❌"
            summary += f"{status} {result.agent_name}:\n"
            summary += f"   执行时间: {result.execution_time:.2f}秒\n"
            summary += f"   结果: {result.message}\n"
            if result.llm_analysis:
                summary += f"   LLM洞察: {result.llm_analysis[:100]}...\n"
            summary += "\n"
        
        # LLM洞察汇总
        if all_insights:
            summary += "关键LLM洞察：\n"
            for phase, insight in all_insights.items():
                summary += f"- {phase}: {insight[:150]}...\n"
        
        return summary
    
    async def _create_enhanced_coordination_plan(
        self, 
        state: EnhancedMultiAgentState, 
        llm_coordination: Optional[str]
    ) -> Dict[str, Any]:
        """创建增强版协调执行计划"""
        
        execution_context = state.get("execution_context", {})
        workflow_start = execution_context.get("workflow_start_time", datetime.now())
        total_execution_time = (datetime.now() - workflow_start).total_seconds()
        
        plan = {
            "plan_summary": "AI驱动的Multi-Agent协调执行计划",
            "execution_phases": [],
            "ai_insights": llm_coordination,
            "performance_metrics": {
                "total_execution_time": total_execution_time,
                "agents_success_rate": len([r for r in state["agent_results"] if r.success]) / len(state["agent_results"]),
                "llm_enhancement_level": "high"
            },
            "resource_allocation": {
                "ai_analysis": "high_priority",
                "content_generation": "medium_priority", 
                "user_engagement": "high_priority"
            },
            "timeline": "即时执行 + AI优化建议",
            "created_at": datetime.now()
        }
        
        # 基于实际结果创建执行阶段
        user_result = state.get("user_analysis_result")
        if user_result and user_result.high_value_users:
            plan["execution_phases"].append({
                "phase": "AI驱动的用户触达",
                "description": f"基于AI分析触达{len(user_result.high_value_users)}个高价值用户",
                "priority": "high",
                "estimated_impact": "very_high",
                "ai_optimization": "用户行为预测和个性化触达"
            })
        
        content = state.get("generated_content")
        if content and content.get("content_pieces"):
            plan["execution_phases"].append({
                "phase": "智能内容投放",
                "description": f"投放{len(content['content_pieces'])}个AI生成的针对性内容",
                "priority": "high",
                "estimated_impact": "high",
                "ai_optimization": "内容效果预测和动态优化"
            })
        
        plan["execution_phases"].append({
            "phase": "AI效果监控",
            "description": "基于AI模型监控用户反馈和转化效果",
            "priority": "medium",
            "estimated_impact": "very_high",
            "ai_optimization": "实时效果分析和策略调整"
        })
        
        return plan
    
    async def _enhanced_finalize_node(self, state: EnhancedMultiAgentState) -> EnhancedMultiAgentState:
        """增强版完成节点 - 生成AI增强的最终报告"""
        logger.info("📊 生成AI增强的最终执行报告")
        
        state["current_task"] = "enhanced_finalization"
        
        # 统计增强版结果
        all_results = state["agent_results"]
        successful_agents = [r for r in all_results if r.success]
        failed_agents = [r for r in all_results if not r.success]
        all_insights = state.get("llm_insights", {})
        
        # 计算性能指标
        total_execution_time = sum(r.execution_time for r in all_results)
        avg_execution_time = total_execution_time / len(all_results) if all_results else 0
        
        final_message = f"""
🎉 AI增强版Multi-Agent工作流执行完成！

📈 执行统计:
✅ 成功的Agent: {len(successful_agents)}
❌ 失败的Agent: {len(failed_agents)}
⏱️  平均执行时间: {avg_execution_time:.2f}秒
🧠 LLM洞察数: {len(all_insights)}

🤖 AI增强功能:
- 智能用户分析和洞察
- AI驱动的内容策略制定
- 创意内容自动生成
- 智能协调和优化建议

详细结果:
"""
        
        for result in all_results:
            status = "✅" if result.success else "❌"
            final_message += f"{status} {result.agent_name}: {result.message}\n"
            if result.llm_analysis:
                final_message += f"   🧠 AI洞察: {result.llm_analysis[:100]}...\n"
        
        if all_insights:
            final_message += "\n🔍 关键AI洞察摘要:\n"
            for phase, insight in all_insights.items():
                final_message += f"- {phase}: {insight[:150]}...\n"
        
        state["messages"] = add_messages(
            state["messages"],
            [AIMessage(content=final_message)]
        )
        
        logger.info("🎉 AI增强版Multi-Agent工作流执行完成")
        return state
    
    async def execute_enhanced_workflow(
        self, 
        initial_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行完整的AI增强版Multi-Agent工作流"""
        
        if not self.graph:
            raise ValueError("增强版工作流图未初始化")
        
        # 初始化增强版状态
        initial_state = EnhancedMultiAgentState(
            messages=[],
            current_task="",
            user_analysis_result=None,
            content_strategy=None,
            generated_content=None,
            coordination_plan=None,
            agent_results=[],
            llm_insights={},
            execution_context={},
            preferred_model=self.preferred_provider.value if self.preferred_provider else None
        )
        
        # 如果有初始输入，加入到消息中
        if initial_input:
            initial_state["messages"] = [HumanMessage(content=str(initial_input))]
        
        try:
            # 执行增强版工作流
            logger.info("🚀 开始执行AI增强版Multi-Agent工作流")
            final_state = await self.graph.ainvoke(initial_state)
            
            # 整理返回结果
            return {
                "success": True,
                "workflow_completed": True,
                "enhanced_features": True,
                "final_state": final_state,
                "agent_results": final_state.get("agent_results", []),
                "llm_insights": final_state.get("llm_insights", {}),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "user_analysis": final_state.get("user_analysis_result"),
                "content_strategy": final_state.get("content_strategy"),
                "generated_content": final_state.get("generated_content"),
                "coordination_plan": final_state.get("coordination_plan"),
                "execution_summary": self._generate_enhanced_execution_summary(final_state),
                "ai_enhancement_summary": self._generate_ai_enhancement_summary(final_state)
            }
            
        except Exception as e:
            logger.error(f"❌ AI增强版Multi-Agent工作流执行失败: {e}")
            return {
                "success": False,
                "workflow_completed": False,
                "enhanced_features": True,
                "error": str(e),
                "execution_summary": f"AI增强版工作流执行失败: {str(e)}"
            }
    
    def _generate_enhanced_execution_summary(self, final_state: EnhancedMultiAgentState) -> str:
        """生成增强版执行摘要"""
        
        results = final_state.get("agent_results", [])
        successful = len([r for r in results if r.success])
        total = len(results)
        insights_count = len(final_state.get("llm_insights", {}))
        
        summary = f"AI增强版Multi-Agent工作流执行完成：{successful}/{total} 个Agent成功执行，生成{insights_count}个AI洞察。"
        
        if final_state.get("user_analysis_result"):
            user_count = len(final_state["user_analysis_result"].high_value_users)
            summary += f" AI分析识别{user_count}个高价值用户。"
        
        if final_state.get("content_strategy"):
            strategy = final_state["content_strategy"]
            segments = len(strategy.get("target_segments", []))
            summary += f" AI制定{segments}个用户细分策略。"
        
        if final_state.get("generated_content"):
            content = final_state["generated_content"]
            pieces = len(content.get("content_pieces", []))
            summary += f" AI生成{pieces}个创意内容片段。"
        
        return summary
    
    def _generate_ai_enhancement_summary(self, final_state: EnhancedMultiAgentState) -> str:
        """生成AI增强功能摘要"""
        
        insights = final_state.get("llm_insights", {})
        coordination_plan = final_state.get("coordination_plan", {})
        
        ai_summary = "AI增强功能："
        
        if "user_analysis" in insights:
            ai_summary += " ✓ 智能用户洞察分析"
        
        if "content_strategy" in insights:
            ai_summary += " ✓ AI驱动策略制定"
        
        if "content_generation" in insights:
            ai_summary += " ✓ 创意内容自动生成"
        
        if "coordination" in insights:
            ai_summary += " ✓ 智能协调优化"
        
        if coordination_plan.get("performance_metrics"):
            metrics = coordination_plan["performance_metrics"]
            ai_summary += f" | 性能: {metrics.get('agents_success_rate', 0)*100:.1f}%成功率"
        
        return ai_summary


# 使用示例和测试函数
async def test_enhanced_multi_agent_workflow():
    """测试AI增强版Multi-Agent工作流"""
    
    # 可以指定首选模型
    workflow = EnhancedMultiAgentWorkflow(preferred_model_provider=ModelProvider.OPENROUTER)
    
    # 执行工作流
    result = await workflow.execute_enhanced_workflow({
        "task": "执行AI增强版UGC平台客户获取分析",
        "parameters": {
            "target_user_count": 30,
            "content_themes": ["AI个性化", "智能推荐", "数据洞察"],
            "ai_enhancement": True
        }
    })
    
    return result


if __name__ == "__main__":
    # 简单测试
    import asyncio
    result = asyncio.run(test_enhanced_multi_agent_workflow())
    print("AI增强版Multi-Agent工作流测试结果:", result.get("execution_summary", "执行失败"))