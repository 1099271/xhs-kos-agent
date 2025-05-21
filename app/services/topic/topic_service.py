from typing import List

from app.config.settings import settings

from app.infra.dao.topic_dao import TopicDAO
from app.infra.models.topic_models import XhsTopicDiscussion, XhsTopicsResponse

from app.services.coze.coze_service import CozeService


class TopicService:
    def __init__(self):
        self.coze_service = CozeService()

    async def get_topics(self, tag: str) -> List[XhsTopicDiscussion]:
        """
        获取话题列表

        Args:
            tag: 搜索的标签

        Returns:
            存储的话题列表
        """
        # 设置API参数
        parameters = {"keyword": tag, "cookie": settings.XHS_COOKIE}

        # 调用API
        result = self.coze_service.call_coze_api(
            workflow_id="7480898701533397031",
            parameters=parameters,
            log_file_prefix="xhs_get_topics",
        )

        # 处理响应
        response_obj, data_json = CozeService.process_response(
            result, XhsTopicsResponse
        )
        if not response_obj:
            return []

        # 准备请求信息
        req_info = {"keyword": tag}

        # 存储数据
        return await CozeService.store_data_in_db(
            db_method=TopicDAO.store_topics,
            req_info=req_info,
            response_obj=response_obj,
            data_type="话题",
        )
