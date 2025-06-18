import uuid
import json
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from app.infra.models.keyword_models import XhsKeywordGroup
from app.utils.logger import app_logger as logger
from app.config.settings import settings


class KeywordDAO:
    @staticmethod
    async def get_or_create_keyword_group(
        db: AsyncSession, keywords: List[str], group_name: Optional[str] = None
    ) -> XhsKeywordGroup:
        """获取或创建关键词群组

        Args:
            db: 数据库会话
            keywords: 关键词列表
            group_name: 可选的群组名称

        Returns:
            XhsKeywordGroup 实例
        """

        try:
            # 确保keywords是一个排序后的列表，便于比较
            sorted_keywords = (
                sorted(keywords) if isinstance(keywords, list) else [str(keywords)]
            )

            # 查找匹配的关键词群组
            # MySQL JSON_CONTAINS必须双向检查才能确保完全匹配
            found_groups = []

            # 获取所有可能的群组
            stmt = select(XhsKeywordGroup)
            result = await db.execute(stmt)
            all_groups = result.scalars().all()

            # 手动比较JSON内容
            for group in all_groups:
                group_keywords = group.keywords
                # 确保数据库中的关键词也是排序列表
                if not isinstance(group_keywords, list):
                    try:
                        if isinstance(group_keywords, str):
                            group_keywords = json.loads(group_keywords)
                    except:
                        continue

                sorted_group_keywords = (
                    sorted(group_keywords)
                    if isinstance(group_keywords, list)
                    else [str(group_keywords)]
                )

                # 比较两个排序列表是否相等
                if sorted_group_keywords == sorted_keywords:
                    found_groups.append(group)
                    break

            if found_groups:
                keyword_group = found_groups[0]
            else:
                unique_group_name = group_name or f"关键词群组-{uuid.uuid4().hex[:8]}"

                belong = settings.GROUP_BELONG
                if not belong:
                    raise ValueError("项目归属未设置")

                keyword_group = XhsKeywordGroup(
                    group_name=unique_group_name,
                    keywords=sorted_keywords,
                    group_belong=belong,
                )
                db.add(keyword_group)
                await db.flush()
                logger.info(
                    f"创建新的关键词群组: {unique_group_name}, 关键词: {sorted_keywords}"
                )

            return keyword_group

        except Exception as e:
            logger.error(f"创建或获取关键词群组时出错: {str(e)}")
            # 创建一个临时的关键词群组对象，不保存到数据库
            temp_group = XhsKeywordGroup(
                group_id=-1,
                group_name="临时关键词群组",
                keywords=keywords,
            )
            return temp_group
