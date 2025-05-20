import os
import typer
import asyncio
from app.infra.db.async_database import async_engine

from cli.xhs.note import app as xhs_note_app


app = typer.Typer()
app.add_typer(xhs_note_app, name="xhs_note")

if __name__ == "__main__":
    app()
