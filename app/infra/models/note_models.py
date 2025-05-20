from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from app.infra.db.async_database import Base


class XhsNote(Base):
    """小红书笔记摘要表"""

    __tablename__ = "xhs_notes"

    note_id = Column(String(64), primary_key=True, index=True, comment="笔记ID")
    auther_user_id = Column(
        String(64), ForeignKey("xhs_authers.auther_user_id"), comment="作者用户ID"
    )
    note_url = Column(String(255), nullable=False, comment="笔记URL")
    note_xsec_token = Column(String(255), nullable=True, comment="笔记xsec令牌")
    note_display_title = Column(String(255), nullable=True, comment="笔记标题")
    note_cover_url_pre = Column(String(255), nullable=True, comment="笔记预览封面URL")
    note_cover_url_default = Column(
        String(255), nullable=True, comment="笔记默认封面URL"
    )
    note_cover_width = Column(Integer, nullable=True, comment="封面宽度")
    note_cover_height = Column(Integer, nullable=True, comment="封面高度")
    note_liked_count = Column(Integer, nullable=True, default=0, comment="点赞数")
    note_liked = Column(Boolean, nullable=True, default=False, comment="是否已点赞")
    note_card_type = Column(String(32), nullable=True, comment="笔记卡片类型")
    note_model_type = Column(String(32), nullable=True, comment="笔记模型类型")
    note_sticky = Column(Boolean, nullable=True, default=False, comment="是否置顶")

    # 作者相关的冗余字段
    auther_user_id = Column(
        String(64), ForeignKey("xhs_authers.auther_user_id"), comment="作者用户ID"
    )
    auther_nick_name = Column(String(128), nullable=True, comment="作者昵称（冗余）")
    auther_avatar = Column(String(255), nullable=True, comment="作者头像URL（冗余）")
    auther_home_page_url = Column(
        String(255), nullable=True, comment="作者主页URL（冗余）"
    )
    note_status = Column(Integer, nullable=False, default=1, comment="笔记状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    auther = relationship("XhsAuther", back_populates="notes")
    details = relationship("XhsNoteDetail", back_populates="note", uselist=False)
    comments = relationship("XhsComment", back_populates="note")
    keyword_group_notes = relationship("XhsKeywordGroupNote", back_populates="note")
    llm_diagnoses = relationship(
        "LlmNoteDiagnosis",
        back_populates="note",
        foreign_keys="[LlmNoteDiagnosis.note_id]",
    )
    tag_comparison_results = relationship(
        "TagComparisonResult",
        back_populates="note",
        foreign_keys="[TagComparisonResult.note_id]",
    )
    llm_comment_analyses = relationship(
        "LlmCommentAnalysis",
        back_populates="note",
        foreign_keys="[LlmCommentAnalysis.note_id]",
    )

    model_config = {"from_attributes": True}


class XhsNoteDetail(Base):
    """小红书笔记详情表"""

    __tablename__ = "xhs_note_details"

    note_id = Column(
        String(64), ForeignKey("xhs_notes.note_id"), primary_key=True, comment="笔记ID"
    )
    note_url = Column(String(255), nullable=False, comment="笔记URL")
    auther_user_id = Column(
        String(64), ForeignKey("xhs_authers.auther_user_id"), comment="作者用户ID"
    )
    note_last_update_time = Column(DateTime, nullable=True, comment="最后更新时间")
    note_create_time = Column(DateTime, nullable=True, comment="创建时间")
    note_model_type = Column(String(32), nullable=True, comment="笔记模型类型")
    note_card_type = Column(String(32), nullable=True, comment="笔记卡片类型")
    note_display_title = Column(String(255), nullable=True, comment="笔记标题")
    note_desc = Column(Text, nullable=True, comment="笔记描述")
    comment_count = Column(Integer, nullable=True, default=0, comment="评论数")
    note_liked_count = Column(Integer, nullable=True, default=0, comment="点赞数")
    share_count = Column(Integer, nullable=True, default=0, comment="分享数")
    collected_count = Column(Integer, nullable=True, default=0, comment="收藏数")
    video_id = Column(String(64), nullable=True, comment="视频ID")
    video_h266_url = Column(String(255), nullable=True, comment="视频H266 URL")
    video_a1_url = Column(String(255), nullable=True, comment="视频a1 URL")
    video_h264_url = Column(String(255), nullable=True, comment="视频H264 URL")
    video_h265_url = Column(String(255), nullable=True, comment="视频H265 URL")
    note_duration = Column(Integer, nullable=True, comment="视频时长")
    note_image_list = Column(JSON, nullable=True, comment="笔记图片列表")
    note_tags = Column(JSON, nullable=True, comment="笔记标签")
    note_liked = Column(Boolean, nullable=True, default=False, comment="是否已点赞")
    collected = Column(Boolean, nullable=True, default=False, comment="是否已收藏")
    note_status = Column(Integer, nullable=False, default=1, comment="笔记状态")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="记录更新时间"
    )

    # 关系
    note = relationship("XhsNote", back_populates="details")
    auther = relationship("XhsAuther", back_populates="note_details")


class XhsNoteItem(BaseModel):
    note_id: str
    note_url: Optional[str] = None
    note_xsec_token: Optional[str] = None
    auther_user_id: Optional[str] = None
    auther_nick_name: Optional[str] = None
    auther_avatar: Optional[str] = None
    auther_home_page_url: Optional[str] = None
    note_display_title: Optional[str] = None
    note_cover_url_pre: Optional[str] = None
    note_cover_url_default: Optional[str] = None
    note_cover_width: Optional[str] = None
    note_cover_height: Optional[str] = None
    note_liked_count: Optional[str] = None
    note_liked: Optional[bool] = None
    note_card_type: Optional[str] = None
    note_model_type: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsSearchResponse(BaseModel):
    data: List[XhsNoteItem]
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class SearchNoteRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsSearchResponse


class XhsNoteDetailItem(BaseModel):
    note_last_update_time: Optional[str] = None
    note_model_type: Optional[str] = None
    video_h266_url: Optional[str] = None
    auther_avatar: Optional[str] = None
    note_card_type: Optional[str] = None
    note_desc: Optional[str] = None
    comment_count: Optional[str] = None
    note_liked_count: Optional[str] = None
    share_count: Optional[str] = None
    video_a1_url: Optional[str] = None
    auther_home_page_url: Optional[str] = None
    auther_user_id: Optional[str] = None
    collected_count: Optional[str] = None
    note_url: Optional[str] = None
    video_id: Optional[str] = None
    note_create_time: Optional[str] = None
    note_display_title: Optional[str] = None
    note_image_list: Optional[List[str]] = None
    note_tags: Optional[List[str]] = None
    video_h264_url: Optional[str] = None
    video_h265_url: Optional[str] = None
    auther_nick_name: Optional[str] = None
    note_duration: Optional[str] = None
    note_id: str
    note_liked: Optional[bool] = None
    collected: Optional[bool] = None

    model_config = {"from_attributes": True}


class XhsNoteDetailData(BaseModel):
    note: XhsNoteDetailItem

    model_config = {"from_attributes": True}


class XhsNoteDetailResponse(BaseModel):
    data: XhsNoteDetailData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class NoteDetailRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsNoteDetailResponse
