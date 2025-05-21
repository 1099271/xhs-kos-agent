from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.models.note_models import (
    XhsNote,
    XhsNoteDetail,
)
from app.infra.models.author_models import XhsAuthor
from app.infra.models.keyword_models import XhsKeywordGroupNote
from app.infra.dao.keyword_dao import KeywordDAO
from app.schemas.note_schemas import XhsSearchResponse
from typing import List, Dict, Any
from datetime import datetime
import traceback
from sqlalchemy import select
import json

from app.utils.logger import app_logger as logger


class NoteDAO:
    @staticmethod
    async def store_coze_search_note_list(
        db: AsyncSession,
        req_info: Dict[str, Any],
        search_response: XhsSearchResponse,
    ) -> List[XhsNote]:
        """存储搜索结果数据，确保幂等性操作"""
        stored_notes = []

        # 在开始前确保会话是干净的
        await db.rollback()

        try:
            # 1. 首先收集所有需要处理的note_ids和author_ids
            note_ids = [note.note_id for note in search_response.data]
            author_ids = [note.author_user_id for note in search_response.data]

            logger.info(f"开始处理 {len(note_ids)} 条笔记数据")

            # 2. 批量查询已存在的笔记和作者
            existing_notes = {}
            existing_authors = {}

            # 查询笔记
            try:
                stmt = select(XhsNote).filter(XhsNote.note_id.in_(note_ids))
                result = await db.execute(stmt)
                notes = result.scalars().all()
                existing_notes = {note.note_id: note for note in notes}
                logger.info(f"找到 {len(existing_notes)} 条已存在的笔记")
            except Exception as e:
                logger.error(f"查询笔记信息时出错: {str(e)}")

            # 查询作者
            try:
                stmt = select(XhsAuthor).filter(
                    XhsAuthor.author_user_id.in_(author_ids)
                )
                result = await db.execute(stmt)
                authors = result.scalars().all()
                existing_authors = {author.author_user_id: author for author in authors}
                logger.info(f"找到 {len(existing_authors)} 个已存在的作者")
            except Exception as e:
                logger.error(f"查询作者信息时出错: {str(e)}")

                # 尝试单独查询每个作者，以便找出问题所在
                for author_id in author_ids:
                    try:
                        stmt = select(XhsAuthor).filter(
                            XhsAuthor.author_user_id == author_id
                        )
                        result = await db.execute(stmt)
                        author = result.scalars().first()
                        if author:
                            existing_authors[author.author_user_id] = author
                    except Exception as e2:
                        logger.error(f"查询单个作者 {author_id} 时出错: {str(e2)}")

            # 3. 获取或创建关键词群组
            keyword_group = None
            existing_associations = set()

            keywords = [req_info.get("keywords")] if req_info.get("keywords") else []
            if keywords:
                # 确保关键词是字符串
                # keywords = [str(k) for k in keywords if k]
                try:

                    keyword_group = await KeywordDAO.get_or_create_keyword_group(
                        db, keywords
                    )

                    # 只有当关键词群组创建成功且有有效ID时才查询关联关系
                    if keyword_group and keyword_group.group_id > 0:
                        # 批量查询已存在的关联关系
                        stmt = select(XhsKeywordGroupNote.note_id).filter(
                            XhsKeywordGroupNote.group_id == keyword_group.group_id,
                            XhsKeywordGroupNote.note_id.in_(note_ids),
                        )
                        result = await db.execute(stmt)
                        existing_associations = {note_id for (note_id,) in result.all()}
                        logger.info(
                            f"关键词群组: {keywords}, 已存在关联关系数量: {len(existing_associations)}"
                        )
                except Exception as e:
                    logger.error(f"处理关键词群组时出错: {str(e)}")
                    keyword_group = None
                    existing_associations = set()

            # 4. 处理每个笔记
            for note_item in search_response.data:
                try:
                    # 检查 author_user_id 是否为空
                    if not note_item.author_user_id:
                        logger.error(
                            f"笔记 {getattr(note_item, 'note_id', '未知')} 的 author_user_id 为空，跳过处理"
                        )
                        continue

                    # 处理作者信息
                    author_data = {
                        "author_user_id": str(note_item.author_user_id),
                        "author_nick_name": (
                            str(note_item.author_nick_name)
                            if note_item.author_nick_name
                            else ""
                        ),
                        "author_avatar": (
                            str(note_item.author_avatar)
                            if note_item.author_avatar
                            else ""
                        ),
                        "author_home_page_url": (
                            str(note_item.author_home_page_url)
                            if note_item.author_home_page_url
                            else ""
                        ),
                        "author_desc": "",  # 添加默认值
                        "author_interaction": 0,  # 根据数据库结构设置默认值为0
                        "author_ip_location": None,
                        "author_red_id": None,
                        "author_tags": None,
                        "author_fans": 0,
                        "author_follows": 0,
                        "author_gender": None,
                    }

                    # 获取或更新作者
                    author = existing_authors.get(note_item.author_user_id)
                    if author:
                        # 更新现有作者信息
                        for key, value in author_data.items():
                            if hasattr(author, key):
                                setattr(author, key, value)
                        author.updated_at = datetime.now()
                        logger.info(f"更新作者信息: {author.author_user_id}")
                    else:
                        # 创建新作者
                        author = XhsAuthor(**author_data)
                        db.add(author)
                        existing_authors[author.author_user_id] = author
                        logger.info(f"创建新作者: {author.author_user_id}")

                    # 准备笔记数据（确保数值类型正确）
                    note_data = {
                        "note_id": str(note_item.note_id) if note_item.note_id else "",
                        "author_user_id": str(note_item.author_user_id),
                        "note_url": (
                            str(note_item.note_url) if note_item.note_url else ""
                        ),
                        "note_xsec_token": (
                            str(note_item.note_xsec_token)
                            if note_item.note_xsec_token
                            else ""
                        ),
                        "note_display_title": (
                            str(note_item.note_display_title)
                            if note_item.note_display_title
                            else ""
                        ),
                        "note_cover_url_pre": (
                            str(note_item.note_cover_url_pre)
                            if note_item.note_cover_url_pre
                            else ""
                        ),
                        "note_cover_url_default": (
                            str(note_item.note_cover_url_default)
                            if note_item.note_cover_url_default
                            else ""
                        ),
                        "note_cover_width": (
                            int(note_item.note_cover_width)
                            if note_item.note_cover_width
                            and str(note_item.note_cover_width).isdigit()
                            else None
                        ),
                        "note_cover_height": (
                            int(note_item.note_cover_height)
                            if note_item.note_cover_height
                            and str(note_item.note_cover_height).isdigit()
                            else None
                        ),
                        "note_liked_count": (
                            int(note_item.note_liked_count)
                            if note_item.note_liked_count
                            and str(note_item.note_liked_count).isdigit()
                            else 0
                        ),
                        "note_liked": (
                            bool(note_item.note_liked)
                            if note_item.note_liked is not None
                            else False
                        ),
                        "note_card_type": (
                            str(note_item.note_card_type)
                            if note_item.note_card_type
                            else ""
                        ),
                        "note_model_type": (
                            str(note_item.note_model_type)
                            if note_item.note_model_type
                            else ""
                        ),
                        "author_nick_name": (
                            str(note_item.author_nick_name)
                            if note_item.author_nick_name
                            else ""
                        ),
                        "author_avatar": (
                            str(note_item.author_avatar)
                            if note_item.author_avatar
                            else ""
                        ),
                        "author_home_page_url": (
                            str(note_item.author_home_page_url)
                            if note_item.author_home_page_url
                            else ""
                        ),
                    }

                    # 获取或更新笔记
                    note = existing_notes.get(note_item.note_id)
                    if note:
                        # 更新现有笔记
                        for key, value in note_data.items():
                            if hasattr(note, key):
                                setattr(note, key, value)
                        note.updated_at = datetime.now()
                        logger.info(f"更新笔记: {note.note_id}")
                    else:
                        # 创建新笔记
                        note = XhsNote(**note_data)
                        db.add(note)
                        existing_notes[note.note_id] = note
                        logger.info(f"创建新笔记: {note.note_id}")

                    # 同步存储或更新笔记详情
                    note_detail_data = {
                        "note_id": note.note_id,
                        "note_url": note.note_url,  # 从笔记中获取URL
                        "author_user_id": note.author_user_id,
                        "note_last_update_time": datetime.now(),
                        "note_create_time": datetime.now(),
                        "note_model_type": note.note_model_type,  # 从笔记中获取模型类型
                        "note_card_type": note.note_card_type,  # 从笔记中获取卡片类型
                        "note_display_title": note.note_display_title,  # 从笔记中获取标题
                        "note_desc": None,
                        "comment_count": 0,
                        "note_liked_count": note.note_liked_count,  # 从笔记中获取点赞数
                        "share_count": 0,
                        "collected_count": 0,
                        "video_id": None,
                        "video_h266_url": None,
                        "video_a1_url": None,
                        "video_h264_url": None,
                        "video_h265_url": None,
                        "note_duration": None,
                        "note_image_list": None,
                        "note_tags": None,
                        "note_liked": note.note_liked,  # 从笔记中获取是否点赞
                        "collected": False,
                    }

                    # 获取或更新笔记详情
                    stmt = select(XhsNoteDetail).filter(
                        XhsNoteDetail.note_id == note.note_id
                    )
                    result = await db.execute(stmt)
                    note_detail = result.scalars().first()
                    if note_detail:
                        # 更新现有笔记详情
                        for key, value in note_detail_data.items():
                            if hasattr(note_detail, key):
                                setattr(note_detail, key, value)
                        note_detail.updated_at = datetime.now()
                        logger.info(f"更新笔记详情: {note_detail.note_id}")
                    else:
                        # 创建新笔记详情
                        note_detail = XhsNoteDetail(**note_detail_data)
                        db.add(note_detail)
                        logger.info(f"创建新笔记详情: {note_detail.note_id}")

                    stored_notes.append(note)

                    # 处理关键词群组关联
                    if (
                        keywords
                        and keyword_group
                        and keyword_group.group_id > 0
                        and note.note_id not in existing_associations
                    ):
                        try:
                            association = XhsKeywordGroupNote(
                                note_id=note.note_id,
                                group_id=keyword_group.group_id,  # 使用整数类型，不需要转换为字符串
                                retrieved_at=datetime.now(),
                            )
                            db.add(association)
                            existing_associations.add(note.note_id)
                            logger.info(f"创建关键词关联: {note.note_id} -> {keywords}")
                        except Exception as e:
                            logger.error(f"创建关键词关联时出错: {str(e)}")

                except Exception as e:
                    logger.error(
                        f"处理笔记时出错 {getattr(note_item, 'note_id', '未知')}: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
                    )
                    continue

            # 5. 提交事务
            try:
                # 每100条记录提交一次，避免事务过大
                await db.flush()
                await db.commit()
                logger.info(f"成功处理并存储 {len(stored_notes)} 条笔记数据")
            except Exception as e:
                await db.rollback()
                logger.error_detail = f"提交事务时出错: {str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
                logger.error(logger.error_detail)
                # 不抛出异常，而是返回已处理的笔记
                logger.warning("由于事务提交错误，可能有部分数据未能成功存储")

        except Exception as e:
            await db.rollback()
            logger.error_detail = (
                f"{str(e)}\n{''.join(traceback.format_tb(e.__traceback__))}"
            )
            logger.error(f"存储过程中发生错误: {logger.error_detail}")
            raise

        return stored_notes

    async def store_spider_note_list(
        db: AsyncSession,
        tag: str,
        notes: List[Dict[str, Any]],
    ) -> List[XhsNote]:
        """存储爬虫获取的笔记列表数据，确保幂等性操作"""
        stored_notes_result = []
        await db.rollback()  # 确保会话干净

        try:
            if not notes:
                logger.info("没有笔记数据需要处理。")
                return []

            note_ids = [note.get("id") for note in notes if note.get("id")]
            author_ids = [
                note.get("note_card", {}).get("user", {}).get("user_id")
                for note in notes
                if note.get("note_card", {}).get("user", {}).get("user_id")
            ]

            logger.info(
                f"开始处理 {len(note_ids)} 条来自爬虫的笔记数据，关联标签: {tag}"
            )

            existing_notes_dict = {}
            existing_authors_dict = {}

            if note_ids:
                try:
                    stmt = select(XhsNote).filter(XhsNote.note_id.in_(note_ids))
                    result = await db.execute(stmt)
                    existing_notes = result.scalars().all()
                    existing_notes_dict = {n.note_id: n for n in existing_notes}
                    logger.info(f"找到 {len(existing_notes_dict)} 条已存在的笔记")
                except Exception as e:
                    logger.error(f"查询笔记信息时出错: {str(e)}")

            if author_ids:
                try:
                    stmt = select(XhsAuthor).filter(
                        XhsAuthor.author_user_id.in_(author_ids)
                    )
                    result = await db.execute(stmt)
                    existing_authors = result.scalars().all()
                    existing_authors_dict = {
                        a.author_user_id: a for a in existing_authors
                    }
                    logger.info(f"找到 {len(existing_authors_dict)} 个已存在的作者")
                except Exception as e:
                    logger.error(f"查询作者信息时出错: {str(e)}")

            keyword_group = None
            existing_associations = set()
            if tag:
                try:
                    keyword_group = await KeywordDAO.get_or_create_keyword_group(
                        db, [tag]
                    )
                    if keyword_group and keyword_group.group_id > 0 and note_ids:
                        stmt = select(XhsKeywordGroupNote.note_id).filter(
                            XhsKeywordGroupNote.group_id == keyword_group.group_id,
                            XhsKeywordGroupNote.note_id.in_(note_ids),
                        )
                        result = await db.execute(stmt)
                        existing_associations = {
                            note_id_tuple[0] for note_id_tuple in result.all()
                        }
                        logger.info(
                            f"标签 '{tag}' (群组ID: {keyword_group.group_id}) 已关联笔记数量: {len(existing_associations)}"
                        )
                except Exception as e:
                    logger.error(f"处理标签 '{tag}' 时出错: {str(e)}")
                    keyword_group = None  # 出错则不进行关联

            for note_item_data in notes:
                try:
                    # 从根级别获取xsec_token

                    note_id = note_item_data.get("id")
                    note_xsec_token = str(note_item_data.get("xsec_token", ""))
                    if not note_id or not note_xsec_token:
                        logger.warning(
                            f"笔记缺少ID或xsec_token，跳过: {note_item_data.get('note_card', {}).get('display_title', '未知标题')}"
                        )
                        continue

                    note_card = note_item_data.get("note_card", {})
                    user_info = note_card.get("user", {})
                    author_user_id = user_info.get("user_id")

                    if not author_user_id:
                        logger.warning(f"笔记 {note_id} 的作者ID为空，跳过处理")
                        continue

                    # 确保author_user_id是字符串
                    author_user_id = str(author_user_id)

                    # 从用户信息中获取xsec_token作为备用
                    user_xsec_token = str(user_info.get("xsec_token", ""))

                    author_data = {
                        "author_user_id": author_user_id,
                        "author_nick_name": str(
                            user_info.get("nickname")
                            or user_info.get("nick_name")
                            or ""
                        ),
                        "author_avatar": str(user_info.get("avatar", "")),
                        "author_home_page_url": f"https://www.xiaohongshu.com/user/profile/{author_user_id}?xsec_token={user_xsec_token}&xsec_source=pc_note",  # 可以尝试拼接
                        "author_desc": "",
                        "author_interaction": 0,
                        "author_ip_location": None,
                        "author_red_id": None,
                        "author_tags": None,
                        "author_fans": 0,
                        "author_follows": 0,
                        "author_gender": None,
                    }

                    author = existing_authors_dict.get(author_user_id)
                    if author:
                        for key, value in author_data.items():
                            if (
                                hasattr(author, key) and value is not None
                            ):  # 确保只更新非None值
                                setattr(author, key, value)
                        author.updated_at = datetime.now()
                    else:
                        author = XhsAuthor(**author_data)
                        db.add(author)
                        existing_authors_dict[author_user_id] = author
                        logger.info(f"创建新作者: {author_user_id}")

                    interact_info = note_card.get("interact_info", {})
                    cover_info = note_card.get("cover", {})

                    note_liked_count_str = interact_info.get("liked_count", "0")
                    note_liked_count = (
                        int(note_liked_count_str)
                        if note_liked_count_str.isdigit()
                        else 0
                    )

                    collected_count_str = interact_info.get("collected_count", "0")
                    collected_count = (
                        int(collected_count_str) if collected_count_str.isdigit() else 0
                    )

                    comment_count_str = interact_info.get("comment_count", "0")
                    comment_count = (
                        int(comment_count_str) if comment_count_str.isdigit() else 0
                    )

                    shared_count_str = interact_info.get("shared_count", "0")
                    shared_count = (
                        int(shared_count_str) if shared_count_str.isdigit() else 0
                    )

                    note_main_data = {
                        "note_id": str(note_id),
                        "author_user_id": author_user_id,
                        "note_url": f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={note_xsec_token}&xsec_source=pc_note",
                        "note_xsec_token": note_xsec_token,
                        "note_display_title": str(note_card.get("display_title", "")),
                        "note_cover_url_pre": str(cover_info.get("url_pre", "")),
                        "note_cover_url_default": str(
                            cover_info.get("url_default", "")
                        ),
                        "note_cover_width": (
                            int(cover_info.get("width"))
                            if cover_info.get("width")
                            else None
                        ),
                        "note_cover_height": (
                            int(cover_info.get("height"))
                            if cover_info.get("height")
                            else None
                        ),
                        "note_liked_count": note_liked_count,
                        "note_liked": bool(interact_info.get("liked", False)),
                        "note_card_type": str(
                            note_card.get("type", "normal")
                        ),  # 默认为 normal
                        "note_model_type": str(
                            note_item_data.get("model_type", "note")
                        ),  # 默认为 note
                        "author_nick_name": author_data["author_nick_name"],
                        "author_avatar": author_data["author_avatar"],
                        "author_home_page_url": author_data["author_home_page_url"],
                    }

                    note_obj = existing_notes_dict.get(note_id)
                    if note_obj:
                        for key, value in note_main_data.items():
                            if hasattr(note_obj, key) and value is not None:
                                setattr(note_obj, key, value)
                        note_obj.updated_at = datetime.now()
                    else:
                        note_obj = XhsNote(**note_main_data)
                        db.add(note_obj)
                        existing_notes_dict[note_id] = note_obj
                        logger.info(f"创建新笔记: {note_id}")

                    # 处理笔记详情
                    publish_time_info = note_card.get("corner_tag_info", [])
                    publish_time_str = None
                    if (
                        publish_time_info
                        and isinstance(publish_time_info, list)
                        and len(publish_time_info) > 0
                    ):
                        # 假设第一个 corner_tag_info 且 type 为 publish_time 是发布时间
                        for p_info in publish_time_info:
                            if p_info.get("type") == "publish_time":
                                publish_time_str = p_info.get("text")
                                break

                    note_create_time = None  # 默认为空
                    if publish_time_str:
                        try:
                            # 尝试解析完整日期格式 (YYYY-MM-DD)
                            try:
                                note_create_time = datetime.strptime(
                                    publish_time_str, "%Y-%m-%d"
                                )
                            except ValueError:
                                # 如果是 MM-DD 格式，添加当前年份
                                current_year = datetime.now().year
                                note_create_time = datetime.strptime(
                                    f"{current_year}-{publish_time_str}", "%Y-%m-%d"
                                )
                        except (ValueError, TypeError) as e:
                            logger.warning(
                                f"笔记 {note_id} 的发布时间解析失败: {publish_time_str}, 错误: {str(e)}"
                            )

                    image_list_db = None
                    if note_card.get("image_list"):
                        try:
                            image_list_db = json.dumps(
                                [
                                    {
                                        "url": (
                                            img.get("info_list", [{}])[0].get("url")
                                            if img.get("info_list")
                                            else None
                                        ),  # 取第一个info_list的url
                                        "height": img.get("height"),
                                        "width": img.get("width"),
                                    }
                                    for img in note_card.get("image_list")
                                ]
                            )
                        except Exception as e:
                            logger.error(
                                f"序列化 image_list 失败: {note_id}, error: {e}"
                            )

                    # 视频相关信息处理
                    video_id = None
                    video_h266_url = None
                    video_a1_url = None
                    video_h264_url = None
                    video_h265_url = None
                    note_duration = None

                    # 判断是否为视频类型
                    is_video = note_card.get("type") == "video"
                    if is_video:
                        note_obj.note_model_type = "video"

                    note_detail_data = {
                        "note_id": note_obj.note_id,
                        "note_url": note_obj.note_url,
                        "author_user_id": note_obj.author_user_id,
                        "note_last_update_time": datetime.now(),  # 详情的更新时间
                        "note_create_time": note_create_time,  # 笔记的发布时间
                        "note_model_type": note_obj.note_model_type,
                        "note_card_type": note_obj.note_card_type,
                        "note_display_title": note_obj.note_display_title,
                        "note_desc": None,  # 爬虫数据中无直接的 note_desc，可以后续通过 get_note_info 补充
                        "comment_count": comment_count,
                        "note_liked_count": note_obj.note_liked_count,
                        "share_count": shared_count,
                        "collected_count": collected_count,
                        "video_id": video_id,
                        "video_h266_url": video_h266_url,
                        "video_a1_url": video_a1_url,
                        "video_h264_url": video_h264_url,
                        "video_h265_url": video_h265_url,
                        "note_duration": note_duration,
                        "note_image_list": image_list_db,  # 存储 image_list
                        "note_tags": None,  # 爬虫的 search_some_note 结果不直接包含笔记标签
                        "note_liked": note_obj.note_liked,
                        "collected": bool(interact_info.get("collected", False)),
                    }

                    stmt_detail = select(XhsNoteDetail).filter(
                        XhsNoteDetail.note_id == note_obj.note_id
                    )
                    result_detail = await db.execute(stmt_detail)
                    note_detail_obj = result_detail.scalars().first()

                    if note_detail_obj:
                        for key, value in note_detail_data.items():
                            if hasattr(note_detail_obj, key) and value is not None:
                                setattr(note_detail_obj, key, value)
                        note_detail_obj.updated_at = datetime.now()
                    else:
                        note_detail_obj = XhsNoteDetail(**note_detail_data)
                        db.add(note_detail_obj)
                        logger.info(f"创建新笔记详情: {note_detail_obj.note_id}")

                    stored_notes_result.append(note_obj)

                    if (
                        tag
                        and keyword_group
                        and keyword_group.group_id > 0
                        and note_obj.note_id not in existing_associations
                    ):
                        try:
                            association = XhsKeywordGroupNote(
                                note_id=note_obj.note_id,
                                group_id=keyword_group.group_id,
                                retrieved_at=datetime.now(),
                            )
                            db.add(association)
                            existing_associations.add(note_obj.note_id)
                        except Exception as e:
                            logger.error(f"创建笔记与标签关联时出错: {str(e)}")

                except Exception as e:
                    logger.error(
                        f"处理来自爬虫的笔记时出错 {note_item_data.get('id', '未知ID')}: {str(e)}\\n{traceback.format_exc()}"
                    )
                    continue

            try:
                await db.flush()
                await db.commit()
                logger.info(
                    f"成功处理并存储 {len(stored_notes_result)} 条来自爬虫的笔记数据"
                )
            except Exception as e:
                await db.rollback()
                logger.error(f"提交事务时出错: {str(e)}\\n{traceback.format_exc()}")
                logger.warning("由于事务提交错误，可能有部分爬虫笔记数据未能成功存储")

        except Exception as e:
            await db.rollback()
            logger.error(
                f"存储爬虫笔记过程中发生严重错误: {str(e)}\\n{traceback.format_exc()}"
            )
            # 根据实际情况决定是否向上抛出异常
            # raise

        return stored_notes_result
