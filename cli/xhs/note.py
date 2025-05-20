import typer
import asyncio

# import click # No longer directly needed

app = typer.Typer()

from app.utils.logger import app_logger as logger
from app.services.topic.topic_service import TopicService


# @app.command()
# def hello(name: str):
#     print(f"Hello xhs_note {name}!")


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
