from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.infra.db.async_database import Base


class XhsKeywordGroup(Base):
    """小红书关键词群表"""

    __tablename__ = "xhs_keyword_groups"

    group_id = Column(Integer, primary_key=True, autoincrement=True, comment="群组ID")
    group_name = Column(String(100), nullable=True, comment="群组名称")
    keywords = Column(JSON, nullable=True, comment="关键词列表")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    notes = relationship("XhsKeywordGroupNote", back_populates="keyword_group")


class XhsKeywordGroupNote(Base):
    """小红书关键词群笔记关联表"""

    __tablename__ = "xhs_keyword_group_notes"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    group_id = Column(
        Integer, ForeignKey("xhs_keyword_groups.group_id"), comment="群组ID"
    )
    note_id = Column(String(64), ForeignKey("xhs_notes.note_id"), comment="笔记ID")
    retrieved_at = Column(DateTime, default=datetime.now, comment="检索时间")

    # 关系
    keyword_group = relationship("XhsKeywordGroup", back_populates="notes")
    note = relationship("XhsNote", back_populates="keyword_group_notes")
