from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.infra.db.async_database import Base


class TagStandard(Base):
    """标准标签模型"""

    __tablename__ = "tag_standards"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    tag_name = Column(String(128), nullable=False, comment="标签名称")
    tag_type = Column(String(32), nullable=False, comment="标签类型")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )


class TagComparisonResult(Base):
    """标签对比结果模型"""

    __tablename__ = "tag_comparison_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增主键")
    note_id = Column(
        String(64), ForeignKey("xhs_notes.note_id"), nullable=False, comment="笔记ID"
    )
    llm_name = Column(String(128), nullable=False, comment="LLM模型名称")
    tag_type = Column(String(32), nullable=False, comment="标签类型")
    compare_model_name = Column(String(255), nullable=False, comment="比较模型名称")
    collected_tags = Column(JSON, nullable=False, comment="收集到的标签列表")
    standard_tags = Column(JSON, nullable=False, comment="对应的标准标签列表")
    similarity_matrix = Column(JSON, nullable=False, comment="相似度矩阵")
    max_similarity = Column(
        Float(precision=3), nullable=False, comment="最大匹配相似度"
    )
    optimal_matching = Column(
        Float(precision=3), nullable=False, comment="最优匹配相似度"
    )
    threshold_matching = Column(
        Float(precision=3), nullable=False, comment="阈值匹配相似度"
    )
    average_similarity = Column(
        Float(precision=3), nullable=False, comment="平均相似度"
    )
    coverage = Column(Float(precision=3), nullable=False, comment="标签覆盖率")
    weighted_score = Column(Float(precision=3), nullable=False, comment="加权总分")
    interpretation = Column(String(64), nullable=False, comment="相似度解释")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    note = relationship("XhsNote", back_populates="tag_comparison_results")
