from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.infra.db.async_database import Base


class LlmConfiguration(Base):
    """LLM配置表"""

    __tablename__ = "llm_configurations"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    config_alias = Column(String(128), nullable=False, unique=True, comment="配置别名")
    model_name = Column(String(128), nullable=False, comment="模型名称")
    parameter_size = Column(String(64), nullable=False, comment="模型参数大小")
    temperature = Column(DECIMAL(3, 2), nullable=True, comment="温度设置")
    top_p = Column(DECIMAL(3, 2), nullable=True)
    max_tokens = Column(Integer, nullable=True)
    model_type = Column(String(32), nullable=True)
    other_params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class LlmNoteDiagnosis(Base):
    """LLM笔记诊断表"""

    __tablename__ = "llm_note_diagnosis"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    note_id = Column(
        String(64),
        ForeignKey("xhs_notes.note_id"),
        nullable=False,
        index=True,
        comment="笔记ID",
    )
    llm_name = Column(String(128), nullable=False, comment="LLM模型名称")
    geo_tags = Column(JSON, nullable=True, comment="地理位置标签")
    cultural_tags = Column(JSON, nullable=True, comment="文化元素标签")
    other_tags = Column(JSON, nullable=True, comment="其他标签")
    user_gender = Column(String(16), nullable=True, comment="用户性别")
    user_age_range = Column(String(64), nullable=True, comment="年龄区间")
    user_location = Column(String(128), nullable=True, comment="地理位置")
    user_tags = Column(JSON, nullable=True, comment="用户标签")
    post_summary = Column(JSON, nullable=True, comment="帖子摘要")
    post_publish_time = Column(String(64), nullable=True, comment="发布时间")
    content_tendency = Column(String(16), nullable=True, comment="内容倾向")
    content_tendency_reason = Column(JSON, nullable=True, comment="倾向原因")
    has_visited = Column(Boolean, nullable=True, comment="是否去过")
    diagnosed_at = Column(DateTime, default=datetime.now, comment="诊断时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 添加反向关系
    note = relationship("XhsNote", back_populates="llm_diagnoses")


class LlmNoteTagExtraction(Base):
    """LLM笔记标签提取表"""

    __tablename__ = "llm_note_tag_extraction"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    note_id = Column(String(64), ForeignKey("xhs_notes.note_id"), comment="笔记ID")
    model_name = Column(String(128), nullable=False, comment="模型名称")
    extracted_tags = Column(JSON, nullable=True, comment="提取的标签")
    extraction_result = Column(Text, nullable=True, comment="提取结果")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class LlmCommentAnalysis(Base):
    """LLM评论分析结果表"""

    __tablename__ = "llm_comment_analysis"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    note_id = Column(
        String(64),
        ForeignKey("xhs_notes.note_id"),
        nullable=False,
        index=True,
        comment="笔记ID",
    )
    comment_user_id = Column(
        String(64), nullable=False, index=True, comment="评论用户ID"
    )
    comment_user_nickname = Column(String(128), nullable=True, comment="评论用户昵称")

    # 分析结果字段
    emotional_preference = Column(
        String(20), nullable=True, comment="情感倾向(正向/中性/负向/未知)"
    )
    emotional_desc = Column(Text, nullable=True, comment="情感倾向描述")
    aips_preference = Column(
        String(10), nullable=True, comment="AIPS偏好(A/I/TI/P/S/未知)"
    )
    has_visited = Column(String(10), nullable=True, comment="是否去过(是/否/未知)")
    unmet_preference = Column(
        String(10), nullable=True, comment="未满足需求偏好(是/否/未知)"
    )
    unmet_desc = Column(Text, nullable=True, comment="未满足需求描述")
    gender = Column(String(10), nullable=True, comment="性别(男/女/未知)")
    age = Column(String(20), nullable=True, comment="年龄段(如:90后/00后等)")

    # 元数据
    llm_alias = Column(String(50), nullable=True, comment="使用的LLM模型")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 添加反向关系
    note = relationship("XhsNote", back_populates="llm_comment_analyses")

    def __repr__(self):
        return f"<LlmCommentAnalysis(id={self.id}, note_id={self.note_id}, user_id={self.comment_user_id})>"
