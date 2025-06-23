import random
import time
import traceback
from typing import List
from sqlalchemy import text

from app.utils.logger import app_logger as logger
from app.infra.models.comment_models import XhsComment
from app.schemas.comment_schemas import XhsCommentsResponse
from app.infra.dao.comment_dao import CommentDAO
from app.services.coze.coze_service import CozeService
from app.services.spider.spider_service import SpiderService

from app.infra.db.async_database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


async def finish_note_comments(use_coze: bool = False):
    """
    补全没有笔记评论内容的笔记内容，查询所有没有评论内容的笔记，然后通过爬虫获取评论并更新

    Args:
        use_coze: 是否使用Coze API获取笔记详情，默认使用爬虫

    Returns:
        处理的笔记数量
    """
    logger.info("开始查询并补全笔记评论内容")

    async for session in get_async_db():
        db: AsyncSession = session

        try:
            stmt = text(
                """
                SELECT nd.note_id, nd.note_url, nd.comment_count
                FROM xhs_note_details nd
                LEFT JOIN (
                    SELECT note_id, COUNT(*) AS actual_comment_count
                    FROM xhs_comments
                    GROUP BY note_id
                ) c ON nd.note_id = c.note_id
                WHERE nd.comment_count > 0
                AND (c.note_id IS NULL OR c.actual_comment_count = 0)
                and nd.note_url not like '%_token=&%';
            """
            )
            result = await db.execute(stmt)
            notes_to_process = result.all()
            logger.info(f"找到 {len(notes_to_process)} 条需要补全详情的笔记")
            for index, note_record in enumerate(notes_to_process):
                note_id = note_record[0]
                note_url = note_record[1]
                comment_count = note_record[2]

                try:
                    logger.info(f"处理第 {index} 条笔记: {note_url}")
                    if use_coze:
                        await get_note_comments_by_coze(note_url, comment_count)
                    else:
                        await get_note_comments_by_spider(note_url, comment_count)
                except ValueError as e:
                    logger.error(f"获取笔记评论失败: {e}")
                    continue
                except Exception as e:
                    logger.error(f"处理笔记 {note_id} 时出错: {str(e)}")

                # 随机等待1-5秒
                sleep_time = random.randint(5, 12)
                logger.info(f"等待 {sleep_time} 秒后继续...")
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"处理笔记详情时出错: {e}")
            logger.error(traceback.format_exc())
            return 0
        finally:
            await db.close()


async def get_note_comments_by_coze(
    note_url: str, comment_count: int
) -> List[XhsComment]:
    """
    通过Coze API获取笔记评论内容
    """
    # 设置API参数
    parameters = {
        "noteUrl": note_url,
        "comments_num": comment_count,
    }
    result = CozeService.call_coze_api(
        workflow_id="7480889721393152035",
        parameters=parameters,
        log_file_prefix="get_xhs_comments_by_note",
    )

    # 处理响应
    response_obj, data_json = CozeService.process_response(result, XhsCommentsResponse)
    if not response_obj:
        return []

    req_info = {"noteUrl": note_url}

    # 存储数据
    return await CozeService.store_data_in_db(
        db_method=CommentDAO.store_coze_comments,
        req_info=req_info,
        response_obj=response_obj,
        data_type="笔记评论",
    )


async def get_note_comments_by_spider(
    note_url: str, comment_count: int
) -> List[XhsComment]:
    """
    通过爬虫获取笔记评论内容
    """
    spider_service = SpiderService()
    note_all_comment, log_filename = await spider_service.get_note_comments(note_url)

    if not note_all_comment:
        raise ValueError(f"评论结构为空: {note_url}")

    async for session in get_async_db():
        db: AsyncSession = session
        try:
            result = await CommentDAO.store_spider_note_detail(
                db, note_all_comment, log_filename
            )
            return result
        finally:
            await db.close()  # 确保在任何情况下都关闭数据库连接
