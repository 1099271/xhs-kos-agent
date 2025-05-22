import typer
import asyncio

app = typer.Typer()

from app.utils.logger import app_logger as logger


@app.command()
def tag_cli():
    logger.info("开始执行tag_cli")
