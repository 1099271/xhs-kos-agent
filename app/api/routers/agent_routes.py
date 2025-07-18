"""
Multi-Agent系统的FastAPI接口
提供Agent管理和工作流执行的RESTful API
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import asyncio

from app.agents.strategy_coordinator_agent import StrategyCoordinatorAgent, StrategyObjective, StrategyType
from app.agents.content_generator_agent import ContentGeneratorAgent, ContentGenerationRequest, GeneratedContent
from app.agents.enhanced_user_analyst_agent import EnhancedUserAnalystAgent
from app.agents.enhanced_multi_agent_workflow import EnhancedMultiAgentWorkflow
from app.agents.llamaindex_manager import LlamaIndexManager
from app.agents.llm_manager import ModelProvider
from app.utils.logger import app_logger as logger


# Pydantic模型定义
class StrategyObjectiveRequest(BaseModel):
    """策略目标请求模型"""
    objective_type: str = Field(..., description="策略类型", example="engagement")
    target_metrics: Dict[str, float] = Field(..., description="目标指标", example={"engagement_rate": 0.05})
    timeline_days: int = Field(..., description="时间周期(天)", example=7)
    budget_limit: Optional[float] = Field(None, description="预算限制")
    target_audience_size: Optional[int] = Field(30, description="目标受众数量")


class ContentGenerationRequestModel(BaseModel):
    """内容生成请求模型"""
    user_profile: Dict[str, Any] = Field(..., description="用户画像")
    content_type: str = Field(..., description="内容类型", example="creative")
    topic: str = Field(..., description="内容主题", example="夏季护肤心得")
    platform: str = Field(..., description="发布平台", example="xhs")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="具体要求")
    brand_guidelines: Optional[Dict[str, Any]] = Field(None, description="品牌指南")
    constraints: Optional[Dict[str, Any]] = Field(None, description="限制条件")


class WorkflowExecutionRequest(BaseModel):
    """工作流执行请求模型"""
    strategy_objective: Optional[StrategyObjectiveRequest] = None
    user_criteria: Dict[str, Any] = Field(default_factory=dict, description="用户筛选条件")
    workflow_config: Dict[str, Any] = Field(default_factory=dict, description="工作流配置")
    async_execution: bool = Field(False, description="是否异步执行")


class AgentStatusResponse(BaseModel):
    """Agent状态响应模型"""
    agent_name: str
    status: str
    last_activity: Optional[datetime] = None
    version: str = "1.0.0"


class ContentPlanResponse(BaseModel):
    """内容计划响应模型"""
    plan_id: str
    strategy_objective: Dict[str, Any]
    target_users_count: int
    content_calendar_length: int
    expected_outcomes: Dict[str, float]
    risk_assessment: Dict[str, Any]
    created_at: datetime


class ExecutionResultResponse(BaseModel):
    """执行结果响应模型"""
    result_id: str
    plan_id: str
    executed_content_count: int
    success_rate: float
    actual_metrics: Dict[str, float]
    optimization_suggestions: List[str]
    lessons_learned: List[str]
    executed_at: datetime


# 创建路由器
router = APIRouter(prefix="/api/v1/agents", tags=["Multi-Agent系统"])

# 全局Agent实例
strategy_coordinator = StrategyCoordinatorAgent()
content_generator = ContentGeneratorAgent()
user_analyst = EnhancedUserAnalystAgent()
workflow_engine = EnhancedMultiAgentWorkflow()


@router.get("/status", response_model=List[AgentStatusResponse])
async def get_agent_status():
    """获取所有Agent的状态"""
    try:
        return [
            AgentStatusResponse(
                agent_name="StrategyCoordinatorAgent",
                status="active",
                last_activity=datetime.now(),
                version="1.0.0"
            ),
            AgentStatusResponse(
                agent_name="ContentGeneratorAgent",
                status="active",
                last_activity=datetime.now(),
                version="1.0.0"
            ),
            AgentStatusResponse(
                agent_name="EnhancedUserAnalystAgent",
                status="active",
                last_activity=datetime.now(),
                version="1.0.0"
            ),
            AgentStatusResponse(
                agent_name="EnhancedMultiAgentWorkflow",
                status="active",
                last_activity=datetime.now(),
                version="1.0.0"
            )
        ]
    except Exception as e:
        logger.error(f"获取Agent状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/create", response_model=ContentPlanResponse)
async def create_content_strategy(
    request: StrategyObjectiveRequest,
    background_tasks: BackgroundTasks = None
):
    """创建内容策略"""
    try:
        # 转换策略目标
        strategy_objective = StrategyObjective(
            objective_type=StrategyType(request.objective_type),
            target_metrics=request.target_metrics,
            timeline_days=request.timeline_days,
            budget_limit=request.budget_limit,
            target_audience_size=request.target_audience_size
        )
        
        # 创建内容计划
        content_plan = await strategy_coordinator.create_content_strategy(
            strategy_objective,
            {"min_engagement_rate": 0.03, "min_comment_count": 3, "limit": request.target_audience_size}
        )
        
        return ContentPlanResponse(
            plan_id=content_plan.plan_id,
            strategy_objective={
                "type": content_plan.strategy_objective.objective_type.value,
                "metrics": content_plan.strategy_objective.target_metrics,
                "timeline": content_plan.strategy_objective.timeline_days,
                "budget": content_plan.strategy_objective.budget_limit
            },
            target_users_count=len(content_plan.target_users),
            content_calendar_length=len(content_plan.content_calendar),
            expected_outcomes=content_plan.expected_outcomes,
            risk_assessment=content_plan.risk_assessment,
            created_at=content_plan.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建内容策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/generate", response_model=Dict[str, Any])
async def generate_content(
    request: ContentGenerationRequestModel
):
    """生成个性化内容"""
    try:
        # 创建内容生成请求
        content_request = ContentGenerationRequest(
            user_profile=request.user_profile,
            content_type=request.content_type,
            topic=request.topic,
            platform=request.platform,
            requirements=request.requirements,
            brand_guidelines=request.brand_guidelines,
            constraints=request.constraints
        )
        
        # 生成内容
        generated_content = await content_generator.generate_content(content_request)
        
        # 验证内容质量
        quality_check = await content_generator.validate_content_quality(generated_content)
        
        return {
            "content": {
                "content_id": generated_content.content_id,
                "title": generated_content.title,
                "main_content": generated_content.main_content,
                "hashtags": generated_content.hashtags,
                "media_suggestions": generated_content.media_suggestions,
                "platform_specific": generated_content.platform_specific,
                "generation_timestamp": generated_content.generation_timestamp,
                "ai_explanation": generated_content.ai_explanation
            },
            "quality_check": quality_check,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content/generate-batch", response_model=Dict[str, Any])
async def generate_content_batch(
    requests: List[ContentGenerationRequestModel]
):
    """批量生成内容"""
    try:
        # 创建批量请求
        content_requests = []
        for req in requests:
            content_requests.append(ContentGenerationRequest(
                user_profile=req.user_profile,
                content_type=req.content_type,
                topic=req.topic,
                platform=req.platform,
                requirements=req.requirements,
                brand_guidelines=req.brand_guidelines,
                constraints=req.constraints
            ))
        
        # 批量生成内容
        generated_contents = await content_generator.generate_content_batch(content_requests)
        
        return {
            "contents": [
                {
                    "content_id": content.content_id,
                    "title": content.title,
                    "main_content": content.main_content,
                    "hashtags": content.hashtags,
                    "platform_specific": content.platform_specific
                }
                for content in generated_contents
            ],
            "total_count": len(generated_contents),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"批量内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/execute", response_model=Dict[str, Any])
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks = None
):
    """执行完整工作流"""
    try:
        # 准备策略目标
        strategy_objective = None
        if request.strategy_objective:
            strategy_objective = StrategyObjective(
                objective_type=StrategyType(request.strategy_objective.objective_type),
                target_metrics=request.strategy_objective.target_metrics,
                timeline_days=request.strategy_objective.timeline_days,
                budget_limit=request.strategy_objective.budget_limit,
                target_audience_size=request.strategy_objective.target_audience_size
            )
        
        # 执行工作流
        if request.async_execution and background_tasks:
            # 异步执行
            background_tasks.add_task(
                workflow_engine.execute_complete_workflow,
                {
                    "strategy_objective": strategy_objective,
                    "user_criteria": request.user_criteria,
                    "workflow_config": request.workflow_config
                }
            )
            
            return {
                "workflow_id": f"workflow_{datetime.now().timestamp()}",
                "status": "started",
                "message": "工作流已启动，将在后台执行"
            }
        else:
            # 同步执行
            result = await workflow_engine.execute_complete_workflow({
                "strategy_objective": strategy_objective,
                "user_criteria": request.user_criteria,
                "workflow_config": request.workflow_config
            })
            
            return result
            
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/high-value", response_model=Dict[str, Any])
async def get_high_value_users(
    limit: int = 50,
    min_engagement_rate: float = 0.03,
    min_comment_count: int = 3
):
    """获取高价值用户"""
    try:
        users = await user_analyst.identify_high_value_users(
            min_engagement_rate=min_engagement_rate,
            min_comment_count=min_comment_count,
            limit=limit
        )
        
        return {
            "users": [
                {
                    "user_id": user.user_id,
                    "nickname": user.nickname,
                    "value_score": user.value_score,
                    "engagement_rate": user.engagement_rate,
                    "follower_count": user.follower_count,
                    "emotional_preference": user.emotional_preference,
                    "unmet_desc": user.unmet_desc,
                    "interaction_count": user.interaction_count
                }
                for user in users
            ],
            "total_count": len(users),
            "criteria": {
                "limit": limit,
                "min_engagement_rate": min_engagement_rate,
                "min_comment_count": min_comment_count
            }
        }
        
    except Exception as e:
        logger.error(f"获取高价值用户失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/insights", response_model=Dict[str, Any])
async def get_user_insights(user_id: str):
    """获取用户洞察"""
    try:
        insights = await user_analyst.get_user_insights(user_id)
        
        if not insights:
            raise HTTPException(status_code=404, detail="用户未找到")
        
        return {
            "user_id": insights.user_id,
            "nickname": insights.nickname,
            "value_score": insights.value_score,
            "engagement_rate": insights.engagement_rate,
            "influence_score": insights.influence_score,
            "interests": insights.interests,
            "pain_points": insights.pain_points,
            "content_preferences": insights.content_preferences,
            "semantic_search_results": insights.semantic_search_results,
            "ai_insights": insights.ai_insights,
            "retrieval_score": insights.retrieval_score
        }
        
    except Exception as e:
        logger.error(f"获取用户洞察失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy/optimize", response_model=Dict[str, Any])
async def optimize_strategy(
    plan_id: str,
    execution_result_id: str
):
    """优化现有策略"""
    try:
        # 这里应该根据实际存储的plan和execution结果进行优化
        # 简化处理：创建新的优化策略
        
        new_strategy = StrategyObjective(
            objective_type=StrategyType.ENGAGEMENT,
            target_metrics={"engagement_rate": 0.06, "reach": 12000},
            timeline_days=10,
            budget_limit=1200.0,
            target_audience_size=35
        )
        
        optimized_plan = await strategy_coordinator.create_content_strategy(
            new_strategy,
            {"min_engagement_rate": 0.035, "min_comment_count": 4, "limit": 35}
        )
        
        return {
            "optimized_plan_id": optimized_plan.plan_id,
            "original_plan_id": plan_id,
            "improvements": [
                "提高目标互动率至6%",
                "扩大目标受众至35人",
                "延长执行周期至10天"
            ],
            "optimizations": {
                "target_metrics": {"engagement_rate": 0.06, "reach": 12000},
                "timeline_days": 10,
                "target_audience_size": 35
            }
        }
        
    except Exception as e:
        logger.error(f"策略优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "agents": {
            "StrategyCoordinatorAgent": "available",
            "ContentGeneratorAgent": "available",
            "EnhancedUserAnalystAgent": "available",
            "EnhancedMultiAgentWorkflow": "available"
        }
    }