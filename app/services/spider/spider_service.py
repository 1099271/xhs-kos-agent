from app.config.settings import settings
from app.ingest.xhs_spider.apis.xhs_pc_apis import XHS_Apis
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

    async def get_note_detail(self, note_url: str):
        cookies_str = settings.XHS_COOKIE
        success, msg, code, note_detail = self.spider_xhs.get_note_info(
            note_url, cookies_str
        )
        save_json_response(note_detail, "spider_get_note_detail")

        if success and code == 0 and note_detail:
            return note_detail
        elif code == 300013:
            raise SystemExit(f"爬虫触发防控规则，整体流程中止: {code}|{msg}")
        elif code == -510000:
            raise ValueError(f"笔记不存在: {code}|{msg}")
        elif code == -1:
            raise SystemExit(f"未知异常情况: {code}|{msg}")
        else:
            logger.error(f"获取笔记详情失败: {code}|{msg}")
            return {}

    async def get_note_comments(self, note_url: str):
        cookies_str = settings.XHS_COOKIE
        success, msg, note_all_comment = self.spider_xhs.get_note_all_comment(
            note_url, cookies_str
        )
        log_filename = save_json_response(note_all_comment, "spider_get_note_comments")

        if success and note_all_comment:
            return note_all_comment, log_filename
        else:
            raise ValueError(f"获取笔记评论失败: {msg}")
