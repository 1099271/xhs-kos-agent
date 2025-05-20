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
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from app.infra.db.async_database import Base


class XhsComment(Base):
    """小红书评论表"""

    __tablename__ = "xhs_comments"

    comment_id = Column(String(64), primary_key=True, index=True, comment="评论ID")
    note_id = Column(String(64), ForeignKey("xhs_notes.note_id"), comment="笔记ID")
    parent_comment_id = Column(String(64), nullable=True, comment="父评论ID")
    comment_user_id = Column(String(64), nullable=False, comment="评论用户ID")
    comment_user_image = Column(String(255), nullable=True, comment="评论者头像URL")
    comment_user_nickname = Column(String(128), nullable=True, comment="评论用户昵称")
    comment_user_home_page_url = Column(
        String(255), nullable=True, comment="评论者主页URL"
    )
    comment_content = Column(Text, nullable=True, comment="评论内容")
    comment_like_count = Column(Integer, nullable=True, default=0, comment="点赞数")
    comment_sub_comment_count = Column(
        Integer, nullable=True, default=0, comment="子评论数量"
    )
    comment_create_time = Column(DateTime, nullable=True, comment="评论创建时间")
    comment_liked = Column(Boolean, nullable=True, default=False, comment="是否已点赞")
    comment_show_tags = Column(JSON, nullable=True, comment="评论显示标签")
    comment_sub_comment_cursor = Column(
        String(64), nullable=True, comment="子评论分页游标"
    )
    comment_sub_comment_has_more = Column(
        Boolean, nullable=True, default=False, comment="子评论是否有更多"
    )
    ip_location = Column(String(255), nullable=True, comment="所在地")
    created_at = Column(DateTime, default=datetime.now, comment="记录创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="记录更新时间"
    )

    # 关系
    note = relationship("XhsNote", back_populates="comments")
    at_users = relationship("XhsCommentAtUser", back_populates="comment")


class XhsCommentAtUser(Base):
    """小红书评论@用户表"""

    __tablename__ = "xhs_comment_at_users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    comment_id = Column(
        String(64), ForeignKey("xhs_comments.comment_id"), comment="评论ID"
    )
    at_user_id = Column(String(64), nullable=False, comment="被@用户ID")
    at_user_nickname = Column(String(128), nullable=True, comment="被@用户昵称")
    at_user_home_page_url = Column(String(255), nullable=True, comment="被@用户主页")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    comment = relationship("XhsComment", back_populates="at_users")


class XhsCommentAtUserItem(BaseModel):
    at_user_id: str
    at_user_nickname: Optional[str] = None
    at_user_home_page_url: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsCommentSubItem(BaseModel):
    comment_id: str
    note_id: str
    comment_user_id: str
    comment_user_nickname: Optional[str] = None
    comment_user_image: Optional[str] = None
    comment_user_home_page_url: Optional[str] = None
    comment_content: Optional[str] = None
    comment_like_count: Optional[str] = None
    comment_sub_comment_count: Optional[str] = None
    comment_create_time: Optional[str] = None
    comment_liked: Optional[bool] = False
    comment_show_tags: Optional[List[str]] = None
    comment_sub_comment_cursor: Optional[str] = None
    comment_sub_comment_has_more: Optional[bool] = False
    comment_at_users: Optional[List[XhsCommentAtUserItem]] = Field(default_factory=list)
    comment_sub: Optional[List["XhsCommentSubItem"]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class XhsCommentItem(BaseModel):
    comment_id: str
    note_id: str
    comment_user_id: str
    comment_user_nickname: Optional[str] = None
    comment_user_image: Optional[str] = None
    comment_user_home_page_url: Optional[str] = None
    comment_content: Optional[str] = None
    comment_like_count: Optional[str] = None
    comment_sub_comment_count: Optional[str] = None
    comment_create_time: Optional[str] = None
    comment_liked: Optional[bool] = False
    comment_show_tags: Optional[List[str]] = None
    comment_sub_comment_cursor: Optional[str] = None
    comment_sub_comment_has_more: Optional[bool] = False
    comment_at_users: Optional[List[XhsCommentAtUserItem]] = Field(default_factory=list)
    comment_sub: Optional[List[XhsCommentSubItem]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class XhsCommentsData(BaseModel):
    comments: List[XhsCommentItem]
    cursor: Optional[str] = None
    has_more: Optional[bool] = False

    model_config = {"from_attributes": True}


class XhsCommentsResponse(BaseModel):
    data: XhsCommentsData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class CommentsRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsCommentsResponse
