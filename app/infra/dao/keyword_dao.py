import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infra.models.keyword_models import XhsKeywordGroup
from app.utils.logger import app_logger as logger


class KeywordDAO:
    @staticmethod
    async def get_or_create_keyword_group(
        db: AsyncSession, keywords: str, group_name: Optional[str] = None
    ) -> XhsKeywordGroup:
        """获取或创建关键词群组"""

        try:
            # 使用 select 语句替代 query
            stmt = select(XhsKeywordGroup).filter(XhsKeywordGroup.keywords == keywords)
            result = await db.execute(stmt)
            keyword_group = result.scalars().first()

            # 如果关键词群组不存在，创建新的关键词群组
            if not keyword_group:
                # 生成唯一的群组名称
                unique_group_name = group_name or f"关键词群组-{uuid.uuid4().hex[:8]}"

                keyword_group = XhsKeywordGroup(
                    group_name=unique_group_name,
                    keywords=keywords,
                )
                db.add(keyword_group)
                await db.flush()
                logger.info(
                    f"创建新的关键词群组: {unique_group_name}, 关键词: {keywords}"
                )
            else:
                logger.info(
                    f"找到现有关键词群组: {keyword_group.group_name}, ID: {keyword_group.group_id}"
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
