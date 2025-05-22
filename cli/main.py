import typer

from cli.xhs.note import app as xhs_note_app
from cli.llm.tag import app as llm_tag_app

app = typer.Typer()
app.add_typer(xhs_note_app, name="xhs_note")
app.add_typer(llm_tag_app, name="llm_tag")
if __name__ == "__main__":
    app()
