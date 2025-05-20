from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from app.infra.db.async_database import Base


class XhsTopicDiscussion(Base):
    """小红书话题讨论量记录表"""

    __tablename__ = "xhs_topic_discussions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    topic_name = Column(String(255), nullable=False, comment="话题名称")
    topic_type = Column(String(32), nullable=False, comment="话题类型")
    view_num = Column(Integer, nullable=False, default=0, comment="讨论量/浏览数")
    smart = Column(Boolean, nullable=False, default=False, comment="是否智能")
    record_date = Column(DateTime, nullable=False, comment="记录日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    model_config = {"from_attributes": True}


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
