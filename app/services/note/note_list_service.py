import random
import time
import traceback
from typing import List
from sqlalchemy import text
from loguru import logger

from app.infra.models.note_models import XhsNote

from app.services.coze.coze_service import CozeService
from app.config.settings import settings
from app.schemas.note_schemas import XhsSearchResponse
from app.infra.dao.note_dao import NoteDAO
from app.services.spider.spider_service import SpiderService

from app.infra.db.async_database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.note.note_detail_service import (
    get_note_detail_by_coze,
    get_note_detail_by_spider,
)


async def get_notes_by_topic_tag(
    tag: str, num: int, use_coze: bool = True
) -> List[XhsNote]:
    """
    根据标签获取小红书笔记（使用Coze插件）

    Args:
        tag: 搜索的标签
        num: 获取的笔记数量

    Returns:
        存储的笔记列表
    """
    if use_coze:
        return await get_notes_by_coze(tag, num)
    else:
        return await get_notes_by_spider(tag, num)


async def get_notes_by_spider(tag: str, num: int) -> List[XhsNote]:
    """
    根据标签获取小红书笔记（使用Spider_XHS爬虫）
    """
    spider_service = SpiderService()
    notes_data = await spider_service.get_notes(tag, num)

    async for session in get_async_db():
        db: AsyncSession = session
        return await NoteDAO.store_spider_note_list(db, tag, notes_data)


async def get_notes_by_coze(tag: str, num: int) -> List[XhsNote]:
    """
    根据标签获取小红书笔记（使用Coze插件）

    Args:
        tag: 搜索的标签
        num: 获取的笔记数量

    Returns:
        存储的笔记列表
    """
    # 设置API参数
    parameters = {
        "search_tag": tag,
        "search_num": num,
        "cookie": settings.XHS_COOKIE,
    }

    result = CozeService.call_coze_api(
        workflow_id="7480441452158648331",
        parameters=parameters,
        log_file_prefix="get_notes_by_tag",
    )

    # 处理响应
    response_obj, data_json = CozeService.process_response(result, XhsSearchResponse)
    if not response_obj:
        return []

    # 准备请求信息
    req_info = {"keywords": tag, "search_num": num}

    # 存储数据
    return await CozeService.store_data_in_db(
        db_method=NoteDAO.store_coze_search_note_list,
        req_info=req_info,
        response_obj=response_obj,
        data_type="笔记",
    )


async def finish_note_detail(use_coze: bool = False):
    """
    补全没有笔记详情的笔记内容，查询所有没有详情内容的笔记，然后通过爬虫获取详情并更新

    Args:
        use_coze: 是否使用Coze API获取笔记详情，默认使用爬虫

    Returns:
        处理的笔记数量
    """
    logger.info("开始查询并补全笔记详情内容")

    async for session in get_async_db():
        db: AsyncSession = session

        try:
            stmt = text(
                """
                SELECT xhs_notes.note_id, xhs_notes.note_url, xhs_notes.note_xsec_token 
                FROM xhs_notes 
                LEFT JOIN xhs_note_details ON xhs_notes.note_id = xhs_note_details.note_id
                WHERE xhs_note_details.note_desc IS NULL OR xhs_note_details.note_id IS NULL
            """
            )
            processed_count = 0
            result = await db.execute(stmt)
            notes_to_process = result.all()
            logger.info(f"找到 {len(notes_to_process)} 条需要补全详情的笔记")
            for index, note_record in enumerate(notes_to_process):
                note_id = note_record[0]
                note_url = note_record[1]
                note_xsec_token = note_record[2]

                try:
                    # 构建完整URL
                    if not note_url or "xsec_token" not in note_url:
                        note_url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={note_xsec_token}&xsec_source=pc_note"
                    logger.info(f"处理第 {index} 条笔记: {note_url}")
                    if use_coze:
                        note_detail = await get_note_detail_by_coze(note_url)
                    else:
                        note_detail = await get_note_detail_by_spider(note_url)

                    if note_detail:
                        processed_count += 1
                    else:
                        logger.warning(f"获取笔记详情页失败: {note_url}")
                except Exception as e:
                    logger.error(f"处理笔记 {note_id} 时出错: {str(e)}")

                # 随机等待1-5秒
                sleep_time = random.randint(1, 3)
                logger.info(f"等待 {sleep_time} 秒后继续...")
                time.sleep(sleep_time)

            logger.info("完成笔记详情补全任务")

        except Exception as e:
            logger.error(f"处理笔记详情时出错: {e}")
            logger.error(traceback.format_exc())
            return 0
        finally:
            await db.close()
