"""
LlamaIndex集成模块
提供智能文档索引、语义搜索和知识检索功能
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.indices.postprocessor import SimilarityPostprocessor

try:
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI
except ImportError:
    # Fallback for different llama-index versions
    try:
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding
    except ImportError:
        OpenAI = None
        OpenAIEmbedding = None

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.infra.db.async_database import get_session_context
from app.infra.models.comment_models import XhsComment
from app.infra.models.note_models import XhsNote
from app.infra.models.llm_models import LlmCommentAnalysis
from app.config.settings import settings
from app.utils.logger import app_logger as logger


class LlamaIndexManager:
    """LlamaIndex管理器 - 提供智能文档索引和检索功能"""

    def __init__(self, persist_dir: str = "./storage"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)

        # 索引存储
        self.comment_index: Optional[VectorStoreIndex] = None
        self.note_index: Optional[VectorStoreIndex] = None
        self.analysis_index: Optional[VectorStoreIndex] = None

        # 配置LlamaIndex设置
        self._setup_llamaindex_settings()

        # 初始化存储上下文
        self._init_storage_context()

    def _setup_llamaindex_settings(self):
        """配置LlamaIndex全局设置"""

        # 设置嵌入模型
        try:
            # 优先使用OpenAI嵌入模型
            if settings.OPENAI_KEY and OpenAIEmbedding:
                Settings.embed_model = OpenAIEmbedding(
                    api_key=settings.OPENAI_KEY, model="text-embedding-3-small"
                )
                logger.info("✅ 使用OpenAI嵌入模型")
            else:
                logger.warning("⚠️ 未配置嵌入模型，使用默认模型")

        except Exception as e:
            logger.warning(f"⚠️ 嵌入模型设置失败，使用默认模型: {e}")

        # 设置LLM
        try:
            if settings.OPENAI_KEY and OpenAI:
                Settings.llm = OpenAI(
                    api_key=settings.OPENAI_KEY, model="gpt-3.5-turbo"
                )
                logger.info("✅ 使用OpenAI LLM")
        except Exception as e:
            logger.warning(f"⚠️ LLM设置失败: {e}")

        # 设置文本分割器
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    def _init_storage_context(self):
        """初始化存储上下文"""

        # 为不同类型的数据创建独立的存储
        self.comment_storage_dir = self.persist_dir / "comments"
        self.note_storage_dir = self.persist_dir / "notes"
        self.analysis_storage_dir = self.persist_dir / "analysis"

        for storage_dir in [
            self.comment_storage_dir,
            self.note_storage_dir,
            self.analysis_storage_dir,
        ]:
            storage_dir.mkdir(exist_ok=True)

    async def build_comment_index(self, limit: int = 1000) -> bool:
        """构建评论数据索引"""

        logger.info(f"🔍 开始构建评论数据索引 (限制: {limit}条)")

        try:
            # 从数据库获取评论数据
            async with get_session_context() as session:
                query = select(XhsComment).limit(limit)
                result = await session.execute(query)
                comments = result.scalars().all()

            if not comments:
                logger.warning("❌ 没有找到评论数据")
                return False

            # 转换为LlamaIndex文档
            documents = []
            for comment in comments:
                content = f"""
评论ID: {comment.comment_id}
笔记ID: {comment.note_id}
用户昵称: {comment.comment_user_nickname}
评论内容: {comment.comment_content}
点赞数: {comment.comment_like_count}
创建时间: {comment.comment_create_time}
"""

                doc = Document(
                    text=content,
                    metadata={
                        "comment_id": comment.comment_id,
                        "note_id": comment.note_id,
                        "user_id": comment.comment_user_id,
                        "user_nickname": comment.comment_user_nickname,
                        "like_count": comment.comment_like_count,
                        "create_time": str(comment.comment_create_time),
                        "type": "comment",
                    },
                )
                documents.append(doc)

            # 创建存储上下文
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.comment_storage_dir)
            )

            # 构建索引
            self.comment_index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, show_progress=True
            )

            # 持久化索引
            self.comment_index.storage_context.persist(
                persist_dir=str(self.comment_storage_dir)
            )

            logger.info(f"✅ 评论索引构建完成，共处理 {len(documents)} 条评论")
            return True

        except Exception as e:
            logger.error(f"❌ 构建评论索引失败: {e}")
            return False

    async def build_note_index(self, limit: int = 500) -> bool:
        """构建笔记数据索引"""

        logger.info(f"📝 开始构建笔记数据索引 (限制: {limit}条)")

        try:
            # 从数据库获取笔记数据
            async with get_session_context() as session:
                query = select(XhsNote).limit(limit)
                result = await session.execute(query)
                notes = result.scalars().all()

            if not notes:
                logger.warning("❌ 没有找到笔记数据")
                return False

            # 转换为LlamaIndex文档
            documents = []
            for note in notes:
                content = f"""
笔记ID: {note.note_id}
标题: {note.note_display_title}
作者ID: {note.author_user_id}
点赞数: {note.note_liked_count}
卡片类型: {note.note_card_type}
模型类型: {note.note_model_type}
创建时间: {note.created_at if hasattr(note, 'created_at') else 'N/A'}
"""

                doc = Document(
                    text=content,
                    metadata={
                        "note_id": note.note_id,
                        "title": note.note_display_title,
                        "author_user_id": note.author_user_id,
                        "liked_count": note.note_liked_count,
                        "card_type": note.note_card_type,
                        "model_type": note.note_model_type,
                        "created_at": (
                            str(note.created_at)
                            if hasattr(note, "created_at")
                            else "N/A"
                        ),
                        "type": "note",
                    },
                )
                documents.append(doc)

            # 创建存储上下文
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.note_storage_dir)
            )

            # 构建索引
            self.note_index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, show_progress=True
            )

            # 持久化索引
            self.note_index.storage_context.persist(
                persist_dir=str(self.note_storage_dir)
            )

            logger.info(f"✅ 笔记索引构建完成，共处理 {len(documents)} 条笔记")
            return True

        except Exception as e:
            logger.error(f"❌ 构建笔记索引失败: {e}")
            return False

    async def build_analysis_index(self, limit: int = 1000) -> bool:
        """构建LLM分析数据索引"""

        logger.info(f"🧠 开始构建LLM分析数据索引 (限制: {limit}条)")

        try:
            # 从数据库获取LLM分析数据
            async with get_session_context() as session:
                query = select(LlmCommentAnalysis).limit(limit)
                result = await session.execute(query)
                analyses = result.scalars().all()

            if not analyses:
                logger.warning("❌ 没有找到LLM分析数据")
                return False

            # 转换为LlamaIndex文档
            documents = []
            for analysis in analyses:
                content = f"""
分析ID: {analysis.id}
评论ID: {analysis.comment_id}
笔记ID: {analysis.note_id}
用户昵称: {analysis.comment_user_nickname}
情感倾向: {analysis.emotional_preference}
AIPS偏好: {analysis.aips_preference}
是否去过: {analysis.has_visited}
未满足需求: {analysis.unmet_preference}
未满足需求描述: {analysis.unmet_desc}
性别: {analysis.gender}
年龄: {analysis.age}
分析时间: {analysis.created_at}
"""

                doc = Document(
                    text=content,
                    metadata={
                        "analysis_id": analysis.id,
                        "comment_id": analysis.comment_id,
                        "note_id": analysis.note_id,
                        "user_id": analysis.comment_user_id,
                        "user_nickname": analysis.comment_user_nickname,
                        "emotional_preference": analysis.emotional_preference,
                        "aips_preference": analysis.aips_preference,
                        "has_visited": analysis.has_visited,
                        "unmet_preference": analysis.unmet_preference,
                        "gender": analysis.gender,
                        "age": analysis.age,
                        "created_at": str(analysis.created_at),
                        "type": "analysis",
                    },
                )
                documents.append(doc)

            # 创建存储上下文
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.analysis_storage_dir)
            )

            # 构建索引
            self.analysis_index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, show_progress=True
            )

            # 持久化索引
            self.analysis_index.storage_context.persist(
                persist_dir=str(self.analysis_storage_dir)
            )

            logger.info(f"✅ LLM分析索引构建完成，共处理 {len(documents)} 条分析")
            return True

        except Exception as e:
            logger.error(f"❌ 构建LLM分析索引失败: {e}")
            return False

    def load_existing_indexes(self) -> bool:
        """加载已存在的索引"""

        logger.info("📂 加载已存在的索引")

        try:
            # 加载评论索引
            if (self.comment_storage_dir / "docstore.json").exists():
                try:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=str(self.comment_storage_dir)
                    )
                    self.comment_index = VectorStoreIndex.from_documents(
                        [], storage_context=storage_context
                    )
                    logger.info("✅ 评论索引加载成功")
                except Exception as e:
                    logger.warning(f"⚠️ 评论索引加载失败: {e}")

            # 加载笔记索引
            if (self.note_storage_dir / "docstore.json").exists():
                try:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=str(self.note_storage_dir)
                    )
                    self.note_index = VectorStoreIndex.from_documents(
                        [], storage_context=storage_context
                    )
                    logger.info("✅ 笔记索引加载成功")
                except Exception as e:
                    logger.warning(f"⚠️ 笔记索引加载失败: {e}")

            # 加载分析索引
            if (self.analysis_storage_dir / "docstore.json").exists():
                try:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=str(self.analysis_storage_dir)
                    )
                    self.analysis_index = VectorStoreIndex.from_documents(
                        [], storage_context=storage_context
                    )
                    logger.info("✅ LLM分析索引加载成功")
                except Exception as e:
                    logger.warning(f"⚠️ LLM分析索引加载失败: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ 加载索引失败: {e}")
            return False

    async def semantic_search(
        self,
        query: str,
        index_type: str = "all",
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """语义搜索"""

        logger.info(f"🔍 执行语义搜索: '{query}' (类型: {index_type}, Top-K: {top_k})")

        results = []

        try:
            # 选择要搜索的索引
            indexes_to_search = []

            if index_type == "all" or index_type == "comment":
                if self.comment_index:
                    indexes_to_search.append(("comment", self.comment_index))

            if index_type == "all" or index_type == "note":
                if self.note_index:
                    indexes_to_search.append(("note", self.note_index))

            if index_type == "all" or index_type == "analysis":
                if self.analysis_index:
                    indexes_to_search.append(("analysis", self.analysis_index))

            # 对每个索引执行搜索
            for index_name, index in indexes_to_search:
                try:
                    # 创建检索器
                    retriever = VectorIndexRetriever(
                        index=index, similarity_top_k=top_k
                    )

                    # 执行检索
                    nodes = retriever.retrieve(query)

                    # 处理结果
                    for node in nodes:
                        # 修复: 处理 node.score 可能为 None 的情况
                        if (
                            node.score is not None
                            and node.score >= similarity_threshold
                        ):
                            result = {
                                "index_type": index_name,
                                "content": node.text,
                                "metadata": node.metadata,
                                "score": node.score,
                                "node_id": node.node_id,
                            }
                            results.append(result)

                except Exception as e:
                    logger.warning(f"⚠️ 搜索索引 {index_name} 失败: {e}")

            # 按相似度分数排序
            results.sort(key=lambda x: x["score"], reverse=True)

            logger.info(f"✅ 语义搜索完成，找到 {len(results)} 个相关结果")
            return results[:top_k]

        except Exception as e:
            logger.error(f"❌ 语义搜索失败: {e}")
            return []

    async def intelligent_query(
        self, question: str, context_type: str = "all", max_context_length: int = 2000
    ) -> Optional[str]:
        """智能问答 - 基于索引内容回答问题"""

        logger.info(f"❓ 智能问答: '{question}' (上下文类型: {context_type})")

        try:
            # 首先进行语义搜索获取相关内容
            search_results = await self.semantic_search(
                query=question,
                index_type=context_type,
                top_k=3,
                similarity_threshold=0.6,
            )

            if not search_results:
                logger.warning("⚠️ 没有找到相关内容")
                return "抱歉，没有找到与您问题相关的信息。"

            # 构建上下文
            context_parts = []
            current_length = 0

            for result in search_results:
                content = result["content"]
                if current_length + len(content) <= max_context_length:
                    context_parts.append(f"[{result['index_type']}] {content}")
                    current_length += len(content)
                else:
                    break

            context = "\n\n".join(context_parts)

            # 使用LLM生成答案
            from app.agents.llm_manager import call_llm

            system_prompt = """你是一个专业的数据分析助手，基于提供的上下文信息回答用户问题。

请注意：
1. 只基于提供的上下文信息回答
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、简洁、有用
4. 可以进行合理的分析和推理"""

            user_prompt = f"""基于以下上下文信息回答问题：

上下文信息：
{context}

用户问题：{question}

请提供详细、准确的回答。"""

            answer = await call_llm(system_prompt, user_prompt)

            if answer:
                logger.info("✅ 智能问答完成")
                return answer
            else:
                logger.warning("⚠️ LLM回答生成失败")
                return "抱歉，无法生成回答，请稍后重试。"

        except Exception as e:
            logger.error(f"❌ 智能问答失败: {e}")
            return f"查询过程中出现错误: {str(e)}"

    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """获取特定用户的深度洞察"""

        logger.info(f"👤 获取用户洞察: {user_id}")

        try:
            # 搜索该用户的所有相关信息
            user_query = f"用户ID:{user_id} OR comment_user_id:{user_id}"

            search_results = await self.semantic_search(
                query=user_query, index_type="all", top_k=10, similarity_threshold=0.5
            )

            # 分类整理结果
            comments = []
            notes = []
            analyses = []

            for result in search_results:
                if result["index_type"] == "comment":
                    comments.append(result)
                elif result["index_type"] == "note":
                    notes.append(result)
                elif result["index_type"] == "analysis":
                    analyses.append(result)

            # 生成用户洞察报告
            insights = {
                "user_id": user_id,
                "total_records": len(search_results),
                "comments_count": len(comments),
                "notes_count": len(notes),
                "analyses_count": len(analyses),
                "comments": comments,
                "notes": notes,
                "analyses": analyses,
                "summary": f"用户 {user_id} 共有 {len(search_results)} 条相关记录",
                "generated_at": datetime.now().isoformat(),
            }

            logger.info(f"✅ 用户洞察获取完成: {len(search_results)} 条记录")
            return insights

        except Exception as e:
            logger.error(f"❌ 获取用户洞察失败: {e}")
            return {"error": str(e)}

    async def build_all_indexes(self) -> Dict[str, bool]:
        """构建所有索引"""

        logger.info("🏗️ 开始构建所有索引")

        results = {}

        # 构建评论索引
        results["comment_index"] = await self.build_comment_index()

        # 构建笔记索引
        results["note_index"] = await self.build_note_index()

        # 构建分析索引
        results["analysis_index"] = await self.build_analysis_index()

        success_count = sum(results.values())
        total_count = len(results)

        logger.info(f"🎉 索引构建完成: {success_count}/{total_count} 个索引成功")

        return results


# 全局LlamaIndex管理器实例
llamaindex_manager = LlamaIndexManager()
