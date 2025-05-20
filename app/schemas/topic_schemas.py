from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class XhsTopicItem(BaseModel):
    """话题项目模型"""

    type: str
    view_num: str
    name: str
    smart: str


class XhsTopicsData(BaseModel):
    """话题数据模型"""

    topic_list: List[XhsTopicItem]


class XhsTopicsResponse(BaseModel):
    """话题响应模型"""

    msg: str = ""
    tips: str = ""
    code: int = 0
    data: XhsTopicsData


class TopicsRequest(BaseModel):
    """话题请求模型"""

    req_info: Dict[str, Any]
    req_body: XhsTopicsResponse
