"""
Multi-Agent工作流系统
基于LangGraph实现的多Agent协作框架，用于UGC内容平台客户获取
"""

from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.async_database import get_session_context
from app.agents.user_analyst_agent import UserAnalystAgent, UserProfile, AnalysisResult
from app.utils.logger import app_logger as logger


@dataclass
class AgentResult:
    """Agent执行结果"""

    agent_name: str
    success: bool
    data: Any
    message: str
    timestamp: datetime


class MultiAgentState(TypedDict):
    """Multi-Agent工作流状态"""

    messages: List[BaseMessage]
    current_task: str
    user_analysis_result: Optional[AnalysisResult]
    content_strategy: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    coordination_plan: Optional[Dict[str, Any]]
    agent_results: List[AgentResult]
    session_context: Optional[AsyncSession]


class MultiAgentWorkflow:
    """Multi-Agent工作流引擎"""

    def __init__(self):
        self.graph = None
        self.user_analyst = UserAnalystAgent()
        self._build_workflow()

    def _build_workflow(self):
        """构建LangGraph工作流"""

        # 创建状态图
        workflow = StateGraph(MultiAgentState)

        # 添加节点
        workflow.add_node("start_node", self._start_node)
        workflow.add_node("user_analysis_node", self._user_analysis_node)
        workflow.add_node("content_strategy_node", self._content_strategy_node)
        workflow.add_node("content_generation_node", self._content_generation_node)
        workflow.add_node("coordination_node", self._coordination_node)
        workflow.add_node("finalize_node", self._finalize_node)

        # 设置入口点
        workflow.set_entry_point("start_node")

        # 添加边（工作流路径）
        workflow.add_edge("start_node", "user_analysis_node")
        workflow.add_edge("user_analysis_node", "content_strategy_node")
        workflow.add_edge("content_strategy_node", "content_generation_node")
        workflow.add_edge("content_generation_node", "coordination_node")
        workflow.add_edge("coordination_node", "finalize_node")
        workflow.add_edge("finalize_node", END)

        # 编译图
        self.graph = workflow.compile()

    async def _start_node(self, state: MultiAgentState) -> MultiAgentState:
        """启动节点 - 初始化工作流"""
        logger.info("🚀 启动Multi-Agent工作流")

        state["current_task"] = "workflow_initialization"
        state["agent_results"] = []
        state["messages"] = add_messages(
            state.get("messages", []),
            [HumanMessage(content="启动Multi-Agent UGC客户获取工作流")],
        )

        # 初始化数据库会话
        if not state.get("session_context"):
            # 注意：这里我们不能直接使用async with，因为状态需要在节点间传递
            # 我们将在每个需要数据库的节点中临时创建会话
            pass

        return state

    async def _user_analysis_node(self, state: MultiAgentState) -> MultiAgentState:
        """用户分析节点 - UserAnalystAgent执行用户分析"""
        logger.info("👥 执行用户分析Agent")

        state["current_task"] = "user_analysis"

        try:
            # 使用临时数据库会话
            async with get_session_context() as session:
                # 执行用户分析
                criteria = {
                    "emotional_preference": ["正向"],
                    "unmet_preference": ["是"],
                    "exclude_visited": True,
                    "min_interaction_count": 1,
                    "limit": 50,
                }

                analysis_result = await self.user_analyst.execute(session, criteria)
                state["user_analysis_result"] = analysis_result

                # 记录结果
                result = AgentResult(
                    agent_name="UserAnalystAgent",
                    success=True,
                    data=analysis_result,
                    message=f"成功识别{len(analysis_result.high_value_users)}个高价值用户",
                    timestamp=datetime.now(),
                )
                state["agent_results"].append(result)

                # 添加消息
                state["messages"] = add_messages(
                    state["messages"],
                    [
                        AIMessage(
                            content=f"用户分析完成：发现{len(analysis_result.high_value_users)}个高价值用户"
                        )
                    ],
                )

                logger.info(
                    f"✅ 用户分析完成，识别到{len(analysis_result.high_value_users)}个高价值用户"
                )

        except Exception as e:
            logger.error(f"❌ 用户分析失败: {e}")
            result = AgentResult(
                agent_name="UserAnalystAgent",
                success=False,
                data=None,
                message=f"用户分析失败: {str(e)}",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"], [AIMessage(content=f"用户分析失败: {str(e)}")]
            )

        return state

    async def _content_strategy_node(self, state: MultiAgentState) -> MultiAgentState:
        """内容策略节点 - 基于用户分析制定内容策略"""
        logger.info("📋 制定内容策略")

        state["current_task"] = "content_strategy"

        try:
            analysis_result = state.get("user_analysis_result")
            if not analysis_result or not analysis_result.high_value_users:
                raise ValueError("缺少用户分析结果，无法制定内容策略")

            # 分析用户特征，制定内容策略
            strategy = await self._analyze_user_characteristics(
                analysis_result.high_value_users
            )
            state["content_strategy"] = strategy

            result = AgentResult(
                agent_name="ContentStrategyAgent",
                success=True,
                data=strategy,
                message=f"成功制定内容策略，包含{len(strategy.get('target_segments', []))}个用户细分",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)

            state["messages"] = add_messages(
                state["messages"],
                [
                    AIMessage(
                        content=f"内容策略制定完成：{strategy.get('strategy_summary', '')}"
                    )
                ],
            )

            logger.info("✅ 内容策略制定完成")

        except Exception as e:
            logger.error(f"❌ 内容策略制定失败: {e}")
            result = AgentResult(
                agent_name="ContentStrategyAgent",
                success=False,
                data=None,
                message=f"内容策略制定失败: {str(e)}",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"], [AIMessage(content=f"内容策略制定失败: {str(e)}")]
            )

        return state

    async def _content_generation_node(self, state: MultiAgentState) -> MultiAgentState:
        """内容生成节点 - 基于策略生成个性化内容"""
        logger.info("✍️ 生成个性化内容")

        state["current_task"] = "content_generation"

        try:
            strategy = state.get("content_strategy")
            if not strategy:
                raise ValueError("缺少内容策略，无法生成内容")

            # 基于策略生成内容
            generated_content = await self._generate_targeted_content(strategy)
            state["generated_content"] = generated_content

            result = AgentResult(
                agent_name="ContentGeneratorAgent",
                success=True,
                data=generated_content,
                message=f"成功生成{len(generated_content.get('content_pieces', []))}个内容片段",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)

            state["messages"] = add_messages(
                state["messages"],
                [
                    AIMessage(
                        content=f"内容生成完成：生成{len(generated_content.get('content_pieces', []))}个内容片段"
                    )
                ],
            )

            logger.info("✅ 内容生成完成")

        except Exception as e:
            logger.error(f"❌ 内容生成失败: {e}")
            result = AgentResult(
                agent_name="ContentGeneratorAgent",
                success=False,
                data=None,
                message=f"内容生成失败: {str(e)}",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"], [AIMessage(content=f"内容生成失败: {str(e)}")]
            )

        return state

    async def _coordination_node(self, state: MultiAgentState) -> MultiAgentState:
        """协调节点 - 整合所有Agent结果，制定执行计划"""
        logger.info("🎯 协调和优化执行计划")

        state["current_task"] = "coordination"

        try:
            # 整合所有Agent的结果
            user_result = state.get("user_analysis_result")
            strategy = state.get("content_strategy")
            content = state.get("generated_content")

            coordination_plan = await self._create_coordination_plan(
                user_result, strategy, content
            )
            state["coordination_plan"] = coordination_plan

            result = AgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=True,
                data=coordination_plan,
                message="成功整合所有Agent结果，制定协调执行计划",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)

            state["messages"] = add_messages(
                state["messages"],
                [
                    AIMessage(
                        content=f"协调计划制定完成：{coordination_plan.get('plan_summary', '')}"
                    )
                ],
            )

            logger.info("✅ 协调计划制定完成")

        except Exception as e:
            logger.error(f"❌ 协调计划制定失败: {e}")
            result = AgentResult(
                agent_name="StrategyCoordinatorAgent",
                success=False,
                data=None,
                message=f"协调计划制定失败: {str(e)}",
                timestamp=datetime.now(),
            )
            state["agent_results"].append(result)
            state["messages"] = add_messages(
                state["messages"], [AIMessage(content=f"协调计划制定失败: {str(e)}")]
            )

        return state

    async def _finalize_node(self, state: MultiAgentState) -> MultiAgentState:
        """完成节点 - 生成最终报告"""
        logger.info("📊 生成最终执行报告")

        state["current_task"] = "finalization"

        # 统计成功/失败的Agent
        successful_agents = [r for r in state["agent_results"] if r.success]
        failed_agents = [r for r in state["agent_results"] if not r.success]

        final_message = f"""
🎉 Multi-Agent工作流执行完成！

✅ 成功的Agent: {len(successful_agents)}
❌ 失败的Agent: {len(failed_agents)}

详细结果:
"""

        for result in state["agent_results"]:
            status = "✅" if result.success else "❌"
            final_message += f"{status} {result.agent_name}: {result.message}\n"

        state["messages"] = add_messages(
            state["messages"], [AIMessage(content=final_message)]
        )

        logger.info("🎉 Multi-Agent工作流执行完成")
        return state

    async def _analyze_user_characteristics(
        self, users: List[UserProfile]
    ) -> Dict[str, Any]:
        """分析用户特征，制定内容策略"""

        if not users:
            return {
                "strategy_summary": "无用户数据，无法制定策略",
                "target_segments": [],
            }

        # 分析用户群体特征
        emotional_dist = {}
        aips_dist = {}
        unmet_needs = []

        for user in users:
            # 情感分布
            emotional_dist[user.emotional_preference] = (
                emotional_dist.get(user.emotional_preference, 0) + 1
            )
            # AIPS分布
            aips_dist[user.aips_preference] = aips_dist.get(user.aips_preference, 0) + 1
            # 收集未满足需求
            if user.unmet_desc:
                unmet_needs.append(user.unmet_desc)

        # 识别主要用户群体
        primary_emotion = (
            max(emotional_dist, key=emotional_dist.get) if emotional_dist else "未知"
        )
        primary_aips = max(aips_dist, key=aips_dist.get) if aips_dist else "未知"

        # 制定针对性策略
        strategy = {
            "strategy_summary": f"针对{primary_emotion}情感倾向用户，重点关注{primary_aips}需求",
            "target_segments": [
                {
                    "segment_name": "高价值潜在客户",
                    "size": len(users),
                    "characteristics": {
                        "emotional_preference": primary_emotion,
                        "aips_preference": primary_aips,
                        "avg_value_score": sum(u.value_score for u in users)
                        / len(users),
                    },
                    "content_themes": self._suggest_content_themes(
                        primary_emotion, primary_aips
                    ),
                }
            ],
            "unmet_needs_analysis": unmet_needs[:10],  # 取前10个需求作为参考
            "user_count": len(users),
            "created_at": datetime.now(),
        }

        return strategy

    def _suggest_content_themes(self, emotion: str, aips: str) -> List[str]:
        """根据用户特征建议内容主题"""

        themes = []

        # 基于情感倾向的主题
        if emotion == "正向":
            themes.extend(["成功案例分享", "激励性内容", "正能量故事"])
        elif emotion == "中性":
            themes.extend(["实用指南", "客观分析", "知识科普"])

        # 基于AIPS偏好的主题
        if "注意" in aips:
            themes.extend(["引人注目的标题", "热点话题", "新颖观点"])
        elif "兴趣" in aips:
            themes.extend(["深度内容", "专业见解", "个人兴趣"])
        elif "搜索" in aips:
            themes.extend(["问题解答", "教程指南", "解决方案"])
        elif "行动" in aips:
            themes.extend(["行动指南", "实操建议", "立即可用的建议"])

        return themes[:5]  # 返回前5个主题

    async def _generate_targeted_content(
        self, strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """基于策略生成针对性内容"""

        target_segments = strategy.get("target_segments", [])
        if not target_segments:
            return {
                "content_pieces": [],
                "generation_summary": "无目标用户群体，无法生成内容",
            }

        primary_segment = target_segments[0]
        themes = primary_segment.get("content_themes", [])

        # 模拟内容生成（实际应用中会调用LLM）
        content_pieces = []
        for i, theme in enumerate(themes):
            content_pieces.append(
                {
                    "content_id": f"content_{i+1}",
                    "theme": theme,
                    "title": f"基于{theme}的内容标题",
                    "content_type": "social_media_post",
                    "target_segment": primary_segment["segment_name"],
                    "estimated_engagement": "high" if i < 2 else "medium",
                    "created_at": datetime.now(),
                }
            )

        return {
            "content_pieces": content_pieces,
            "generation_summary": f"基于{len(themes)}个主题生成{len(content_pieces)}个内容片段",
            "target_audience_size": primary_segment["size"],
            "strategy_alignment": "high",
        }

    async def _create_coordination_plan(
        self,
        user_result: Optional[AnalysisResult],
        strategy: Optional[Dict[str, Any]],
        content: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """创建协调执行计划"""

        plan = {
            "plan_summary": "Multi-Agent协调执行计划",
            "execution_phases": [],
            "resource_allocation": {},
            "success_metrics": {},
            "timeline": "即时执行",
            "created_at": datetime.now(),
        }

        # 阶段1：用户触达
        if user_result and user_result.high_value_users:
            plan["execution_phases"].append(
                {
                    "phase": "用户触达",
                    "description": f"触达{len(user_result.high_value_users)}个高价值用户",
                    "priority": "high",
                    "estimated_impact": "high",
                }
            )

        # 阶段2：内容投放
        if content and content.get("content_pieces"):
            plan["execution_phases"].append(
                {
                    "phase": "内容投放",
                    "description": f"投放{len(content['content_pieces'])}个针对性内容",
                    "priority": "high",
                    "estimated_impact": "medium",
                }
            )

        # 阶段3：效果监控
        plan["execution_phases"].append(
            {
                "phase": "效果监控",
                "description": "监控用户反馈和转化效果",
                "priority": "medium",
                "estimated_impact": "high",
            }
        )

        return plan

    async def execute_workflow(
        self, initial_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行完整的Multi-Agent工作流"""

        if not self.graph:
            raise ValueError("工作流图未初始化")

        # 初始化状态
        initial_state = MultiAgentState(
            messages=[],
            current_task="",
            user_analysis_result=None,
            content_strategy=None,
            generated_content=None,
            coordination_plan=None,
            agent_results=[],
            session_context=None,
        )

        # 如果有初始输入，加入到消息中
        if initial_input:
            initial_state["messages"] = [HumanMessage(content=str(initial_input))]

        try:
            # 执行工作流
            logger.info("🚀 开始执行Multi-Agent工作流")
            final_state = await self.graph.ainvoke(initial_state)

            # 整理返回结果
            return {
                "success": True,
                "workflow_completed": True,
                "final_state": final_state,
                "agent_results": final_state.get("agent_results", []),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "user_analysis": final_state.get("user_analysis_result"),
                "content_strategy": final_state.get("content_strategy"),
                "generated_content": final_state.get("generated_content"),
                "coordination_plan": final_state.get("coordination_plan"),
                "execution_summary": self._generate_execution_summary(final_state),
            }

        except Exception as e:
            logger.error(f"❌ Multi-Agent工作流执行失败: {e}")
            return {
                "success": False,
                "workflow_completed": False,
                "error": str(e),
                "execution_summary": f"工作流执行失败: {str(e)}",
            }

    def _generate_execution_summary(self, final_state: MultiAgentState) -> str:
        """生成执行摘要"""

        results = final_state.get("agent_results", [])
        successful = len([r for r in results if r.success])
        total = len(results)

        summary = f"Multi-Agent工作流执行完成：{successful}/{total} 个Agent成功执行。"

        if final_state.get("user_analysis_result"):
            user_count = len(final_state["user_analysis_result"].high_value_users)
            summary += f" 识别{user_count}个高价值用户。"

        if final_state.get("content_strategy"):
            strategy = final_state["content_strategy"]
            segments = len(strategy.get("target_segments", []))
            summary += f" 制定{segments}个用户细分策略。"

        if final_state.get("generated_content"):
            content = final_state["generated_content"]
            pieces = len(content.get("content_pieces", []))
            summary += f" 生成{pieces}个内容片段。"

        return summary


# 使用示例和测试函数
async def test_multi_agent_workflow():
    """测试Multi-Agent工作流"""

    workflow = MultiAgentWorkflow()

    # 执行工作流
    result = await workflow.execute_workflow(
        {
            "task": "执行UGC平台客户获取分析",
            "parameters": {
                "target_user_count": 50,
                "content_themes": ["旅游攻略", "美食推荐"],
            },
        }
    )

    return result


if __name__ == "__main__":
    # 简单测试
    import asyncio

    result = asyncio.run(test_multi_agent_workflow())
    print("Multi-Agent工作流测试结果:", result.get("execution_summary", "执行失败"))
