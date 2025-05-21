from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.models.comment_models import XhsComment, XhsCommentAtUser
from app.schemas.comment_schemas import (
    XhsCommentItem,
    XhsCommentsResponse,
    XhsCommentAtUserItem,
)
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback
import json
from sqlalchemy import select

from app.utils.logger import app_logger as logger


class CommentDAO:
    @staticmethod
    async def store_coze_comments(
        db: AsyncSession,
        req_info: Dict[str, Any],
        comments_response: XhsCommentsResponse,
    ) -> List[XhsComment]:
        """存储评论数据，确保幂等性操作"""

        # 在开始前确保会话是干净的
        await db.rollback()

        try:
            # 获取评论数据
            comments_data = comments_response.data.comments

            if not comments_data:
                logger.warning("请求体中缺少有效的评论数据")
                return []

            logger.info(f"开始处理评论数据，共 {len(comments_data)} 条评论")

            # 收集所有评论ID和用户ID
            comment_ids = []
            user_ids = []

            for comment in comments_data:
                comment_ids.append(comment.comment_id)
                user_ids.append(comment.comment_user_id)

                # 收集子评论的ID和用户ID
                for sub_comment in comment.comment_sub:
                    comment_ids.append(sub_comment.comment_id)
                    user_ids.append(sub_comment.comment_user_id)

            # 去重
            comment_ids = list(set(comment_ids))
            user_ids = list(set(user_ids))

            logger.info(
                f"共有 {len(comment_ids)} 条不重复评论，{len(user_ids)} 个不重复用户"
            )

            # 查询已存在的评论
            stmt = select(XhsComment).filter(XhsComment.comment_id.in_(comment_ids))
            result = await db.execute(stmt)
            existing_comments = {
                comment.comment_id: comment for comment in result.scalars().all()
            }

            logger.info(f"找到 {len(existing_comments)} 条已存在的评论")

            # 存储评论数据
            stored_comments = []

            for comment_item in comments_data:
                try:
                    # 处理主评论
                    comment = await CommentDAO._process_comment(
                        db, comment_item, existing_comments
                    )

                    # 处理@用户
                    if comment_item.comment_at_users:
                        for at_user in comment_item.comment_at_users:
                            await CommentDAO._process_comment_at_user(
                                db, comment.comment_id, at_user
                            )

                    # 处理子评论
                    if comment_item.comment_sub:
                        for sub_comment_item in comment_item.comment_sub:
                            sub_comment = await CommentDAO._process_comment(
                                db,
                                sub_comment_item,
                                existing_comments,
                                parent_id=comment.comment_id,
                            )

                            # 处理子评论的@用户
                            if sub_comment_item.comment_at_users:
                                for at_user in sub_comment_item.comment_at_users:
                                    await CommentDAO._process_comment_at_user(
                                        db, sub_comment.comment_id, at_user
                                    )

                    stored_comments.append(comment)

                except Exception as e:
                    logger.error(f"处理评论时出错 {comment_item.comment_id}: {str(e)}")
                    continue

            # 提交事务
            try:
                await db.flush()
                await db.commit()
                logger.info(f"成功处理并存储 {len(stored_comments)} 条评论数据")
            except Exception as e:
                await db.rollback()
                error_detail = f"提交事务时出错: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
                logger.error(error_detail)
                logger.warning("由于事务提交错误，可能有部分数据未能成功存储")

            return stored_comments

        except Exception as e:
            await db.rollback()
            error_detail = f"{str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
            logger.error(f"存储评论过程中发生错误: {error_detail}")
            raise

    @classmethod
    async def _process_comment(
        cls,
        db: AsyncSession,
        comment_item: "XhsCommentItem",
        existing_comments: Dict[str, XhsComment],
        parent_id: Optional[str] = None,
    ) -> XhsComment:
        """处理单条评论数据"""

        # 检查评论是否已存在
        comment = existing_comments.get(comment_item.comment_id)

        # 转换评论创建时间
        comment_create_time = None
        if comment_item.comment_create_time:
            try:
                comment_create_time = datetime.strptime(
                    comment_item.comment_create_time, "%Y-%m-%d %H:%M:%S"
                )
            except Exception as e:
                logger.warning(f"解析评论创建时间出错: {str(e)}")
                comment_create_time = datetime.now()
        else:
            comment_create_time = datetime.now()

        # 转换评论标签
        comment_show_tags = None
        if comment_item.comment_show_tags:
            try:
                comment_show_tags = json.dumps(comment_item.comment_show_tags)
            except Exception as e:
                logger.warning(f"转换评论标签出错: {str(e)}")

        if not comment:
            # 创建新评论
            comment = XhsComment(
                comment_id=comment_item.comment_id,
                note_id=comment_item.note_id,
                parent_comment_id=parent_id,
                comment_user_id=comment_item.comment_user_id,
                comment_user_image=comment_item.comment_user_image,
                comment_user_nickname=comment_item.comment_user_nickname,
                comment_user_home_page_url=comment_item.comment_user_home_page_url,
                comment_content=comment_item.comment_content,
                comment_like_count=(
                    int(comment_item.comment_like_count)
                    if comment_item.comment_like_count
                    and str(comment_item.comment_like_count).isdigit()
                    else 0
                ),
                comment_sub_comment_count=(
                    int(comment_item.comment_sub_comment_count)
                    if comment_item.comment_sub_comment_count
                    and str(comment_item.comment_sub_comment_count).isdigit()
                    else 0
                ),
                comment_create_time=comment_create_time,
                comment_liked=comment_item.comment_liked,
                comment_show_tags=comment_show_tags,
                comment_sub_comment_cursor=comment_item.comment_sub_comment_cursor,
                comment_sub_comment_has_more=comment_item.comment_sub_comment_has_more,
            )
            db.add(comment)
            await db.flush()
            existing_comments[comment.comment_id] = comment
            logger.info(f"创建新评论: {comment.comment_id}")
        else:
            # 更新现有评论
            comment.note_id = comment_item.note_id
            comment.parent_comment_id = parent_id
            comment.comment_user_id = comment_item.comment_user_id
            comment.comment_user_image = comment_item.comment_user_image
            comment.comment_user_nickname = comment_item.comment_user_nickname
            comment.comment_user_home_page_url = comment_item.comment_user_home_page_url
            comment.comment_content = comment_item.comment_content
            comment.comment_like_count = (
                int(comment_item.comment_like_count)
                if comment_item.comment_like_count
                and str(comment_item.comment_like_count).isdigit()
                else 0
            )
            comment.comment_sub_comment_count = (
                int(comment_item.comment_sub_comment_count)
                if comment_item.comment_sub_comment_count
                and str(comment_item.comment_sub_comment_count).isdigit()
                else 0
            )
            comment.comment_create_time = comment_create_time
            comment.comment_liked = comment_item.comment_liked
            comment.comment_show_tags = comment_show_tags
            comment.comment_sub_comment_cursor = comment_item.comment_sub_comment_cursor
            comment.comment_sub_comment_has_more = (
                comment_item.comment_sub_comment_has_more
            )
            comment.updated_at = datetime.now()
            logger.info(f"更新评论: {comment.comment_id}")

        return comment

    @staticmethod
    async def _process_comment_at_user(
        db: AsyncSession, comment_id: str, at_user_item: "XhsCommentAtUserItem"
    ) -> XhsCommentAtUser:
        """处理评论@用户数据"""

        # 检查@用户关系是否已存在
        stmt = select(XhsCommentAtUser).filter(
            XhsCommentAtUser.comment_id == comment_id,
            XhsCommentAtUser.at_user_id == at_user_item.at_user_id,
        )
        result = await db.execute(stmt)
        at_user = result.scalars().first()

        if not at_user:
            # 创建新的@用户关系
            at_user = XhsCommentAtUser(
                comment_id=comment_id,
                at_user_id=at_user_item.at_user_id,
                at_user_nickname=at_user_item.at_user_nickname,
                at_user_home_page_url=at_user_item.at_user_home_page_url,
            )
            db.add(at_user)
            await db.flush()
            logger.info(f"创建新的@用户关系: {comment_id} -> {at_user_item.at_user_id}")
        else:
            # 更新现有@用户关系
            at_user.at_user_nickname = at_user_item.at_user_nickname
            at_user.at_user_home_page_url = at_user_item.at_user_home_page_url
            logger.info(f"更新@用户关系: {comment_id} -> {at_user_item.at_user_id}")

        return at_user

    async def store_spider_note_detail(
        db: AsyncSession, note_all_comment: List[XhsCommentItem], log_filename: str
    ):
        # 判断评论数量
        comment_count = (
            len(note_all_comment) if isinstance(note_all_comment, list) else 0
        )
        if comment_count > 50:
            logger.info(f"评论数量过多 ({comment_count}条)，从文件读取数据")
            try:
                with open(log_filename, "r", encoding="utf-8") as f:
                    note_all_comment = json.load(f)
            except Exception as e:
                logger.error(f"从文件读取评论数据失败: {str(e)}")

    async def store_comments_from_spider(
        db: AsyncSession, note_all_comment: List[Dict[str, Any]]
    ):
        """从爬虫获取的笔记评论数据（包含主评论和子评论），存储到数据库中。"""

        if not note_all_comment or not isinstance(note_all_comment, list):
            # 这种大概率是这条笔记找不到了
            raise Exception(f"无效的评论数据输入 (类型或为空): {note_all_comment}")

        stored_count = 0
        updated_count = 0
        processed_comment_ids = set()  # 用于防止重复处理同一评论（如果数据源有重叠）

        try:
            # 1. 收集所有评论ID以批量查询
            all_comment_ids = []
            queue = list(note_all_comment)  # 使用队列进行迭代处理
            while queue:
                comment_data = queue.pop(0)
                if isinstance(comment_data, dict):
                    comment_id = comment_data.get("id")
                    if comment_id:
                        all_comment_ids.append(str(comment_id))
                    # 将子评论也加入队列
                    sub_comments = comment_data.get("sub_comments", [])
                    if isinstance(sub_comments, list):
                        queue.extend(sub_comments)
                else:
                    logger.warning(f"评论数据列表中包含非字典元素: {comment_data}")

            all_comment_ids = list(set(all_comment_ids))
            if not all_comment_ids:
                logger.info("评论数据中未找到任何评论ID")
                return  # 无需继续，直接返回

            # 2. 批量查询已存在的评论 (改为异步方式)
            existing_comments = {}
            try:
                # 使用AsyncSession的异步查询方法
                stmt = select(XhsComment).filter(
                    XhsComment.comment_id.in_(all_comment_ids)
                )
                result = await db.execute(stmt)
                existing_comments = {
                    comment.comment_id: comment for comment in result.scalars().all()
                }
                logger.info(f"查询到 {len(existing_comments)} 条已存在的评论记录")
            except Exception as e:
                logger.error(f"批量查询评论时出错: {e}", exc_info=True)
                # 即使查询失败，也尝试继续处理，但可能导致重复插入或更新失败

            # 3. 处理并存储评论 (转换为异步方法)
            async def _process_and_store_comment_async(
                comment_data: Dict[str, Any], parent_id: Optional[str] = None
            ):
                nonlocal stored_count, updated_count
                comment_id = comment_data.get("id")
                if not comment_id:
                    logger.warning(f"跳过缺少 'id' 的评论数据: {comment_data}")
                    return

                comment_id_str = str(comment_id)
                if comment_id_str in processed_comment_ids:
                    return  # 防止因数据源问题导致的无限递归或重复处理
                processed_comment_ids.add(comment_id_str)

                user_info = comment_data.get("user_info", {})
                note_id = comment_data.get("note_id")  # 评论数据中通常包含 note_id

                # 安全地获取和转换数据
                create_time_ms = comment_data.get("create_time")
                comment_create_time = None
                if create_time_ms:
                    try:
                        # 假设 create_time 是毫秒级时间戳
                        comment_create_time = datetime.fromtimestamp(
                            int(create_time_ms) / 1000
                        )
                    except (
                        ValueError,
                        TypeError,
                        OverflowError,
                    ) as e:  # 添加 OverflowError
                        logger.warning(
                            f"解析评论 {comment_id_str} 创建时间戳失败 ({create_time_ms}): {e}"
                        )
                        comment_create_time = datetime.now()
                else:
                    comment_create_time = datetime.now()

                like_count_str = comment_data.get("like_count", "0")
                comment_like_count = (
                    int(like_count_str)
                    if isinstance(like_count_str, str) and like_count_str.isdigit()
                    else 0
                )

                sub_comment_count_str = comment_data.get("sub_comment_count", "0")
                # 注意：顶层评论的 sub_comment_count 可能直接是子评论列表长度
                sub_comments_list = comment_data.get("sub_comments", [])
                actual_sub_comment_count = (
                    len(sub_comments_list) if isinstance(sub_comments_list, list) else 0
                )
                # 使用 API 返回的值（如果可靠）或实际列表长度
                comment_sub_comment_count = (
                    int(sub_comment_count_str)
                    if isinstance(sub_comment_count_str, str)
                    and sub_comment_count_str.isdigit()
                    else actual_sub_comment_count
                )

                comment_show_tags = None
                show_tags_data = comment_data.get("show_tags")
                if show_tags_data and isinstance(show_tags_data, list):
                    try:
                        comment_show_tags = json.dumps(
                            show_tags_data, ensure_ascii=False
                        )
                    except TypeError as e:
                        logger.warning(
                            f"序列化评论 {comment_id_str} 的 show_tags 失败 ({show_tags_data}): {e}"
                        )

                # 从 target_comment 中获取 parent_id (如果存在且是子评论)
                target_comment_info = comment_data.get("target_comment")
                effective_parent_id = parent_id  # 默认使用传入的 parent_id
                if target_comment_info and isinstance(target_comment_info, dict):
                    parent_id_from_target = target_comment_info.get("id")
                    if parent_id_from_target:
                        effective_parent_id = str(
                            parent_id_from_target
                        )  # 优先使用 target_comment 的 ID 作为 parent_id

                # 准备评论数据字典
                comment_db_data = {
                    "note_id": str(note_id) if note_id else None,
                    "parent_comment_id": effective_parent_id,
                    "comment_user_id": (
                        str(user_info.get("user_id"))
                        if user_info.get("user_id")
                        else None
                    ),
                    "comment_user_image": user_info.get("image"),
                    "comment_user_nickname": user_info.get("nickname"),
                    # 假设 user_info 中没有 home_page_url，尝试从 target_comment 的 user_info 获取（如果需要）
                    "comment_user_home_page_url": user_info.get(
                        "home_page_url"
                    ),  # 假设爬虫数据结构中有
                    "comment_content": comment_data.get("content"),
                    "comment_like_count": comment_like_count,
                    "comment_sub_comment_count": comment_sub_comment_count,
                    "comment_create_time": comment_create_time,
                    "comment_liked": comment_data.get("liked", False),
                    "comment_show_tags": comment_show_tags,
                    "comment_sub_comment_cursor": comment_data.get(
                        "sub_comment_cursor"
                    ),
                    "comment_sub_comment_has_more": comment_data.get(
                        "sub_comment_has_more", False
                    ),
                    "ip_location": (
                        str(comment_data.get("ip_location"))
                        if comment_data.get("ip_location")
                        else None
                    ),  # 尝试获取ip_location
                }
                # 不过滤，允许用 None 更新
                comment_db_data_filtered = comment_db_data

                # 获取或创建/更新评论记录
                existing_comment = existing_comments.get(comment_id_str)
                comment_obj = None
                is_new = False
                if existing_comment:
                    # 更新
                    is_updated = False
                    for key, value in comment_db_data_filtered.items():
                        if (
                            hasattr(existing_comment, key)
                            and getattr(existing_comment, key) != value
                        ):
                            setattr(existing_comment, key, value)
                            is_updated = True
                    if is_updated:
                        existing_comment.updated_at = datetime.now()
                        updated_count += 1
                    comment_obj = existing_comment

                else:
                    # 创建
                    # 需要确保所有必需字段存在，或者数据库允许 NULL
                    if not comment_db_data_filtered.get("note_id"):
                        logger.warning(f"评论 {comment_id_str} 缺少 note_id，无法创建")
                        return
                    if not comment_db_data_filtered.get("comment_user_id"):
                        logger.warning(f"评论 {comment_id_str} 缺少 user_id，无法创建")
                        return

                    comment_obj = XhsComment(
                        comment_id=comment_id_str, **comment_db_data_filtered
                    )
                    db.add(comment_obj)
                    # 执行flush确保评论实体已创建并分配ID
                    await db.flush()
                    existing_comments[comment_id_str] = (
                        comment_obj  # 添加到缓存，以便子评论查找
                    )
                    stored_count += 1
                    is_new = True

                # 处理 @ 用户 (只有在 comment_obj 有效时才处理)
                if comment_obj:
                    at_users_data = comment_data.get("at_users", [])
                    if (
                        isinstance(at_users_data, list) and at_users_data
                    ):  # 仅当列表非空时处理
                        try:
                            # 先查询现有的 @ 用户关系 ID (改为异步查询)
                            stmt = select(XhsCommentAtUser.at_user_id).filter(
                                XhsCommentAtUser.comment_id == comment_id_str
                            )
                            result = await db.execute(stmt)
                            existing_at_user_ids = {row[0] for row in result.all()}
                            current_at_user_ids = set()

                            for at_user_data in at_users_data:
                                if isinstance(at_user_data, dict):
                                    at_user_id = at_user_data.get("user_id")
                                    if at_user_id:
                                        at_user_id_str = str(at_user_id)
                                        current_at_user_ids.add(at_user_id_str)
                                        if at_user_id_str not in existing_at_user_ids:
                                            # 创建新的 @ 用户关系
                                            at_user_db = XhsCommentAtUser(
                                                comment_id=comment_id_str,
                                                at_user_id=at_user_id_str,
                                                at_user_nickname=at_user_data.get(
                                                    "nickname"
                                                ),
                                                at_user_home_page_url=at_user_data.get(
                                                    "home_page_url"
                                                ),
                                            )
                                            db.add(at_user_db)
                                else:
                                    logger.warning(
                                        f"评论 {comment_id_str} 的 at_users 列表包含非字典元素: {at_user_data}"
                                    )

                            # 删除不再存在的 @ 用户关系 (使用异步方式)
                            ids_to_delete = existing_at_user_ids - current_at_user_ids
                            if ids_to_delete:
                                stmt = select(XhsCommentAtUser).filter(
                                    XhsCommentAtUser.comment_id == comment_id_str,
                                    XhsCommentAtUser.at_user_id.in_(ids_to_delete),
                                )
                                result = await db.execute(stmt)
                                for at_user in result.scalars().all():
                                    await db.delete(at_user)

                        except Exception as e_at:
                            logger.error(
                                f"处理评论 {comment_id_str} 的 @ 用户时出错: {e_at}",
                                exc_info=True,
                            )
                            # 可以选择回滚部分操作或继续，这里选择继续

                    elif at_users_data:  # 如果字段存在但不是列表
                        logger.warning(
                            f"评论 {comment_id_str} 的 at_users 字段不是列表: {at_users_data}"
                        )

                # 递归处理子评论 (并行异步处理)
                sub_comments_list = comment_data.get("sub_comments", [])
                if isinstance(sub_comments_list, list) and sub_comments_list:
                    # 使用asyncio.gather进行并行处理子评论
                    import asyncio

                    sub_comment_tasks = []
                    for sub_comment_data in sub_comments_list:
                        if isinstance(sub_comment_data, dict):
                            # 传入当前评论的 ID 作为子评论的 parent_id
                            sub_comment_tasks.append(
                                _process_and_store_comment_async(
                                    sub_comment_data, parent_id=comment_id_str
                                )
                            )
                        else:
                            logger.warning(
                                f"主评论 {comment_id_str} 的 sub_comments 列表包含非字典元素: {sub_comment_data}"
                            )

                    # 等待所有子评论处理完成
                    if sub_comment_tasks:
                        await asyncio.gather(*sub_comment_tasks)
                elif sub_comments_list:  # 如果字段存在但不是列表
                    logger.warning(
                        f"主评论 {comment_id_str} 的 sub_comments 字段不是列表: {sub_comments_list}"
                    )

            # 4. 并行处理主评论
            import asyncio

            main_comment_tasks = []
            logger.info(f"开始处理 {len(note_all_comment)} 条主评论及其子评论")

            for main_comment_data in note_all_comment:
                if isinstance(main_comment_data, dict):
                    main_comment_tasks.append(
                        _process_and_store_comment_async(main_comment_data)
                    )
                else:
                    logger.warning(
                        f"输入的主评论列表包含非字典元素: {main_comment_data}"
                    )

            # 并行执行所有主评论处理任务
            if main_comment_tasks:
                await asyncio.gather(*main_comment_tasks)

            # 5. 提交事务
            await db.commit()  # 异步提交所有更改
            logger.info(
                f"成功处理评论，新增 {stored_count} 条，更新 {updated_count} 条，总处理评论数: {len(processed_comment_ids)}"
            )

        except Exception as e:
            await db.rollback()  # 发生任何错误时异步回滚事务
            error_detail = f"{str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
            logger.error(f"从爬虫存储评论过程中发生错误: {error_detail}")
            # 此处不应再次 raise，避免中断调用流程
