import json

from app.config.settings import settings
from app.ingest.xhs_spider.apis.pc_apis import XHS_Apis
from app.utils.logger import app_logger as logger


class SpiderService:
    def __init__(self):
        self.spider_xhs = XHS_Apis()

    async def get_notes(self, tag: str, num: int):
        cookies_str = settings.XHS_COOKIE

        sort = "general"
        note_type = 0
        success, msg, notes = self.spider_xhs.search_some_note(
            tag, num, cookies_str, sort, note_type
        )

        # notes 是一个列表，每个元素是一个字典，包含笔记的详细信息
        # 例如: [{"note_id": "123", "title": "标题", "desc": "描述", ...}, ...]
        if success and notes:
            logger.info(f"成功获取到 {len(notes)} 条笔记")
            return notes
        else:
            logger.warning(f"获取笔记失败: {msg}")
            return []
