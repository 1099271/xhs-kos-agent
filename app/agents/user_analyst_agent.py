"""
用户分析Agent基类
用于分析用户评论行为，识别高价值用户
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.infra.models.llm_models import LlmCommentAnalysis
from app.infra.models.comment_models import XhsComment
from app.infra.models.note_models import XhsNote
from app.utils.logger import app_logger as logger


@dataclass
class UserProfile:
    """用户画像数据结构"""

    user_id: str
    nickname: str
    emotional_preference: str  # 情感倾向
    aips_preference: str  # AIPS偏好
    has_visited: str  # 是否去过
    unmet_preference: str  # 未满足需求
    unmet_desc: str  # 未满足需求描述
    gender: str
    age: str
    value_score: float  # 价值评分
    interaction_count: int  # 互动次数
    latest_activity: datetime  # 最新活动时间
    notes_engaged: List[str]  # 参与的笔记ID列表


@dataclass
class AnalysisResult:
    """分析结果数据结构"""

    high_value_users: List[UserProfile]
    total_analyzed: int
    analysis_time: datetime
    criteria_used: Dict[str, Any]


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """执行Agent的核心功能"""
        pass


class UserAnalystAgent(BaseAgent):
    """用户分析Agent - 基于LLM评论分析数据识别高价值用户"""

    def __init__(self):
        super().__init__("UserAnalystAgent")

    async def execute(
        self, db_session: AsyncSession, criteria: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        执行用户分析，识别高价值用户

        Args:
            db_session: 数据库会话
            criteria: 筛选条件

        Returns:
            AnalysisResult: 分析结果
        """
        start_time = datetime.now()

        # 设置默认筛选条件
        default_criteria = {
            "emotional_preference": ["正向"],  # 正向情感
            "unmet_preference": ["是"],  # 有未满足需求
            "min_interaction_count": 1,  # 最少互动次数
            "exclude_visited": False,  # 是否排除已去过的用户
            "limit": 100,  # 返回用户数量限制
        }

        if criteria:
            default_criteria.update(criteria)

        self.logger.info(f"开始用户分析，筛选条件: {default_criteria}")

        # 查询LLM评论分析数据
        high_value_users = await self._query_high_value_users(
            db_session, default_criteria
        )

        # 为每个用户计算价值评分
        enriched_users = await self._enrich_user_profiles(db_session, high_value_users)

        # 按价值评分排序
        enriched_users.sort(key=lambda x: x.value_score, reverse=True)

        # 限制返回数量
        if default_criteria.get("limit"):
            enriched_users = enriched_users[: default_criteria["limit"]]

        result = AnalysisResult(
            high_value_users=enriched_users,
            total_analyzed=len(enriched_users),
            analysis_time=start_time,
            criteria_used=default_criteria,
        )

        self.logger.info(f"用户分析完成，识别到 {len(enriched_users)} 个高价值用户")
        return result

    async def _query_high_value_users(
        self, db_session: AsyncSession, criteria: Dict[str, Any]
    ) -> List[LlmCommentAnalysis]:
        """查询符合条件的用户评论分析数据"""

        query = select(LlmCommentAnalysis)

        # 构建筛选条件
        conditions = []

        # 情感倾向筛选
        if criteria.get("emotional_preference"):
            conditions.append(
                LlmCommentAnalysis.emotional_preference.in_(
                    criteria["emotional_preference"]
                )
            )

        # 未满足需求筛选
        if criteria.get("unmet_preference"):
            conditions.append(
                LlmCommentAnalysis.unmet_preference.in_(criteria["unmet_preference"])
            )

        # 是否去过筛选
        if criteria.get("exclude_visited"):
            conditions.append(LlmCommentAnalysis.has_visited == "否")

        # 应用筛选条件
        if conditions:
            query = query.where(and_(*conditions))

        # 按创建时间排序
        query = query.order_by(desc(LlmCommentAnalysis.created_at))

        result = await db_session.execute(query)
        return result.scalars().all()

    async def _enrich_user_profiles(
        self, db_session: AsyncSession, analysis_data: List[LlmCommentAnalysis]
    ) -> List[UserProfile]:
        """丰富用户画像数据，添加互动统计等信息"""

        user_profiles = {}

        for analysis in analysis_data:
            user_id = analysis.comment_user_id

            if user_id not in user_profiles:
                # 查询用户的评论统计信息
                comment_stats = await self._get_user_comment_stats(db_session, user_id)

                user_profiles[user_id] = UserProfile(
                    user_id=user_id,
                    nickname=analysis.comment_user_nickname or "未知用户",
                    emotional_preference=analysis.emotional_preference or "未知",
                    aips_preference=analysis.aips_preference or "未知",
                    has_visited=analysis.has_visited or "未知",
                    unmet_preference=analysis.unmet_preference or "未知",
                    unmet_desc=analysis.unmet_desc or "",
                    gender=analysis.gender or "未知",
                    age=analysis.age or "未知",
                    value_score=0,  # 稍后计算
                    interaction_count=comment_stats["total_comments"],
                    latest_activity=comment_stats["latest_comment_time"],
                    notes_engaged=comment_stats["note_ids"],
                )

            # 更新笔记参与列表
            if analysis.note_id not in user_profiles[user_id].notes_engaged:
                user_profiles[user_id].notes_engaged.append(analysis.note_id)

        # 计算价值评分
        enriched_users = list(user_profiles.values())
        for user in enriched_users:
            user.value_score = self._calculate_value_score(user)

        return enriched_users

    async def _get_user_comment_stats(
        self, db_session: AsyncSession, user_id: str
    ) -> Dict[str, Any]:
        """获取用户评论统计信息"""

        query = select(XhsComment).where(XhsComment.comment_user_id == user_id)
        result = await db_session.execute(query)
        comments = result.scalars().all()

        if not comments:
            return {
                "total_comments": 0,
                "latest_comment_time": datetime.now(),
                "note_ids": [],
            }

        # 统计信息
        note_ids = list(set([c.note_id for c in comments]))
        latest_time = max(
            [c.comment_create_time for c in comments if c.comment_create_time]
        )

        return {
            "total_comments": len(comments),
            "latest_comment_time": latest_time or datetime.now(),
            "note_ids": note_ids,
        }

    def _calculate_value_score(self, user: UserProfile) -> float:
        """计算用户价值评分"""
        score = 0.0

        # 情感倾向评分
        emotional_scores = {"正向": 10, "中性": 5, "负向": 0, "未知": 2}
        score += emotional_scores.get(user.emotional_preference, 0)

        # 未满足需求评分 (有需求的用户更有价值)
        if user.unmet_preference == "是":
            score += 15

        # 是否去过评分 (没去过的更有获客价值)
        if user.has_visited == "否":
            score += 10
        elif user.has_visited == "未知":
            score += 5

        # 互动活跃度评分
        if user.interaction_count >= 10:
            score += 10
        elif user.interaction_count >= 5:
            score += 7
        elif user.interaction_count >= 2:
            score += 5
        else:
            score += 2

        # 参与笔记多样性评分
        note_count = len(user.notes_engaged)
        if note_count >= 5:
            score += 8
        elif note_count >= 3:
            score += 5
        elif note_count >= 2:
            score += 3
        else:
            score += 1

        # 活跃度时间评分 (最近活跃的用户更有价值)
        days_since_activity = (datetime.now() - user.latest_activity).days
        if days_since_activity <= 7:
            score += 10
        elif days_since_activity <= 30:
            score += 7
        elif days_since_activity <= 90:
            score += 4
        else:
            score += 1

        return round(score, 2)

    async def get_user_detailed_analysis(
        self, db_session: AsyncSession, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取特定用户的详细分析"""

        # 查询用户所有评论分析
        query = select(LlmCommentAnalysis).where(
            LlmCommentAnalysis.comment_user_id == user_id
        )
        result = await db_session.execute(query)
        analyses = result.scalars().all()

        if not analyses:
            return None

        # 查询用户评论详情
        comment_query = (
            select(XhsComment)
            .where(XhsComment.comment_user_id == user_id)
            .options(selectinload(XhsComment.note))
        )

        comment_result = await db_session.execute(comment_query)
        comments = comment_result.scalars().all()

        return {
            "user_id": user_id,
            "total_analyses": len(analyses),
            "total_comments": len(comments),
            "analysis_history": [
                {
                    "note_id": a.note_id,
                    "emotional_preference": a.emotional_preference,
                    "aips_preference": a.aips_preference,
                    "unmet_desc": a.unmet_desc,
                    "analysis_time": a.created_at,
                }
                for a in analyses
            ],
            "comment_history": [
                {
                    "comment_id": c.comment_id,
                    "note_id": c.note_id,
                    "content": c.comment_content,
                    "create_time": c.comment_create_time,
                    "like_count": c.comment_like_count,
                }
                for c in comments
            ],
        }
