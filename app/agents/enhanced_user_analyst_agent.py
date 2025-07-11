"""
增强版用户分析Agent
集成LlamaIndex智能检索功能，提供更深度的用户洞察分析
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.agents.user_analyst_agent import UserAnalystAgent, UserProfile, AnalysisResult
from app.agents.llamaindex_manager import LlamaIndexManager
from app.agents.llm_manager import AgentLLMCaller, ModelProvider
from app.prompts.user_analyst_prompts import get_user_analyst_prompt
from app.infra.models.llm_models import LlmCommentAnalysis
from app.infra.models.comment_models import XhsComment
from app.utils.logger import app_logger as logger


@dataclass
class EnhancedUserProfile(UserProfile):
    """增强版用户画像 - 包含LlamaIndex检索结果"""
    semantic_search_results: List[Dict[str, Any]]
    related_content_summary: str
    ai_insights: str
    retrieval_score: float


@dataclass
class EnhancedAnalysisResult(AnalysisResult):
    """增强版分析结果 - 包含智能检索洞察"""
    semantic_insights: Dict[str, Any]
    content_analysis: Dict[str, Any]
    retrieval_summary: str


class EnhancedUserAnalystAgent(UserAnalystAgent):
    """增强版用户分析Agent - 集成LlamaIndex智能检索"""
    
    def __init__(self, preferred_model_provider: Optional[ModelProvider] = None):
        super().__init__()
        self.name = "EnhancedUserAnalystAgent"
        self.llamaindex_manager = LlamaIndexManager()
        self.llm_caller = AgentLLMCaller(self.name, preferred_model_provider)
        
        # 尝试加载已有索引
        self.llamaindex_manager.load_existing_indexes()
    
    async def execute_enhanced_analysis(
        self, 
        db_session: AsyncSession, 
        criteria: Optional[Dict[str, Any]] = None
    ) -> EnhancedAnalysisResult:
        """
        执行增强版用户分析，结合传统数据分析和智能检索
        
        Args:
            db_session: 数据库会话
            criteria: 筛选条件
            
        Returns:
            EnhancedAnalysisResult: 增强版分析结果
        """
        start_time = datetime.now()
        
        # 执行基础用户分析
        logger.info("🔍 执行基础用户分析...")
        basic_result = await self.execute(db_session, criteria)
        
        # 执行语义检索增强
        logger.info("🧠 执行语义检索增强...")
        semantic_insights = await self._perform_semantic_analysis(basic_result, criteria)
        
        # 执行内容分析
        logger.info("📝 执行用户内容分析...")
        content_analysis = await self._perform_content_analysis(basic_result.high_value_users)
        
        # 生成检索摘要
        logger.info("📊 生成智能分析摘要...")
        retrieval_summary = await self._generate_retrieval_summary(
            semantic_insights, content_analysis, basic_result
        )
        
        # 增强用户画像
        enhanced_users = await self._enhance_user_profiles(
            db_session, basic_result.high_value_users
        )
        
        # 构建增强版结果
        enhanced_result = EnhancedAnalysisResult(
            high_value_users=enhanced_users,
            total_analyzed=basic_result.total_analyzed,
            analysis_time=start_time,
            criteria_used=basic_result.criteria_used,
            semantic_insights=semantic_insights,
            content_analysis=content_analysis,
            retrieval_summary=retrieval_summary
        )
        
        logger.info(f"✅ 增强版用户分析完成，处理了 {len(enhanced_users)} 个用户")
        return enhanced_result
    
    async def _perform_semantic_analysis(
        self, 
        basic_result: AnalysisResult, 
        criteria: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """执行语义分析"""
        
        try:
            # 构建语义搜索查询
            search_queries = self._build_semantic_queries(criteria)
            
            semantic_results = {}
            
            for query_name, query_text in search_queries.items():
                logger.info(f"执行语义搜索: {query_name}")
                
                search_results = await self.llamaindex_manager.semantic_search(
                    query=query_text,
                    index_type="all",
                    top_k=5,
                    similarity_threshold=0.6
                )
                
                semantic_results[query_name] = {
                    "query": query_text,
                    "results": search_results,
                    "result_count": len(search_results)
                }
            
            # 生成语义洞察摘要
            insights_summary = await self._generate_semantic_insights_summary(semantic_results)
            
            return {
                "search_results": semantic_results,
                "insights_summary": insights_summary,
                "total_queries": len(search_queries),
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 语义分析失败: {e}")
            return {"error": str(e), "search_results": {}}
    
    def _build_semantic_queries(self, criteria: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """构建语义搜索查询"""
        
        queries = {
            "高价值用户特征": "高价值用户 高互动 正向情感 消费能力强",
            "用户行为模式": "用户行为 评论习惯 互动方式 活跃时间",
            "内容偏好分析": "内容偏好 兴趣话题 关注领域 参与度",
            "情感倾向分布": "情感倾向 正向 负向 中性 用户情绪",
            "未满足需求": "未满足需求 用户痛点 需求缺口 改进建议"
        }
        
        # 根据筛选条件调整查询
        if criteria:
            if criteria.get("emotional_preference"):
                emotions = " ".join(criteria["emotional_preference"])
                queries["目标情感群体"] = f"情感倾向 {emotions} 用户特征"
            
            if criteria.get("unmet_preference"):
                queries["需求分析"] = "未满足需求 用户期望 改进空间"
            
            if criteria.get("exclude_visited"):
                queries["潜在客户"] = "未去过 潜在客户 新用户 获客机会"
        
        return queries
    
    async def _generate_semantic_insights_summary(
        self, 
        semantic_results: Dict[str, Any]
    ) -> str:
        """生成语义洞察摘要"""
        
        try:
            # 整理搜索结果
            all_results = []
            for query_name, query_data in semantic_results.items():
                results = query_data.get("results", [])
                all_results.extend([
                    f"查询: {query_name}\n结果: {r['content'][:200]}...\n分数: {r['score']:.3f}"
                    for r in results[:2]  # 每个查询取前2个结果
                ])
            
            if not all_results:
                return "没有找到相关的语义搜索结果"
            
            # 使用LLM生成洞察摘要
            prompt_template = get_user_analyst_prompt("deep_user_analysis")
            
            analysis_prompt = prompt_template.format(
                user_basic_info="基于语义搜索的用户分析",
                user_behavior_data="\n\n".join(all_results[:5]),  # 限制长度
                comment_sentiment_data="多维度语义搜索结果"
            )
            
            insights = await self.llm_caller.analyze_users(
                analysis_prompt, 
                "生成基于语义搜索结果的用户洞察摘要"
            )
            
            return insights if insights else "无法生成语义洞察摘要"
            
        except Exception as e:
            logger.error(f"❌ 生成语义洞察摘要失败: {e}")
            return f"语义洞察摘要生成失败: {str(e)}"
    
    async def _perform_content_analysis(
        self, 
        high_value_users: List[UserProfile]
    ) -> Dict[str, Any]:
        """执行用户内容分析"""
        
        try:
            if not high_value_users:
                return {"message": "没有高价值用户数据进行内容分析"}
            
            content_insights = {}
            
            # 分析前几个高价值用户的内容
            for i, user in enumerate(high_value_users[:5], 1):
                logger.info(f"分析用户 {user.user_id} 的内容...")
                
                # 使用LlamaIndex获取用户详细洞察
                user_insights = await self.llamaindex_manager.get_user_insights(user.user_id)
                
                if "error" not in user_insights:
                    content_insights[f"user_{i}"] = {
                        "user_id": user.user_id,
                        "nickname": user.nickname,
                        "insights": user_insights,
                        "content_summary": self._summarize_user_content(user_insights)
                    }
            
            # 生成整体内容分析
            overall_analysis = await self._generate_content_analysis_summary(content_insights)
            
            return {
                "individual_insights": content_insights,
                "overall_analysis": overall_analysis,
                "analyzed_users_count": len(content_insights),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 内容分析失败: {e}")
            return {"error": str(e)}
    
    def _summarize_user_content(self, user_insights: Dict[str, Any]) -> str:
        """总结用户内容"""
        
        try:
            summary_parts = []
            
            # 总结数据量
            summary_parts.append(f"总记录: {user_insights.get('total_records', 0)}")
            summary_parts.append(f"评论: {user_insights.get('comments_count', 0)}")
            summary_parts.append(f"笔记: {user_insights.get('notes_count', 0)}")
            summary_parts.append(f"分析: {user_insights.get('analyses_count', 0)}")
            
            # 添加关键洞察
            if user_insights.get('analyses'):
                analyses = user_insights['analyses']
                if analyses:
                    first_analysis = analyses[0]
                    metadata = first_analysis.get('metadata', {})
                    if metadata.get('emotional_preference'):
                        summary_parts.append(f"情感倾向: {metadata['emotional_preference']}")
                    if metadata.get('unmet_preference'):
                        summary_parts.append(f"未满足需求: {metadata['unmet_preference']}")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"用户内容总结失败: {e}")
            return "内容总结生成失败"
    
    async def _generate_content_analysis_summary(
        self, 
        content_insights: Dict[str, Any]
    ) -> str:
        """生成内容分析总结"""
        
        try:
            if not content_insights:
                return "没有内容洞察数据"
            
            # 整理用户内容数据
            summary_data = []
            for user_key, user_data in content_insights.items():
                summary_data.append(
                    f"用户 {user_data['user_id']} ({user_data['nickname']}): "
                    f"{user_data['content_summary']}"
                )
            
            content_summary = "\n".join(summary_data)
            
            # 使用LLM生成深度分析
            prompt_template = get_user_analyst_prompt("user_journey_mapping")
            
            analysis_prompt = prompt_template.format(
                touchpoint_data=content_summary,
                conversion_funnel_data="用户内容参与和互动数据",
                user_feedback_data="用户评论和分析数据"
            )
            
            analysis = await self.llm_caller.analyze_users(
                analysis_prompt,
                "基于用户内容数据生成深度分析报告"
            )
            
            return analysis if analysis else "无法生成内容分析总结"
            
        except Exception as e:
            logger.error(f"❌ 生成内容分析总结失败: {e}")
            return f"内容分析总结生成失败: {str(e)}"
    
    async def _generate_retrieval_summary(
        self,
        semantic_insights: Dict[str, Any],
        content_analysis: Dict[str, Any], 
        basic_result: AnalysisResult
    ) -> str:
        """生成智能检索摘要"""
        
        try:
            summary_parts = []
            
            # 基础分析摘要
            summary_parts.append(f"基础分析: 识别 {len(basic_result.high_value_users)} 个高价值用户")
            
            # 语义检索摘要
            if semantic_insights.get("search_results"):
                search_count = len(semantic_insights["search_results"])
                summary_parts.append(f"语义检索: 执行 {search_count} 个查询")
            
            # 内容分析摘要
            if content_analysis.get("analyzed_users_count"):
                analyzed_count = content_analysis["analyzed_users_count"]
                summary_parts.append(f"内容分析: 深度分析 {analyzed_count} 个用户")
            
            # 智能洞察
            if semantic_insights.get("insights_summary"):
                summary_parts.append("生成智能洞察摘要")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"❌ 生成检索摘要失败: {e}")
            return f"检索摘要生成失败: {str(e)}"
    
    async def _enhance_user_profiles(
        self,
        db_session: AsyncSession,
        basic_users: List[UserProfile]
    ) -> List[EnhancedUserProfile]:
        """增强用户画像"""
        
        enhanced_users = []
        
        for user in basic_users:
            try:
                # 获取用户的语义搜索结果
                user_query = f"用户 {user.nickname} {user.user_id}"
                search_results = await self.llamaindex_manager.semantic_search(
                    query=user_query,
                    index_type="all",
                    top_k=3,
                    similarity_threshold=0.5
                )
                
                # 生成相关内容摘要
                related_summary = self._generate_related_content_summary(search_results)
                
                # 生成AI洞察
                ai_insights = await self._generate_user_ai_insights(user, search_results)
                
                # 计算检索分数
                retrieval_score = self._calculate_retrieval_score(search_results)
                
                # 创建增强版用户画像
                enhanced_user = EnhancedUserProfile(
                    user_id=user.user_id,
                    nickname=user.nickname,
                    emotional_preference=user.emotional_preference,
                    aips_preference=user.aips_preference,
                    has_visited=user.has_visited,
                    unmet_preference=user.unmet_preference,
                    unmet_desc=user.unmet_desc,
                    gender=user.gender,
                    age=user.age,
                    value_score=user.value_score,
                    interaction_count=user.interaction_count,
                    latest_activity=user.latest_activity,
                    notes_engaged=user.notes_engaged,
                    semantic_search_results=search_results,
                    related_content_summary=related_summary,
                    ai_insights=ai_insights,
                    retrieval_score=retrieval_score
                )
                
                enhanced_users.append(enhanced_user)
                
            except Exception as e:
                logger.error(f"❌ 增强用户 {user.user_id} 画像失败: {e}")
                # 如果增强失败，至少保留基础信息
                enhanced_user = EnhancedUserProfile(
                    user_id=user.user_id,
                    nickname=user.nickname,
                    emotional_preference=user.emotional_preference,
                    aips_preference=user.aips_preference,
                    has_visited=user.has_visited,
                    unmet_preference=user.unmet_preference,
                    unmet_desc=user.unmet_desc,
                    gender=user.gender,
                    age=user.age,
                    value_score=user.value_score,
                    interaction_count=user.interaction_count,
                    latest_activity=user.latest_activity,
                    notes_engaged=user.notes_engaged,
                    semantic_search_results=[],
                    related_content_summary="增强失败",
                    ai_insights=f"增强失败: {str(e)}",
                    retrieval_score=0.0
                )
                enhanced_users.append(enhanced_user)
        
        return enhanced_users
    
    def _generate_related_content_summary(self, search_results: List[Dict[str, Any]]) -> str:
        """生成相关内容摘要"""
        
        if not search_results:
            return "没有找到相关内容"
        
        summary_parts = []
        for result in search_results[:3]:
            content_type = result.get("index_type", "unknown")
            score = result.get("score", 0)
            summary_parts.append(f"{content_type}(相似度:{score:.2f})")
        
        return " | ".join(summary_parts)
    
    async def _generate_user_ai_insights(
        self, 
        user: UserProfile, 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """生成用户AI洞察"""
        
        try:
            if not search_results:
                return "没有足够的数据生成AI洞察"
            
            # 整理搜索结果
            context_data = []
            for result in search_results[:2]:
                context_data.append(result.get("content", "")[:300])
            
            context = "\n".join(context_data)
            
            # 构建用户基础信息
            user_info = f"""
用户ID: {user.user_id}
昵称: {user.nickname}  
价值评分: {user.value_score}
情感倾向: {user.emotional_preference}
互动次数: {user.interaction_count}
未满足需求: {user.unmet_desc[:100]}...
"""
            
            # 使用专业提示词生成洞察
            prompt_template = get_user_analyst_prompt("deep_user_analysis")
            
            analysis_prompt = prompt_template.format(
                user_basic_info=user_info,
                user_behavior_data=context,
                comment_sentiment_data="基于语义搜索的用户行为分析"
            )
            
            insights = await self.llm_caller.analyze_users(
                analysis_prompt,
                "生成单个用户的深度AI洞察分析"
            )
            
            return insights[:500] if insights else "无法生成AI洞察"
            
        except Exception as e:
            logger.error(f"❌ 生成用户AI洞察失败: {e}")
            return f"AI洞察生成失败: {str(e)}"
    
    def _calculate_retrieval_score(self, search_results: List[Dict[str, Any]]) -> float:
        """计算检索评分"""
        
        if not search_results:
            return 0.0
        
        # 基于搜索结果的数量和质量计算分数
        total_score = sum(result.get("score", 0) for result in search_results)
        result_count = len(search_results)
        
        # 归一化分数
        avg_score = total_score / result_count if result_count > 0 else 0
        count_bonus = min(result_count / 5.0, 1.0)  # 最多5个结果的奖励
        
        final_score = (avg_score * 0.7) + (count_bonus * 0.3)
        
        return round(final_score, 3)
    
    async def smart_user_query(self, question: str) -> str:
        """智能用户查询 - 直接回答关于用户的问题"""
        
        logger.info(f"🤔 智能用户查询: {question}")
        
        try:
            # 使用LlamaIndex进行智能问答
            answer = await self.llamaindex_manager.intelligent_query(
                question=question,
                context_type="all",
                max_context_length=2000
            )
            
            return answer if answer else "抱歉，无法找到相关信息回答您的问题。"
            
        except Exception as e:
            logger.error(f"❌ 智能用户查询失败: {e}")
            return f"查询失败: {str(e)}"