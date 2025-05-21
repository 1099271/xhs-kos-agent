import typer
import asyncio

# import click # No longer directly needed

app = typer.Typer()

from app.utils.logger import app_logger as logger
from app.services.topic.topic_service import TopicService
from app.services.note.note_service import NoteService


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
    logger.info(f"正在获取改标签相关的笔记列表")
    note_service = NoteService()
    res_notes = await note_service.get_notes_by_topic_tag(tag, num, use_coze=False)
    logger.info(f"Done! 共获取到了 {len(res_notes)} 个笔记")


# 3. 补全没有笔记详情的笔记内容
@app.command()
def finish_note_detail_cli():
    asyncio.run(finish_note_detail_cli_async())


async def finish_note_detail_cli_async():
    logger.info(f"正在获取笔记详情")
    note_service = NoteService()
    await note_service.finish_note_detail()
