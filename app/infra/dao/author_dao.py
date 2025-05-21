from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.models.author_models import XhsAuthor
from app.utils.logger import app_logger as logger
from sqlalchemy import select
from datetime import datetime
from typing import Dict, Any


class AuthorDAO:

    @classmethod
    async def store_author(
        cls, db: AsyncSession, author_data: Dict[str, Any]
    ) -> XhsAuthor:
        stmt = select(XhsAuthor).filter(
            XhsAuthor.author_user_id == author_data["author_user_id"]
        )
        result = await db.execute(stmt)
        author = result.scalars().first()

        if author:
            # 更新现有作者信息
            for key, value in author_data.items():
                if hasattr(author, key):
                    setattr(author, key, value)
            author.updated_at = datetime.now()
            logger.info(f"更新作者信息: {author.author_user_id}")
        else:
            # 创建新作者
            author = XhsAuthor(**author_data)
            await db.add(author)
            logger.info(f"创建新作者: {author.author_user_id}")

        return author
