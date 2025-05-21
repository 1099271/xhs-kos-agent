from typing import List

from app.infra.models.note_models import XhsNote

from app.services.coze.coze_service import CozeService
from app.config.settings import settings
from app.schemas.note_schemas import XhsSearchResponse
from app.infra.dao.note_dao import NoteDAO
from app.services.spider.spider_service import SpiderService

from app.infra.db.async_database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


class NoteService:
    def __init__(self):
        self.coze_service = CozeService()

    async def get_notes_by_topic_tag(
        self, tag: str, num: int, use_coze: bool = True
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
            return await self.get_notes_by_coze(tag, num)
        else:
            return await self.get_notes_by_spider(tag, num)

    async def get_notes_by_spider(self, tag: str, num: int) -> List[XhsNote]:
        """
        根据标签获取小红书笔记（使用Spider_XHS爬虫）
        """
        spider_service = SpiderService()
        notes_data = await spider_service.get_notes(tag, num)

        async for session in get_async_db():
            db: AsyncSession = session
            return await NoteDAO.store_spider_note_list(db, tag, notes_data)

    async def get_notes_by_coze(self, tag: str, num: int) -> List[XhsNote]:
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

        # 调用API
        result = self.coze_service.call_coze_api(
            workflow_id="7480441452158648331",
            parameters=parameters,
            log_file_prefix="get_notes_by_tag",
        )

        # 处理响应
        response_obj, data_json = CozeService.process_response(
            result, XhsSearchResponse
        )
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

    async def finish_note_detail(self):
        """
        补全没有笔记详情的笔记内容
        """
        pass
