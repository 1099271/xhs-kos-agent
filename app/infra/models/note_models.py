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
from app.infra.db.async_database import Base

from app.infra.models.author_models import XhsAuthor
from app.infra.models.comment_models import XhsComment
from app.infra.models.keyword_models import XhsKeywordGroupNote
from app.infra.models.llm_models import LlmNoteDiagnosis, LlmCommentAnalysis
from app.infra.models.tag_models import TagComparisonResult


class XhsNote(Base):
    """小红书笔记摘要表"""

    __tablename__ = "xhs_notes"

    note_id = Column(String(64), primary_key=True, index=True, comment="笔记ID")
    author_user_id = Column(
        String(64), ForeignKey("xhs_authors.author_user_id"), comment="作者用户ID"
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
    author_user_id = Column(
        String(64), ForeignKey("xhs_authors.author_user_id"), comment="作者用户ID"
    )
    author_nick_name = Column(String(128), nullable=True, comment="作者昵称（冗余）")
    author_avatar = Column(String(255), nullable=True, comment="作者头像URL（冗余）")
    author_home_page_url = Column(
        String(255), nullable=True, comment="作者主页URL（冗余）"
    )
    note_status = Column(Integer, nullable=False, default=1, comment="笔记状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    author = relationship("XhsAuthor", back_populates="notes")
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
    author_user_id = Column(
        String(64), ForeignKey("xhs_authors.author_user_id"), comment="作者用户ID"
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
    author = relationship("XhsAuthor", back_populates="note_details")
