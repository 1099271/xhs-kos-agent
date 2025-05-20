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

from app.infra.db.async_database import Base


class XhsAuthor(Base):
    """小红书作者信息表"""

    __tablename__ = "xhs_authors"

    author_user_id = Column(
        String(64), primary_key=True, index=True, comment="作者用户ID"
    )
    author_nick_name = Column(String(128), nullable=True, comment="作者昵称")
    author_avatar = Column(String(255), nullable=True, comment="作者头像URL")
    author_home_page_url = Column(String(255), nullable=True, comment="作者主页URL")
    author_desc = Column(Text, nullable=True, comment="作者简介")
    author_interaction = Column(Integer, nullable=True, default=0, comment="互动数")
    author_ip_location = Column(String(64), nullable=True, comment="作者所在地")
    author_red_id = Column(String(64), nullable=True, comment="红书ID")
    author_tags = Column(JSON, nullable=True, comment="作者标签")
    author_fans = Column(Integer, nullable=True, default=0, comment="粉丝数量")
    author_follows = Column(Integer, nullable=True, default=0, comment="关注数量")
    author_gender = Column(String(16), nullable=True, comment="作者性别")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关系
    notes = relationship("XhsNote", back_populates="author")
    note_details = relationship("XhsNoteDetail", back_populates="author")

    model_config = {"from_attributes": True}
