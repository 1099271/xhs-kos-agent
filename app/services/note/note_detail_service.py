from app.config import settings
from app.utils.logger import app_logger as logger
from app.services.coze.coze_service import CozeService
from app.schemas.note_schemas import XhsNoteDetailResponse
from app.infra.dao.note_dao import NoteDAO
from app.services.spider.spider_service import SpiderService
from app.infra.db.async_database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_note_detail_by_coze(note_url: str) -> dict:
    # 设置API参数
    parameters = {"noteUrl": note_url}
    result = CozeService.call_coze_api(
        workflow_id="7480895021278920716",
        parameters=parameters,
        log_file_prefix="get_note_detail_by_coze",
    )

    # 处理响应
    response_obj, data_json = CozeService.process_response(
        result, XhsNoteDetailResponse
    )
    if not response_obj:
        return []

    req_info = {"noteUrl": note_url}

    # 存储数据
    return await CozeService.store_data_in_db(
        db_method=NoteDAO.store_coze_note_detail,
        req_info=req_info,
        response_obj=response_obj,
        data_type="笔记",
    )


async def get_note_detail_by_spider(note_url: str) -> dict:
    """
    根据标签获取小红书笔记详情（使用Spider_XHS爬虫）
    """
    spider_service = SpiderService()
    note_detail = await spider_service.get_note_detail(note_url)

    async for session in get_async_db():
        db: AsyncSession = session
        try:
            result = await NoteDAO.store_spider_note_detail(db, note_detail)
            return result
        finally:
            await db.close()  # 确保在任何情况下都关闭数据库连接
