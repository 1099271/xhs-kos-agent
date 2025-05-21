import json

from app.config.settings import settings
from app.ingest.xhs_spider.apis.pc_apis import XHS_Apis
from app.utils.logger import app_logger as logger
from app.utils.file import save_json_response


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
        save_json_response(notes, "spider_get_notes")

        if success and notes:
            logger.info(f"成功获取到 {len(notes)} 条笔记")
            return notes
        else:
            logger.warning(f"获取笔记失败: {msg}")
            return []
