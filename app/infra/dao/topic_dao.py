import traceback
from datetime import datetime

from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infra.models.topic_models import XhsTopicDiscussion, XhsTopicsResponse
from app.utils.logger import app_logger as logger


class TopicDAO:
    def __init__(self):
        pass

    async def store_topics(
        db: AsyncSession,
        req_info: Dict[str, Any],
        topics_response: XhsTopicsResponse,
    ) -> List[XhsTopicDiscussion]:
        """存储话题数据，确保幂等性操作"""
        try:
            # 获取话题数据
            topics_data = topics_response.data.topic_list

            if not topics_data:
                logger.warning("请求体中缺少有效的话题数据")
                return []

            logger.info(f"开始处理话题数据，共 {len(topics_data)} 个话题")

            # 获取当前日期（只保留到日期部分）
            current_date = datetime.now().date()

            # 收集所有话题名称
            topic_names = [topic.name for topic in topics_data]

            # 查询当天已存在的话题记录 (Async version)
            stmt = select(XhsTopicDiscussion).filter(
                XhsTopicDiscussion.topic_name.in_(topic_names),
                XhsTopicDiscussion.record_date == current_date,
            )
            result = await db.execute(stmt)
            existing_topics_list = result.scalars().all()

            existing_topics = {
                (
                    topic.topic_name,
                    (
                        topic.record_date.date()
                        if isinstance(topic.record_date, datetime)
                        else topic.record_date
                    ),
                ): topic
                for topic in existing_topics_list
            }

            logger.info(f"找到 {len(existing_topics)} 条当天已存在的话题记录")

            # 存储话题数据
            stored_topics = []

            for topic_item in topics_data:
                try:
                    # 转换浏览量为整数
                    view_num = (
                        int(topic_item.view_num) if topic_item.view_num.isdigit() else 0
                    )

                    # 转换smart为布尔值
                    smart = topic_item.smart.lower() == "true"

                    # 检查是否存在当天的记录
                    # Ensure record_date from DB is compared as date object if current_date is a date object
                    key_to_check = (topic_item.name, current_date)
                    existing_topic = existing_topics.get(key_to_check)

                    if existing_topic:
                        # 更新现有记录
                        existing_topic.topic_type = topic_item.type
                        existing_topic.view_num = view_num
                        existing_topic.smart = smart
                        logger.info(f"更新话题记录: {topic_item.name}")
                        stored_topics.append(existing_topic)
                    else:
                        # 创建新记录
                        new_topic = XhsTopicDiscussion(
                            topic_name=topic_item.name,
                            topic_type=topic_item.type,
                            view_num=view_num,
                            smart=smart,
                            record_date=current_date,  # Store as date object
                        )
                        db.add(new_topic)  # add is synchronous
                        stored_topics.append(new_topic)
                        logger.info(f"创建新话题记录: {topic_item.name}")

                except Exception as e:
                    logger.error(f"处理话题时出错 {topic_item.name}: {str(e)}")
                    continue  # Continue with the next item

            # 提交事务
            try:
                await db.flush()
                await db.commit()
                logger.info(f"成功处理并存储 {len(stored_topics)} 条话题数据")
                return stored_topics
            except Exception as e:
                await db.rollback()
                error_detail = f"提交事务时出错: {str(e)}\\n{''.join(traceback.format_tb(e.__traceback__))}"
                logger.error(error_detail)
                logger.warning("由于事务提交错误，可能有部分数据未能成功存储")
                return []

        except Exception as e:
            # This rollback might also be handled by get_async_db if the exception propagates
            await db.rollback()
            error_detail = f"{str(e)}\\n{''.join(traceback.format_tb(e.__traceback__))}"
            logger.error(f"存储话题过程中发生错误: {error_detail}")
            raise  # Re-raise the exception so get_async_db can also see it and rollback if it hasn't already
