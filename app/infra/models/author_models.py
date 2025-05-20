from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from app.infra.models.note_models import XhsNoteItem

from app.infra.db.async_database import Base


class XhsAuthor(Base):
    """小红书作者信息表"""

    __tablename__ = "xhs_authers"

    auther_user_id = Column(
        String(64), primary_key=True, index=True, comment="作者用户ID"
    )
    auther_nick_name = Column(String(128), nullable=True, comment="作者昵称")
    auther_avatar = Column(String(255), nullable=True, comment="作者头像URL")
    auther_home_page_url = Column(String(255), nullable=True, comment="作者主页URL")
    auther_desc = Column(Text, nullable=True, comment="作者简介")
    auther_interaction = Column(Integer, nullable=True, default=0, comment="互动数")
    auther_ip_location = Column(String(64), nullable=True, comment="作者所在地")
    auther_red_id = Column(String(64), nullable=True, comment="红书ID")
    auther_tags = Column(JSON, nullable=True, comment="作者标签")
    auther_fans = Column(Integer, nullable=True, default=0, comment="粉丝数量")
    auther_follows = Column(Integer, nullable=True, default=0, comment="关注数量")
    auther_gender = Column(String(16), nullable=True, comment="作者性别")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    notes = relationship("XhsNote", back_populates="auther")
    note_details = relationship("XhsNoteDetail", back_populates="auther")

    model_config = {"from_attributes": True}


class XhsAutherInfo(BaseModel):
    user_link_url: Optional[str] = None
    desc: Optional[str] = None
    interaction: Optional[str] = None
    ip_location: Optional[str] = None
    red_id: Optional[str] = None
    user_id: str
    tags: Optional[List[str]] = None
    avatar: Optional[str] = None
    fans: Optional[str] = None
    follows: Optional[str] = None
    gender: Optional[str] = None
    nick_name: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsAutherNotesData(BaseModel):
    notes: List[XhsNoteItem]
    auther_info: XhsAutherInfo
    cursor: Optional[str] = None
    has_more: Optional[bool] = False

    model_config = {"from_attributes": True}


class XhsAutherNotesResponse(BaseModel):
    data: XhsAutherNotesData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class AutherNotesRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsAutherNotesResponse
