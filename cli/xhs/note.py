import typer
import asyncio

# import click # No longer directly needed

app = typer.Typer()

from app.utils.logger import app_logger as logger
from app.services.topic.topic_service import TopicService
from app.services.note.note_list_service import (
    get_notes_by_topic_tag,
    finish_note_detail,
)
from app.services.comment.comment_service import (
    finish_note_comments,
)


# 1. 通过特定标签获取标签浏览量
@app.command()
def get_xhs_topics_cli(  # Synchronous wrapper
    tag: str = typer.Option(..., "--tag", "-t", help="搜索的标签")
):
    """
    根据某个关键词获取Coze上的关联词浏览量
    """
    asyncio.run(get_xhs_topics_cli_async(tag))  # Call asyncio.run internally


async def get_xhs_topics_cli_async(tag: str):  # Actual async logic
    logger.info(f"正在获取该话题详细信息")
    topic_service = TopicService()
    res_topics = await topic_service.get_topics(tag)
    logger.info(f"Done! 共获取到了 {len(res_topics)} 个话题")


# 2. 通过特定标签获取笔记列表
@app.command()
def get_xhs_note_by_topic_cli(
    tag: str = typer.Option(..., "--tag", "-t", help="搜索的标签"),
    num: int = typer.Option(..., "--num", "-n", help="获取的笔记数量"),
):
    """
    根据某个话题获取该话题下的所有笔记
    """
    asyncio.run(get_xhs_note_by_topic_cli_async(tag, num))


async def get_xhs_note_by_topic_cli_async(tag: str, num: int):
    logger.info(f"正在获取标签相关的笔记列表")
    res_notes = await get_notes_by_topic_tag(tag, num, use_coze=False)
    logger.info(f"Done! 共获取到了 {len(res_notes)} 个笔记")


# 3. 补全没有笔记详情的笔记内容
@app.command()
def get_note_detail_cli(
    use_crawler: bool = typer.Option(
        False,
        "--use-crawler",
        "-c",
        help="使用爬虫替代Coze获取笔记详情（默认使用Coze）",
    )
):
    if use_crawler:
        use_coze = False
    else:
        use_coze = True
    """
    补全没有详情内容的笔记
    """
    asyncio.run(get_note_detail_cli_async(use_coze))


async def get_note_detail_cli_async(use_coze: bool = False):
    logger.info(f"正在获取笔记详情，使用{'Coze API' if use_coze else '爬虫'}")
    processed_count = await finish_note_detail(use_coze=use_coze)
    logger.info(f"完成笔记详情补全，共处理 {processed_count} 条笔记")


# 4. 获取笔记评论内容
@app.command()
def get_xhs_note_comments_cli(
    use_crawler: bool = typer.Option(
        False,
        "--use-crawler",
        "-c",
        help="使用爬虫替代Coze获取笔记详情（默认使用Coze）",
    )
):
    """
    获取笔记评论内容
    """
    if use_crawler:
        use_coze = False
    else:
        use_coze = True
    """
    补全没有详情内容的笔记
    """
    asyncio.run(get_note_comments_cli_async(use_coze))


async def get_note_comments_cli_async(use_coze: bool = False):
    logger.info(f"正在获取笔记评论内容，使用{'Coze API' if use_coze else '爬虫'}")
    processed_count = await finish_note_comments(use_coze=use_coze)
    logger.info(f"完成笔记评论内容获取，共处理 {processed_count} 条笔记")
