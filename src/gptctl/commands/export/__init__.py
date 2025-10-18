import typer
from .json import app as exp_json_app
from .markdown import app as exp_md_app
from .extract import app as exp_partial

app = typer.Typer(
    help="See individual command --help for details", no_args_is_help=True
)
app.add_typer(exp_json_app)
app.add_typer(exp_md_app)
app.add_typer(exp_partial)